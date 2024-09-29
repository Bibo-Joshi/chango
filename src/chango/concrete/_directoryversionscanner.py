#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
import itertools
import re
from pathlib import Path
from typing import NamedTuple, override

from .._changenoteinfo import ChangeNoteInfo
from .._utils.filename import FileName
from .._utils.types import PathLike, VUIDInput
from .._version import Version
from ..abc import VersionScanner
from ..helpers import ensure_uid

_DEFAULT_PATTERN = re.compile(r"(?P<uid>[^_]+)_(?P<date>[\d-]+)")


class _VersionInfo(NamedTuple):
    date: dtm.date
    directory: Path


class DirectoryVersionScanner(VersionScanner):
    """Implementation of a version scanner that assumes that change notes are stored in
    subdirectories named after the version identifier.

    Args:
        base_directory: The base directory to scan for version directories.
        unreleased_directory: The directory that contains unreleased changes. If
            :meth:`path.Path.is_dir` returns :obj:`False` for this directory, it will be assumed
            to be a subdirectory of the base directory.
        directory_pattern: The pattern to match version directories against. Must contain one named
            group ``uid`` for the version identifier and a second named group for the ``date`` for
            the date of the version release in ISO format.

    Attributes:
        base_directory: The base directory to scan for version directories.
        directory_pattern: The pattern to match version directories against.
        unreleased_directory: The directory that contains unreleased changes.

    """

    def __init__(
        self,
        base_directory: PathLike,
        unreleased_directory: PathLike,
        directory_pattern: str | re.Pattern[str] = _DEFAULT_PATTERN,
    ):
        self.directory_pattern: re.Pattern[str] = re.compile(directory_pattern)

        self.base_directory: Path = Path(base_directory)
        if not self.base_directory.is_dir():
            raise ValueError(f"Base directory '{self.base_directory}' does not exist.")

        if (path := Path(unreleased_directory)).is_dir():
            self.unreleased_directory: Path = path
        else:
            self.unreleased_directory = self.base_directory / unreleased_directory

        self.__available_versions: dict[str, _VersionInfo] | None = None

    @property
    def _available_versions(self) -> dict[str, _VersionInfo]:
        # Simple Cache for the available versions
        if self.__available_versions is not None:
            return self.__available_versions

        self.__available_versions = {}
        for directory in self.base_directory.iterdir():
            if not directory.is_dir() or not (
                match := self.directory_pattern.match(directory.name)
            ):
                continue

            uid = match.group("uid")
            date = dtm.date.fromisoformat(match.group("date"))
            self.__available_versions[uid] = _VersionInfo(date, directory)

        return self.__available_versions

    def _get_available_version(self, uid: str) -> Version:
        return Version(uid=uid, date=self._available_versions[uid].date)

    @override
    def is_available(self, uid: VUIDInput) -> bool:
        if uid is None:
            return self.has_unreleased_changes()
        return ensure_uid(uid) in self._available_versions

    @override
    def has_unreleased_changes(self) -> bool:
        """Implementation of :meth:`chango.abc.VersionScanner.has_unreleased_changes`.
        Checks if :attr:`unreleased_directory` contains any files.
        """
        try:
            next(file.is_file() for file in self.unreleased_directory.iterdir())
            return True
        except StopIteration:
            return False

    @override
    def get_latest_version(self) -> Version:
        """Implementation of :meth:`chango.abc.VersionScanner.get_latest_version`.

        Important:
            If the release date is available for all versions, the latest version is determined
            based on the release date. Otherwise, and in case of multiple releases on the same day,
            lexicographical comparison of the version identifiers is employed.
        """
        if all(vi.date is not None or uid is None for uid, vi in self._available_versions.items()):
            uid: str = max(
                self._available_versions, key=lambda uid: (self._available_versions[uid].date, uid)
            )
        else:
            uid = max(self._available_versions)

        return self._get_available_version(uid)

    @override
    def get_available_versions(
        self, start_from: VUIDInput = None, end_at: VUIDInput = None
    ) -> tuple[Version, ...]:
        """Implementation of :meth:`chango.abc.VersionScanner.get_available_versions`.

        Important:
            Limiting the version range by
            :paramref:`~chango.abc.VersionScanner.get_available_versions.start_from` and
            :paramref:`~chango.abc.VersionScanner.get_available_versions.end_at` is based on
            lexicographical comparison of the version identifiers.

        Returns:
            The available versions within the specified range.
        """
        start = ensure_uid(start_from)
        end = ensure_uid(end_at)
        return tuple(
            self._get_available_version(uid)
            for uid in self._available_versions
            if (start is None or uid >= start) and (end is None or uid <= end)
        )

    def _get_file_names(self, uid: VUIDInput) -> tuple[str, ...]:
        directory = (
            self._available_versions[ensure_uid(uid)].directory
            if uid
            else self.unreleased_directory
        )

        return tuple(change.name for change in directory.iterdir() if change.is_file())

    @override
    def lookup_change_note(self, uid: str) -> ChangeNoteInfo:
        try:
            version, file_name = next(
                (self._get_available_version(version_uid) if version_uid else None, name)
                for version_uid in itertools.chain(self._available_versions, (None,))
                for name in self._get_file_names(version_uid)
                if uid == FileName.from_string(name).uid
            )
            directory = (
                self._available_versions[version.uid].directory
                if version
                else self.unreleased_directory
            )
        except StopIteration as exc:
            raise ValueError(f"Change note '{uid}' not found in any version.") from exc

        return ChangeNoteInfo(uid, version, directory / file_name)

    @override
    def get_version(self, uid: str) -> Version:
        return self._get_available_version(uid)

    @override
    def get_changes(self, uid: VUIDInput) -> tuple[str, ...]:
        return tuple(FileName.from_string(name).uid for name in self._get_file_names(uid))

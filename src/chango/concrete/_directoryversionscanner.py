#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
import datetime as dtm
import inspect
import itertools
import re
from pathlib import Path
from typing import NamedTuple, override

from .._changenoteinfo import ChangeNoteInfo
from .._utils.filename import FileName
from .._utils.types import PathLike, VUIDInput
from .._version import Version
from ..abc import VersionScanner
from ..error import ValidationError
from ..helpers import ensure_uid

_DEFAULT_PATTERN = re.compile(r"(?P<uid>[^_]+)_(?P<date>[\d-]+)")


class _VersionInfo(NamedTuple):
    date: dtm.date
    directory: Path


class _FileInfo(NamedTuple):
    uid: str
    file: Path


def _make_relative_to(base: Path, path: Path) -> Path:
    if path.is_absolute():
        return path.resolve().absolute()
    return (base / path).resolve().absolute()


class DirectoryVersionScanner(VersionScanner):
    """Implementation of a version scanner that assumes that change notes are stored in
    subdirectories named after the version identifier.

    Args:
        base_directory (:obj:`str` | :class:`~pathlib.Path`): The base directory to scan for
            version directories.

            Important:
                If the path is relative, it will be resolved relative to the
                directory of the calling module.

                .. admonition:: Example

                    If you build your :class:`DirectoryVersionScanner` within
                    ``/home/user/project/chango.py``,
                    passing ``base_directory="changes"`` will resolve to
                    ``/home/user/project/changes``.
        unreleased_directory (:obj:`str` | :class:`~pathlib.Path`): The directory that contains
            unreleased changes.

            Important:
                If :meth:`pathlib.Path.is_dir` returns :obj:`False` for this
                directory, it will be assumed to be a subdirectory of the
                :paramref:`base_directory`.
        directory_pattern (:obj:`str` | :obj:`re.Pattern`, optional): The pattern to match version
            directories against. Must contain one named group ``uid`` for the version identifier
            and a second named group for the ``date`` for the date of the version release in ISO
            format.

    Attributes:
        base_directory (:class:`~pathlib.Path`): The base directory to scan for version
            directories.
        directory_pattern (:obj:`re.Pattern`): The pattern to match version directories against.
        unreleased_directory (:class:`~pathlib.Path`): The directory that contains unreleased
            changes.

    """

    def __init__(
        self,
        base_directory: PathLike,
        unreleased_directory: PathLike,
        directory_pattern: str | re.Pattern[str] = _DEFAULT_PATTERN,
    ):
        self.directory_pattern: re.Pattern[str] = re.compile(directory_pattern)

        caller_dir = Path(inspect.stack()[1].filename).resolve().absolute().parent
        self.base_directory: Path = _make_relative_to(caller_dir, Path(base_directory))
        if not self.base_directory.is_dir():
            raise ValueError(f"Base directory '{self.base_directory}' does not exist.")

        if (path := Path(unreleased_directory)).is_dir():
            self.unreleased_directory: Path = path.resolve().absolute()
        else:
            self.unreleased_directory = self.base_directory / unreleased_directory
            if not self.unreleased_directory.is_dir():
                raise ValueError(
                    f"Unreleased directory '{self.unreleased_directory}' does not exist."
                )

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
        try:
            return Version(uid=uid, date=self._available_versions[uid].date)
        except KeyError as exc:
            raise ValueError(f"Version '{uid}' not available.") from exc

    def invalidate_caches(self) -> None:
        self.__available_versions = None

    @override
    def is_available(self, uid: VUIDInput) -> bool:
        if uid is None:
            return self.has_unreleased_changes()

        if (version := self._available_versions.get(ensure_uid(uid))) is None:
            return False

        if isinstance(uid, Version):
            return version.date == uid.date

        return True

    @override
    def has_unreleased_changes(self) -> bool:
        """Implementation of :meth:`chango.abc.VersionScanner.has_unreleased_changes`.
        Checks if :attr:`unreleased_directory` contains any files.

        Returns:
            :obj:`bool`: :obj:`True` if there are unreleased changes, :obj:`False` otherwise.
        """
        return bool(self._get_file_names(None))

    @override
    def get_latest_version(self) -> Version:
        """Implementation of :meth:`chango.abc.VersionScanner.get_latest_version`.

        Important:
            In case of multiple releases on the same day,
            lexicographical comparison of the version identifiers is employed.

        Returns:
            :class:`~chango.Version`: The latest version
        """
        return self._get_available_version(
            max(
                self._available_versions, key=lambda uid: (self._available_versions[uid].date, uid)
            )
        )

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
            Tuple[:class:`~chango.Version`]: The available versions within the specified range.
        """
        start = ensure_uid(start_from)
        end = ensure_uid(end_at)
        return tuple(
            self._get_available_version(uid)
            for uid in self._available_versions
            if (start is None or uid >= start) and (end is None or uid <= end)
        )

    def _get_file_names(self, uid: VUIDInput) -> tuple[_FileInfo, ...]:
        try:
            directory = (
                self._available_versions[ensure_uid(uid)].directory
                if uid
                else self.unreleased_directory
            )
        except KeyError as exc:
            raise ValueError(f"Version '{uid}' not available.") from exc

        out = []
        # Sorting is an undocumented implementation detail for now!
        for change in sorted(directory.iterdir()):
            if not change.is_file():
                continue

            with contextlib.suppress(ValidationError):
                name = FileName.from_string(change.name)
                out.append(_FileInfo(name.uid, change))

        return tuple(out)

    @override
    def lookup_change_note(self, uid: str) -> ChangeNoteInfo:
        try:
            version, file_name = next(
                (
                    self._get_available_version(version_uid) if version_uid else None,
                    file_info.file.name,
                )
                for version_uid in itertools.chain(self._available_versions, (None,))
                for file_info in self._get_file_names(version_uid)
                if uid == file_info.uid
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
        return tuple(file_info.uid for file_info in self._get_file_names(uid))

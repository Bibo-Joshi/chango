#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import override

from .._utils.types import VUIDInput
from ..abc import ChangeNote, ChanGo, VersionHistory, VersionNote
from ._directoryversionscanner import DirectoryVersionScanner


class DirectoryChanGo[VHT: VersionHistory, VNT: VersionNote, CNT: ChangeNote](
    ChanGo[DirectoryVersionScanner, VHT, VNT, CNT]
):
    """Implementation of the :class:`~chango.abc.ChanGo` interface that works with
    :class:`~chango.concrete.DirectoryVersionScanner` and assumes that change notes are stored in
    subdirectories named after the version identifier.

    Args:
        change_note_type: The type of change notes to load. Must be a subclass of
            :class:`~chango.abc.ChangeNote`.
        version_note_type: The type of version notes to load. Must be a subclass of
            :class:`~chango.abc.VersionNote`.
        version_history_type: The type of version histories to load. Must be a subclass of
            :class:`~chango.abc.VersionHistory`.
        scanner: The version scanner to use.
        directory_format: Reverse of
            :paramref:`~chango.concrete.DirectoryVersionScannerdirectory_pattern`.
            Must be a string that can be used
            with :meth:`str.format` and contain at least one named field ``uid`` for the version
            identifier and optionally a second named field ``date`` for the date of the version
            release in ISO format. The default value is compatible with the default value of
            :paramref:`~chango.concrete.DirectoryVersionScannerdirectory_pattern`.

    Attributes:
        directory_format: The format string used to create version directories.
    """

    def __init__(
        self: "DirectoryChanGo[VHT, VNT, CNT]",
        change_note_type: type[CNT],
        version_note_type: type[VNT],
        version_history_type: type[VHT],
        scanner: DirectoryVersionScanner,
        directory_format: str = "{uid}_{date}",
    ):
        self._scanner: DirectoryVersionScanner = scanner
        self.directory_format: str = directory_format
        self.change_note_type: type[CNT] = change_note_type
        self.version_note_type: type[VNT] = version_note_type
        self.version_history_type: type[VHT] = version_history_type

    @property
    @override
    def scanner(self) -> DirectoryVersionScanner:
        return self._scanner

    @override
    def build_template_change_note(self, slug: str, uid: str | None = None) -> CNT:
        return self.change_note_type.build_template(slug=slug, uid=uid)

    @override
    def build_version_note(self, version: VUIDInput) -> VNT:
        return self.version_note_type(version=version)

    @override
    def build_version_history(self) -> VHT:
        return self.version_history_type()

    @override
    def load_change_note(self, uid: str) -> CNT:
        return self.change_note_type.from_file(self.scanner.lookup_change_note(uid).file_path)

    @override
    def get_write_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        if version is None:
            directory = self.scanner.unreleased_directory
        else:
            version_obj = (
                self.scanner.get_version(version) if isinstance(version, str) else version
            )

            directory = self.scanner.base_directory / self.directory_format.format(
                uid=version_obj.uid, date=version_obj.date.isoformat()
            )

        directory.mkdir(parents=True, exist_ok=True)
        return directory

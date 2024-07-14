#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from pathlib import Path

from chango._utils.files import UTF8
from chango._utils.types import VUIDInput

from ._changenote import ChangeNote
from ._versionhistory import VersionHistory
from ._versionnote import VersionNote
from ._versionscanner import VersionScanner


class IO[VST: VersionScanner, VHT: VersionHistory, VNT: VersionNote, CNT: ChangeNote](abc.ABC):
    """Abstract base class for loading :class:`~chango.abc.ChangeNote`,
    :class:`~chango.abc.VersionNote` and :class:`~chango.abc.VersionHistory` objects as well
    as writing :class:`~chango.abc.ChangeNote` objects.
    """

    @property
    @abc.abstractmethod
    def scanner(self) -> VST:
        """The used :class:`~chango.abc.VersionScanner`."""

    @abc.abstractmethod
    def build_version_note(self, version: VUIDInput) -> VNT:
        """Build a new empty version note.

        Args:
            version: The version of the software project this note is for.
                May be :obj:`None` if the version is not yet released.
        """

    @abc.abstractmethod
    def build_version_history(self) -> VHT:
        """Build a new empty version history."""

    @abc.abstractmethod
    def load_change_note(self, uid: str) -> CNT:
        """Load a change note with the given identifier.

        Args:
            uid: The unique identifier or file name of the change note to load.
        """

    @abc.abstractmethod
    def get_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        """Determine the directory to write a change note to.

        Hint:
            Ideally, it should be ensured that the directory exists.

        Args:
            change_note: The change note to write or its UID.
            version: The version the change note belongs to. Maybe be
                :obj:`None` if the change note is not yet released.
        """

    def write_change_note(
        self, change_note: CNT, version: VUIDInput, encoding: str = UTF8
    ) -> Path:
        """Write a change note to disk.

        Args:
            change_note: The change note to write.
            version: The version the change note belongs to. Maybe be
                :obj:`None` if the change note is not yet released.
            encoding: The encoding to use for writing.

        Returns:
            The file path the change note was written to.
        """
        return change_note.to_file(
            self.get_directory(change_note=change_note, version=version), encoding=encoding
        )

    def load_version_note(self, version: VUIDInput) -> VersionNote:
        """Load a version note.

        Args:
            version: The version of the version note to load. May be :obj:`None` if the version is
                not yet released.
        """
        changes = self.scanner.get_changes(version)
        version_note = self.build_version_note(version=version)
        for change in changes:
            version_note.add_change_note(self.load_change_note(change))

        return version_note

    def load_version_history(
        self, start_from: VUIDInput = None, end_at: VUIDInput = None
    ) -> VersionHistory:
        """Load the version history.

        Important:
            Unreleased changes must be included in the returned version history, if available.

        Args:
            start_from: The version to start from. If :obj:`None`, start from the
                earliest available version.
            end_at: The version to end at. If :obj:`None`, end at the latest available
                version, *including* unreleased changes.

        Returns:
            The loaded version history.
        """
        version_history = self.build_version_history()
        for version in self.scanner.get_available_versions(start_from=start_from, end_at=end_at):
            version_history.add_version_note(self.load_version_note(version))

        return version_history

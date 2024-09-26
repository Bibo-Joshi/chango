#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from pathlib import Path
from typing import TYPE_CHECKING

from .._utils.files import UTF8
from .._utils.types import VUIDInput
from ._changenote import ChangeNote
from ._versionhistory import VersionHistory
from ._versionnote import VersionNote
from ._versionscanner import VersionScanner

if TYPE_CHECKING:
    from .. import Version


class ChanGo[VST: VersionScanner, VHT: VersionHistory, VNT: VersionNote, CNT: ChangeNote](abc.ABC):
    """Abstract base class for loading :class:`~chango.abc.ChangeNote`,
    :class:`~chango.abc.VersionNote` and :class:`~chango.abc.VersionHistory` objects as well
    as writing :class:`~chango.abc.ChangeNote` objects.
    This class holds the main interface for interacting with the version history and change notes.
    """

    @property
    @abc.abstractmethod
    def scanner(self) -> VST:
        """The used :class:`~chango.abc.VersionScanner`."""

    @abc.abstractmethod
    def build_template_change_note(self, slug: str, uid: str | None = None) -> CNT:
        """Build a template change note for the concrete change note type.

        Tip:
            This will be used to create a new change note in the CLI.

        Args:
            slug: The slug to use for the change note.
            uid: The unique identifier for the change note or :obj:`None` to generate a random one.

        Returns:
            The :class:`ChangeNote` object.
        """

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
    def get_write_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        """Determine the directory to write a change note to.

        Important:
            * It should be ensured that the directory exists.
            * The :paramref:`version` does *not* need to be already available. In that case, it's
              expected that :paramref:`version` is of type :class:`~chango.Version`.

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
            self.get_write_directory(change_note=change_note, version=version), encoding=encoding
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
            Unreleased changes are included in the returned version history, if available.

        Args:
            start_from: The version to start from. If :obj:`None`, start from the
                earliest available version.
            end_at: The version to end at. If :obj:`None`, end at the latest available
                version, *including* unreleased changes.

        Returns:
            The loaded version history.
        """
        version_history = self.build_version_history()

        if self.scanner.has_unreleased_changes():
            version_history.add_version_note(self.load_version_note(None))

        for version in self.scanner.get_available_versions(start_from=start_from, end_at=end_at):
            version_history.add_version_note(self.load_version_note(version))

        return version_history

    def release(self, version: "Version") -> bool:
        """Release a version.
        This calls :meth:`get_write_directory` for all unreleased change notes and moves the file
        if necessary.

        Args:
            version: The version to release.

        Returns:
            Whether a release was performed. If no unreleased changes are available, this method
            returns :obj:`False`.
        """
        if not self.scanner.has_unreleased_changes():
            return False
        for uid in self.scanner.get_changes(None):
            change_info = self.scanner.lookup_change_note(uid)
            write_dir = self.get_write_directory(uid, version)
            if change_info.path.parent != write_dir:
                change_info.path.rename(write_dir / change_info.path.name)

        return True

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
        """:class:`VST <typing.TypeVar>`: The :class:`~chango.abc.VersionScanner` used by this
        instance.
        """

    @abc.abstractmethod
    def build_template_change_note(self, slug: str, uid: str | None = None) -> CNT:
        """Build a template change note for the concrete change note type.

        Tip:
            This will be used to create a new change note in the CLI.

        Args:
            slug (:obj:`str`): The slug to use for the change note.
            uid (:obj:`str`, optional): The unique identifier for the change note or :obj:`None`
                to generate a random one.

        Returns:
            :class:`CNT <typing.TypeVar>`:The :class:`~chango.abc.ChangeNote` object.
        """

    @abc.abstractmethod
    def build_version_note(self, version: VUIDInput) -> VNT:
        """Build a new empty version note.

        Args:
            version (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version of the
                software project this note is for. May be :obj:`None` if the version is not yet
                released.

        Returns:
            :class:`VNT <typing.TypeVar>`: The :class:`~chango.abc.VersionNote` object.
        """

    @abc.abstractmethod
    def build_version_history(self) -> VHT:
        """:class:`VHT <typing.TypeVar>`: Build a new empty version history."""

    @abc.abstractmethod
    def load_change_note(self, uid: str) -> CNT:
        """Load a change note with the given identifier.

        Args:
            uid (:obj:`str`): The unique identifier or file name of the change note to load.

        Returns:
            :class:`CNT <typing.TypeVar>`: The :class:`~chango.abc.ChangeNote` object.
        """

    @abc.abstractmethod
    def get_write_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        """Determine the directory to write a change note to.

        Important:
            * It should be ensured that the directory exists.
            * The :paramref:`version` does *not* need to be already available. In that case, it's
              expected that :paramref:`version` is of type :class:`~chango.Version`.

        Args:
            change_note (:class:`CNT <typing.TypeVar>` | :obj:`str`): The change note to write or
                its UID.
            version (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version the change
                note belongs to. Maybe be :obj:`None` if the change note is not yet released.

        Returns:
            :class:`pathlib.Path`: The directory to write the change note to.
        """

    def write_change_note(
        self, change_note: CNT, version: VUIDInput, encoding: str = UTF8
    ) -> Path:
        """Write a change note to disk.

        Args:
            change_note (:class:`CNT <typing.TypeVar>` | :obj:`str`): The change note to write.
            version (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version the change
                note belongs to. Maybe be :obj:`None` if the change note is not yet released.
            encoding (:obj:`str`): The encoding to use for writing.

        Returns:
            :class:`pathlib.Path`: The file path the change note was written to.
        """
        return change_note.to_file(
            self.get_write_directory(change_note=change_note, version=version), encoding=encoding
        )

    def load_version_note(self, version: VUIDInput) -> VNT:
        """Load a version note.

        Args:
            version (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version of the
                version note to load. May be :obj:`None` if the version is not yet released.

        Returns:
            :class:`VNT <typing.TypeVar>`: The loaded :class:`~chango.abc.VersionNote`.
        """
        changes = self.scanner.get_changes(version)
        version_note = self.build_version_note(version=version)
        for change in changes:
            version_note.add_change_note(self.load_change_note(change))

        return version_note

    def load_version_history(self, start_from: VUIDInput = None, end_at: VUIDInput = None) -> VHT:
        """Load the version history.

        Important:
            By default, unreleased changes are included in the returned version history, if
            available.

        Args:
            start_from (:class:`~chango.Version` | :obj:`str`, optional): The version to start
                from. If :obj:`None`, start from the earliest available version.
            end_at (:class:`~chango.Version` | :obj:`str`, optional): The version to end at.
                If :obj:`None`, end at the latest available version, *including* unreleased
                changes.

        Returns:
            :class:`VHT <typing.TypeVar>`: The loaded version :class:`~chango.abc.VersionHistory`.
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
            version (:class:`~chango.Version`): The version to release.

        Returns:
            :obj:`bool`: Whether a release was performed. If no unreleased changes are available,
            this method returns :obj:`False`.
        """
        if not self.scanner.has_unreleased_changes():
            return False
        for uid in self.scanner.get_changes(None):
            change_info = self.scanner.lookup_change_note(uid)
            write_dir = self.get_write_directory(uid, version)
            if change_info.file_path.parent != write_dir:
                change_info.file_path.rename(write_dir / change_info.file_path.name)

        return True

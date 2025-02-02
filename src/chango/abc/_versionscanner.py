#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from collections.abc import Collection, Iterator

from .._changenoteinfo import ChangeNoteInfo
from .._utils.types import VUIDInput
from .._version import Version


class VersionScanner(Collection[Version]):
    """Abstract base class for a version scanner that can list available versions.

    Hint:
        Objects of this class can be used as :class:`~collections.abc.Collection` of versions
        as returned by the :meth:`get_available_versions` method.
    """

    def __contains__(self, x: object, /) -> bool:
        if x is None:
            return self.has_unreleased_changes()
        if not isinstance(x, str | Version):
            return False
        return self.is_available(x)

    def __iter__(self) -> Iterator[Version]:
        return iter(self.get_available_versions())

    def __len__(self) -> int:
        return len(self.get_available_versions())

    @abc.abstractmethod
    def is_available(self, uid: VUIDInput) -> bool:
        """Check if the version with the given identifier is available.

        Tip:
            :obj:`None` may be passed for convenience, but it's recommended that an implementation
            calls :meth:`has_unreleased_changes` internally.

        Args:
            uid (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version identifier to
                check.
        """

    @abc.abstractmethod
    def has_unreleased_changes(self) -> bool:
        """Check if there are changes in the repository that are not yet released in a version.

        Returns:
            :obj:`bool`: :obj:`True` if there are unreleased changes, :obj:`False` otherwise.
        """

    @abc.abstractmethod
    def get_latest_version(self) -> Version:
        """Get the latest version

        Returns:
            :class:`~chango.Version`: The latest version
        """

    @abc.abstractmethod
    def get_available_versions(
        self, start_from: VUIDInput = None, end_at: VUIDInput = None
    ) -> tuple[Version, ...]:
        """Get the available versions.

        Important:
            Unreleased changes must *not* be included in the returned version identifiers.

        Args:
            start_from (:class:`~chango.Version` | :obj:`str`, optional): The version identifier
                to start from. If :obj:`None`, start from the earliest available version.
            end_at (:class:`~chango.Version` | :obj:`str`, optional): The version identifier to end
                at. If :obj:`None`, end at the latest available version, *excluding* unreleased
                changes.

        Returns:
            Tuple[:class:`~chango.Version`]: The available versions.
        """

    @abc.abstractmethod
    def lookup_change_note(self, uid: str) -> ChangeNoteInfo:
        """Lookup a change note with the given identifier.

        Args:
            uid (:obj:`str`): The unique identifier or file name of the change note to lookup

        Returns:
            :class:`chango.ChangeNoteInfo`: The metadata about the change note specifying the file
                path and version it belongs to.
        """

    def get_version(self, uid: str) -> Version:
        """Get the version with the given identifier.

        Hint:
            The default implementation calls :meth:`get_available_versions`. Implementations may
            override this method to provide a more efficient way to get the version.

        Args:
            uid (:obj:`str`): The version identifier to get the version for.

        Returns:
            :class:`~chango.Version`: The version.

        Raises:
            ValueError: If the version with the given identifier is not available.
        """
        try:
            return next(version for version in self if version.uid == uid)
        except StopIteration as exc:
            raise ValueError(f"Version '{uid}' not available.") from exc

    @abc.abstractmethod
    def get_changes(self, uid: VUIDInput) -> tuple[str, ...]:
        """Get the changes either for a given version identifier or all available.

        Hint:
            To easily extract the UIDs from the change files,
            :meth:`chango.helpers.change_uid_from_file` can be used.

        Important:
            The returned UIDs must be in the order in which the changes were made.

        Args:
            uid (:class:`~chango.Version` | :obj:`str` | :obj:`None`): The version identifier to
                get the change files for. If :obj:`None`, get the change files for unreleased
                changes must be returned.

        Returns:
            Tuple[:obj:`str`]: UIDs of the changes corresponding to the version identifier.

        Raises:
            ValueError: If the version with the given identifier is not available.
        """

    def invalidate_caches(self) -> None:
        """Invalidate any internal caches that may be used by the implementation.

        Important:

            * This method is not required to do anything if the implementation does not use any
              caches. By default, it does nothing.
            * This method is called by :meth:`chango.abc.ChanGo.release` and
              :meth:`chango.abc.ChanGo.write_change_note` after the respective operation has been
              completed. This gives the implementation the opportunity to clear any caches that
              may have been affected by the operation.
        """

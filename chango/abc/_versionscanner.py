#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
import datetime as dtm
from collections.abc import Collection, Iterator

from chango._utils.types import VersionUID


class VersionScanner(Collection[str]):
    """Abstract base class for a version scanner that can list available versions.

    Hint:
        Objects of this class can be used as :class:`~collections.abc.Collection` of version
        identifier as returned by the :meth:`get_available_versions` method.
    """

    def __contains__(self, __x: object) -> bool:
        if not isinstance(__x, str):
            return False
        return self.is_available(__x)

    def __iter__(self) -> Iterator[str]:
        return iter(self.get_available_versions())

    def __len__(self) -> int:
        return len(self.get_available_versions())

    @abc.abstractmethod
    def is_available(self, uid: str) -> bool:
        """Check if the version with the given identifier is available.

        Args:
            uid: The version identifier to check.
        """

    @abc.abstractmethod
    def has_unreleased_changes(self) -> bool:
        """Check if there are changes in the repository that are not yet released in a version."""

    @abc.abstractmethod
    def get_latest_version(self) -> str:
        """Get the latest version identifier."""

    @abc.abstractmethod
    def get_available_versions(
        self, start_from: str | None = None, end_at: str | None = None
    ) -> tuple[str]:
        """Get the available version identifiers.

        Args:
            start_from: The version identifier to start from. If :obj:`None`, start from the
                earliest available version.
            end_at: The version identifier to end at. If :obj:`None`, end at the latest available
                version, including unreleased changes.
        """

    @abc.abstractmethod
    def get_changes(self, uid: VersionUID | None = None) -> tuple[str]:
        """Get the changes either for a given version identifier or all available.

        Hint:
            To easily extract the UIDs from the change files,
            :meth:`chango.helpers.change_uid_from_file` can be used.

        Important:
            The returned UIDs must be in the order in which the changes were made.

        Args:
            uid: The version identifier to get the change files for. If
                :attr:`~chango.constants.UNRELEASED`, get the change files for the latest version.
                If :obj:`None`, get all available change files.

        Returns:
            UIDs of the changes corresponding to the version identifier.
        """

    @abc.abstractmethod
    def get_release_date(self, uid: VersionUID) -> dtm.date | None:
        """Get the release date of a given version

        Args:
            uid: The version identifier to get the release date for. If
                :attr:`~chango.constants.UNRELEASED`, get the release date for the latest version.
        """

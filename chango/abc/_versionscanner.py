#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from collections.abc import Collection, Iterator


class VersionScanner[EAT](Collection[str]):
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
    def is_available(self, uid: str, extra_arguments: EAT | None = None) -> bool:
        """Check if the version with the given identifier is available.

        Args:
            uid: The version identifier to check.
            extra_arguments: Extra arguments to pass to the scanner, depending on the
                implementation.
        """

    @abc.abstractmethod
    def has_unreleased_changes(self, extra_arguments: EAT | None = None) -> bool:
        """Check if there are changes in the repository that are not yet released in a version.

        Args:
            extra_arguments: Extra arguments to pass to the scanner, depending on the
                implementation.
        """

    @abc.abstractmethod
    def get_latest_version(self, extra_arguments: EAT | None = None) -> str:
        """Get the latest version identifier.

        Args:
            extra_arguments: Extra arguments to pass to the scanner, depending on the
                implementation.
        """

    @abc.abstractmethod
    def get_available_versions(
        self, start_from: str | None = None, extra_arguments: EAT | None = None
    ) -> tuple[str]:
        """Get the available version identifiers.

        Args:
            start_from: The version identifier to start from. If None, start from the
                earliest available version.
            extra_arguments: Extra arguments to pass to the scanner, depending on the
                implementation.
        """

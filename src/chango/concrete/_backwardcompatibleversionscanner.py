#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
import contextlib
from collections.abc import Collection
from typing import override

from .._changenoteinfo import ChangeNoteInfo
from .._utils.types import VUIDInput
from .._version import Version
from ..abc import VersionScanner
from ..error import ChanGoError


class BackwardCompatibleVersionScanner(VersionScanner):
    """An Implementation of the :class:`~chango.abc.VersionScanner` interface that wraps multiple
    other implementations of :class:`~chango.abc.VersionScanner`.
    The purpose of this class is to ease transition between different version note formats in
    a project.

    Warning:
        This assumes that the versions available for each of the scanners are mutually exclusive,
        i.e. no two scanners can return the same version.

    Tip:
        Use together with :class:`~chango.concrete.BackwardCompatibleChanGo`.

    Args:
        scanners (Collection[:class:`~chango.abc.VersionScanner`]): The scanners to wrap.
    """

    def __init__(self, scanners: Collection[VersionScanner]):
        self._scanners = tuple(scanners)

    @override
    def is_available(self, uid: VUIDInput) -> bool:
        return any(scanner.is_available(uid) for scanner in self._scanners)

    @override
    def has_unreleased_changes(self) -> bool:
        return any(scanner.has_unreleased_changes() for scanner in self._scanners)

    @override
    def get_latest_version(self) -> Version:
        """Implementation of :meth:`chango.abc.VersionScanner.get_latest_version`.

        Important:
            The newest version is determined by the date of the version, not the order in which
            the scanners were passed to the constructor.

        Returns:
            :class:`~chango.Version`: The latest version
        """
        versions = []
        for scanner in self._scanners:
            with contextlib.suppress(ChanGoError):
                versions.append(scanner.get_latest_version())
        if not versions:
            raise ChanGoError("No versions available.")
        return max(versions, key=lambda v: v.date)

    @override
    def get_available_versions(
        self, start_from: VUIDInput = None, end_at: VUIDInput = None
    ) -> tuple[Version, ...]:
        return tuple(
            version
            for scanner in self._scanners
            for version in scanner.get_available_versions(start_from, end_at)
        )

    @override
    def lookup_change_note(self, uid: str) -> ChangeNoteInfo:
        """Lookup a change note with the given identifier.

        Args:
            uid (:obj:`str`): The unique identifier or file name of the change note to lookup

        Returns:
            :class:`chango.ChangeNoteInfo`: The metadata about the change note specifying the file
                path and version it belongs to.
        """
        for scanner in self._scanners:
            with contextlib.suppress(ChanGoError):
                return scanner.lookup_change_note(uid)
        raise ChanGoError(f"Change note '{uid}' not available.")

    @override
    def get_changes(self, uid: VUIDInput) -> tuple[str, ...]:
        for scanner in self._scanners:
            with contextlib.suppress(ChanGoError):
                return scanner.get_changes(uid)
        raise ChanGoError(f"Version '{uid}' not available.")

    @override
    def invalidate_caches(self) -> None:
        for scanner in self._scanners:
            scanner.invalidate_caches()

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
from collections.abc import Collection, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, override

from .._utils.types import VUIDInput
from ..abc import ChangeNote, ChanGo, VersionHistory, VersionNote, VersionScanner
from ..action import ChanGoActionData
from ..error import ChanGoError
from ._backwardcompatibleversionscanner import BackwardCompatibleVersionScanner

if TYPE_CHECKING:
    from .. import Version


class BackwardCompatibleChanGo[VHT: VersionHistory, VNT: VersionNote, CNT: ChangeNote](
    ChanGo["BackwardCompatibleVersionScanner", VHT, VNT, CNT]
):
    """An Implementation of the :class:`~chango.abc.ChanGo` interface that wraps multiple
    other implementations of :class:`~chango.abc.ChanGo`.
    The purpose of this class is to ease transition between different version note formats in
    a project.

    Args:
        scanner (:class:`~chango.concrete.BackwardCompatibleVersionScanner`): The version scanner
            to use.
        main_chango (:class:`~chango.abc.ChanGo`): The main :class:`~chango.abc.ChanGo` instance
            to use for creating new changes.
        legacy_changos (Collection[:class:`~chango.abc.ChanGo`]): A collection of legacy
            :class:`~chango.abc.ChanGo` instances to use for loading old changes.

    """

    def __init__(
        self,
        main_chango: "ChanGo[Any,VHT, VNT, CNT]",
        main_scanner: VersionScanner,
        legacy: Collection[tuple[ChanGo[Any, Any, Any, Any], VersionScanner]],
    ):
        self._main_chango = main_chango
        self._main_scanner = main_scanner
        self._legacy = tuple(legacy)
        self._scanner = BackwardCompatibleVersionScanner(
            (main_scanner, *tuple(x[1] for x in legacy))
        )

    @property
    def _legacy_changos(self) -> Iterator[ChanGo[Any, Any, Any, Any]]:
        return (x[0] for x in self._legacy)

    @property
    @override
    def scanner(self) -> "BackwardCompatibleVersionScanner":
        return self._scanner

    @override
    def build_template_change_note(self, slug: str, uid: str | None = None) -> CNT:
        """Calls :meth:`~chango.abc.ChanGo.build_template_change_note` on
        :paramref:`~chango.abc.BackwardCompatibleChanGo.main_chango`.
        """
        return self._main_chango.build_template_change_note(slug, uid)

    @override
    def build_version_note(self, version: Optional["Version"]) -> VNT:
        """Calls :meth:`~chango.abc.ChanGo.build_version_note`
        on :paramref:`~chango.abc.BackwardCompatibleChanGo.main_chango` or one of the legacy
        changos depending on the result of :meth:`~chango.abc.VersionScanner.is_available`.
        """
        for chango, scanner in ((self._main_chango, self._main_scanner), *self._legacy):
            if scanner.is_available(version):
                return chango.build_version_note(version)
        raise ChanGoError(f"Version {version} not found")

    @override
    def build_version_history(self) -> VHT:
        """Calls :meth:`~chango.abc.ChanGo.build_version_history`
        on :paramref:`~chango.abc.BackwardCompatibleChanGo.main_chango`.
        """
        return self._main_chango.build_version_history()

    @override
    def load_change_note(self, uid: str) -> CNT:
        """Load a change note with the given identifier.
        Tries to load the change note from the main chango first and then from the legacy changos.
        """
        for chango in (self._main_chango, *self._legacy_changos):
            with contextlib.suppress(ChanGoError):
                try:
                    return chango.load_change_note(uid)
                except ChanGoError as exc:
                    raise exc
        raise ChanGoError(f"Change note with uid {uid} not found")

    @override
    def get_write_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        """Calls :meth:`~chango.abc.ChanGo.get_write_directory`
        on :paramref:`~chango.abc.BackwardCompatibleChanGo.main_chango`.
        """
        return self._main_chango.get_write_directory(change_note, version)

    def build_github_event_change_note(
        self, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> CNT | None:
        """Calls :meth:`~chango.abc.ChanGo.build_github_event_change_note`
        on :paramref:`~chango.abc.BackwardCompatibleChanGo.main_chango`.
        """
        return self._main_chango.build_github_event_change_note(event, data)

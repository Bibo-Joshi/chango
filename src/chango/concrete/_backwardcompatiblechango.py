#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
from collections.abc import Collection
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, override

from .._utils.types import VUIDInput
from ..abc import ChangeNote, ChanGo, VersionHistory, VersionNote
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
        main_instance(:class:`~chango.abc.ChanGo`): The :class:`~chango.abc.ChanGo` instance that
            should be used for new version notes.
        legacy_instances(Collection[:class:`~chango.abc.ChanGo`]): A collection of
            :class:`~chango.abc.ChanGo` instances that should be used for loading older version
            notes.
    """

    def __init__(
        self,
        main_instance: "ChanGo[Any,VHT, VNT, CNT]",
        legacy_instances: Collection[ChanGo[Any, Any, Any, Any]],
    ):
        self._main_instance = main_instance
        self._legacy_instances = tuple(legacy_instances)
        self._scanner = BackwardCompatibleVersionScanner(
            (main_instance.scanner, *(chango.scanner for chango in self._legacy_instances))
        )

    @property
    @override
    def scanner(self) -> "BackwardCompatibleVersionScanner":
        """The :class:`~chango.concrete.BackwardCompatibleVersionScanner` instance that is used
        by this :class:`BackwardCompatibleChanGo`.

        Hint:
            The scanner is a composite of the scanners of
            :paramref:`~BackwardCompatibleChanGo.main_instance` and
            :paramref:`~BackwardCompatibleChanGo.legacy_instance`.
        """
        return self._scanner

    @override
    def build_template_change_note(self, slug: str, uid: str | None = None) -> CNT:
        """Calls :meth:`~chango.abc.ChanGo.build_template_change_note` on
        :paramref:`~BackwardCompatibleChanGo.main_instance`.
        """
        return self._main_instance.build_template_change_note(slug, uid)

    @override
    def build_version_note(self, version: Optional["Version"]) -> VNT:
        """Calls :meth:`~chango.abc.ChanGo.build_version_note`
        on :paramref:`~BackwardCompatibleChanGo.main_instance` or one of the legacy
        instances depending on the result of :meth:`~chango.abc.VersionScanner.is_available`.
        """
        for chango in (self._main_instance, *self._legacy_instances):
            if chango.scanner.is_available(version):
                return chango.build_version_note(version)
        raise ChanGoError(f"Version {version} not found")

    @override
    def build_version_history(self) -> VHT:
        """Calls :meth:`~chango.abc.ChanGo.build_version_history`
        on :paramref:`~BackwardCompatibleChanGo.main_instance`.
        """
        return self._main_instance.build_version_history()

    @override
    def load_change_note(self, uid: str) -> CNT:
        """Load a change note with the given identifier.
        Tries to load the change note from the main chango first and then from the legacy changos.
        """
        for chango in (self._main_instance, *self._legacy_instances):
            with contextlib.suppress(ChanGoError):
                return chango.load_change_note(uid)
        raise ChanGoError(f"Change note with uid {uid} not found")

    @override
    def get_write_directory(self, change_note: CNT | str, version: VUIDInput) -> Path:
        """Calls :meth:`~chango.abc.ChanGo.get_write_directory`
        on :paramref:`~BackwardCompatibleChanGo.main_instance`.
        """
        return self._main_instance.get_write_directory(change_note, version)

    def build_github_event_change_note(
        self, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> CNT | None:
        """Calls :meth:`~chango.abc.ChanGo.build_github_event_change_note`
        on :paramref:`~BackwardCompatibleChanGo.main_instance`.
        """
        return self._main_instance.build_github_event_change_note(event, data)

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, override

from .._utils.types import VUIDInput
from ..abc import ChangeNote, ChanGo, VersionHistory, VersionNote
from ..action import ChanGoActionData
from ._directoryversionscanner import DirectoryVersionScanner
from .sections import PullRequest, SectionChangeNote

if TYPE_CHECKING:
    from chango import Version


class DirectoryChanGo[VHT: VersionHistory, VNT: VersionNote, CNT: ChangeNote](
    ChanGo[DirectoryVersionScanner, VHT, VNT, CNT]
):
    """Implementation of the :class:`~chango.abc.ChanGo` interface that works with
    :class:`~chango.concrete.DirectoryVersionScanner` and assumes that change notes are stored in
    subdirectories named after the version identifier.

    Args:
        change_note_type (:class:`type`): The type of change notes to load. Must be a subclass of
            :class:`~chango.abc.ChangeNote`.
        version_note_type (:class:`type`): The type of version notes to load. Must be a subclass of
            :class:`~chango.abc.VersionNote`.
        version_history_type (:class:`type`): The type of version histories to load. Must be a
            subclass of :class:`~chango.abc.VersionHistory`.
        scanner (:class:`~chango.concrete.DirectoryVersionScanner`): The version scanner to use.
        directory_format (:obj:`str`, optional): Reverse of
            :paramref:`~chango.concrete.DirectoryVersionScannerdirectory_pattern`.
            Must be a string that can be used
            with :meth:`str.format` and contain at least one named field ``uid`` for the version
            identifier and optionally a second named field ``date`` for the date of the version
            release in ISO format. The default value is compatible with the default value of
            :paramref:`~chango.concrete.DirectoryVersionScannerdirectory_pattern`.

    Attributes:
        directory_format (:obj:`str`): The format string used to create version directories.
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
    def build_version_note(self, version: Optional["Version"]) -> VNT:
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
            if isinstance(version, str):
                try:
                    version_obj = self.scanner.get_version(version)
                except ValueError as exc:
                    raise TypeError(
                        f"Version '{version}' not available yet. To get the write directory for a "
                        "new version, pass the version as `change.Version` object."
                    ) from exc
            else:
                version_obj = version

            directory = self.scanner.base_directory / self.directory_format.format(
                uid=version_obj.uid, date=version_obj.date.isoformat()
            )

        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @override
    def build_github_event_change_note(
        self, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> CNT:
        """Implementation of :meth:`~chango.abc.ChanGo.build_github_event_change_note`.

        Important:
            By default, this will always call :meth:`chango.abc.ChangeNote.build_from_github_event`
            and does not check if a new change note is necessary.
            The only exception is when :paramref:`~DirectoryChanGo.change_note_type` is a subclass
            of :class:`~chango.concrete.sections.SectionChangeNote` and the ``data`` parameter is
            an instance of :class:`~chango.action.ChanGoActionData` with a parent pull request.
            In this case, the method will try to find an existing *unreleased* change note for the
            parent pull request and append the new information to it.
        """
        if (
            (change_note := self.change_note_type.build_from_github_event(event=event, data=data))
            is None
            or not isinstance(data, ChanGoActionData)
            or not data.parent_pull_request
            or not issubclass(self.change_note_type, SectionChangeNote)
        ):
            return change_note

        if not isinstance(change_note, SectionChangeNote):
            raise TypeError(
                f"Expected change note of type {SectionChangeNote}, got {type(change_note)}"
            )

        # Special handling for SectionChangeNote
        parent_pr = data.parent_pull_request

        # load all unreleased change notes and find the one for the parent pull request
        for existing_change_note in self.load_version_note(None).values():
            if parent_pr.number not in (pr.uid for pr in existing_change_note.pull_requests):
                continue

            # Append the PR information to the existing change note
            existing_change_note.pull_requests.append(
                PullRequest(
                    uid=str(parent_pr.number),
                    author_uid=data.parent_pull_request.author_login,
                    closes_threads=tuple(str(issue.number) for issue in data.linked_issues or ()),
                )
            )

            for section_name in change_note.SECTIONS:
                if not (new_value := getattr(change_note, section_name)):
                    continue
                if not (existing_value := getattr(existing_change_note, section_name)):
                    setattr(existing_change_note, section_name, new_value)
                else:
                    setattr(existing_change_note, section_name, f"{existing_value}\n{new_value}")

            return existing_change_note

        # return unchanged change note if no parent pull request found
        # mypy doesn't quite get that self.change_note_type is the same as CNT
        return change_note  # type: ignore[return-value]

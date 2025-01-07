#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from collections import defaultdict
from typing import TYPE_CHECKING, override

from ..._utils.strings import indent_multiline
from ...abc import VersionNote
from ...constants import MarkupLanguage
from ...error import UnsupportedMarkupError
from ._pullrequest import PullRequest
from ._sectionchangenote import SectionChangeNote

if TYPE_CHECKING:
    from chango import Version


class SectionVersionNote[V: (Version, None), SCN: SectionChangeNote](VersionNote[SCN, V]):
    """An implementation of :class:`~chango.abc.VersionNote` that works with
    :class:`~chango.concrete.sections.SectionChangeNote`.

    Important:
        Currently, only :attr:`~chango.constants.MarkupLanguage.RESTRUCTUREDTEXT` is supported.

    Args:
        section_change_note_type (\
            type[:class:`~chango.concrete.sections.SectionChangeNote`]): The type of
            the section change note to use.

            Hint:
                It will not be possible to add change notes of a different type to this version
                note.
    """

    def __init__(self, version: V, section_change_note_type: type[SCN]) -> None:
        super().__init__(version)  # type: ignore[arg-type]

        if section_change_note_type.MARKUP != MarkupLanguage.RESTRUCTUREDTEXT:
            raise UnsupportedMarkupError(
                "This version note currently only supports reStructuredText markup."
            )

        self._section_change_note_type = section_change_note_type
        self._sorted_sections = dict(
            sorted(section_change_note_type.SECTIONS.items(), key=lambda x: x[1].sort_order)
        )

    @override
    def __setitem__(self, key: str, value: SCN, /) -> None:
        if not isinstance(value, self._section_change_note_type):
            raise TypeError(
                f"Expected a {self._section_change_note_type} instance, got {type(value)}"
            )
        super().__setitem__(key, value)

    def _render_pr(self, pr: PullRequest) -> str:
        pr_url = self._section_change_note_type.get_pull_request_url(pr.uid)
        author = self._section_change_note_type.get_author_url(pr.author_uid)

        thread_links = [
            f"`#{thread_uid} <{self._section_change_note_type.get_thread_url(thread_uid)}>`_"
            for thread_uid in pr.closes_threads
        ]

        base = f"`#{pr.uid} <{pr_url}>`_ by `@{pr.author_uid} <{author}>`_"
        if not thread_links:
            return base
        return f"{base} closes {', '.join(thread_links)}"

    def _render_section_entry(
        self, content: str, pull_requests: tuple[PullRequest, ...] | None = None
    ) -> str:
        indented_content = f"- {indent_multiline(content, newlines=2)}"

        if not pull_requests:
            return indented_content

        pr_details = "; ".join(self._render_pr(pr) for pr in pull_requests)
        if "\n" not in content:
            return f"{indented_content} ({pr_details})"
        return f"{indented_content}\n\n  ({pr_details})"

    @override
    def render(self, markup: str) -> str:
        """Render the version note to a string by listing all contained change notes.
        Aggregates the content of all change notes for each section and renders them in the order
        defined by :attr:`~chango.concrete.sections.Section.sort_order`.

        Important:
            Currently, only :attr:`~chango.constants.MarkupLanguage.RESTRUCTUREDTEXT` is supported.
        """
        try:
            markup = MarkupLanguage.from_string(markup)
        except ValueError as exc:
            raise UnsupportedMarkupError(markup) from exc

        if markup != MarkupLanguage.RESTRUCTUREDTEXT:
            raise UnsupportedMarkupError(markup)

        section_contents: dict[str, str] = defaultdict(str)
        for change_note in self.values():
            for section_uid, section in self._sorted_sections.items():
                if section_content := getattr(change_note, section_uid):
                    section_contents[section_uid] = "\n".join(
                        (
                            section_contents[section_uid],
                            self._render_section_entry(
                                section_content,
                                change_note.pull_requests if section.render_pr_details else None,
                            ),
                        )
                    )

        return "\n\n".join(
            f"{section.title}\n{'-' * len(section.title)}\n{content}"
            for uid, section in self._sorted_sections.items()
            if (content := section_contents[uid])
        )

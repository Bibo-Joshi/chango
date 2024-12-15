#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import TYPE_CHECKING, NamedTuple, override

from ...abc import VersionNote
from ...constants import MarkupLanguage
from ...error import UnsupportedMarkupError
from ._pullrequest import PullRequest
from ._section import Section
from ._sectionchangenote import SectionChangeNote

if TYPE_CHECKING:
    from chango import Version


def _indent_multiline(text: str, indent: int = 2, newlines: int = 1) -> str:
    """Indent all lines of a multi-line string except the first one."""
    return (newlines * "\n").join(
        line if i == 0 else " " * indent + line for i, line in enumerate(text.splitlines())
    )


class _SectionEntry(NamedTuple):
    content: str
    change_note: SectionChangeNote
    pull_requests: tuple[PullRequest, ...]


class SectionVersionNote[V: (Version, None), SCN: SectionChangeNote](VersionNote[SCN, V]):
    @staticmethod
    def _render_pr(pr: PullRequest, change_note: SectionChangeNote) -> str:
        pr_url = change_note.get_pull_request_url(pr.uid)
        author = change_note.get_author_url(pr.author_uid)

        thread_links = [
            f"`#{thread_uid}` <{change_note.get_thread_url(thread_uid)}>`_"
            for thread_uid in pr.closes_threads
        ]

        base = f"`#{pr.uid} <{pr_url}>`_ by `@{pr.author_uid} <{author}>`_"
        if not thread_links:
            return base
        return f"{base} closes {', '.join(thread_links)}"

    @classmethod
    def _render_section_entry(cls, section_entry: _SectionEntry, section: Section) -> str:
        if not section.render_pr_details:
            return section_entry.content
        pr_details = "; ".join(
            cls._render_pr(pr, section_entry.change_note) for pr in section_entry.pull_requests
        )
        return f"{section_entry.content} ({pr_details})"

    @override
    def render(self, markup: str) -> str:
        try:
            markup = MarkupLanguage.from_string(markup)
        except ValueError as exc:
            raise UnsupportedMarkupError(markup) from exc

        if markup != MarkupLanguage.RESTRUCTUREDTEXT:
            raise UnsupportedMarkupError(markup)

        sections: dict[str, Section] = next(iter(self.values())).SECTIONS
        section_contents: dict[str, list[_SectionEntry]] = {
            section_uid: [] for section_uid in sections
        }
        for change_note in self.values():
            for section_uid in change_note.SECTIONS:
                if section_content := getattr(change_note, section_uid):
                    section_contents[section_uid].append(
                        _SectionEntry(
                            content=section_content,
                            pull_requests=change_note.pull_requests,
                            change_note=change_note,
                        )
                    )

        output = ""
        for section_uid, section_entries in sorted(
            section_contents.items(), key=lambda x: sections[x[0]].sort_order
        ):
            section = sections[section_uid]
            if not section_entries:
                continue
            output += f"\n{section.title}\n{'=' * len(section.title)}\n\n"
            for section_entry in section_entries:
                output += _indent_multiline(self._render_section_entry(section_entry, section))
                output += "\n\n"

        return output

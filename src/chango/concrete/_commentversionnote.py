#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import TYPE_CHECKING, override

from ..abc import VersionNote
from ..concrete import CommentChangeNote
from ..constants import MarkupLanguage

if TYPE_CHECKING:
    from chango import Version


def _indent_multiline(text: str, indent: int = 2) -> str:
    """Indent all lines of a multi-line string except the first one."""
    return "\n".join(
        line if i == 0 else " " * indent + line for i, line in enumerate(text.splitlines())
    )


class CommentVersionNote[V: (Version, None)](VersionNote[CommentChangeNote, V]):
    """A simple version note implementation that works with
    :class:`~chango.concrete.CommentChangeNote`.
    """

    @override
    def render(self, markup: str) -> str:
        """Render the version note to a string by listing all contained change notes separated
        by a newline.
        For markup languages Markdown, HTML and reStructuredText, the change notes will be
        rendered as unordered lists.

        Raises:
            :exc:`~chango.error.UnsupportedMarkupError`: If the ``markup`` parameter does not
                coincide with :attr:`chango.concrete.CommentChangeNote.MARKUP`
        """
        match MarkupLanguage.from_string(markup):
            case MarkupLanguage.MARKDOWN:
                return "\n".join(f"- {_indent_multiline(note.comment)}" for note in self.values())
            case MarkupLanguage.HTML:
                return (
                    "<ul>\n"
                    + "\n".join(f"<li>{note.comment}</li>" for note in self.values())
                    + "\n</ul>"
                )
            case MarkupLanguage.RESTRUCTUREDTEXT:
                return "\n".join(f"- {_indent_multiline(note.comment)}" for note in self.values())
            case _:
                return "\n".join(note.comment for note in self.values())

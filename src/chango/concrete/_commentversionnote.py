#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import TYPE_CHECKING, override

from .._utils.strings import indent_multiline
from ..abc import VersionNote
from ..concrete import CommentChangeNote
from ..constants import MarkupLanguage
from ..error import UnsupportedMarkupError

if TYPE_CHECKING:
    from chango import Version


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

        Args:
            markup (:obj:`str`): The markup language to use for rendering.

        Raises:
            :exc:`~chango.error.UnsupportedMarkupError`: If the ``markup`` parameter does not
                coincide with :attr:`chango.concrete.CommentChangeNote.MARKUP`

        Returns:
            :obj:`str`: The rendered version note.
        """
        try:
            markup = MarkupLanguage.from_string(markup)
        except ValueError as exc:
            raise UnsupportedMarkupError(markup) from exc

        match markup:
            case MarkupLanguage.MARKDOWN:
                return "\n".join(
                    f"- {indent_multiline(note.comment, indent=4, newlines=2)}"
                    for note in self.values()
                )
            case MarkupLanguage.HTML:
                return (
                    "<ul>\n"
                    + "\n".join(
                        f"<li>{note.comment.replace("\n", "<br>")}</li>" for note in self.values()
                    )
                    + "\n</ul>"
                )
            case MarkupLanguage.RESTRUCTUREDTEXT:
                return "\n".join(
                    f"- {indent_multiline(note.comment, newlines=2)}" for note in self.values()
                )
            case _:
                return "\n\n".join(note.comment for note in self.values())

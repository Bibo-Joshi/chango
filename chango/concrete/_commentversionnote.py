#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from chango._utils.files import UTF8
from chango.abc import VersionNote
from chango.concrete import CommentChangeNote
from chango.constants import MarkupLanguage
from chango.errors import UnsupportedMarkupError


class CommentVersionNote(VersionNote[CommentChangeNote]):
    """A simple version note implementation that works with
    :class:`~chango.concrete.CommentChangeNote`.
    """

    def render(self, markup: str, encoding: str = UTF8) -> str:
        """Render the version note to a string by listing all contained change notes separated
        by a newline.
        For markup languages Markdown, HTML and reStructuredText, the change notes will be
        rendered as unordered lists.

        Caution:
            The ``encoding`` parameter is currently ignored.

        Raises:
            :exc:`~chango.error.UnsupportedMarkupError`: If the ``markup`` parameter does not
                coincide with :attr:`chango.concrete.CommentChangeNote.MARKUP`
        """
        if markup != CommentChangeNote.MARKUP:
            raise UnsupportedMarkupError(
                f"Got unsupported markup '{markup}', can only render '{CommentChangeNote.MARKUP}'"
            )

        match MarkupLanguage.from_string(markup):
            case MarkupLanguage.MARKDOWN:
                return "\n".join(f"- {note.comment}" for note in self.values())
            case MarkupLanguage.HTML:
                return (
                    "<ul>\n"
                    + "\n".join(f"<li>{note.comment}</li>" for note in self.values())
                    + "\n</ul>"
                )
            case MarkupLanguage.RESTRUCTUREDTEXT:
                return "\n".join(f"- {note.comment}" for note in self.values())
            case _:
                return "\n".join(note.comment for note in self.values())

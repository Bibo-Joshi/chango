#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import string
from typing import override

from ..abc import VersionHistory, VersionNote
from ..constants import MarkupLanguage
from ..error import UnsupportedMarkupError


class HeaderVersionHistory[VNT: VersionNote](VersionHistory[VNT]):
    """A simple version history implementation that renders version notes by prefixing them with
    the version UID as header, followed by the release date if available.
    """

    @override
    def render(self, markup: str) -> str:
        """Does the rendering.

        Tip:
            Version notes are automatically sorted by release date before rendering. If unreleased
            changes are present, they are rendered first.

        Important:
            Currently, only Markdown, HTML and reStructuredText are supported as markup languages.

        Args:
            markup (:obj:`str`): The markup language to use for rendering.

        Returns:
            :obj:`str`: The rendered version history.

        Raises:
            :exc:`~chango.error.UnsupportedMarkupError`: If the ``markup`` parameter does not
                coincide with :attr:`~chango.constants.MarkupLanguage.MARKDOWN`,
                :attr:`~chango.constants.MarkupLanguage.HTML`, or
                :attr:`~chango.constants.MarkupLanguage.RESTRUCTUREDTEXT`
        """
        released_notes = list(filter(lambda note: note.version, self.values()))
        changes = sorted(
            released_notes,
            key=lambda note: note.date,  # type: ignore[arg-type,return-value]
            reverse=True,
        )
        match markup:
            case MarkupLanguage.MARKDOWN:
                tpl_str = "# $uid\n*$date*\n\n$comment"
            case MarkupLanguage.HTML:
                tpl_str = "<h1>$uid</h1>\n<i>$date</i>\n\n$comment"
            case MarkupLanguage.RESTRUCTUREDTEXT:
                tpl_str = "$uid\n$rst_underline\n*$date*\n\n$comment"
            case _:
                raise UnsupportedMarkupError(
                    f"Got unsupported markup '{markup}', can only render Markdown, HTML, "
                    f"and reStructuredText"
                )

        if None in self:
            changes.insert(0, self[None])

        template = string.Template(tpl_str)
        return "\n\n".join(
            template.substitute(
                uid=note.uid or "Unreleased",  # type: ignore[truthy-function]
                rst_underline="=" * len(note.uid or "Unreleased"),  # type: ignore[truthy-function,arg-type]
                date=(
                    "unknown" if (note.date is None) else note.date.isoformat()  # type: ignore[attr-defined]
                ),
                comment=note.render(markup),
            )
            for note in changes
        )

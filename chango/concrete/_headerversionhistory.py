#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import string

from chango._utils.files import UTF8
from chango.abc import VersionHistory, VersionNote
from chango.constants import MarkupLanguage
from chango.errors import UnsupportedMarkupError


class HeaderVersionHistory[VNT: VersionNote](VersionHistory[VNT]):
    """A simple version history implementation that renders version notes by prefixing them with
    the version UID as header, followed by the release date if available.
    """

    def render(self, markup: str, encoding: str = UTF8) -> str:
        """Does the rendering.

        Important:
            Currently, only Markdown, HTML and reStructuredText are supported as markup languages.

        Warning:
            Version notes are sorted only if all of them have a date. Otherwise, they are rendered
            in the order they were added to the version history.

        """
        has_dates = all(note.date for note in self.values())
        if has_dates:
            changes = sorted(
                self.values(),
                key=lambda note: note.date,  # type: ignore[reportArgumentType]
            )
            match markup:
                case MarkupLanguage.MARKDOWN:
                    tpl_str = "#$uid\n*$date*\n\n$comment"
                case MarkupLanguage.HTML:
                    tpl_str = "<h1>$uid</h1>\n<i>$date</i>\n\n$comment"
                case MarkupLanguage.RESTRUCTUREDTEXT:
                    tpl_str = "$uid\n=====\n$date\n\n$comment"
                case _:
                    raise UnsupportedMarkupError(
                        f"Got unsupported markup '{markup}', can only render Markdown, HTML, "
                        f"and reStructuredText"
                    )
        else:
            changes = self.values()
            match markup:
                case MarkupLanguage.MARKDOWN:
                    tpl_str = "#$uid\n\n$comment"
                case MarkupLanguage.HTML:
                    tpl_str = "<h1>$uid</h1>\n\n$comment"
                case MarkupLanguage.RESTRUCTUREDTEXT:
                    tpl_str = "$uid\n=====\n\n$comment"
                case _:
                    raise UnsupportedMarkupError(
                        f"Got unsupported markup '{markup}', can only render Markdown, HTML, "
                        f"and reStructuredText"
                    )

        template = string.Template(tpl_str)
        return "\n\n".join(
            template.substitute(
                uid=note.uid,
                date=note.date.isoformat() if note.date else "",
                comment=note.render(markup, encoding),
            )
            for note in changes
        )

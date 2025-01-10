#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT


from rich.errors import StyleSyntaxError
from rich.style import Style
from rich.text import Span, Text


class RichConverter:
    """Minimal effort implementation of converting text with python-rich formatting options
    to rST formatted text."""

    def __init__(self, rich_text: str) -> None:
        self.rich_text = rich_text
        self.spans: list[Span] = []
        self.plain_text: str = ""

    def parse_rich_text(self) -> None:
        """Reads the rich-formatted text. Parses it to plain text + a list of formatting entities.
        Those are then stored in :attr:`spans` and :attr:`plain_text`.
        """
        text = Text.from_markup(self.rich_text)

        # Extract plain text
        self.plain_text = text.plain

        # Extract formatting data
        self.spans.extend(text.spans)

    @staticmethod
    def _process_rich_style(plain_text: str, style: Style) -> str:
        """Given a text and a rich Style object, return the corresponding rst string.
        If the style is not known, the plain text is returned unchanged.
        """
        rst_text = plain_text

        if style.italic:
            rst_text = f"*{rst_text}*"
        if style.bold:
            rst_text = f"**{rst_text}**"
        if style.link:
            if not style.link.startswith("https://chango.readthedocs.io/"):
                rst_text = f"`{rst_text} <{style.link}>`_"
            else:
                try:
                    reference = style.link.rsplit("#", 1)[1]
                except IndexError:
                    reference = style.link.rsplit("/", 1)[1].removesuffix(".html")
                rst_text = f":attr:`{reference}`"

        return rst_text

    @staticmethod
    def _process_rich_string(plain_text: str, style: str) -> str:
        """Given a text and a rich style in string representation, return the corresponding rst
        string.
        If the style is not known, the plain text is returned unchanged.
        """
        rst_text = plain_text

        if style == "code":
            rst_text = f"``{rst_text}``"

        return rst_text

    @classmethod
    def process_rich_span(cls, plain_text: str, style: str | Style) -> str:
        """Given a plain text and a rich style in string representation, return the corresponding
        rst formatted string.
        """
        if isinstance(style, str):
            try:
                style_obj: Style | str = Style.parse(style)
            except StyleSyntaxError:
                style_obj = style
        else:
            style_obj = style

        if isinstance(style_obj, Style):
            return cls._process_rich_style(plain_text, style_obj)
        return cls._process_rich_string(plain_text, style_obj)

    @classmethod
    def _render_rst_text(cls, plain_text: str, spans: list[Span], offset: int = 0) -> str:
        # Implementation heavily borrows from
        # https://github.com/python-telegram-bot/python-telegram-bot/blob/…
        # …5ab82a9c2b09286b66777ad0345b1abf3dedf131/telegram/_message.py#L4487-L4574
        rst_text = ""
        last_offset = 0
        sorted_spans = sorted(spans, key=lambda s: s.start)
        parsed_spans = []

        for span in sorted_spans:
            if span in parsed_spans:
                continue

            span_start = span.start - offset
            span_end = span.end - offset
            span_text = plain_text[span_start:span_end]
            nested_spans = [
                s
                for s in sorted_spans
                if s.start >= span_start and s.end <= span_end and s != span
            ]
            parsed_spans.extend(nested_spans)

            if nested_spans:
                span_text = cls._render_rst_text(
                    plain_text=span_text, spans=nested_spans, offset=span_start
                )

            insert = cls.process_rich_span(span_text, span.style)
            rst_text += plain_text[last_offset:span_start] + insert
            last_offset = span_start + (span.end - span.start)

        rst_text += plain_text[last_offset:]
        return rst_text

    def render_rst_text(self) -> str:
        """Render :attr:`plain_text` with rst formatting based on :attr:`spans`."""
        return self._render_rst_text(self.plain_text, self.spans)

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import ClassVar, Self, override

from chango._utils.files import UTF8
from chango.abc import ChangeNote
from chango.constants import MarkupLanguage


class CommentChangeNote(ChangeNote):
    """A simple change note that consists of a single comment. May be multi-line.

    Args:
        comment: The comment text.

    Attributes:
        comment: The comment text.
    """

    MARKUP: ClassVar[str] = MarkupLanguage.TEXT
    """The markup language used in the comment. Will also be used as file extension.
    """

    @override
    def __init__(self, slug: str, comment: str, uid: str | None = None):
        super().__init__(slug=slug, uid=uid)
        self.comment: str = comment

    @property
    @override
    def file_extension(self) -> str:
        return self.MARKUP

    @classmethod
    @override
    def from_string(cls, slug: str, uid: str, string: str) -> Self:
        return cls(slug=slug, comment=string, uid=uid)

    @override
    def to_bytes(self, encoding: str = UTF8) -> bytes:
        return self.comment.encode(encoding)

    @override
    def to_string(self, encoding: str = UTF8) -> str:
        return self.comment

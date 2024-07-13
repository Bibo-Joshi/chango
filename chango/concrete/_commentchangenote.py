#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from dataclasses import dataclass
from typing import ClassVar, Self, override

from chango._utils.files import UTF8
from chango.abc import ChangeNote


@dataclass
class CommentChangeNote(ChangeNote):
    """A simple change note that consists of a single comment. May be multi-line.

    Args:
        comment: The comment text.

    Attributes:
        comment: The comment text.
    """

    comment: str

    MARKUP: ClassVar[str] = "txt"
    """The markup language used in the comment. Will also be used as file extension.
    """

    @property
    def file_extension(self) -> str:
        return self.MARKUP

    @classmethod
    def from_string(cls, string: str) -> Self:
        return cls(string)

    def to_bytes(self, encoding: str = UTF8) -> bytes:
        return self.comment.encode(encoding)

    @override
    def to_string(self, encoding: str = UTF8) -> str:
        return self.comment

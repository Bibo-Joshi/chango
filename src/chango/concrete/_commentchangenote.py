#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import Any, ClassVar, Self, override

from .._utils.files import UTF8
from ..abc import ChangeNote
from ..action import ChanGoActionData
from ..constants import MarkupLanguage


class CommentChangeNote(ChangeNote):
    """A simple change note that consists of a single comment. May be multi-line.

    Args:
        comment (:obj:`str`): The comment text.

    Attributes:
        comment (:obj:`str`): The comment text.
    """

    MARKUP: ClassVar[str] = MarkupLanguage.TEXT
    """:obj:`str`: The markup language used in the comment. Will also be used as file extension.
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
    def to_string(self, encoding: str = UTF8) -> str:
        return self.comment

    @classmethod
    @override
    def build_template(cls, slug: str, uid: str | None = None) -> Self:
        return cls(slug=slug, comment="example comment", uid=uid)

    @classmethod
    @override
    def build_from_github_event(
        cls, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> Self:
        """Implementation of :meth:`~chango.abc.ChangeNote.build_from_github_event`.

        Considers only events of type ``pull_request`` and ``pull_request_target``.
        Uses the pull request number as slug and the pull request title as comment.

        Currently only supports :attr:`~chango.constants.MarkupLanguage.TEXT`,
            :attr:`~chango.constants.MarkupLanguage.MARKDOWN`,
            :attr:`~chango.constants.MarkupLanguage.RESTRUCTUREDTEXT` and
            :attr:`~chango.constants.MarkupLanguage.HTML`.

        Caution:
            Does not consider any formatting in the pull request title!

        Raises:
            ValueError: If required data is missing or not in the expected format or
                if :attr:`MARKUP` is not supported.
        """
        try:
            pull_request = event["pull_request"]
            pr_number = pull_request["number"]
            html_url = pull_request["html_url"]
        except KeyError as exc:
            raise ValueError("Unable to extract required data from event.") from exc

        match cls.MARKUP:
            case MarkupLanguage.TEXT:
                link = f"({html_url})"
            case MarkupLanguage.MARKDOWN:
                link = f"([#{pr_number}]({html_url}))"
            case MarkupLanguage.RESTRUCTUREDTEXT:
                link = f"(`#{pr_number} <{html_url}>`_)"
            case MarkupLanguage.HTML:
                link = f'(<a href="{html_url}">#{pr_number}</a>)'
            case _:
                raise ValueError(f"Unsupported markup language: {cls.MARKUP}")

        return cls(slug=f"{pr_number:04}", comment=f'{pull_request["title"]} {link}')

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module contains functionality required when using chango in :ref:`action`."""

from typing import ClassVar, Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict

__all__ = ["ChanGoActionData", "LinkedIssue", "ParentPullRequest"]


class _FrozenModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)


class ParentPullRequest(_FrozenModel):
    """Data structure for a pull request associated with the target branch of the current pull
    request.

    Args:
        number (:obj:`int`): The pull request number.
        title (:obj:`str`): The title of the pull request.
        url (:obj:`str`): The URL of the pull request.
        state (:obj:`str`): The state of the pull request. Possible values are ``open``,
            ``closed``, and ``merged``.

    Attributes:
        number (:obj:`int`): The pull request number.
        author_login (:obj:`str`): The login of the author of the pull request.
        title (:obj:`str`): The title of the pull request.
        url (:obj:`str`): The URL of the pull request.
        state (:obj:`str`): The state of the pull request. Possible values are ``OPEN``,
            ``CLOSED``, and ``MERGED``.
    """

    number: int
    author_login: str
    title: str
    url: AnyHttpUrl
    state: Literal["OPEN", "CLOSED", "MERGED"]


class LinkedIssue(_FrozenModel):
    """Data structure for an issue linked in a GitHub pull request.

    Args:
        number (:obj:`int`): The issue number.
        title (:obj:`str`): The title of the issue.
        labels (tuple[:obj:`str`], optional): The labels of the issue.
        issue_type (:obj:`str`, optional): The type of the issue.

    Attributes:
        number (:obj:`int`): The issue number.
        title (:obj:`str`): The title of the issue.
        labels (tuple[:obj:`str`]): Optional. The labels of the issue.
        issue_type (:obj:`str`): Optional. The type of the issue.
    """

    number: int
    title: str
    labels: tuple[str, ...] | None
    issue_type: str | None = None


class ChanGoActionData(_FrozenModel):
    """Data structure for the additional information that the ``chango`` action automatically
    provides in addition to the GitHub event payload.

    Args:
        parent_pull_request (:class:`ParentPullRequest` | :obj:`None`): If there is a pull request
            associated with the target branch of the current pull request, this field contains
            information about it.
        linked_issues (tuple[:class:`LinkedIssue`], optional): Information about linked issues,
            i.e., issues that will be closed when the current pull request is merged.

    Attributes:
        parent_pull_request (:class:`ParentPullRequest`): Optional. If there is a pull request
            associated with the target branch of the current pull request, this field contains
            information about it.
        linked_issues (tuple[:class:`LinkedIssue`]): Optional. Information about linked issues,
            i.e., issues that will be closed when the current pull request is merged.
    """

    parent_pull_request: ParentPullRequest | None
    linked_issues: tuple[LinkedIssue, ...] | None

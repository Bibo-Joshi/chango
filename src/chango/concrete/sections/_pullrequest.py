#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import Annotated, Any

import pydantic as pydt
from pydantic import BeforeValidator


def _validate_author_uid(value: str | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return value


class PullRequest(pydt.BaseModel):
    """Simple data structure to represent a pull/merge request.

    Args:
        uid (:obj:`str`): The unique identifier for the pull request. For example, the pull request
            number.
        author_uids (:obj:`str` | tuple[:obj:`str`, ...]): The unique identifier of the author(s)
            of the pull request. For example, the author's username.
        closes_threads (tuple[:obj:`str`], optional): The threads that are closed by this pull
            request.

    Attributes:
        uid (:obj:`str`): The unique identifier for the pull request.
        author_uids (tuple[:obj:`str`, ...]): The unique identifier of the author(s) of the pull
            request.
        closes_threads (tuple[:obj:`str`]): The threads that are closed by this pull request.
            May be empty.

    """

    uid: str
    author_uids: Annotated[tuple[str, ...], BeforeValidator(_validate_author_uid)]
    closes_threads: tuple[str, ...] = pydt.Field(default_factory=tuple)

    @pydt.model_validator(mode="before")
    def unify_author_ids(cls, data: Any) -> Any:
        # for backwards compatibility, we allow both `author_uid` and `author_uids`
        if not isinstance(data, dict):
            return data

        author_uid = data.pop("author_uid", None)
        author_uids = data.pop("author_uids", None)

        if author_uid is not None and author_uids is not None:
            raise ValueError("author_uid and author_uids are mutually exclusive")
        data["author_uids"] = author_uid or author_uids
        return data

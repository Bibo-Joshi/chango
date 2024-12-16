#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pydantic as pydt


class PullRequest(pydt.BaseModel):
    """Simple data structure to represent a pull/merge request.

    Args:
        uid (:obj:`str`): The unique identifier for the pull request. For example, the pull request
            number.
        author_uid (:obj:`str`): The unique identifier of the author of the pull request.
            For example, the author's username.
        closes_threads (tuple[:obj:`str`], optional): The threads that are closed by this pull
            request.

    Attributes:
        uid (:obj:`str`): The unique identifier for the pull request.
        author_uid (:obj:`str`): The unique identifier of the author of the pull request.
        closes_threads (tuple[:obj:`str`]): The threads that are closed by this pull request.
            May be empty.

    """

    uid: str
    author_uid: str
    closes_threads: tuple[str, ...] = pydt.Field(default_factory=tuple)

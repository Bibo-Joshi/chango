#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
from typing import ClassVar, override

from ._sectionchangenote import SectionChangeNote


class GitHubSectionChangeNote(SectionChangeNote):
    """Specialization of :class:`~chango.concrete.sections.SectionChangeNote` for
    projects hosted on GitHub.

    Example:
        .. code-block:: python

            from chango.concrete.sections import GitHubSectionChangeNote, Section


            class MySectionChangeNote(
                GitHubSectionChangeNote.with_sections(
                    [
                        Section(uid="req_section", title="Required Section", is_required=True),
                        Section(uid="opt_section", title="Optional Section"),
                    ]
                )
            ):
                OWNER = "my-username"
                REPOSITORY = "my-repo"

    """

    OWNER: ClassVar[str | None] = None
    """:obj:`str`: The owner of the repository on GitHub. This must be set as a class variable."""
    REPOSITORY: ClassVar[str | None] = None
    """:obj:`str`: The name of the repository on GitHub. This must be set as a class variable."""

    @classmethod
    def _get_owner(cls) -> str:
        if cls.OWNER is None:
            raise ValueError("OWNER must be set as class variable.")
        return cls.OWNER

    @classmethod
    def _get_repository(cls) -> str:
        if cls.REPOSITORY is None:
            raise ValueError("REPOSITORY must be set as class variable.")
        return cls.REPOSITORY

    @classmethod
    @override
    def get_pull_request_url(cls, pr_uid: str) -> str:
        """Implementation of :meth:`SectionChangeNote.get_pull_request_url` based on
        :attr:`OWNER` and :attr:`REPOSITORY`.
        """
        return f"https://github.com/{cls._get_owner()}/{cls._get_repository()}/pull/{pr_uid}"

    @classmethod
    @override
    def get_thread_url(cls, thread_uid: str) -> str:
        """Implementation of :meth:`SectionChangeNote.get_pull_request_url` based on
        :attr:`OWNER` and :attr:`REPOSITORY`.
        """
        return f"https://github.com/{cls._get_owner()}/{cls._get_repository()}/issue/{thread_uid}"

    @classmethod
    @override
    def get_author_url(cls, author_uid: str) -> str:
        """Get the URL of the author with the given UID.

        Args:
            author_uid (:obj:`str`): The UID of the author as defined in
                :attr:`chango.concrete.sections.PullRequest.author_uid`.

        Returns:
            :obj:`str`: The URL of the author.

        """
        return f"https://github.com/{author_uid}"

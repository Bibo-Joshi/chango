#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
from typing import ClassVar, override

from ._sectionchangenote import SectionChangeNote


class GitHubSectionChangeNote(SectionChangeNote):
    """Specialization of :class:`~chango.concrete.section_change_note.SectionChangeNote` for
    projects hosted on GitHub.

    Example:
        .. code-block:: python

            from chango.concrete.section_change_note import GitHubSectionChangeNote, Section


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

    @property
    def _owner(self) -> str:
        if self.OWNER is None:
            raise ValueError("OWNER must be set as class variable.")
        return self.OWNER

    @property
    def _repository(self) -> str:
        if self.REPOSITORY is None:
            raise ValueError("REPOSITORY must be set as class variable.")
        return self.REPOSITORY

    @override
    def get_pull_request_url(self, pr_uid: str) -> str:
        """Implementation of :meth:`SectionChangeNote.get_pull_request_url` based on
        :attr:`OWNER` and :attr:`REPOSITORY`.
        """
        return f"https://github.com/{self._owner}/{self._repository}/pull/{pr_uid}"

    @override
    def get_thread_url(self, thread_uid: str) -> str:
        """Implementation of :meth:`SectionChangeNote.get_pull_request_url` based on
        :attr:`OWNER` and :attr:`REPOSITORY`.
        """
        return f"https://github.com/{self._owner}/{self._repository}/issue/{thread_uid}"

    @override
    def get_author_url(self, author_uid: str) -> str:
        """Get the URL of the author with the given UID.

        Args:
            author_uid (:obj:`str`): The UID of the author as defined in
                :attr:`chango.concrete.section_change_note.PullRequest.author_uid`.

        Returns:
            :obj:`str`: The URL of the author.

        """
        return f"https://github.com/{author_uid}"

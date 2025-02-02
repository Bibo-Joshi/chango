#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
from collections.abc import Collection
from typing import Any, ClassVar, Self, override

from ...action import ChanGoActionData
from ._pullrequest import PullRequest
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

    @classmethod
    def get_sections(
        cls,
        labels: Collection[str],  # noqa: ARG003
        issue_types: Collection[str] | None,  # noqa: ARG003
    ) -> set[str]:
        """Determine appropriate sections based on the labels of a pull request as well as
        the labels and types of the issues closed by the pull request.

        If this class has required sections, they are all returned.
        Otherwise, the first section in the order of
        :attr:`~chango.concrete.sections.Section.sort_order` is returned.

        Tip:
            This method can be overridden to provide custom logic for determining the
            section based on the labels and issue types.

        Args:
            labels (Collection[:obj:`str`]): The combined set of labels of the pull request and
                the issues closed by the pull request.
            issue_types (Collection[:obj:`str`]): The types of the issues closed by the pull
                request.

                Caution:
                    Since issue types are currently in
                    `public preview <https://github.com/orgs/community/discussions/139933>`_,
                    this set may be empty.

        Returns:
            Set[:obj:`str`]: The UIDs of the sections.

        """
        sorted_sections = sorted(
            (section for section in cls.SECTIONS.values()), key=lambda section: section.sort_order
        )
        required_sections = {section.uid for section in sorted_sections if section.is_required}
        return required_sections or {sorted_sections[0].uid}

    @classmethod
    @override
    def build_from_github_event(
        cls, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> Self:
        """Implementation of :meth:`chango.abc.ChangeNote.build_from_github_event`.

        This writes the pull request title to the sections determined by :meth:`get_sections`.
        Uses the pull request number as slug.

        Caution:
            * Does not consider any formatting in the pull request title!
            * Considers the ``data`` argument only if it is an instance of
              :class:`~chango.action.ChanGoActionData`.

        Raises:
            ValueError: If required data is missing or not in the expected format.
        """
        try:
            pull_request = event["pull_request"]
            pr_number = pull_request["number"]
            pr_title = pull_request["title"]
            pr_labels = {label["name"] for label in pull_request.get("labels", [])}
            author_uid = pull_request["user"]["login"]
        except (KeyError, TypeError) as exc:
            raise ValueError("Unable to extract required data from event.") from exc

        issue_types: set[str] = set()
        closes_threads: set[int] = set()
        labels = pr_labels

        if isinstance(data, ChanGoActionData) and data.linked_issues:
            for issue in data.linked_issues:
                closes_threads.add(issue.number)
                if issue.labels:
                    labels.update(issue.labels)
                if issue.issue_type:
                    issue_types.add(issue.issue_type)

        sections = cls.get_sections(labels, issue_types)
        return cls(
            slug=f"{pr_number:04}",  # type: ignore[call-arg]
            pull_requests=(
                PullRequest(
                    uid=str(pr_number),
                    author_uid=author_uid,
                    closes_threads=tuple(map(str, closes_threads)),
                ),
            ),
            **{section: pr_title for section in sections},
        )

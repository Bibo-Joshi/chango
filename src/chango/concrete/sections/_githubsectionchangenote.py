#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
from collections.abc import Collection
from typing import Any, ClassVar, Self, override

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
    def get_section(
        cls,
        labels: Collection[str],  # noqa: ARG003
        issue_types: Collection[str],  # noqa: ARG003
    ) -> str:
        """Determine an appropriate section based on the labels of a pull request as well as
        the labels and types of the issues closed by the pull request.

        Tip:
            This method can be overridden to provide custom logic for determining the
            section based on the labels and issue types.
            By default, it returns the UID of the first (in terms of
            :attr:`~chango.concrete.sections.Section.sort_order`) required section.

        Args:
            labels (Collection[:obj:`str`]): The combined set of labels of the pull request and
                the issues closed by the pull request.
            issue_types (Collection[:obj:`str`]): The types of the issues closed by the pull
                request.

        Returns:
            :obj:`str`: The UID of the section.

        """
        return next(
            iter(
                sorted(
                    (section for section in cls.SECTIONS.values() if section.is_required),
                    key=lambda section: section.sort_order,
                )
            )
        ).uid

    @classmethod
    @override
    def build_from_github_event(
        cls, event: dict[str, Any], data: dict[str, Any] | None = None
    ) -> Self:
        """Implementation of :meth:`chango.abc.ChangeNote.build_from_github_event`.

        This writes the pull request title to the section determined by :meth:`get_section`.
        Uses the pull request number as slug.

        Caution:
            Does not consider any formatting in the pull request title!

        Raises:
            ValueError: If the event is not a ``pull_request`` or ``pull_request_target``.
        """
        pull_request = event.get("pull_request") or event.get("pull_request_target")
        if pull_request is None:
            raise ValueError("Event is not a pull request event.")

        linked_issues = (data or {}).get("linked_issues", [])

        number = pull_request["number"]
        title = pull_request["title"]
        labels = {label["name"] for label in pull_request["labels"]} | {
            label["name"] for issue in linked_issues or [] for label in issue["labels"]
        }
        issue_types = {issue["type"] for issue in linked_issues or []}

        section = cls.get_section(labels, issue_types)
        return cls(slug=f"{number:04}", **{section: title})  # type: ignore[call-arg]

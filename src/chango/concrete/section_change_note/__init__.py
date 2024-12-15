#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module contains an implementation of :class:`~chango.abc.ChangeNote` that consists of
multiple sections and includes references to pull requests that are related to the change.
The main class is :class:`SectionChangeNote`, while :class:`Section` and
:class:`PullRequest` are used to define the sections and pull requests, respectively.

Example:
    To create a change note with two sections, one required and one optional, use

    .. code-block:: python

        from chango.concrete.section_change_note import SectionChangeNote, Section

        MySectionChangeNote = SectionChangeNote.with_sections(
            [
                Section(uid="required_section", title="Required Section", is_required=True),
                Section(uid="optional_section", title="Optional Section"),
            ]
        )
"""

__all__ = ["GitHubSectionChangeNote", "PullRequest", "Section", "SectionChangeNote"]

from ._githubsectionchangenote import GitHubSectionChangeNote
from ._pullrequest import PullRequest
from ._section import Section
from ._sectionchangenote import SectionChangeNote

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.concrete.sections import (
    GitHubSectionChangeNote,
    PullRequest,
    Section,
    SectionChangeNote,
    SectionVersionNote,
)
from chango.error import UnsupportedMarkupError


class DummySectionChangeNote(
    GitHubSectionChangeNote.with_sections(
        [
            Section(uid="req_section", title="Required Section", is_required=True, sort_order=10),
            Section(uid="opt_section", title="Optional Section", render_pr_details=False),
        ]
    )
):
    OWNER = "my-username"
    REPOSITORY = "my-repo"


OtherSectionChangeNote = GitHubSectionChangeNote.with_sections(
    [Section(uid="req_section", title="Required Section", is_required=True)]
)


@pytest.fixture
def section_version_note():
    return SectionVersionNote(None, DummySectionChangeNote)


class TestSectionVersionNote:
    def test_init_invalid_markup(self):
        class InvalidSectionChangeNote(SectionChangeNote):
            MARKUP = "invalid"

        with pytest.raises(UnsupportedMarkupError, match="only supports reStructuredText"):
            SectionVersionNote(None, InvalidSectionChangeNote)

    def test_setitem_invalid_type(self, section_version_note):
        other_section_change_note = OtherSectionChangeNote(slug="slug", req_section="req_section")
        with pytest.raises(TypeError, match="Expected a"):
            section_version_note["key"] = other_section_change_note
        with pytest.raises(TypeError, match="Expected a"):
            section_version_note.add_change_note(other_section_change_note)

    def test_render_unknown_markup(self, section_version_note):
        with pytest.raises(UnsupportedMarkupError, match="unknown"):
            section_version_note.render("unknown")

    def test_render_unsupported_markup(self, section_version_note):
        with pytest.raises(UnsupportedMarkupError, match="markdown"):
            section_version_note.render("markdown")

    def test_render(self, section_version_note):
        section_version_note.add_change_note(
            DummySectionChangeNote(
                slug="slug1",
                uid="uid1",
                req_section="change note 1 req.\nWith multiple lines.",
                opt_section="change note 1 opt.",
                pull_requests=[
                    PullRequest(
                        uid="pr1", closes_threads=("thread1", "thread2"), author_uid="author1"
                    ),
                    PullRequest(uid="pr2", author_uid="author2"),
                ],
            )
        )
        section_version_note.add_change_note(
            DummySectionChangeNote(slug="slug2", uid="uid2", req_section="change note 2 req.")
        )
        section_version_note.add_change_note(
            DummySectionChangeNote(
                slug="slug3",
                uid="uid3",
                req_section="change note 3 req.",
                pull_requests=[PullRequest(uid="pr_a", author_uid="author_b")],
            )
        )
        assert (
            section_version_note.render("rst")
            == """\
Optional Section
----------------

- change note 1 opt.

Required Section
----------------

- change note 1 req.

  With multiple lines.

  (`#pr1 <https://github.com/my-username/my-repo/pull/pr1>`_ by `@author1 \
<https://github.com/author1>`_ closes `#thread1 \
<https://github.com/my-username/my-repo/issue/thread1>`_, `#thread2 \
<https://github.com/my-username/my-repo/issue/thread2>`_; `#pr2 \
<https://github.com/my-username/my-repo/pull/pr2>`_ by `@author2 <https://github.com/author2>`_)
- change note 2 req.
- change note 3 req. (`#pr_a <https://github.com/my-username/my-repo/pull/pr_a>`_ by \
`@author_b <https://github.com/author_b>`_)\
"""
        )

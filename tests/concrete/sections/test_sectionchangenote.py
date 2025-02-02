#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest
import shortuuid

from chango.concrete.sections import (
    GitHubSectionChangeNote,
    PullRequest,
    Section,
    SectionChangeNote,
)
from chango.constants import MarkupLanguage
from chango.error import ValidationError


class DummyChangNote(
    GitHubSectionChangeNote.with_sections(
        [
            Section(uid="req_section", title="Required Section", is_required=True),
            Section(uid="opt_section", title="Optional Section"),
        ]
    )
):
    OWNER = "my-username"
    REPOSITORY = "my-repo"


@pytest.fixture
def section_change_note():
    return DummyChangNote(
        slug="slug",
        req_section="req 𝛙𝌢𑁍",
        opt_section="opt 𝛙𝌢𑁍",
        pull_requests=(
            PullRequest(uid="uid1", closes_threads=("thread1",), author_uid="author1"),
            PullRequest(uid="uid2", closes_threads=("thread2",), author_uid="author2"),
        ),
    )


class TestSectionChangeNote:
    """Since TestSectionChangeNote is an abstract base class, we are testing with
    GitHubTestSectionChangeNote as a simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    sections = (
        Section(uid="req_section", title="Required Section", is_required=True),
        Section(uid="opt_section", title="Optional Section"),
    )

    def test_manual_subclass(self):
        class SubClass(SectionChangeNote):
            @classmethod
            def get_pull_request_url(cls, pr_uid: str) -> str:
                pass

            @classmethod
            def get_thread_url(cls, thread_uid: str) -> str:
                pass

            @classmethod
            def get_author_url(cls, author_uid: str) -> str:
                pass

        with pytest.raises(TypeError, match="SectionChangeNote must not be subclassed manually"):
            SubClass(slug="slug")

    @pytest.mark.parametrize("name", [None, "CustomName"])
    def test_with_sections(self, name):
        cls = SectionChangeNote.with_sections(self.sections, name=name)
        assert cls.SECTIONS["req_section"] is self.sections[0]
        assert cls.SECTIONS["opt_section"] is self.sections[1]
        assert cls.__name__ == (name or "DynamicSectionChangeNote")

    def test_with_sections_empty_sequence(self):
        with pytest.raises(ValueError, match="Class must have at least one section"):
            SectionChangeNote.with_sections([])

    def test_empty_init(self):
        cls = GitHubSectionChangeNote.with_sections(
            [Section(uid=f"opt_{i}", title=f"Optional {i}") for i in range(10)]
        )
        with pytest.raises(ValidationError, match="At least one section must be specified"):
            cls(slug="slug", opt_0="", opt_1=None)

    def test_constants(self, section_change_note):
        assert section_change_note.file_extension == "toml"
        assert section_change_note.MARKUP == MarkupLanguage.RESTRUCTUREDTEXT

    @pytest.mark.parametrize("has_prs", [True, False])
    def test_from_string(self, section_change_note, has_prs):
        string = """
req_section = '''Required section.
With multiple lines.'''

opt_section = "Optional Section."
"""
        if has_prs:
            string += """
[[pull_requests]]
uid = "uid1"
closes_threads = ["thread1", "thread2"]
author_uid = "author1"

[[pull_requests]]
uid = "uid2"
closes_threads = ["thread3"]
author_uid = "author2"
"""

        change_note = section_change_note.from_string("slug", "uid", string)
        assert change_note.slug == "slug"
        assert change_note.uid == "uid"
        assert change_note.req_section == "Required section.\nWith multiple lines."
        assert change_note.opt_section == "Optional Section."
        if has_prs:
            assert len(change_note.pull_requests) == 2  # noqa: PLR2004
            assert change_note.pull_requests[0].uid == "uid1"
            assert change_note.pull_requests[0].closes_threads == ("thread1", "thread2")
            assert change_note.pull_requests[0].author_uid == "author1"
            assert change_note.pull_requests[1].uid == "uid2"
            assert change_note.pull_requests[1].closes_threads == ("thread3",)
            assert change_note.pull_requests[1].author_uid == "author2"
        else:
            assert change_note.pull_requests == ()

    def test_from_string_invalid(self, section_change_note):
        with pytest.raises(ValidationError, match="Invalid TOML data"):
            section_change_note.from_string("slug", "uid", "invalid toml")

    @pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
    def test_to_string(self, section_change_note, encoding):
        string = section_change_note.to_string(encoding=encoding)
        assert (
            string
            == """req_section = "req 𝛙𝌢𑁍"
opt_section = "opt 𝛙𝌢𑁍"
[[pull_requests]]
uid = "uid1"
author_uid = "author1"
closes_threads = ["thread1"]

[[pull_requests]]
uid = "uid2"
author_uid = "author2"
closes_threads = ["thread2"]
"""
        )

    @pytest.mark.parametrize("uid", ["uid1", None])
    def test_build_template(self, uid):
        change_note = DummyChangNote.build_template("slug", uid)
        assert change_note.req_section == "Required Section Content"
        assert change_note.opt_section == "Optional Section Content"
        assert change_note.pull_requests == (
            PullRequest(
                uid="pr-number-1", closes_threads=("thread1", "thread2"), author_uid="author1"
            ),
            PullRequest(uid="pr-number-2", closes_threads=("thread3",), author_uid="author2"),
        )

        assert change_note.slug == "slug"
        if uid:
            assert change_note.uid == "uid1"
        else:
            assert isinstance(change_note.uid, str)
            assert len(change_note.uid) == len(shortuuid.ShortUUID().uuid())

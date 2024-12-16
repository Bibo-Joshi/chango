#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from chango.concrete.sections import GitHubSectionChangeNote, Section


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


class TestGitHubSectionChangeNote:
    """Since TestSectionChangeNote is an abstract base class, we are testing with
    GitHubTestSectionChangeNote as a simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    def test_class_variables(self):
        assert DummyChangNote.OWNER == "my-username"
        assert DummyChangNote.REPOSITORY == "my-repo"

    def test_get_pull_request_url(self):
        assert (
            DummyChangNote.get_pull_request_url("123")
            == "https://github.com/my-username/my-repo/pull/123"
        )

    def test_get_thread_ulr(self):
        assert (
            DummyChangNote.get_thread_url("123")
            == "https://github.com/my-username/my-repo/issue/123"
        )

    def test_get_author_url(self):
        assert DummyChangNote.get_author_url("123") == "https://github.com/123"

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.concrete.sections import GitHubSectionChangeNote, Section, PullRequest


class DummyChangNote(
    GitHubSectionChangeNote.with_sections([Section(uid="req", title="Req", is_required=True)])
):
    OWNER = "my-username"
    REPOSITORY = "my-repo"


class DummyChangNoteNoOwner(
    GitHubSectionChangeNote.with_sections([Section(uid="req", title="Req", is_required=True)])
):
    REPOSITORY = "my-repo"


class DummyChangNoteNoRepository(
    GitHubSectionChangeNote.with_sections([Section(uid="req", title="Req", is_required=True)])
):
    OWNER = "my-username"


class FromGitHubEvent(
    GitHubSectionChangeNote.with_sections(
            [
                Section(uid="opt_0", title="Opt", is_required=False, sort_order=0),
                Section(uid="req_1", title="Req", is_required=True, sort_order=1),
                Section(uid="req_0", title="Req", is_required=True, sort_order=0),
            ]
        )
):
    pass


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

    def test_get_pull_request_url_invalid(self):
        with pytest.raises(ValueError, match="OWNER must be set as class variable."):
            DummyChangNoteNoOwner.get_pull_request_url("123")
        with pytest.raises(ValueError, match="REPOSITORY must be set as class variable."):
            DummyChangNoteNoRepository.get_pull_request_url("123")

    def test_get_thread_url(self):
        assert (
            DummyChangNote.get_thread_url("123")
            == "https://github.com/my-username/my-repo/issue/123"
        )

    def test_get_thread_url_invalid(self):
        with pytest.raises(ValueError, match="OWNER must be set as class variable."):
            DummyChangNoteNoOwner.get_thread_url("123")
        with pytest.raises(ValueError, match="REPOSITORY must be set as class variable."):
            DummyChangNoteNoRepository.get_thread_url("123")

    def test_get_author_url(self):
        assert DummyChangNote.get_author_url("123") == "https://github.com/123"

    def test_get_section(self):
        assert FromGitHubEvent.get_section(None, None) == "req_0"

    def test_build_from_github_event_unsupported_event(self):
        with pytest.raises(ValueError, match="not a pull request event"):
            FromGitHubEvent.build_from_github_event({})

    @pytest.mark.parametrize("event_type", ["pull_request", "pull_request_target"])
    def test_build_from_github_event_basic(self, event_type):
        event_data = {
            event_type: {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
                "user": {"login": "author_uid"},
                "labels": [
                    {"name": "label1"},
                    {"name": "label2"}
                ]
            }
        }

        change_note = FromGitHubEvent.build_from_github_event(event_data)
        assert change_note.req_0 == "example title"
        assert change_note.pull_requests == (
            PullRequest(uid="42", author_uid="author_uid", closes_threads=())
        )
        assert change_note.slug == "0042"
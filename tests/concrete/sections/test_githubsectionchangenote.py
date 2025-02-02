#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.action import ChanGoActionData, LinkedIssue
from chango.concrete.sections import GitHubSectionChangeNote, PullRequest, Section


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

    def test_get_sections_has_required(self):
        assert FromGitHubEvent.get_sections(None, None) == {"req_0", "req_1"}

    def test_get_sections_no_required(self):
        NoRequired = GitHubSectionChangeNote.with_sections(
            [
                Section(uid="opt_0", title="Opt", is_required=False, sort_order=5),
                Section(uid="opt_1", title="Opt", is_required=False, sort_order=42),
                Section(uid="opt_2", title="Opt", is_required=False, sort_order=-3),
            ]
        )
        assert NoRequired.get_sections(None, None) == {"opt_2"}

    def test_build_from_github_event_missing_data(self):
        with pytest.raises(ValueError, match="required data"):
            FromGitHubEvent.build_from_github_event({})

    def test_build_from_github_event_basic(self):
        event_data = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
                "user": {"login": "author_uid"},
                "labels": [{"name": "label1"}, {"name": "label2"}],
            }
        }

        change_note = FromGitHubEvent.build_from_github_event(event_data)
        assert change_note.req_0 == "example title"
        assert change_note.pull_requests == (
            PullRequest(uid="42", author_uid="author_uid", closes_threads=()),
        )
        assert change_note.slug == "0042"

    def test_build_from_github_event_custom_get_sections(self):
        class CustomGetSections(FromGitHubEvent):
            @classmethod
            def get_sections(cls, event_data, sections):  # noqa: ARG003
                return {"opt_0", "req_1", "req_0"}

        event_data = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
                "user": {"login": "author_uid"},
                "labels": [{"name": "label1"}, {"name": "label2"}],
            }
        }

        change_note = CustomGetSections.build_from_github_event(event_data)
        assert change_note.req_0 == "example title"
        assert change_note.req_1 == "example title"
        assert change_note.opt_0 == "example title"
        assert change_note.pull_requests == (
            PullRequest(uid="42", author_uid="author_uid", closes_threads=()),
        )
        assert change_note.slug == "0042"

    def test_build_from_github_event_chango_action_data_no_linked_issues(self, monkeypatch):
        received_data = {}

        def get_sections(labels, issue_types):
            received_data["labels"] = labels
            received_data["issue_types"] = issue_types
            return {"req_0", "req_1"}

        monkeypatch.setattr(FromGitHubEvent, "get_sections", get_sections)

        event_data = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
                "user": {"login": "author_uid"},
                "labels": [],
            }
        }
        data = ChanGoActionData(linked_issues=None, parent_pull_request=None)

        FromGitHubEvent.build_from_github_event(event_data, data)
        assert received_data["labels"] == set()
        assert received_data["issue_types"] == set()

    def test_build_from_github_event_chango_action_data(self, monkeypatch):
        received_data = {}

        def get_sections(labels, issue_types):
            received_data["labels"] = labels
            received_data["issue_types"] = issue_types
            return {"req_0", "req_1"}

        monkeypatch.setattr(FromGitHubEvent, "get_sections", get_sections)

        event_data = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
                "user": {"login": "author_uid"},
                "labels": [{"name": "pr_label1"}, {"name": "pr_label2"}],
            }
        }
        data = ChanGoActionData(
            linked_issues=(
                LinkedIssue(number=1, title="issue_title", labels=None, issue_type="issue_type"),
                LinkedIssue(
                    number=2,
                    title="issue_title",
                    labels=("issue_label1", "issue_label2"),
                    issue_type=None,
                ),
            ),
            parent_pull_request=None,
        )

        FromGitHubEvent.build_from_github_event(event_data, data)
        assert received_data["labels"] == {
            "pr_label1",
            "pr_label2",
            "issue_label1",
            "issue_label2",
        }
        assert received_data["issue_types"] == {"issue_type"}

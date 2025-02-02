#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

import pytest
from pydantic import ValidationError

from chango.action import ChanGoActionData, LinkedIssue, ParentPullRequest


@pytest.fixture(scope="module")
def parent_pull_request():
    return ParentPullRequest(
        number=1, author_login="author", title="title", url="http://example.com", state="OPEN"
    )


@pytest.fixture(scope="module")
def linked_issue():
    return LinkedIssue(number=1, title="title", labels=["label1", "label2"], issue_type="type")


class TestParentPullRequest:
    def test_init_basic(self, parent_pull_request):
        assert parent_pull_request.number == 1
        assert parent_pull_request.author_login == "author"
        assert parent_pull_request.title == "title"
        assert str(parent_pull_request.url) == "http://example.com/"
        assert parent_pull_request.state == "OPEN"

    def test_frozen(self, parent_pull_request):
        with pytest.raises(ValidationError, match="frozen"):
            parent_pull_request.number = 2

    def test_invalid_url(self):
        with pytest.raises(ValidationError, match="input_value='example.com'"):
            ParentPullRequest(
                number=1, author_login="author", title="title", url="example.com", state="open"
            )

    def test_invalid_state(self):
        with pytest.raises(ValidationError, match="input_value='invalid'"):
            ParentPullRequest(
                number=1,
                author_login="author",
                title="title",
                url="http://example.com",
                state="invalid",
            )


class TestLinkedIssue:
    def test_init_basic(self, linked_issue):
        assert linked_issue.number == 1
        assert linked_issue.title == "title"
        assert linked_issue.labels == ("label1", "label2")
        assert linked_issue.issue_type == "type"

    def test_init_no_optional(self):
        linked_issue = LinkedIssue(number=1, title="title", labels=None)
        assert linked_issue.labels is None
        assert linked_issue.issue_type is None

    def test_frozen(self, linked_issue):
        with pytest.raises(ValidationError, match="frozen"):
            linked_issue.number = 2

    def test_init_none_labels(self):
        linked_issue = LinkedIssue(number=1, title="title", labels=None, issue_type=None)
        assert linked_issue.labels is None
        assert linked_issue.issue_type is None


class TestChanGoActionData:
    def test_init_basic(self, parent_pull_request, linked_issue):
        data = ChanGoActionData(
            parent_pull_request=parent_pull_request, linked_issues=[linked_issue]
        )
        assert data.parent_pull_request == parent_pull_request
        assert data.linked_issues == (linked_issue,)

    def test_init_none(self):
        data = ChanGoActionData(parent_pull_request=None, linked_issues=None)
        assert data.parent_pull_request is None
        assert data.linked_issues is None

    def test_frozen(self, parent_pull_request, linked_issue):
        data = ChanGoActionData(
            parent_pull_request=parent_pull_request, linked_issues=[linked_issue]
        )
        with pytest.raises(ValidationError, match="frozen"):
            data.parent_pull_request = None

        with pytest.raises(ValidationError, match="frozen"):
            data.linked_issues = None

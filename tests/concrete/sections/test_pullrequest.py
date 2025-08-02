#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest
from pydantic import ValidationError

from chango.concrete.sections import PullRequest


class TestPullRequest:
    def test_init_required_args(self):
        pr = PullRequest(uid="uid1", author_uids=("author1",))
        assert pr.uid == "uid1"
        assert pr.author_uids == ("author1",)
        assert pr.closes_threads == ()

    def test_init_all_args(self):
        pr = PullRequest(uid="uid2", author_uids=("author2",), closes_threads=("thread3",))
        assert pr.uid == "uid2"
        assert pr.author_uids == ("author2",)
        assert pr.closes_threads == ("thread3",)

    def test_init_legacy_author_uid(self):
        pr = PullRequest(uid="uid3", author_uid="author3")
        assert pr.uid == "uid3"
        assert pr.author_uids == ("author3",)
        assert pr.closes_threads == ()

    def test_init_mutually_exclusive_author_fields(self):
        with pytest.raises(
            ValidationError, match="author_uid and author_uids are mutually exclusive"
        ):
            PullRequest(uid="uid4", author_uid="author4", author_uids=("author5",))

    def test_init_invalid_author_type(self):
        with pytest.raises(ValidationError, match="should be a valid tuple"):
            PullRequest(uid="uid5", author_uids=42)

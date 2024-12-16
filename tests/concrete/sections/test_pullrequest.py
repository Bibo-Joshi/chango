#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from chango.concrete.sections import PullRequest


class TestPullRequest:
    def test_init_required_args(self):
        pr = PullRequest(uid="uid1", author_uid="author1")
        assert pr.uid == "uid1"
        assert pr.author_uid == "author1"
        assert pr.closes_threads == ()

    def test_init_all_args(self):
        pr = PullRequest(uid="uid2", author_uid="author2", closes_threads=("thread3",))
        assert pr.uid == "uid2"
        assert pr.author_uid == "author2"
        assert pr.closes_threads == ("thread3",)

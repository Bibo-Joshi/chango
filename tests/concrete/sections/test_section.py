#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from chango.concrete.sections import Section


class TestSection:
    def test_init_required_args(self):
        section = Section(uid="uid1", title="Title 1")
        assert section.uid == "uid1"
        assert section.title == "Title 1"
        assert section.is_required is False
        assert section.render_pr_details is True
        assert section.sort_order == 0

    def test_init_all_args(self):
        section = Section(
            uid="uid2", title="Title 2", is_required=True, render_pr_details=False, sort_order=1
        )
        assert section.uid == "uid2"
        assert section.title == "Title 2"
        assert section.is_required is True
        assert section.render_pr_details is False
        assert section.sort_order == 1

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm

import pytest

from chango import Version
from chango.concrete import CommentChangeNote, CommentVersionNote
from chango.error import UnsupportedMarkupError


class TestCommentVersionNote:
    comments = ("comment 1", "a\nmulti-line\ncomment 2", "comment 3")
    change_notes = tuple(
        CommentChangeNote(slug=f"slug-{i}", comment=comment) for i, comment in enumerate(comments)
    )

    @pytest.fixture(
        autouse=True,
        params=[None, Version(uid="1.0.0", date=dtm.date(2024, 1, 1))],
        ids=["None", "Version"],
    )
    def setup(self, request):
        # This is the next best thing to parametrizing __init__ that I could find
        # in reasonable time
        version = request.param
        self.version = version
        self.version_note = CommentVersionNote(version=version)
        for change_note in self.change_notes:
            self.version_note.add_change_note(change_note)

    def test_unsupported_markup(self):
        with pytest.raises(UnsupportedMarkupError):
            self.version_note.render("unsupported markup")

    def test_markdown(self):
        rendered = self.version_note.render("markdown")
        assert (
            rendered
            == """- comment 1
- a

    multi-line

    comment 2
- comment 3"""
        )

    def test_html(self):
        rendered = self.version_note.render("html")
        assert (
            rendered
            == """<ul>
<li>comment 1</li>
<li>a<br>multi-line<br>comment 2</li>
<li>comment 3</li>
</ul>"""
        )

    def test_restructuredtext(self):
        rendered = self.version_note.render("restructuredtext")
        assert (
            rendered
            == """- comment 1
- a

  multi-line

  comment 2
- comment 3"""
        )

    def test_fallback(self):
        rendered = self.version_note.render("text")
        assert (
            rendered
            == """comment 1

a
multi-line
comment 2

comment 3"""
        )

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm

import pytest

from chango import Version
from chango.concrete import CommentChangeNote, CommentVersionNote, HeaderVersionHistory


class TestVersionHistory:
    """Since VersionHistory is an abstract base class, we are testing with CommentVersionHistory as
    a simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.version_notes = []
        for i in range(5):
            version_note = CommentVersionNote(
                version=Version(f"1.0.{i}", date=dtm.date(2024, 1, i + 1))
            )
            for j in range(5):
                version_note.add_change_note(
                    CommentChangeNote(
                        slug=f"1-0-{i}-slug-{j}",
                        uid=f"1-0-{i}-uid-{j}",
                        comment=f"1-0-{i}-comment-{j}",
                    )
                )
            self.version_notes.append(version_note)

        self.version_note = self.version_notes[0]
        self.version_history = HeaderVersionHistory()

    @pytest.fixture(params=["uid", "Version", "None"])
    def key(self, request):
        if request.param == "uid":
            return self.version_note.uid
        if request.param == "Version":
            return self.version_note.version
        return None

    def test_set_get_del_item(self, key):
        version_note = self.version_note if key else CommentVersionNote(None)
        self.version_history[key] = version_note
        assert self.version_history[key] == version_note
        del self.version_history[key]

        with pytest.raises(KeyError):
            self.version_history[key]

        with pytest.raises(KeyError):
            del self.version_history[self.version_note.uid]

    def test_setitem_warning(self):
        with pytest.warns(
            UserWarning, match="Key 'non-matching-key' does not match version note UID"
        ):
            self.version_history["non-matching-key"] = self.version_note

    def test_add_remove_note(self, key):
        if key is None:
            pytest.skip("Not relevant for None key")

        self.version_history.add_version_note(self.version_note)
        assert self.version_history[key] == self.version_note
        self.version_history.remove_version_note(self.version_note)

        with pytest.raises(KeyError):
            self.version_history.remove_version_note(self.version_note)

    def test_iter(self):
        for version_note in self.version_notes:
            self.version_history.add_version_note(version_note)

        for i, key in enumerate(self.version_history):
            assert self.version_history[key] is self.version_notes[i]

    def test_len(self):
        assert len(self.version_history) == 0
        for version_note in self.version_notes:
            self.version_history.add_version_note(version_note)
        assert len(self.version_history) == len(self.version_notes)

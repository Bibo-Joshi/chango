#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm

import pytest

from chango import Version
from chango.concrete import CommentChangeNote, CommentVersionNote


class TestVersionNote:
    """Since VersionNote is an abstract base class, we are testing with CommentVersionNote as a
    simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

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
        self.change_notes = [
            CommentChangeNote(slug=f"slug-{i}", uid=f"uid-{i}", comment=f"comment-{i}")
            for i in range(5)
        ]

    @property
    def change_note(self) -> CommentChangeNote:
        return self.change_notes[0]

    def test_init(self):
        assert self.version_note.version == self.version
        assert len(self.version_note) == 0

    def test_uid(self):
        assert self.version_note.uid == (self.version.uid if self.version else None)

    def test_date(self):
        assert self.version_note.date == (self.version.date if self.version else None)

    @pytest.mark.parametrize("key_type", ["uid", "filename"])
    def test_set_get_del_item(self, key_type):
        key = self.change_note.uid if key_type == "uid" else self.change_note.file_name

        self.version_note[key] = self.change_note
        assert self.version_note[key] == self.change_note
        del self.version_note[key]

        with pytest.raises(KeyError):
            self.version_note[key]

        with pytest.raises(KeyError):
            del self.version_note[self.change_note.uid]

    def test_setitem_warning(self):
        with pytest.warns(
            UserWarning, match="Key 'non-matching-key' does not match change note UID"
        ):
            self.version_note["non-matching-key"] = self.change_note

    @pytest.mark.parametrize("key_type", ["uid", "filename"])
    def test_add_remove_note(self, key_type):
        key = self.change_note.uid if key_type == "uid" else self.change_note.file_name

        self.version_note.add_change_note(self.change_note)
        assert self.version_note[key] == self.change_note
        self.version_note.remove_change_note(self.change_note)

        with pytest.raises(KeyError):
            self.version_note.remove_change_note(self.change_note)

    def test_iter(self):
        for change_note in self.change_notes:
            self.version_note.add_change_note(change_note)

        for i, key in enumerate(self.version_note):
            assert self.version_note[key] is self.change_notes[i]

    def test_len(self):
        assert len(self.version_note) == 0
        for change_note in self.change_notes:
            self.version_note.add_change_note(change_note)
        assert len(self.version_note) == len(self.change_notes)

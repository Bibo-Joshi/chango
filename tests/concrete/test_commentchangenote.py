#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.concrete import CommentChangeNote


class TestCommentChangeNote:
    change_note = CommentChangeNote(slug="slug", comment="comment 𝛙𝌢𑁍")

    def test_init(self):
        assert self.change_note.comment == "comment 𝛙𝌢𑁍"

    def test_file_extension(self):
        assert self.change_note.file_extension == CommentChangeNote.MARKUP

    def test_from_string(self):
        change_note = CommentChangeNote.from_string("slug", "uid", "comment")
        assert change_note.comment == "comment"

    @pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
    def test_to_bytes(self, encoding):
        assert self.change_note.to_bytes(encoding) == (
            b"comment \xf0\x9d\x9b\x99\xf0\x9d\x8c\xa2\xf0\x91\x81\x8d"
            if encoding == "utf-8"
            else (
                b"\xff\xfec\x00o\x00m\x00m\x00e\x00n\x00t\x00 "
                b'\x005\xd8\xd9\xde4\xd8"\xdf\x04\xd8M\xdc'
            )
        )

    @pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
    def test_to_string(self, encoding):
        assert self.change_note.to_string(encoding=encoding) == "comment 𝛙𝌢𑁍"

    def test_build_template(self):
        change_note = CommentChangeNote.build_template("slug", "uid")
        assert change_note.comment == "example comment"
        assert change_note.slug == "slug"
        assert change_note.uid == "uid"

    def test_build_template_no_uid(self):
        change_note = CommentChangeNote.build_template("slug")
        assert change_note.comment == "example comment"
        assert change_note.slug == "slug"
        assert isinstance(change_note.uid, str)
        assert len(change_note.uid) > 0

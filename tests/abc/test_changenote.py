#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

import pytest
import shortuuid

from chango.abc import ChangeNote
from chango.concrete import CommentChangeNote
from chango.error import ValidationError
from tests.auxil.files import data_path

UTF_8_PATH = data_path("comment-change-note.uid.txt")
UTF_16_PATH = data_path("comment-change-note-utf16.uid.txt")


@pytest.fixture(params=["string", "path"])
def utf_8_path(request):
    if request.param == "string":
        return str(UTF_8_PATH)
    return UTF_8_PATH


@pytest.fixture(params=["string", "path"])
def utf_16_path(request):
    if request.param == "string":
        return str(UTF_16_PATH)
    return UTF_16_PATH


class TestChangeNote:
    """Since ChangeNote is an abstract base class, we are testing with CommentChangeNote as a
    simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    change_note = CommentChangeNote(slug="slug", comment="this is a comment", uid="uid")

    def test_init(self):
        assert self.change_note.slug == "slug"
        assert self.change_note.uid == "uid"

        change_note = CommentChangeNote(slug="slug", comment="this is a comment")
        assert change_note.slug == "slug"
        assert isinstance(change_note.uid, str)
        assert len(change_note.uid) == len(shortuuid.ShortUUID().uuid())

    def test_init_invalid_slug(self):
        with pytest.raises(ValidationError, match="slug must not contain"):
            CommentChangeNote(slug="slug.with.dot", comment="this is a comment")

    def test_file_name(self):
        assert self.change_note.file_name == "slug.uid.txt"

    def test_from_file(self, utf_8_path):
        change_note = CommentChangeNote.from_file(utf_8_path)
        assert change_note.slug == "comment-change-note"
        assert change_note.uid == "uid"

    def test_from_file_encoding(self, utf_16_path):
        change_note = CommentChangeNote.from_file(utf_16_path, encoding="utf-16")
        assert change_note.slug == "comment-change-note-utf16"
        assert change_note.uid == "uid"
        assert change_note.comment == "this is an utf-16 comment 𝛙𝌢𑁍"

        with pytest.raises(UnicodeDecodeError):
            CommentChangeNote.from_file(utf_16_path, encoding="utf-8")

    def test_from_bytes(self):
        change_note = CommentChangeNote.from_bytes(
            slug="slug", uid="uid", data=UTF_8_PATH.read_bytes()
        )
        assert change_note.slug == "slug"
        assert change_note.uid == "uid"
        assert change_note.comment == "this is a comment"

    def test_from_bytes_encoding(self):
        change_note = CommentChangeNote.from_bytes(
            slug="slug", uid="uid", data=UTF_16_PATH.read_bytes(), encoding="utf-16"
        )
        assert change_note.slug == "slug"
        assert change_note.uid == "uid"
        assert change_note.comment == "this is an utf-16 comment 𝛙𝌢𑁍"

        with pytest.raises(UnicodeDecodeError):
            CommentChangeNote.from_bytes(
                slug="slug", uid="uid", data=UTF_16_PATH.read_bytes(), encoding="utf-8"
            )

    def test_to_bytes(self):
        assert self.change_note.to_bytes() == b"this is a comment"

    def test_to_bytes_encoding(self):
        change_note = CommentChangeNote(slug="slug", comment="this is a comment 𝛙𝌢𑁍", uid="uid")
        assert change_note.to_bytes(encoding="utf-16") == "this is a comment 𝛙𝌢𑁍".encode("utf-16")

    @pytest.mark.parametrize("directory", [None, "custom"])
    def test_to_file(self, tmp_path, directory):
        path = None
        expected_dir = tmp_path if directory == "custom" else Path.cwd()
        try:
            path = self.change_note.to_file(directory=tmp_path if directory == "custom" else None)
            assert path == expected_dir / "slug.uid.txt"
            assert path.read_text() == "this is a comment"
        finally:
            if path:
                path.unlink()

    @pytest.mark.parametrize("directory", [None, "custom"])
    def test_to_file_encoding(self, tmp_path, directory):
        path = None
        expected_dir = tmp_path if directory == "custom" else Path.cwd()
        change_note = CommentChangeNote(slug="slug", comment="this is a comment 𝛙𝌢𑁍", uid="uid")

        try:
            path = change_note.to_file(
                directory=tmp_path if directory == "custom" else None, encoding="utf-16"
            )
            assert path == expected_dir / "slug.uid.txt"
            assert path.read_text(encoding="utf-16") == "this is a comment 𝛙𝌢𑁍"

            with pytest.raises(UnicodeDecodeError):
                path.read_text(encoding="utf-8")
        finally:
            if path:
                path.unlink()

    def test_build_from_github_event(self, monkeypatch):
        monkeypatch.setattr(
            self.change_note, "build_from_github_event", ChangeNote.build_from_github_event
        )
        with pytest.raises(NotImplementedError):
            self.change_note.build_from_github_event({})

    def test_update_uid(self):
        change_note = CommentChangeNote(slug="slug", comment="this is a comment", uid="uid")
        assert change_note.uid == "uid"
        change_note.update_uid("abc")
        assert change_note.uid == "abc"
        assert change_note.slug == "slug"
        assert change_note.file_name == "slug.abc.txt"

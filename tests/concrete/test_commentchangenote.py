#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.concrete import CommentChangeNote
from chango.constants import MarkupLanguage


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

    def test_build_from_github_event_missing_data(self):
        with pytest.raises(ValueError, match="required data"):
            CommentChangeNote.build_from_github_event({})

    def test_build_from_github_event_unsupported_language(self, monkeypatch):
        monkeypatch.setattr(CommentChangeNote, "MARKUP", "unsupported markup language")
        with pytest.raises(ValueError, match="unsupported markup language"):
            CommentChangeNote.build_from_github_event(
                {
                    "pull_request": {
                        "html_url": "https://example.com/pull/42",
                        "number": 42,
                        "title": "example title",
                    }
                }
            )

    @pytest.mark.parametrize(
        ("language", "expected"),
        [
            (MarkupLanguage.TEXT, "example title (https://example.com/pull/42)"),
            (MarkupLanguage.MARKDOWN, "example title ([#42](https://example.com/pull/42))"),
            (
                MarkupLanguage.RESTRUCTUREDTEXT,
                "example title (`#42 <https://example.com/pull/42>`_)",
            ),
            (MarkupLanguage.HTML, 'example title (<a href="https://example.com/pull/42">#42</a>)'),
        ],
    )
    def test_build_from_github_event(self, language, expected, monkeypatch):
        monkeypatch.setattr(CommentChangeNote, "MARKUP", language)
        event_data = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
            }
        }

        change_note = CommentChangeNote.build_from_github_event(event_data)
        assert change_note.comment == expected
        assert change_note.slug == "0042"

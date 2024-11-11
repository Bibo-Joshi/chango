#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
from pathlib import Path

import pytest

from chango import Version
from chango.concrete import CommentChangeNote, CommentVersionNote, HeaderVersionHistory
from chango.constants import MarkupLanguage
from chango.error import UnsupportedMarkupError
from tests.auxil.files import data_path


class TestHeaderVersionHistory:
    comments = ("comment 1", "a\nmulti-line\ncomment 2", "comment 3")

    @staticmethod
    def get_expected_file(unreleased_changes: bool, markup: MarkupLanguage) -> Path:
        unreleased_prefix = "with-unreleased" if unreleased_changes else "without-unreleased"
        file_name = f"{unreleased_prefix}.{markup}"
        return data_path(Path("headerversionhistory") / file_name)

    @classmethod
    def get_expected_string(cls, unreleased_changes: bool, markup: MarkupLanguage) -> str:
        return cls.get_expected_file(unreleased_changes, markup).read_text()

    def get_version_notes(self, unreleased_changes: bool) -> list[CommentVersionNote]:
        version_notes = []
        for j, version_number in enumerate(range(3)):
            version = Version(uid=f"1.0.{version_number}", date=dtm.date(2024, 1, 1 + j))
            version_note = CommentVersionNote(version=version)
            version_notes.append(version_note)

            for i, comment in enumerate(self.comments):
                change_note = CommentChangeNote(slug=f"slug-{i}", comment=comment)
                version_note.add_change_note(change_note)

        if not unreleased_changes:
            return version_notes

        unreleased_version_note = CommentVersionNote(version=None)
        version_notes.append(unreleased_version_note)
        for i, comment in enumerate(self.comments):
            change_note = CommentChangeNote(slug=f"slug-{i}", comment=comment)
            unreleased_version_note.add_change_note(change_note)

        return version_notes

    @pytest.mark.parametrize(
        "markup", [MarkupLanguage.MARKDOWN, MarkupLanguage.HTML, MarkupLanguage.RESTRUCTUREDTEXT]
    )
    @pytest.mark.parametrize(
        "unreleased_changes", [False, True], ids=["without-unreleased", "with-unreleased"]
    )
    def test_expected_output(self, unreleased_changes: bool, markup: MarkupLanguage):
        version_notes = self.get_version_notes(unreleased_changes=unreleased_changes)
        version_history = HeaderVersionHistory()
        for version_note in version_notes:
            version_history.add_version_note(version_note)
        expected = self.get_expected_string(unreleased_changes=unreleased_changes, markup=markup)
        assert version_history.render(markup) == expected

    def test_unsupported_markup(self):
        version_history = HeaderVersionHistory()
        with pytest.raises(UnsupportedMarkupError, match="Got unsupported markup 'unsupported'"):
            version_history.render("unsupported")

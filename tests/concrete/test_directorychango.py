#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

import datetime as dtm

import pytest
import shortuuid

from chango import Version
from chango.concrete import (
    CommentChangeNote,
    CommentVersionNote,
    DirectoryChanGo,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)
from chango.helpers import ensure_uid
from tests.auxil.files import data_path


@pytest.fixture(scope="module")
def scanner() -> DirectoryVersionScanner:
    return DirectoryVersionScanner(TestDirectoryChango.DATA_ROOT, "unreleased")


@pytest.fixture(scope="module")
def chango(scanner) -> DirectoryChanGo:
    return DirectoryChanGo(
        change_note_type=CommentChangeNote,
        version_note_type=CommentVersionNote,
        version_history_type=HeaderVersionHistory,
        scanner=scanner,
    )


class TestDirectoryChango:
    DATA_ROOT = data_path("directoryversionscanner")

    def test_init_basic(self, chango, scanner):
        assert chango.directory_format == "{uid}_{date}"
        assert chango.change_note_type == CommentChangeNote
        assert chango.version_note_type == CommentVersionNote
        assert chango.version_history_type == HeaderVersionHistory
        assert chango.scanner is scanner

    def test_init_custom_format(self, scanner):
        chango = DirectoryChanGo(
            change_note_type=CommentChangeNote,
            version_note_type=CommentVersionNote,
            version_history_type=HeaderVersionHistory,
            scanner=scanner,
            directory_format="{uid} custom {date}",
        )
        assert chango.directory_format == "{uid} custom {date}"

    @pytest.mark.parametrize("uid", [None, "uid"])
    def test_build_template_change_note(self, chango, uid):
        note = chango.build_template_change_note("slug", uid)
        assert isinstance(note, CommentChangeNote)
        assert note.slug == "slug"
        if uid is not None:
            assert note.uid == uid
        else:
            assert isinstance(note.uid, str)
            assert len(note.uid) == len(shortuuid.ShortUUID().uuid())

    def test_build_github_event_change_note(self, chango):
        event = {
            "pull_request": {
                "html_url": "https://example.com/pull/42",
                "number": 42,
                "title": "example title",
            }
        }
        note = chango.build_github_event_change_note(event)
        assert isinstance(note, CommentChangeNote)
        assert isinstance(note.uid, str)
        assert len(note.uid) == len(shortuuid.ShortUUID().uuid())

    def test_build_version_note_version(self, chango):
        version = Version("uid", dtm.date.today())  # noqa: DTZ011
        note = chango.build_version_note(version)
        assert isinstance(note, CommentVersionNote)
        assert note.version == version

    def test_build_version_note_none(self, chango):
        note = chango.build_version_note(None)
        assert isinstance(note, CommentVersionNote)
        assert note.version is None

    def test_build_version_history(self, chango):
        history = chango.build_version_history()
        assert isinstance(history, HeaderVersionHistory)

    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_load_change_note(self, chango, idx):
        uid = f"uid_1-{idx}_0"
        change_note = chango.load_change_note(uid)
        assert isinstance(change_note, CommentChangeNote)
        assert change_note.uid == uid
        assert change_note.slug == "comment-change-note"
        path = (
            self.DATA_ROOT / f"1.{idx}_2024-01-0{idx}" / f"comment-change-note.uid_1-{idx}_0.txt"
        )
        assert change_note.comment == path.read_text()

    @pytest.mark.parametrize(
        "version",
        [
            None,
            "1.1",
            Version("1.1", dtm.date(2024, 1, 1)),
            "1.2",
            Version("1.2", dtm.date(2024, 1, 2)),
        ],
    )
    @pytest.mark.parametrize(
        "change_note", ["str_change_note", CommentChangeNote.build_template("slug", "uid")]
    )
    def test_get_write_directory(self, chango, version, change_note):
        if version is None:
            expected_path = chango.scanner.unreleased_directory
        else:
            version_uid = ensure_uid(version)
            day = int(version_uid.split(".")[-1])
            expected_path = chango.scanner.base_directory / f"{version_uid}_2024-01-0{day}"

        path_existed = expected_path.is_dir()

        try:
            path = chango.get_write_directory(change_note, version)
            assert path.is_dir()
        finally:
            # Clean up
            if (expected_path is not None) and (not path_existed):
                expected_path.rmdir()

    @pytest.mark.parametrize(
        "change_note", ["str_change_note", CommentChangeNote.build_template("slug", "uid")]
    )
    def test_get_write_directory_new_version(self, chango, change_note):
        version = Version("new-version", dtm.date(2024, 1, 17))
        expected_path = chango.scanner.base_directory / "new-version_2024-01-17"
        try:
            path = chango.get_write_directory(change_note, version)
            assert path.is_dir()
            assert path == expected_path
        finally:
            # Clean up
            expected_path.rmdir()

    @pytest.mark.parametrize(
        "change_note", ["str_change_note", CommentChangeNote.build_template("slug", "uid")]
    )
    def test_get_write_directory_new_str_version(self, chango, change_note):
        with pytest.raises(TypeError, match="Version 'new-version' not available yet."):
            chango.get_write_directory(change_note, "new-version")

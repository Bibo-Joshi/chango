#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
import functools
import shutil

import pytest

from chango import Version
from chango.abc import ChanGo
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
    return DirectoryVersionScanner(TestChanGo.DATA_ROOT, "unreleased")


@pytest.fixture(scope="module")
def chango(scanner) -> DirectoryChanGo:
    return DirectoryChanGo(
        change_note_type=CommentChangeNote,
        version_note_type=CommentVersionNote,
        version_history_type=HeaderVersionHistory,
        scanner=scanner,
    )


@pytest.fixture(scope="module")
def chango_no_unreleased() -> DirectoryChanGo:
    return DirectoryChanGo(
        change_note_type=CommentChangeNote,
        version_note_type=CommentVersionNote,
        version_history_type=HeaderVersionHistory,
        scanner=DirectoryVersionScanner(TestChanGo.DATA_ROOT, "no-unreleased"),
    )


class TestChanGo:
    """Since Chango is an abstract base class, we are testing with DirectoryChanGo as a simple
    implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    DATA_ROOT = data_path("directoryversionscanner")

    @pytest.mark.parametrize(
        "version",
        [
            None,
            "1.1",
            Version("1.1", dtm.date(2024, 1, 1)),
            "1.2",
            Version("1.2", dtm.date(2024, 1, 2)),
            Version("new-version", dtm.date(2024, 1, 17)),
        ],
    )
    @pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
    def test_write_change_note(self, chango, version, monkeypatch, encoding):
        if version is None:
            expected_path = chango.scanner.unreleased_directory
        else:
            version_uid = ensure_uid(version)
            if version_uid == "new-version":
                expected_path = chango.scanner.base_directory / "new-version_2024-01-17"
            else:
                day = int(version_uid.split(".")[-1])
                expected_path = chango.scanner.base_directory / f"{version_uid}_2024-01-0{day}"

        existed = expected_path.is_dir()

        def to_file(*_, **kwargs):
            assert kwargs.get("encoding") == encoding
            assert kwargs.get("directory") == expected_path

        note = chango.build_template_change_note("this-is-a-new-slug")
        monkeypatch.setattr(note, "to_file", to_file)

        try:
            chango.write_change_note(note, version, encoding=encoding)
        finally:
            if not existed and expected_path.is_dir():
                shutil.rmtree(expected_path)

    def test_write_change_note_new_string_version(self, chango):
        note = chango.build_template_change_note("this-is-a-new-slug")
        with pytest.raises(TypeError, match="Version 'new-version-uid' not available yet."):
            chango.write_change_note(note, "new-version-uid")

    def test_load_version_note_unavailable(self, chango):
        with pytest.raises(ValueError, match="Version '1.4' not available."):
            chango.load_version_note("1.4")

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
    def test_load_version_note(self, chango, version):
        version_note = chango.load_version_note(version)

        version_uid = ensure_uid(version)
        expected_uids = {
            f"uid_{(version_uid or 'ur').replace('.', '-')}_{idx}" for idx in range(3)
        }

        assert version_note.uid == version_uid
        assert version_note.date == (
            dtm.date(2024, 1, int(version_uid.split(".")[-1])) if version else None
        )
        assert set(version_note) == expected_uids

    @pytest.mark.parametrize(
        ("start_from", "end_at"),
        [(None, None), (None, "1.2"), ("1.3", None), ("1.2", "1.3"), ("1.3", "1.3")],
    )
    def test_load_version_history(self, chango, start_from, end_at):
        lower_idx = int(start_from.split(".")[-1]) if start_from else 1
        upper_idx = int(end_at.split(".")[-1]) + 1 if end_at else 4

        versions = {
            Version(f"1.{idx}", dtm.date(2024, 1, idx)) for idx in range(lower_idx, upper_idx)
        }
        if not end_at:
            versions |= {Version("1.3.1", dtm.date(2024, 1, 3)), None}
        version_history = chango.load_version_history(start_from, end_at)

        assert set(version_history) == set(map(ensure_uid, versions))
        for version in versions:
            assert version_history[ensure_uid(version)].date == (version.date if version else None)
            assert version_history[ensure_uid(version)].version == version

    def test_release_no_unreleased_changes(self, chango_no_unreleased: ChanGo):
        version = Version("1.4", dtm.date(2024, 1, 4))
        assert not chango_no_unreleased.release(version)
        assert not chango_no_unreleased.scanner.is_available(version)

    def test_release(self, chango):
        version = Version("1.4", dtm.date(2024, 1, 4))
        expected_path = chango.scanner.base_directory / "1.4_2024-01-04"
        expected_files = {
            (file.name, file.read_bytes())
            for file in (self.DATA_ROOT / "unreleased").iterdir()
            if file.name != "not-a-change-note.txt"
        }

        try:
            assert chango.release(version)
            scanner = DirectoryVersionScanner(self.DATA_ROOT, "unreleased")
            assert scanner.is_available(version)
            assert scanner.get_version(version.uid) == version

            assert expected_path.is_dir()
            assert {
                (file.name, file.read_bytes()) for file in expected_path.iterdir()
            } == expected_files
        finally:
            for file_name, file_content in expected_files:
                (self.DATA_ROOT / "unreleased" / file_name).write_bytes(file_content)
            if expected_path.is_dir():
                shutil.rmtree(expected_path)

    def test_release_same_directory(self, chango, monkeypatch):
        def get_write_directory(*_, **__):
            return chango.scanner.unreleased_directory

        monkeypatch.setattr(chango, "get_write_directory", get_write_directory)

        version = Version("1.4", dtm.date(2024, 1, 4))
        expected_files = {
            (file.name, file.read_bytes())
            for file in (self.DATA_ROOT / "unreleased").iterdir()
            if file.name != "not-a-change-note.txt"
        }
        try:
            assert chango.release(version)
            for file_name, file_content in expected_files:
                assert (self.DATA_ROOT / "unreleased" / file_name).read_bytes() == file_content
        except Exception:
            for file_name, file_content in expected_files:
                (self.DATA_ROOT / "unreleased" / file_name).write_bytes(file_content)

    def test_build_github_event_change_note(self, chango, monkeypatch):
        monkeypatch.setattr(
            chango,
            "build_github_event_change_note",
            functools.partial(ChanGo.build_github_event_change_note, chango),
        )
        with pytest.raises(NotImplementedError):
            chango.build_github_event_change_note({})

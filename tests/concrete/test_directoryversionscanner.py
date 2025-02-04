#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

import datetime as dtm
from pathlib import Path

import pytest

from chango import Version
from chango.concrete import DirectoryVersionScanner
from chango.error import ChanGoError
from tests.auxil.files import data_path


@pytest.fixture
def scanner() -> DirectoryVersionScanner:
    return DirectoryVersionScanner(TestDirectoryVersionScanner.DATA_ROOT, "unreleased")


@pytest.fixture
def scanner_no_unreleased() -> DirectoryVersionScanner:
    return DirectoryVersionScanner(TestDirectoryVersionScanner.DATA_ROOT, "no-unreleased")


class TestDirectoryVersionScanner:
    DATA_ROOT = data_path("directoryversionscanner")

    def test_init_basic(self):
        scanner = DirectoryVersionScanner(self.DATA_ROOT, "unreleased")
        assert scanner.base_directory == self.DATA_ROOT
        assert scanner.unreleased_directory == self.DATA_ROOT / "unreleased"

        scanner = DirectoryVersionScanner(self.DATA_ROOT, self.DATA_ROOT / "unreleased")
        assert scanner.base_directory == self.DATA_ROOT
        assert scanner.unreleased_directory == self.DATA_ROOT / "unreleased"

    def test_init_relative(self):
        scanner = DirectoryVersionScanner("../data/directoryversionscanner", "unreleased")
        assert scanner.base_directory == self.DATA_ROOT
        assert scanner.unreleased_directory == self.DATA_ROOT / "unreleased"

    def test_base_directory_not_exists(self):
        with pytest.raises(ValueError, match="does not exist"):
            DirectoryVersionScanner("does_not_exist", "unreleased")

    def test_unreleased_directory_not_exists(self):
        with pytest.raises(ValueError, match="does not exist"):
            DirectoryVersionScanner(self.DATA_ROOT, "does_not_exist")

    @pytest.mark.parametrize(
        ("version", "expected"),
        [
            ("1.1", True),
            (Version("1.1", dtm.date(2024, 1, 1)), True),
            (Version("1.1", dtm.date(2024, 5, 1)), False),
            ("1.2", True),
            (Version("1.2", dtm.date(2024, 1, 2)), True),
            (Version("1.2", dtm.date(2024, 5, 1)), False),
            ("1.3", True),
            (Version("1.3", dtm.date(2024, 1, 3)), True),
            (Version("1.3", dtm.date(2024, 5, 1)), False),
            ("1.3.1", True),
            (Version("1.3.1", dtm.date(2024, 1, 3)), True),
            (Version("1.3.1", dtm.date(2024, 5, 1)), False),
            (None, True),
            ("1.4", False),
            ("1.0", False),
        ],
    )
    def test_is_available(self, scanner, version, expected):
        assert scanner.is_available(version) == expected

    def test_is_available_no_unreleased(self, scanner_no_unreleased):
        assert scanner_no_unreleased.is_available(None) is False

    def test_has_unreleased_changes(self, scanner, scanner_no_unreleased):
        assert scanner.has_unreleased_changes() is True
        assert scanner_no_unreleased.has_unreleased_changes() is False

    def test_get_latest_version(self, scanner):
        # It's important that we get 1.3.1 here and not 1.3, since both are released
        # on the same day such that lexicographical sorting kicks in!
        latest = scanner.get_latest_version()
        assert latest.uid == "1.3.1"
        assert latest.date == dtm.date(2024, 1, 3)

    def test_get_latest_version_nothing_released(self):
        scanner = DirectoryVersionScanner(self.DATA_ROOT / "no-released", "unreleased")
        with pytest.raises(ChanGoError, match="No versions available"):
            scanner.get_latest_version()

    def test_get_available_versions(self, scanner):
        assert set(scanner.get_available_versions()) == {
            Version("1.1", dtm.date(2024, 1, 1)),
            Version("1.2", dtm.date(2024, 1, 2)),
            Version("1.3", dtm.date(2024, 1, 3)),
            Version("1.3.1", dtm.date(2024, 1, 3)),
        }

    def test_get_available_versions_start_from(self, scanner):
        assert set(scanner.get_available_versions(start_from="1.2")) == {
            Version("1.2", dtm.date(2024, 1, 2)),
            Version("1.3", dtm.date(2024, 1, 3)),
            Version("1.3.1", dtm.date(2024, 1, 3)),
        }

    def test_get_available_versions_end_at(self, scanner):
        assert set(scanner.get_available_versions(end_at="1.2")) == {
            Version("1.1", dtm.date(2024, 1, 1)),
            Version("1.2", dtm.date(2024, 1, 2)),
        }

    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_lookup_change_note(self, scanner, idx):
        change_note = scanner.lookup_change_note(f"uid_1-{idx}_0")
        assert change_note.uid == f"uid_1-{idx}_0"
        assert change_note.version == Version(f"1.{idx}", dtm.date(2024, 1, idx))
        assert (
            change_note.file_path
            == self.DATA_ROOT
            / f"1.{idx}_2024-01-0{idx}"
            / f"comment-change-note.uid_1-{idx}_0.txt"
        )

    def test_lookup_change_note_unreleased(self, scanner):
        change_note = scanner.lookup_change_note("uid_ur_0")
        assert change_note.uid == "uid_ur_0"
        assert change_note.version is None
        assert (
            change_note.file_path
            == self.DATA_ROOT / "unreleased" / "comment-change-note.uid_ur_0.txt"
        )

    def test_lookup_change_note_not_found(self, scanner):
        with pytest.raises(ChanGoError, match="not found in any version"):
            scanner.lookup_change_note("unknown_uid")

    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_get_version(self, scanner, idx):
        version = scanner.get_version(f"1.{idx}")
        assert version.uid == f"1.{idx}"
        assert version.date == dtm.date(2024, 1, idx)

    def test_get_version_not_found(self, scanner):
        with pytest.raises(ChanGoError, match="not available"):
            scanner.get_version("1.4")

    @pytest.mark.parametrize(
        "version",
        [
            "1.1",
            Version("1.1", dtm.date(2024, 1, 1)),
            "1.2",
            Version("1.2", dtm.date(2024, 1, 2)),
            "1.3",
            Version("1.3", dtm.date(2024, 1, 3)),
            "1.3.1",
            Version("1.3.1", dtm.date(2024, 1, 3)),
            None,
        ],
    )
    def test_get_changes(self, scanner, version):
        changes = set(scanner.get_changes(version))

        uid = version.uid if isinstance(version, Version) else (version or "ur")

        assert changes == {f"uid_{uid.replace('.', '-')}_{idx}" for idx in range(3)}

    def test_get_changes_not_found(self, scanner):
        with pytest.raises(ChanGoError, match="not available"):
            scanner.get_changes("1.4")

    def test_invalidate_caches(self, scanner):
        original_versions = {
            Version("1.1", dtm.date(2024, 1, 1)),
            Version("1.2", dtm.date(2024, 1, 2)),
            Version("1.3", dtm.date(2024, 1, 3)),
            Version("1.3.1", dtm.date(2024, 1, 3)),
        }

        assert set(scanner.get_available_versions()) == original_versions

        new_directory = Path(self.DATA_ROOT / "1.4_2024-01-04")
        try:
            new_directory.mkdir()
            assert set(scanner.get_available_versions()) == original_versions
            scanner.invalidate_caches()
            assert set(scanner.get_available_versions()) == original_versions | {
                Version("1.4", dtm.date(2024, 1, 4))
            }
        finally:
            new_directory.rmdir()

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm

import pytest

from chango import Version
from chango.abc import VersionScanner
from chango.concrete import DirectoryVersionScanner
from chango.error import ChanGoError
from tests.auxil.files import data_path


@pytest.fixture
def scanner(monkeypatch) -> DirectoryVersionScanner:
    # DVS overrides get_version, but we want to test the base implementation
    monkeypatch.setattr(DirectoryVersionScanner, "get_version", VersionScanner.get_version)
    return DirectoryVersionScanner(TestVersionScanner.DATA_ROOT, "unreleased")


@pytest.fixture
def scanner_no_unreleased(monkeypatch) -> DirectoryVersionScanner:
    # DVS overrides get_version, but we want to test the base implementation
    monkeypatch.setattr(DirectoryVersionScanner, "get_version", VersionScanner.get_version)
    return DirectoryVersionScanner(TestVersionScanner.DATA_ROOT, "no-unreleased")


class TestVersionScanner:
    """Since VersionScanner is an abstract base class, we are testing with DirectoryVersionScanner
    as a simple implementation.

    Note that we do *not* test abstract methods, as that is the responsibility of the concrete
    implementations.
    """

    DATA_ROOT = data_path("directoryversionscanner")

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
            (object(), False),
            (dtm.date(2024, 1, 1), False),
        ],
    )
    def test_contains(self, scanner, version, expected):
        assert (version in scanner) == expected

    def test_contains_no_unreleased_changes(self, scanner_no_unreleased):
        assert None not in scanner_no_unreleased

    def test_iter(self, scanner):
        assert set(scanner) == {
            Version("1.1", dtm.date(2024, 1, 1)),
            Version("1.2", dtm.date(2024, 1, 2)),
            Version("1.3", dtm.date(2024, 1, 3)),
            Version("1.3.1", dtm.date(2024, 1, 3)),
        }

    def test_len(self, scanner):
        assert len(scanner) == len(scanner.get_available_versions())

    @pytest.mark.parametrize("idx", [1, 2, 3])
    def test_get_version(self, scanner, idx):
        version = scanner.get_version(f"1.{idx}")
        assert version.uid == f"1.{idx}"
        assert version.date == dtm.date(2024, 1, idx)

    def test_get_version_not_found(self, scanner):
        with pytest.raises(ChanGoError, match="not available"):
            scanner.get_version("1.4")

    def test_invalidates_caches(self, scanner):
        # This does nothing, but we want to test that it doesn't raise an error
        scanner.invalidate_caches = VersionScanner.invalidate_caches
        scanner.invalidate_caches(scanner)

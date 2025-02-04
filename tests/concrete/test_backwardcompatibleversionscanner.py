#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
from unittest.mock import MagicMock

import pytest

from chango import Version
from chango.concrete import BackwardCompatibleVersionScanner
from chango.error import ChanGoError


class TestBackwardCompatibleVersionScanner:
    @staticmethod
    def build_mock_scanners(method_name: str, expected_results: list[object]) -> list[MagicMock]:
        mocks = [MagicMock() for _ in range(len(expected_results))]
        for mock, result in zip(mocks, expected_results, strict=False):
            method = getattr(mock, method_name)
            if isinstance(result, Exception):
                method.side_effect = result
            else:
                method.return_value = result
        return mocks

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            ([True, False], True),
            ([False, False], False),
            ([False, True], True),
            ([True, True], True),
        ],
    )
    @pytest.mark.parametrize("version", ["1.0.0", "2.0.0", None])
    def test_is_available(self, results, expected, version):
        scanners = self.build_mock_scanners("is_available", results)
        scanner = BackwardCompatibleVersionScanner(scanners)
        assert scanner.is_available(version) == expected

        was_true = False
        for scanner, result in zip(scanners, results, strict=False):
            if not was_true:
                scanner.is_available.assert_called_once_with(version)
                was_true = was_true or result
            else:
                assert not scanner.is_available.called

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            ([True, False], True),
            ([False, False], False),
            ([False, True], True),
            ([True, True], True),
        ],
    )
    def test_has_unreleased_changes(self, results, expected):
        scanners = self.build_mock_scanners("has_unreleased_changes", results)
        scanner = BackwardCompatibleVersionScanner(scanners)
        assert scanner.has_unreleased_changes() == expected

        was_true = False
        for scanner, result in zip(scanners, results, strict=False):
            if not was_true:
                scanner.has_unreleased_changes.assert_called_once_with()
                was_true = was_true or result
            else:
                assert not scanner.has_unreleased_changes.called

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            (
                [
                    Version("1.0.0", date=dtm.date(2025, 1, 1)),
                    Version("1.0.0", date=dtm.date(2025, 1, 10)),
                ],
                Version("1.0.0", date=dtm.date(2025, 1, 10)),
            ),
            (
                [
                    Version("1.0.0", date=dtm.date(2025, 1, 10)),
                    Version("1.0.0", date=dtm.date(2025, 1, 1)),
                ],
                Version("1.0.0", date=dtm.date(2025, 1, 10)),
            ),
            (
                [
                    ChanGoError("No versions available."),
                    Version("1.0.0", date=dtm.date(2025, 1, 10)),
                ],
                Version("1.0.0", date=dtm.date(2025, 1, 10)),
            ),
            (
                [ChanGoError("No versions available."), ChanGoError("No versions available.")],
                ChanGoError("No versions available."),
            ),
        ],
    )
    def test_get_latest_version(self, results, expected):
        scanners = self.build_mock_scanners("get_latest_version", results)
        scanner = BackwardCompatibleVersionScanner(scanners)
        if isinstance(expected, ChanGoError):
            with pytest.raises(ChanGoError, match="No versions available."):
                scanner.get_latest_version()
        else:
            assert scanner.get_latest_version() == expected

        for scanner in scanners:
            scanner.get_latest_version.assert_called_once_with()

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            (
                [
                    (Version("1.0.0", dtm.date.today()), Version("1.0.1", dtm.date.today())),
                    (Version("2.0.0", dtm.date.today()), Version("2.0.1", dtm.date.today())),
                ],
                (
                    Version("1.0.0", dtm.date.today()),
                    Version("1.0.1", dtm.date.today()),
                    Version("2.0.0", dtm.date.today()),
                    Version("2.0.1", dtm.date.today()),
                ),
            ),
            (
                [(Version("1.0.0", dtm.date.today()), Version("1.0.1", dtm.date.today())), []],
                (Version("1.0.0", dtm.date.today()), Version("1.0.1", dtm.date.today())),
            ),
        ],
    )
    def test_get_available_versions(self, results, expected):
        scanners = self.build_mock_scanners("get_available_versions", results)
        scanner = BackwardCompatibleVersionScanner(scanners)
        start_from = object()
        end_at = object()
        assert scanner.get_available_versions(start_from=start_from, end_at=end_at) == expected

        for scanner in scanners:
            scanner.get_available_versions.assert_called_once_with(start_from, end_at)

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            (
                [
                    ChanGoError("Change note '1.0.0' not available."),
                    ChanGoError("Change note '1.0.0' not available."),
                ],
                ChanGoError("Change note '1.0.0' not available."),
            ),
            (
                [
                    "ReturnValueA",
                    ChanGoError("Change note '1.0.0' not available."),
                    "ReturnValueB",
                ],
                "ReturnValueA",
            ),
            (
                [
                    ChanGoError("Change note '1.0.0' not available."),
                    "ReturnValueA",
                    "ReturnValueB",
                ],
                "ReturnValueA",
            ),
        ],
    )
    @pytest.mark.parametrize("method_name", ["lookup_change_note", "get_changes"])
    def test_lookup_change_note_get_changes(self, results, expected, method_name):
        scanners = self.build_mock_scanners(method_name, results)
        scanner = BackwardCompatibleVersionScanner(scanners)
        method_object = getattr(scanner, method_name)
        uid = object()
        if isinstance(expected, ChanGoError):
            with pytest.raises(ChanGoError, match="not available."):
                method_object(uid)
        else:
            assert method_object(uid) == expected

        has_returned = False
        for scanner, result in zip(scanners, results, strict=False):
            if not has_returned:
                getattr(scanner, method_name).assert_called_once_with(uid)
                has_returned = has_returned or not isinstance(result, ChanGoError)
            else:
                assert not getattr(scanner, method_name).called

    def test_invalidate_caches(self):
        scanners = self.build_mock_scanners("invalidate_caches", [None, None])
        scanner = BackwardCompatibleVersionScanner(scanners)
        scanner.invalidate_caches()
        for scanner in scanners:
            scanner.invalidate_caches.assert_called_once_with()

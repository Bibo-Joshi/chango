import inspect
from unittest.mock import MagicMock

import pytest

from chango.concrete import BackwardCompatibleChanGo, BackwardCompatibleVersionScanner
from chango.error import ChanGoError


class TestBackwardCompatibleChanGo:
    @staticmethod
    def build_mocks(
        *,
        chango: tuple[str, list[object]] | None = None,
        scanner: tuple[str, list[object]] | None = None,
    ) -> tuple[MagicMock, list[MagicMock]]:
        if not chango and not scanner:
            raise ValueError("At least one of 'chango' or 'scanner' must be provided.")
        if chango and scanner and len(chango[1]) != len(scanner[1]):
            raise ValueError(
                "The number of chango instances must match the number of scanner instances."
            )
        if (effective_length := len(chango[1] if chango else scanner[1])) < 2:  # noqa PLR2004
            raise ValueError("At least two instances must be provided.")

        def setup_mock(mock, method_name, result_):
            method = getattr(mock, method_name)
            if isinstance(result_, Exception) or (
                inspect.isclass(result_) and issubclass(result_, Exception)
            ):
                method.side_effect = result_
            else:
                method.return_value = result_

        instances = [MagicMock() for _ in range(effective_length)]
        if chango:
            for instance, result in zip(instances, chango[1], strict=False):
                setup_mock(instance, chango[0], result)
        if scanner:
            for instance, result in zip(instances, scanner[1], strict=False):
                setup_mock(instance.scanner, scanner[0], result)

        return instances[0], instances[1:]

    def test_scanner(self):
        chango = BackwardCompatibleChanGo(MagicMock(), [MagicMock(), MagicMock()])
        assert isinstance(chango.scanner, BackwardCompatibleVersionScanner)

    def test_build_template_change_note(self):
        expected_template = object()
        main_instance, legacy_instances = self.build_mocks(
            chango=("build_template_change_note", [expected_template, RuntimeError, RuntimeError]),
            scanner=None,
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        assert chango.build_template_change_note("slug") is expected_template
        main_instance.build_template_change_note.assert_called_once_with("slug", None)
        for legacy_instance in legacy_instances:
            assert not legacy_instance.build_template_change_note.called

        assert chango.build_template_change_note("slug", "uid") is expected_template
        main_instance.build_template_change_note.assert_called_with("slug", "uid")
        for legacy_instance in legacy_instances:
            assert not legacy_instance.build_template_change_note.called

    @pytest.mark.parametrize(
        ("is_available", "version_note", "expected"),
        [
            (
                [True, False, False],
                ["main-version-note", ChanGoError, ChanGoError],
                "main-version-note",
            ),
            (
                [False, True, False],
                [ChanGoError, "legacy-version-note-1", ChanGoError],
                "legacy-version-note-1",
            ),
            (
                [False, False, True],
                [ChanGoError, ChanGoError, "legacy-version-note-2"],
                "legacy-version-note-2",
            ),
        ],
    )
    @pytest.mark.parametrize("version", ["version", None])
    def test_build_version_note(self, is_available, version_note, version, expected):
        main_instance, legacy_instances = self.build_mocks(
            chango=("build_version_note", version_note), scanner=("is_available", is_available)
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        assert chango.build_version_note(version) == expected
        has_returned = False
        for instance, was_available in zip(
            [main_instance, *legacy_instances], is_available, strict=False
        ):
            if not has_returned:
                instance.scanner.is_available.assert_called_once_with(version)
                if was_available:
                    instance.build_version_note.assert_called_once_with(version)
                else:
                    assert not instance.build_version_note.called
                has_returned = has_returned or was_available
            else:
                assert not instance.scanner.is_available.called
                assert not instance.build_version_note.called

    def test_build_version_note_not_found(self):
        main_instance, legacy_instances = self.build_mocks(
            chango=("build_version_note", [ChanGoError, ChanGoError, ChanGoError]),
            scanner=("is_available", [False, False, False]),
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        with pytest.raises(ChanGoError):
            chango.build_version_note("version")

        for instance in [main_instance, *legacy_instances]:
            instance.scanner.is_available.assert_called_once_with("version")
            instance.build_version_note.assert_not_called()

    def test_build_version_history(self):
        expected_history = object()
        main_instance, legacy_instances = self.build_mocks(
            chango=("build_version_history", [expected_history, RuntimeError, RuntimeError]),
            scanner=None,
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        assert chango.build_version_history() is expected_history
        main_instance.build_version_history.assert_called_once_with()
        for legacy_instance in legacy_instances:
            assert not legacy_instance.build_version_history.called

    @pytest.mark.parametrize(
        ("results", "expected"),
        [
            (["main-change-note", ChanGoError, ChanGoError], "main-change-note"),
            ([ChanGoError, "legacy-change-note-1", ChanGoError], "legacy-change-note-1"),
            ([ChanGoError, ChanGoError, "legacy-change-note-2"], "legacy-change-note-2"),
        ],
    )
    def test_load_change_note(self, results, expected):
        main_instance, legacy_instances = self.build_mocks(
            chango=("load_change_note", [expected, ChanGoError, ChanGoError]), scanner=None
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        assert chango.load_change_note("uid") == expected

        has_returned = False
        for instance, result in zip([main_instance, *legacy_instances], results, strict=False):
            if not has_returned:
                instance.load_change_note.assert_called_once_with("uid")
                has_returned = has_returned or not isinstance(result, ChanGoError)
            else:
                assert not instance.load_change_note.called

    def test_load_change_note_not_found(self):
        main_instance, legacy_instances = self.build_mocks(
            chango=("load_change_note", [ChanGoError, ChanGoError, ChanGoError]), scanner=None
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        with pytest.raises(ChanGoError):
            chango.load_change_note("uid")

        for instance in [main_instance, *legacy_instances]:
            instance.load_change_note.assert_called_once_with("uid")

    def test_get_write_directory(self):
        expected_directory = object()
        main_instance, legacy_instances = self.build_mocks(
            chango=("get_write_directory", [expected_directory, RuntimeError, RuntimeError]),
            scanner=None,
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        assert chango.get_write_directory("change_note", "version") is expected_directory
        main_instance.get_write_directory.assert_called_once_with("change_note", "version")
        for legacy_instance in legacy_instances:
            assert not legacy_instance.get_write_directory.called

    def test_build_github_event_change_note(self):
        expected = object()
        main_instance, legacy_instances = self.build_mocks(
            chango=("build_github_event_change_note", [expected, RuntimeError, RuntimeError]),
            scanner=None,
        )
        chango = BackwardCompatibleChanGo(main_instance, legacy_instances)

        call_args = [[("event", "data"), ("event", "data")], [("event",), ("event", None)]]

        for args, expected_args in call_args:
            assert chango.build_github_event_change_note(*args) is expected
            main_instance.build_github_event_change_note.assert_called_with(*expected_args)
            for legacy_instance in legacy_instances:
                assert not legacy_instance.build_github_event_change_note.called

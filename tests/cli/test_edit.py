#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from pathlib import Path
from unittest.mock import MagicMock

from tests.cli.conftest import ReuseCliRunner


class TestEdit:
    def test_release_no_unreleased(self, cli: ReuseCliRunner, mock_chango_instance, monkeypatch):
        launch_mock = MagicMock()
        monkeypatch.setattr("typer.launch", launch_mock)

        test_path = Path("this/is/a/test/path")
        mock_chango_instance.scanner.lookup_change_note.return_value.file_path = test_path

        result = cli.invoke(args=["edit", "some_uid"])

        assert result.check_exit_code()
        assert result.stdout == ""

        mock_chango_instance.scanner.lookup_change_note.assert_called_once_with("some_uid")
        launch_mock.assert_called_once_with(test_path.as_posix())

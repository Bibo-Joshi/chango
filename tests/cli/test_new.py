#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.cli.conftest import ReuseCliRunner


class TestNew:
    @pytest.mark.parametrize("edit", [True, False, None], ids=["Edit", "NoEdit", "DefaultEdit"])
    @pytest.mark.parametrize("slug_option", ["--slug", "-s"], ids=["LongSlug", "ShortSlug"])
    @pytest.mark.parametrize("edit_option", ["--edit", "-e"], ids=["LongEdit", "ShortEdit"])
    @pytest.mark.parametrize(
        "no_edit_option", ["--no-edit", "-ne"], ids=["LongNoEdit", "ShortNoEdit"]
    )
    def test_new(
        self,
        cli: ReuseCliRunner,
        mock_chango_instance,
        monkeypatch,
        edit,
        slug_option,
        edit_option,
        no_edit_option,
    ):
        launch_mock = MagicMock()
        monkeypatch.setattr("typer.launch", launch_mock)

        test_path = Path("this/is/a/test/path")
        change_note = mock_chango_instance.build_template_change_note.return_value
        change_note.file_name = "expected_file_name"
        mock_chango_instance.write_change_note.return_value = test_path

        args = ["new", slug_option, "some_uid"]
        if edit is not None:
            args.extend([edit_option if edit else no_edit_option])
        result = cli.invoke(args=args)

        assert result.check_exit_code()
        assert result.stdout == "Created new change note expected_file_name\n"

        mock_chango_instance.build_template_change_note.assert_called_once_with(slug="some_uid")
        mock_chango_instance.write_change_note.assert_called_once_with(change_note, version=None)
        if edit in (True, None):
            launch_mock.assert_called_once_with(test_path.as_posix())
        else:
            launch_mock.assert_not_called()

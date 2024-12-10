#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

import datetime as dtm

import pytest
from click import UsageError

from chango import Version
from tests.cli.conftest import ReuseCliRunner


class TestRelease:
    @pytest.mark.parametrize("has_unreleased", [True, False])
    def test_release_basic(self, cli: ReuseCliRunner, mock_chango_instance, has_unreleased):
        mock_chango_instance.release.return_value = has_unreleased
        result = cli.invoke(args=["release", "--uid", "1.0.0", "--date", "2024-01-01"])

        assert result.check_exit_code()
        assert result.stdout == (
            "Released version 1.0.0 on 2024-01-01\n"
            if has_unreleased
            else "No unreleased changes found.\n"
        )

        assert len(mock_chango_instance.release.call_args_list) == 1
        assert mock_chango_instance.release.call_args_list[0].args == (
            Version("1.0.0", dtm.date(2024, 1, 1)),
        )

    def test_release_default_date(self, cli: ReuseCliRunner, mock_chango_instance):
        result = cli.invoke(args=["release", "--uid", "1.0.0"])
        assert result.check_exit_code()
        assert result.stdout == f"Released version 1.0.0 on {dtm.date.today()}\n"

        assert len(mock_chango_instance.release.call_args_list) == 1
        assert mock_chango_instance.release.call_args_list[0].args == (
            Version("1.0.0", dtm.date.today()),
        )

    def test_release_invalid_date(self, cli: ReuseCliRunner, mock_chango_instance):
        result = cli.invoke(args=["release", "--uid", "1.0.0", "--date", "invalid"])
        assert result.check_exit_code(UsageError.exit_code)
        assert "Invalid value for '--date':" in result.stdout
        assert len(mock_chango_instance.release.call_args_list) == 0

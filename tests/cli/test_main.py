#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from chango.__about__ import __version__
from tests.cli.conftest import ReuseCliRunner


class TestMain:
    def test_version(self, cli: ReuseCliRunner):
        result = cli.invoke(args=["--version"])
        assert result.check_exit_code()
        assert result.stdout == __version__ + "\n"

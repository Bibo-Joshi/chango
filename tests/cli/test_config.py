#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from contextlib import nullcontext
from pathlib import Path

import pytest
from click import UsageError

from tests.auxil.files import PROJECT_ROOT_PATH, data_path, temporary_chdir
from tests.cli.conftest import ReuseCliRunner


class TestConfig:
    @pytest.mark.parametrize(
        "path",
        [
            None,
            data_path("config/pyproject.toml"),
            data_path("config/pyproject.toml").relative_to(Path.cwd(), walk_up=True),
            data_path("config"),
        ],
        ids=["None", "absolute", "relative", "directory"],
    )
    def test_show_path_selection(self, cli: ReuseCliRunner, path):
        with temporary_chdir(data_path("config")) if path is None else nullcontext():
            args = ["config", "--path", str(path), "show"] if path else ["config", "show"]

            result = cli.invoke(args)
            assert result.check_exit_code(0)

            assert str(data_path("config/pyproject.toml")) in result.stdout
            assert 'sys_path = "/abs/sys_path"' in result.stdout
            assert (
                'chango_instance = { name= "name", module = "module", package = "package" }'
                in result.stdout
            )

    def test_show_path_not_found(self, cli: ReuseCliRunner):
        path = Path("nonexistent").absolute()
        result = cli.invoke(["config", "--path", str(path), "show"])
        assert result.check_exit_code(UsageError.exit_code)
        assert f"File not found: {path!s}" in result.stdout

    def test_show_invalid_toml(self, cli: ReuseCliRunner, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text("invalid toml")

        with temporary_chdir(tmp_path):
            result = cli.invoke(["config", "--path", str(path), "show"])
            assert result.check_exit_code(UsageError.exit_code)
            assert "Failed to parse the configuration file" in result.stdout

    def test_show_no_chango_config(self, cli: ReuseCliRunner, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text("[tool.other]")

        with temporary_chdir(tmp_path):
            result = cli.invoke(["config", "--path", str(path), "show"])
            assert result.check_exit_code(UsageError.exit_code)
            assert "No configuration found for chango" in result.stdout

    def test_validate_invalid_chango_config(self, cli: ReuseCliRunner, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text("[tool.chango]\nsys_path = 42")

        with temporary_chdir(tmp_path):
            result = cli.invoke(["config", "--path", str(path), "validate"])
            assert result.check_exit_code(UsageError.exit_code)
            assert f"Validation of config file at {path!s} failed:" in result.stdout

    def test_validate_import_error(self, cli: ReuseCliRunner, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text(
            "[tool.chango]\nsys_path = 'sys_path'\nchango_instance = { name= 'name', module = "
            "'module', package = 'package' }"
        )

        with temporary_chdir(tmp_path):
            result = cli.invoke(["config", "--path", str(path), "validate"])
            assert result.check_exit_code(UsageError.exit_code)
            assert "importing the ChanGo instance failed" in result.stdout

    def test_validate_success(self, cli: ReuseCliRunner):
        with temporary_chdir(PROJECT_ROOT_PATH):
            result = cli.invoke(["config", "validate"])
            assert result.check_exit_code(0)
            assert "The configuration in" in result.stdout
            assert str(PROJECT_ROOT_PATH / "pyproject.toml") in result.stdout
            assert "valid" in result.stdout

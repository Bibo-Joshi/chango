#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import sys
from collections.abc import Collection
from contextlib import nullcontext
from pathlib import Path
from string import Template
from types import SimpleNamespace

import pytest

from chango.concrete import BackwardCompatibleChanGo
from chango.config import ChanGoConfig, ChanGoInstanceConfig
from tests.auxil.files import PROJECT_ROOT_PATH, data_path, temporary_chdir


class TestChanGoInstanceConfig:
    chango_instance = ChanGoInstanceConfig(name="name", module="module", package="package")

    def test_init(self, tmp_path):
        # To ensure that there is pyproject.toml in the current directory that would interfere
        # with the test.
        with temporary_chdir(tmp_path):
            config = ChanGoConfig(sys_path=Path("sys_path"), chango_instance=self.chango_instance)
            assert config.sys_path == Path("sys_path")
            assert config.chango_instance is self.chango_instance

    def test_init_required(self, tmp_path):
        # To ensure that there is pyproject.toml in the current directory that would interfere
        # with the test.
        with temporary_chdir(tmp_path):
            config = ChanGoConfig(chango_instance=self.chango_instance)
            assert config.sys_path is None
            assert config.chango_instance is self.chango_instance

    @pytest.mark.parametrize(
        "path",
        [
            None,
            data_path("config/pyproject.toml"),
            data_path("config/pyproject.toml").as_posix(),
            data_path("config/pyproject.toml").relative_to(Path.cwd(), walk_up=True),
            data_path("config/pyproject.toml").relative_to(Path.cwd(), walk_up=True).as_posix(),
            data_path("config"),
            data_path("config").as_posix(),
        ],
        ids=[
            "None",
            "absolute",
            "absolute-string",
            "relative",
            "relative-string",
            "directory",
            "directory-string",
        ],
    )
    def test_load_path_input(self, path):
        with temporary_chdir(data_path("config")) if path is None else nullcontext():
            config = ChanGoConfig.load(path)
            assert config.sys_path == Path("/abs/sys_path").absolute()
            assert config.chango_instance == self.chango_instance

    @pytest.mark.parametrize(
        ("sys_path", "expected"),
        [
            (None, None),
            (Path("/abs/sys_path").absolute(), Path("/abs/sys_path").absolute()),
            (Path("relative"), data_path("config/relative").absolute()),
            (Path("../relative"), data_path("relative").absolute()),
        ],
        ids=["None", "absolute", "relative", "relative-parent"],
    )
    def test_load_sys_path_output(self, sys_path, expected):
        tmp_file = data_path("config/tmp.toml")
        try:
            sys_path_entry = f"sys_path = '{sys_path}'" if sys_path else ""
            template = Template(
                data_path("config/pyproject.toml.template").read_text(encoding="utf-8")
            )
            tmp_file.write_text(
                template.substitute(sys_path_entry=sys_path_entry), encoding="utf-8"
            )

            config = ChanGoConfig.load(tmp_file)
            assert config.sys_path == expected
        finally:
            tmp_file.unlink()

    def test_import_chango_instance_basic(self):
        # Testing with importlib is a bit of a hassle, and also we don't want to test
        # the actual import, but the import logic. So here we just test that the
        # config of the chango repo itself is imported correctly.
        with temporary_chdir(PROJECT_ROOT_PATH):
            config = ChanGoConfig.load()
            chango_instance = config.import_chango_instance()
            assert isinstance(chango_instance, BackwardCompatibleChanGo)

    @pytest.mark.parametrize(
        ("sys_path", "expected"),
        [
            (None, None),
            (Path("/abs/sys_path").absolute(), Path("/abs/sys_path").absolute()),
            (Path("relative"), Path.cwd() / "relative"),
        ],
        ids=["None", "relative", "relative-parent"],
    )
    def test_import_chango_instance_sys_path_input(self, monkeypatch, sys_path, expected):
        original_sys_path = sys.path.copy()

        # Here we test that the sys_path is added to the system path correctly.
        def is_in_sys_path(system_path: Collection[str], search_path: Path):
            sys_paths = map(Path, system_path)
            return any(search_path == path for path in sys_paths)

        def import_module(*_, **__):
            return SimpleNamespace(name=sys.path.copy())

        monkeypatch.setattr("importlib.import_module", import_module)

        reported_path = ChanGoConfig(
            sys_path=sys_path, chango_instance=self.chango_instance
        ).import_chango_instance()

        if expected is not None:
            assert is_in_sys_path(reported_path, expected)
        else:
            assert reported_path == original_sys_path

        # Check that everything was restored correctly
        assert sys.path == original_sys_path

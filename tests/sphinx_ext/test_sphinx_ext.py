#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from collections.abc import Callable
from pathlib import Path
from string import Template

import pytest
import shortuuid
from _pytest.tmpdir import TempPathFactory
from sphinx.testing.util import SphinxTestApp

from chango import __version__
from chango._utils.types import PathLike
from tests.auxil.files import data_path, path_to_python_string

MAKE_APP_TYPE = Callable[..., SphinxTestApp]


class TestSphinxExt:
    SPHINX_EXT_TEST_ROOT = data_path("sphinx_ext")

    @classmethod
    def create_template(
        cls,
        *,
        tmp_path_factory: TempPathFactory,
        conf_value_insert: str | None = None,
        directive_insert: str = ".. chango::",
    ) -> Path:
        uid = shortuuid.uuid()
        src_dir = f"test-{uid}"
        tmp_dir = tmp_path_factory.mktemp(src_dir)

        conf_template = Template(
            (cls.SPHINX_EXT_TEST_ROOT / "conf_value.py.template").read_text(encoding="utf-8")
        )
        index_template = Template(
            (cls.SPHINX_EXT_TEST_ROOT / "index.rst.template").read_text(encoding="utf-8")
        )

        (tmp_dir / "conf.py").write_text(
            conf_template.substitute(chango_pyproject_toml_path=conf_value_insert),
            encoding="utf-8",
        )
        (tmp_dir / "index.rst").write_text(
            index_template.substitute(directive=directive_insert), encoding="utf-8"
        )

        return tmp_dir

    @staticmethod
    def compute_chango_pyproject_toml_path_insert(
        path: str | Path, path_representation: PathLike
    ) -> str:
        if path == "explicit_none":
            return "chango_pyproject_toml_path = None"
        if path is None:
            return ""
        return f"chango_pyproject_toml_path = {path_to_python_string(path, path_representation)}"

    @pytest.mark.parametrize(
        "path",
        [
            None,
            "explicit_none",
            data_path("config/pyproject.toml"),
            data_path("config/pyproject.toml").relative_to(Path.cwd(), walk_up=True),
            data_path("config"),
        ],
        ids=["None", "explicit_none", "absolute", "relative", "directory"],
    )
    @pytest.mark.parametrize("path_representation", [str, Path])
    def test_chango_pyproject_toml_path_valid(
        self, path, path_representation, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory
    ):
        app = make_app(
            srcdir=self.create_template(
                conf_value_insert=self.compute_chango_pyproject_toml_path_insert(
                    path, path_representation
                ),
                tmp_path_factory=tmp_path_factory,
            )
        )

        if path in ("explicit_none", None):
            assert app.config.chango_pyproject_toml_path is None
        else:
            assert (
                app.config.chango_pyproject_toml_path == path.as_posix()
                if path_representation is str
                else path
            )

    @pytest.mark.parametrize("path", [1, {"key": "value"}, [1, 2, 3]], ids=["int", "dict", "list"])
    def test_chango_pyproject_toml_path_invalid(
        self, path, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory
    ):
        insert = f"chango_pyproject_toml_path = {path!r}"

        with pytest.raises(
            TypeError, match="Expected 'chango_pyproject_toml_path' to be a string or Path"
        ):
            make_app(
                srcdir=self.create_template(
                    conf_value_insert=insert, tmp_path_factory=tmp_path_factory
                )
            )

    def test_metadata(self, app: SphinxTestApp):
        assert app.extensions["chango.sphinx_ext"].version == __version__
        assert app.extensions["chango.sphinx_ext"].parallel_read_safe is True
        assert app.extensions["chango.sphinx_ext"].parallel_write_safe is True

    @pytest.mark.parametrize(
        "path",
        [
            None,
            "explicit_none",
            data_path("config/pyproject.toml"),
            data_path("config/pyproject.toml").relative_to(Path.cwd(), walk_up=True),
            data_path("config"),
        ],
        ids=["None", "explicit_none", "absolute", "relative", "directory"],
    )
    @pytest.mark.parametrize("path_representation", [str, Path])
    def test_directive_chango_instance_loading(
        self,
        make_app: MAKE_APP_TYPE,
        path,
        path_representation,
        tmp_path_factory: TempPathFactory,
        cg_config_mock,
    ):
        app = make_app(
            srcdir=self.create_template(
                conf_value_insert=self.compute_chango_pyproject_toml_path_insert(
                    path, path_representation
                ),
                tmp_path_factory=tmp_path_factory,
            )
        )
        app.build()
        received_sys_path = cg_config_mock.get().sys_path

        if path in ("explicit_none", None):
            assert received_sys_path is None
        else:
            assert received_sys_path == path

    @pytest.mark.parametrize(
        "headline", [None, "This is a headline"], ids=["no_headline", "headline"]
    )
    def test_directive_rendering_basic(
        self, cg_config_mock, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory, headline
    ):
        directive = f".. chango:: {headline}" if headline else ".. chango::"

        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        app.build()

        index = app.outdir.joinpath("index.html")
        assert index.exists()

        content = index.read_text(encoding="utf-8")
        assert cg_config_mock.rendered_content in content

        if headline:
            assert f"<h1>{headline}" in content

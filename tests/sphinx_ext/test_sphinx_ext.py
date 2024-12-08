#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import logging
from collections.abc import Callable, Sequence
from pathlib import Path
from string import Template
from typing import Annotated

import pytest
import shortuuid
from _pytest.tmpdir import TempPathFactory
from sphinx.testing.util import SphinxTestApp
from sphinx.util.logging import pending_warnings

from chango import __version__
from chango._utils.types import PathLike
from chango.constants import MarkupLanguage
from tests.auxil.files import data_path, path_to_python_string
from tests.sphinx_ext.conftest import MockChanGo, MockStorage

MAKE_APP_TYPE = Callable[..., SphinxTestApp]


class SphinxBuildError(RuntimeError):
    pass


class TestSphinxExt:
    SPHINX_EXT_TEST_ROOT = data_path("sphinx_ext")

    @staticmethod
    def assert_successful_build(app: SphinxTestApp):
        with pending_warnings() as mem_handler:
            app.build()

            for record in mem_handler.buffer:
                if record.levelno == logging.ERROR:
                    raise SphinxBuildError(record.getMessage())

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
        self.assert_successful_build(app)
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

        self.assert_successful_build(app)

        index = app.outdir.joinpath("index.html")
        assert index.exists()

        content = index.read_text(encoding="utf-8")
        assert cg_config_mock.rendered_content in content

        if headline:
            assert f"<h1>{headline}" in content
        else:
            assert f"<h1>{headline}" not in content

    def test_directive_rendering_passed_markup_language(self, cg_config_mock, app: SphinxTestApp):
        self.assert_successful_build(app)
        received_args = cg_config_mock.get().chango.version_history.received_args
        received_kwargs = cg_config_mock.get().chango.version_history.received_kwargs
        assert received_args == (MarkupLanguage.RESTRUCTUREDTEXT,)
        assert received_kwargs == {}

    def test_argument_passing_basic(
        self,
        cg_config_mock: MockStorage,
        make_app: MAKE_APP_TYPE,
        tmp_path_factory: TempPathFactory,
    ):
        directive = """
.. chango::
   :start_from: "start_from"
   :end_at: "end_at"
"""
        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        self.assert_successful_build(app)
        received_kwargs = cg_config_mock.get().chango.received_kwargs
        assert received_kwargs == {"start_from": "start_from", "end_at": "end_at"}

    def test_argument_passing_unknown_option(
        self, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory
    ):
        directive = """
.. chango::
   :unknown:
"""
        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        with pytest.raises(SphinxBuildError, match='unknown option: "unknown"'):
            self.assert_successful_build(app)

    def test_argument_passing_json_data(
        self,
        cg_config_mock: MockStorage,
        make_app: MAKE_APP_TYPE,
        tmp_path_factory: TempPathFactory,
    ):
        directive = """
.. chango::
   :start_from: {"key": "value"}
   :end_at: [false, true, null]
"""
        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        self.assert_successful_build(app)
        received_kwargs = cg_config_mock.get().chango.received_kwargs
        assert received_kwargs == {"start_from": {"key": "value"}, "end_at": [False, True, None]}

    def test_argument_passing_invalid_json_data(
        self, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory
    ):
        directive = """
.. chango::
    :start_from: {"key": "value}
    """
        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        with pytest.raises(SphinxBuildError, match="must be a JSON-loadable value"):
            self.assert_successful_build(app)

    def test_argument_passing_missing_value(
        self, make_app: MAKE_APP_TYPE, tmp_path_factory: TempPathFactory
    ):
        directive = """
.. chango::
    :start_from:
    """
        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        with pytest.raises(SphinxBuildError, match="must be a JSON-loadable value"):
            self.assert_successful_build(app)

    def test_argument_passing_custom_signature(
        self,
        cg_config_mock: MockStorage,
        make_app: MAKE_APP_TYPE,
        tmp_path_factory: TempPathFactory,
        monkeypatch,
    ):
        validator_kwargs = {}

        def sequence_validator(value: str | None) -> Sequence[int]:
            validator_kwargs["sequence_validator"] = value
            return tuple(map(int, value.split(",")))

        def flag_validator(value: str | None) -> bool:
            validator_kwargs["flag_validator"] = value
            return True

        original_load_version_history = MockChanGo.load_version_history

        def load_version_history(
            *args,
            start_from: str | None = None,
            end_at: str | None = None,
            json_dict_arg: dict[str, str] | None = None,
            sequence_arg: Annotated[Sequence[int], sequence_validator] = (1, 2, 3),
            flag_arg: Annotated[bool, flag_validator] = False,
        ):
            return original_load_version_history(
                *args,
                start_from=start_from,
                end_at=end_at,
                json_dict_arg=json_dict_arg,
                sequence_arg=sequence_arg,
                flag_arg=flag_arg,
            )

        monkeypatch.setattr(MockChanGo, "load_version_history", load_version_history)

        directive = """
.. chango::
    :json_dict_arg: {"key": "value"}
    :sequence_arg: 1,2,3
    :flag_arg:
    """

        app = make_app(
            srcdir=self.create_template(
                directive_insert=directive, tmp_path_factory=tmp_path_factory
            )
        )

        self.assert_successful_build(app)

        received_kwargs = cg_config_mock.get().chango.received_kwargs
        assert received_kwargs == {
            "json_dict_arg": {"key": "value"},
            "sequence_arg": (1, 2, 3),
            "flag_arg": True,
            "start_from": None,
            "end_at": None,
        }
        assert validator_kwargs == {"sequence_validator": "1,2,3", "flag_validator": None}

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, cast

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from ...abc import ChanGo
from .pydantic import FrozenModel, TomlSettings

__all__ = ["CLIConfig", "import_chango_instance_from_config"]


@contextlib.contextmanager
def _add_sys_path(path: Path | None) -> Iterator[None]:
    """Temporarily add the given path to `sys.path`."""
    if path is None:
        yield
        return

    if not path.is_absolute():
        path = Path.cwd() / path

    try:
        sys.path.insert(0, str(path))
        yield
    finally:
        sys.path.remove(str(path))


class ObjectConfig(FrozenModel):
    """Data Model for the configuration of an object in the ``pyproject.toml`` file."""

    name: str
    """The name of the object to import."""
    module: Annotated[str, Field(examples=["my_config_module"])]
    """The module to import the object from as passed to
    :meth:`importlib.import_module`.
    """
    package: str | None = None
    """The module to import the object from as passed to
    :meth:`importlib.import_module`.
    """


class CLIConfig(FrozenModel, TomlSettings):
    """Data Model for the CLI configuration in the ``pyproject.toml`` file.

    Important:
        :paramref:`~CLIConfig.module` and :paramref:`~CLIConfig.package` will be passed to
        :meth:`importlib.import_module` to import the user defined objects. For this to work,
        the module must be findable by Python, which may depend on your current working directory
        and the Python path. It can help to set :paramref:`~CLIConfig.sys_path` accordingly. Please
        evaluate the security implications of this before setting it.
    """

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "chango"), extra="ignore"
    )

    sys_path: Path | None = None
    """The path to *temporarily* add to the system path before importing the module. If the path
    is not absolute, it will considered as relative to the current working directory.

    Example:
        To add the current working directory to the system path, set this to ``.``.

    """
    chango_instance: Annotated[
        ObjectConfig,
        Field(examples=[ObjectConfig(name="chango_instance", module="my_config_module")]),
    ]
    """The instance of :class:`~chango.abc.ChanGo` to use in the CLI."""


def import_chango_instance_from_config(config: CLIConfig) -> ChanGo:
    """Parses the TOML configuration and load the ChanGo object.

    Args:
        config: The CLIConfig as specified in the pyproject.toml
    """
    with _add_sys_path(config.sys_path):
        return cast(
            ChanGo,
            getattr(
                importlib.import_module(
                    config.chango_instance.module, config.chango_instance.package
                ),
                config.chango_instance.name,
            ),
        )

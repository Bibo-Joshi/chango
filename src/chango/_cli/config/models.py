#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Self, cast

from pydantic_settings import SettingsConfigDict

from ...abc import IO, ChangeNote
from .pydantic import FrozenModel, TomlSettings


@contextlib.contextmanager
def _add_sys_path(path: Path | None) -> Iterator[None]:
    """Temporarily add the given path to `sys.path`."""
    if path is None:
        yield
        return

    try:
        sys.path.insert(0, path.as_posix())
        yield
    finally:
        sys.path.remove(path.as_posix())


class ObjectConfig(FrozenModel):
    """Data Model for the configuration of an object in the ``pyproject.toml`` file."""

    name: str
    """The name of the object to import."""
    module: str | None = None
    """The module to import the object from. If not passed, defaults to
    :attr:`CLIConfig.module`.
    """
    package: str | None = None
    """The module to import the object from. If not passed, defaults to
    :attr:`CLIConfig.package`.
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

    model_config = SettingsConfigDict(pyproject_toml_table_header=("tool", "chango"))

    module: str
    """The module to import the user defined objects from as passed to
    :meth:`importlib.import_module`.
    """
    package: str | None = None
    """The module to import :paramref:`~CLIConfig.module` from as passed to
    :meth:`importlib.import_module`.
    """
    sys_path: Path | None = None
    """The path to *temporarily* add to the system path before importing the module. If the path
    is not absolute, it will considered as relative to the current working directory.

    Example:
        To add the current working directory to the system path, set this to ``.``.

    """
    io_instance: str | ObjectConfig
    """The instance of :class:`~chango.abc.IO` to use."""
    change_note_type: str | ObjectConfig
    """The type of :class:`~chango.abc.ChangeNote` to use."""


class ParsedCLIConfig(FrozenModel):
    """Load the configuration for the chango command line interface."""

    io_instance: IO
    change_note_type: type[ChangeNote]

    @classmethod
    def from_config(cls, config: CLIConfig) -> Self:
        io_instance, change_note_type = cls._do_import(config)
        return cls(io_instance=io_instance, change_note_type=change_note_type)  # type: ignore

    @staticmethod
    def _do_import(config: CLIConfig) -> tuple[IO, type[ChangeNote]]:
        """Import the object from the module."""

        def _do_import(obj_config: ObjectConfig | str) -> object | type:
            if isinstance(obj_config, str):
                module = config.module
                package = config.package
                name = obj_config
            else:
                module = obj_config.module or config.module
                package = obj_config.package or config.package
                name = obj_config.name

            return getattr(importlib.import_module(module, package), name)

        with _add_sys_path(config.sys_path):
            io_instance = cast(IO, _do_import(config.io_instance))
            change_note = cast(type[ChangeNote], _do_import(config.change_note_type))

        return io_instance, change_note

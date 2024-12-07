#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import importlib
from pathlib import Path
from typing import Annotated, Any, ClassVar, Self, cast

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from chango.abc import ChanGo

from .._utils.config import FrozenModel, TomlSettings, add_sys_path, get_pyproject_toml_path
from .._utils.types import PathLike

__all__ = ["ChanGoConfig", "ChanGoInstanceConfig"]


class ChanGoInstanceConfig(FrozenModel):
    """Data structure for specifying how the :class:`~chango.abc.ChanGo` should be imported for the
    CLI.

    Args:
        name (:obj:`str`): The name of the object to import.
        module (:obj:`str`): The module to import the object from as passed to
            :func:`importlib.import_module`.
        package (:obj:`str` | :obj:`None`, optional): The module to import the object from as
            passed to :func:`importlib.import_module`.

    Attributes:
        name (:obj:`str`): The name of the object to import.
        module (:obj:`str`): The module to import the object from as passed to
            :func:`importlib.import_module`.
        package (:obj:`str` | :obj:`None`): The module to import the object from as passed to
            :func:`importlib.import_module`.
    """

    name: str
    module: Annotated[str, Field(examples=["my_config_module"])]
    package: str | None = None


class ChanGoConfig(FrozenModel, TomlSettings):
    """Data structure for the ChanGos CLI configuration in the ``pyproject.toml`` file.

    Tip:
        Rather than manually creating an instance of this class, use :meth:`load` to load the
        configuration from the ``pyproject.toml`` file.

    Important:
        The attributes of :attr:`chango_instance` will be passed to
        :func:`importlib.import_module` to import the user defined :class:`~chango.abc.ChanGo`
        instance. For this to work,
        the module must be findable by Python, which may depend on your current working directory
        and the Python path. It can help to set :paramref:`sys_path` accordingly.
        Please evaluate the security implications of this before setting it.

    Keyword Args:
        sys_path (:class:`~pathlib.Path`, optional): A path to *temporarily* add to the system
            path before importing the module.

            Example:
                To add the current working directory to the system path, set this to ``.``.

            Caution:
                Since this class is usually loaded via :meth:`load`, the path is resolved relative
                to the ``pyproject.toml`` file path. If the path is absolute, it will be used as
                is.
                When instantiating this class manually, the path is resolved relative to the
                current working directory.

        chango_instance (:class:`~chango.config.ChanGoInstanceConfig`): Specification of how the
            :class:`~chango.abc.ChanGo` instance to use in the CLI is imported.

    Attributes:
        sys_path (:class:`~pathlib.Path` | None): The path to *temporarily* add to the system path
            before importing the module. If the path is not absolute, it will considered as
            relative to the current working directory.
        chango_instance (:class:`~chango.config.ChanGoInstanceConfig`): The instance of
            :class:`~chango.abc.ChanGo` to use in the CLI.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "chango"), extra="ignore"
    )

    sys_path: Path | None = None
    chango_instance: Annotated[
        ChanGoInstanceConfig,
        Field(examples=[ChanGoInstanceConfig(name="chango_instance", module="my_config_module")]),
    ]

    @classmethod
    def load(cls, path: PathLike | None = None) -> Self:
        """Load the :class:`~chango.config.ChanGoConfig` from the ``pyproject.toml`` file.

        Tip:
           If the specification of :attr:`sys_path` is relative, it will be resolved relative to
           the :paramref:`path` parameter by this method.

        Keyword Args:
            path (:class:`~pathlib.Path` | None): The path to the ``pyproject.toml`` file. The
                path resolution works as follows:

                * If ``path`` is ``None``, the current working directory is used.
                * If ``path`` is absolute, it is used as is. Relative paths are resolved relative
                  to the current working directory.
                * If the path does not point to a file, it is assumed to be a directory and the
                  file name ``pyproject.toml`` is appended.

        Returns:
            :class:`~chango.config.ChanGoConfig`: The loaded configuration.
        """
        pyproject_toml_path = get_pyproject_toml_path(path)
        with cls._with_path(get_pyproject_toml_path(path)):
            obj = cls()  # type: ignore[call-arg]
            if obj.sys_path is None or obj.sys_path.is_absolute():
                return obj
            with obj._unfrozen():
                obj.sys_path = (pyproject_toml_path.parent / obj.sys_path).resolve()
            return obj

    def import_chango_instance(self) -> ChanGo[Any, Any, Any, Any]:
        """Import the :class:`~chango.abc.ChanGo` instance specified in :attr:`chango_instance`.
        This considers the :attr:`sys_path` attribute to temporarily add a path to the system path.

        Returns:
            :class:`~chango.abc.ChanGo`: The imported :class:`~chango.abc.ChanGo` instance.
        """
        with add_sys_path(self.sys_path):
            return cast(
                ChanGo,
                getattr(
                    importlib.import_module(
                        self.chango_instance.module, self.chango_instance.package
                    ),
                    self.chango_instance.name,
                ),
            )

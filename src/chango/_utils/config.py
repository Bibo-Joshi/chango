#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import contextlib
import functools
import sys
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
)

from chango._utils.types import PathLike


class FrozenModel(BaseModel):
    """A frozen Pydantic model."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, arbitrary_types_allowed=True, extra="forbid"
    )

    @classmethod
    @contextmanager
    def _unfrozen(cls) -> Generator[None, None, None]:
        original_frozen = cls.model_config["frozen"]
        cls.model_config["frozen"] = False
        try:
            yield
        finally:
            cls.model_config["frozen"] = original_frozen


class TomlSettings(BaseSettings):
    """Example loading values from the table used by default."""

    _SOURCE_FACTORY: Callable[[type[BaseSettings]], PyprojectTomlConfigSettingsSource] = (
        functools.partial(PyprojectTomlConfigSettingsSource)
    )

    @classmethod
    @contextmanager
    def _with_path(cls, path: Path) -> Generator[None, None, None]:
        """Temporarily load from a different path."""
        cls._SOURCE_FACTORY = functools.partial(PyprojectTomlConfigSettingsSource, toml_file=path)
        try:
            yield
        finally:
            cls._SOURCE_FACTORY = functools.partial(PyprojectTomlConfigSettingsSource)

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, cls._SOURCE_FACTORY(settings_cls)


@contextlib.contextmanager
def add_sys_path(path: Path | None) -> Iterator[None]:
    """Temporarily add the given path to `sys.path`."""
    if path is None:
        yield
        return

    effective_path = path.resolve()

    try:
        sys.path.insert(0, str(effective_path))
        yield
    finally:
        sys.path.remove(str(effective_path))


def get_pyproject_toml_path(path: PathLike | None) -> Path:
    """Get the path to the pyproject.toml file."""
    effective_path = Path.cwd() if path is None else Path(path).resolve()
    if not effective_path.is_file():
        effective_path = effective_path / "pyproject.toml"
    return effective_path

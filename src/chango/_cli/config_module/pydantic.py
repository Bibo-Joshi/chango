#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import override

from pydantic import BaseModel, ConfigDict
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
)


class FrozenModel(BaseModel):
    """A frozen Pydantic model."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")


class TomlSettings(BaseSettings):
    """Example loading values from the table used by default."""

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
        return (PyprojectTomlConfigSettingsSource(settings_cls),)

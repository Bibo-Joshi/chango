#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["CLIConfig", "get_chango_instance", "import_chango_instance_from_config"]

from collections.abc import Callable

from ...abc import ChanGo
from .models import CLIConfig, import_chango_instance_from_config


class _UserConfigManager:
    def __init__(self) -> None:
        self._chango_instance: ChanGo | None = None

    def get_chango_instance(self) -> ChanGo:
        if self._chango_instance is None:
            self._chango_instance = import_chango_instance_from_config(
                CLIConfig()  # type: ignore[call-arg]
            )
        return self._chango_instance


get_chango_instance: Callable[[], ChanGo] = _UserConfigManager().get_chango_instance

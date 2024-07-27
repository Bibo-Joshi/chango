#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["CLIConfig", "ParsedCLIConfig", "get_user_config"]

from .models import CLIConfig, ParsedCLIConfig


class _UserConfigManager:
    def __init__(self):
        self._user_config: ParsedCLIConfig | None = None

    def get_user_config(self) -> ParsedCLIConfig:
        if self._user_config is None:
            self._user_config = ParsedCLIConfig.from_config(
                CLIConfig()  # type: ignore[reportCallIssue]
            )
        return self._user_config


get_user_config = _UserConfigManager().get_user_config

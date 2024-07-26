#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["USER_CONFIG", "CLIConfig", "ParsedCLIConfig"]

from .models import CLIConfig, ParsedCLIConfig

USER_CONFIG: ParsedCLIConfig = ParsedCLIConfig.from_config(
    CLIConfig()  # type: ignore[reportCallIssue]
)

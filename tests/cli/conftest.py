#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from collections.abc import Mapping, Sequence
from typing import IO, Any

import pytest
from click.testing import Result
from typer import Typer
from typer.testing import CliRunner

from chango._cli import app as chango_app


class ReuseCliRunner(CliRunner):
    def __init__(
        self,
        app: Typer,
        charset: str = "utf-8",
        env: Mapping[str, str | None] | None = None,
        echo_stdin: bool = False,
        mix_stderr: bool = True,
    ) -> None:
        self.app = app
        super().__init__(charset=charset, env=env, echo_stdin=echo_stdin, mix_stderr=mix_stderr)

    def invoke(
        self,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[Any] | None = None,
        env: Mapping[str, str] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        return super().invoke(
            self.app,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )


@pytest.fixture(scope="session")
def cli():
    return ReuseCliRunner(chango_app)

# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
__all__ = ["app"]

import os
from typing import Annotated

import typer

from .. import __version__
from .config import app as config_app
from .edit import edit
from .new import new
from .release import release
from .report import app as report_app

app = typer.Typer(
    help="CLI for chango - CHANgelog GOvernor for Your Project", rich_markup_mode="rich"
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def main(
    _version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, help="Show the version and exit."),
    ] = False,
) -> None:
    pass


app.add_typer(config_app, name="config")
app.command()(edit)
app.command()(new)
app.command()(release)
app.add_typer(report_app, name="report")

if os.getenv("SPHINX_BUILD") == "True":  # pragma: no cover
    # See https://github.com/fastapi/typer/issues/200#issuecomment-795873331
    _typer_click_object = typer.main.get_command(app)

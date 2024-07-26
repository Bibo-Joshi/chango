# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
__all__ = ["app"]

from typing import Annotated

import typer

from .. import __version__
from .edit import edit
from .new import new
from .release import release
from .report import app as report_app

app = typer.Typer(help="CLI for chango - CHANgelog GOvernor for Your Project")


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def main(
    _version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, help="Show the version and exit."),
    ] = False,
):
    pass


app.command()(edit)
app.command()(new)
app.command()(release)
app.add_typer(report_app, name="report")

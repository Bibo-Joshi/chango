#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import Annotated

import typer

from chango._cli.utils.common import description

from .. import __version__
from .edit import app as edit_app
from .new import app as new_app
from .report import app as report_app

app = typer.Typer(help=f"CLI for chango - {description}")


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


app.add_typer(report_app, name="report")
app.add_typer(new_app, name="new")
app.add_typer(edit_app, name="edit")

if __name__ == "__main__":
    app()

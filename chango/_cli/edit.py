#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["app"]

from typing import Annotated

import typer

from chango._cli.utils.common import IO

app = typer.Typer(help="Edit an existing change note in the default editor.")


@app.command()
def edit(
    uid: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the change note to edit.", show_default=False
        ),
    ],
):
    typer.launch(IO.scanner.lookup_change_note(uid).path.as_posix())

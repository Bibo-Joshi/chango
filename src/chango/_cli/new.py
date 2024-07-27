#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT

__all__ = ["new"]

from typing import Annotated

import typer

from .config_module import get_chango_instance


def new(
    slug: Annotated[str, typer.Argument(help="The slug of the change note.", show_default=False)],
    edit: Annotated[
        bool, typer.Option(help="Whether to open the change note in the default editor.")
    ] = True,
):
    """Create a new change note."""
    change_note = get_chango_instance().build_template_change_note(slug=slug)
    path = get_chango_instance().write_change_note(change_note, version=None)
    typer.echo(f"Created new change note {change_note.file_name}")
    if edit:
        typer.launch(path.as_posix())

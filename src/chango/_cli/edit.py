#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["edit"]

from typing import Annotated

import typer

from chango.config import get_chango_instance


def edit(
    uid: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the change note to edit.", show_default=False
        ),
    ],
) -> None:
    """Edit an existing change note in the default editor."""
    typer.launch(get_chango_instance().scanner.lookup_change_note(uid).file_path.as_posix())

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT

__all__ = ["edit"]

from typing import Annotated

import typer

from .config import USER_CONFIG


def edit(
    uid: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the change note to edit.", show_default=False
        ),
    ],
):
    """Edit an existing change note in the default editor."""
    typer.launch(USER_CONFIG.io_instance.scanner.lookup_change_note(uid).path.as_posix())

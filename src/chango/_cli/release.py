#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["release"]

import datetime as dtm
from typing import Annotated

import typer

from chango import Version
from chango.config import get_chango_instance

from .utils.types import date as date_callback


def release(
    uid: Annotated[str, typer.Argument(help="The unique identifier of the version release.")],
    date: Annotated[
        dtm.date, typer.Argument(help="The date of the version release.", parser=date_callback)
    ],
) -> None:
    """Release the unreleased changes to a new version."""
    if get_chango_instance().release(Version(uid, date)):
        typer.echo(f"Released version {uid} on {date}")
    else:
        typer.echo("No unreleased changes found.")

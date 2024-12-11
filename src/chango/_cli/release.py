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


def _today() -> dtm.date:
    return dtm.date.today()


def release(
    uid: Annotated[
        str, typer.Option(help="The unique identifier of the version release.", show_default=False)
    ],
    date: Annotated[
        dtm.date,
        typer.Option(
            help="The date of the version release. Defaults to today.",
            parser=date_callback,
            default_factory=_today,
        ),
    ],
) -> None:
    """Release the unreleased changes to a new version."""
    if get_chango_instance().release(Version(uid, date)):
        typer.echo(f"Released version {uid} on {date}")
    else:
        typer.echo("No unreleased changes found.")

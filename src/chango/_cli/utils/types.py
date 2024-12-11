#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
from pathlib import Path
from typing import Annotated, Optional

import typer

from chango.constants import MarkupLanguage


def markup_callback(value: str) -> MarkupLanguage:
    try:
        return MarkupLanguage.from_string(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def date(value: str | dtm.date) -> dtm.date:
    if isinstance(value, dtm.date):
        return value
    try:
        return dtm.date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


MARKUP = Annotated[
    str,
    typer.Option(
        ...,
        "-m",
        "--markup",
        help="The markup language to use for the report.",
        callback=markup_callback,
    ),
]
OUTPUT_FILE = Annotated[
    Optional[Path],  # noqa: UP007 - typer currently can't handle Path | None
    typer.Option(
        ...,
        "-o",
        "--output",
        help="The file to write to. If not specified, the output is printed to the console.",
        dir_okay=False,
        writable=True,
    ),
]

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT

__all__ = ["app"]

from typing import Annotated

import typer

from chango._cli.utils.common import IO
from chango._cli.utils.types import MARKUP, OUTPUT_FILE
from chango.constants import MarkupLanguage

app = typer.Typer(help="Generate reports for one or multiple versions.")


@app.command()
def version(
    uid: Annotated[
        str,
        typer.Argument(
            help=(
                "The unique identifier of the version to report on. Leave empty for unreleased "
                "changes."
            ),
            show_default=False,
        ),
    ],
    markup: MARKUP = MarkupLanguage.MARKDOWN,
    output: OUTPUT_FILE = None,
):
    """Print a report of the change notes for a specific version."""
    version_note = IO.load_version_note(uid)
    text = version_note.render(markup=markup)
    if output:
        output.write_text(text)
        typer.echo(f"Report written to {output}")
    else:
        typer.echo(text)


@app.command()
def history(markup: MARKUP = MarkupLanguage.MARKDOWN, output: OUTPUT_FILE = None):
    """Print a report of the version history."""
    version_history = IO.load_version_history()
    text = version_history.render(markup=markup)
    if output:
        output.write_text(text)
        typer.echo(f"Report written to {output}")
    else:
        typer.echo(text)

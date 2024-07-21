#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import tomllib
from pathlib import Path
from typing import Annotated

import typer

from .. import __version__
from ..concrete import (
    CommentChangeNote,
    CommentVersionNote,
    DirectoryIO,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)
from ..constants import MarkupLanguage

# get project description from pyproject.toml
root = Path(__file__).parent.parent.parent.resolve().absolute()
description = tomllib.load((root / "pyproject.toml").open("rb"))["project"]["description"]

app = typer.Typer(help=f"CLI for chango - {description}")
report_app = typer.Typer()

root = Path(r"C:\Users\hinri\PycharmProjects\chango\data")
IO = DirectoryIO(
    change_note_type=CommentChangeNote,
    version_note_type=CommentVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=DirectoryVersionScanner(base_directory=root, unreleased_directory="unreleased"),
)


def markup_callback(value: str) -> MarkupLanguage:
    try:
        return MarkupLanguage.from_string(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


MARKUP_ANNOTATION = Annotated[
    str, typer.Option(help="The markup language to use for the report.", callback=markup_callback)
]


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


@app.command()
def new(
    slug: Annotated[str, typer.Argument(help="The slug of the change note.", show_default=False)],
    edit: Annotated[
        bool, typer.Option(help="Whether to open the change note in the default editor.")
    ] = True,
):
    """Create a new change note."""
    change_note = CommentChangeNote.build_template(slug=slug)
    path = IO.write_change_note(change_note, version=None)
    typer.echo(f"Created new change note {change_note.file_name}")
    if edit:
        typer.launch(path.as_posix())


@app.command()
def edit(
    uid: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the change note to edit.", show_default=False
        ),
    ],
):
    """Edit an existing change note in the default editor."""
    typer.launch(IO.scanner.lookup_change_note(uid).path.as_posix())


@report_app.command()
def version(
    uid: Annotated[
        str,
        typer.Option(
            help=(
                "The unique identifier of the version to report on. Leave empty for unreleased "
                "changes."
            )
        ),
    ] = "unreleased",
    markup: MARKUP_ANNOTATION = MarkupLanguage.MARKDOWN,
):
    """Print a report of the change notes for a specific version."""
    version_note = IO.load_version_note(None if uid == "unreleased" else uid)
    typer.echo(version_note.render(markup=markup))


@report_app.command()
def history(markup: MARKUP_ANNOTATION = MarkupLanguage.MARKDOWN):
    """Print a report of the version history."""
    version_history = IO.load_version_history()
    typer.echo(version_history.render(markup=markup))


app.add_typer(report_app, name="report")

if __name__ == "__main__":
    app()

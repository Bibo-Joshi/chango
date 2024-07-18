#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

import typer

from ..concrete import (
    CommentChangeNote,
    CommentVersionNote,
    DirectoryIO,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)
from ..constants import MarkupLanguage

app = typer.Typer()
report_app = typer.Typer()

root = Path(r"C:\Users\hinri\PycharmProjects\chango\data")
IO = DirectoryIO(
    change_note_type=CommentChangeNote,
    version_note_type=CommentVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=DirectoryVersionScanner(base_directory=root, unreleased_directory="unreleased"),
)


@app.command()
def new(slug: str, edit: bool = True):
    """Create a new change note.

    Args:
        slug: The slug of the change note.
        edit: Whether to open the change note in the default editor.
    """
    change_note = CommentChangeNote(slug=slug, comment="comment")
    path = IO.write_change_note(change_note, version=None)
    typer.echo(f"Created new change note {change_note.file_name}")
    if edit:
        typer.launch(path.as_posix())


@app.command()
def edit(uid: str):
    """Edit an existing change note in the default editor.

    Args:
        uid: The unique identifier of the change note to edit.
    """
    typer.launch(IO.scanner.lookup_change_note(uid).path.as_posix())


@report_app.command()
def version(uid: str = "unreleased", markup: MarkupLanguage = MarkupLanguage.MARKDOWN):
    """Print a report of the change notes for a specific version.

    Args:
        uid: The unique identifier of the version to report on. Leave empty for unreleased
            changes.
        markup: The markup language to use for the report.
    """
    version_note = IO.load_version_note(None if uid == "unreleased" else uid)
    typer.echo(version_note.render(markup=markup))


@report_app.command()
def history(markup: MarkupLanguage = MarkupLanguage.MARKDOWN):
    """Print a report of the version history.

    Args:
        markup: The markup language to use for the report.
    """
    version_history = IO.load_version_history()
    typer.echo(version_history.render(markup=markup))


app.add_typer(report_app, name="report")

if __name__ == "__main__":
    app()

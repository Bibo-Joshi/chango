#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["app"]

from pathlib import Path
from typing import Annotated, Optional

import tomlkit
import typer
from pydantic import ValidationError
from rich import print as rprint
from rich.markdown import Markdown

from .._utils.config import get_pyproject_toml_path
from ..config import ChanGoConfig

app = typer.Typer(help="Show or verify the configuration of the chango CLI.")

_PATH_ANNOTATION = Annotated[
    Optional[Path],  # noqa: UP007 - typer currently can't handle Path | None
    typer.Option(
        help=(
            "The path to the [code]pyproject.toml[/code] file. "
            "Input behavior as for [code]chango.config.ChanGoConfig.load[/code]."
        )
    ),
]


@app.callback(rich_help_panel="Meta Functionality")
def callback(context: typer.Context, path: _PATH_ANNOTATION = None) -> None:
    effective_path = get_pyproject_toml_path(path)

    if not effective_path.exists():
        raise typer.BadParameter(f"File not found: {effective_path}")

    context.obj = {"path": effective_path}

    try:
        toml_data = tomlkit.load(context.obj["path"].open("rb"))
    except Exception as exc:
        raise typer.BadParameter(f"Failed to parse the configuration file: {exc}") from exc

    try:
        context.obj["data"] = toml_data["tool"]["chango"]  # type: ignore[index]
    except KeyError as exc:
        raise typer.BadParameter(
            "No configuration found for chango in the configuration file."
        ) from exc


@app.command()
def show(context: typer.Context) -> None:
    """Show the configuration."""
    string = f"""
Showing the configuration of the chango CLI as configured in ``{context.obj['path']}``.
```toml
{tomlkit.dumps(context.obj["data"])}
```
    """
    rprint(Markdown(string))


@app.command()
def validate(context: typer.Context) -> None:
    """Validate the configuration."""
    try:
        config = ChanGoConfig.load(context.obj["path"])
    except ValidationError as exc:
        raise typer.BadParameter(
            f"Validation of config file at {context.obj['path']} failed:\n{exc}"
        ) from exc

    try:
        config.import_chango_instance()
    except ImportError as exc:
        raise typer.BadParameter(
            f"Config file at {context.obj['path']} is valid "
            f"but importing the ChanGo instance failed:\n{exc}"
        ) from exc

    rprint(f"The configuration in [code]{context.obj['path']}[/code] is valid.")

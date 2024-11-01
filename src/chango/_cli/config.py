#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["app"]

import json
from pathlib import Path
from typing import Annotated, Optional

import tomlkit
import typer
from rich import print as rprint
from rich.markdown import Markdown

from chango._cli.config_module import CLIConfig, import_chango_instance_from_config

app = typer.Typer(help="Show or verify the configuration of the chango CLI.")

_PATH_ANNOTATION = Annotated[
    Optional[Path],  # noqa: UP007 - typer currently can't handle Path | None
    typer.Option(
        help=(
            "The path to the [code]pyproject.toml[/code] file. "
            "Defaults to the current working directory."
        ),
        dir_okay=False,
    ),
]


@app.callback(rich_help_panel="Meta Functionality")
def callback(context: typer.Context, path: _PATH_ANNOTATION = None) -> None:
    if not path:
        effective_path = Path.cwd() / "pyproject.toml"
    elif path.is_absolute():
        effective_path = path
    else:
        effective_path = Path.cwd() / path

    if not effective_path.exists():
        raise typer.BadParameter(f"File not found: {effective_path}")

    context.obj = {"path": path or Path.cwd() / "pyproject.toml"}

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
Showing the configuration of the chango CLIas configured in {context.obj['path']}.
```toml
{tomlkit.dumps(context.obj["data"])}
```
    """
    rprint(Markdown(string))


@app.command()
def schema() -> None:
    """Show the JSON schema of the configuration."""
    rprint(Markdown(f"```json\n{json.dumps(CLIConfig.model_json_schema(), indent=2)}\n```"))


@app.command()
def validate(context: typer.Context) -> None:
    """Validate the configuration."""
    try:
        config = CLIConfig.model_validate(dict(context.obj["data"]))
    except ValueError as exc:
        raise typer.BadParameter(
            f"Validation of config file at {context.obj['path']} failed:\n{exc}"
        ) from exc

    try:
        import_chango_instance_from_config(config)
    except ImportError as exc:
        raise typer.BadParameter(
            f"Config file at {context.obj['path']} is valid "
            f"but importing the objects failed:\n{exc}"
        ) from exc

    typer.echo("The configuration is valid.")

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT

__all__ = ["app"]

from pathlib import Path
from typing import Annotated, Optional

import tomlkit
import typer
from rich import print as rprint
from rich.markdown import Markdown

from chango._cli.config_module import CLIConfig, ParsedCLIConfig

app = typer.Typer(help="Show or verify the configuration of the chango CLI.")

_PATH_ANNOTATION = Annotated[
    Optional[Path],  # noqa: UP007 - typer currently can't handle Path | None
    typer.Option(
        help="The path to the pyproject.toml file. Defaults to the current working directory.",
        dir_okay=False,
    ),
]


@app.callback()
def callback(context: typer.Context, path: _PATH_ANNOTATION = None):
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
        context.obj["data"] = toml_data["tool"]["chango"]  # type: ignore[reportIndexIssue]
    except KeyError as exc:
        raise typer.BadParameter(
            "No configuration found for chango in the configuration file."
        ) from exc


@app.command()
def show(context: typer.Context):
    """Show the configuration."""
    string = f"""
Showing the configuration of the chango CLIas configured in {context.obj['path']}.
```toml
{tomlkit.dumps(context.obj["data"])}
```
    """
    rprint(Markdown(string))


@app.command()
def validate(context: typer.Context):
    """Validate the configuration."""
    try:
        config = CLIConfig.model_validate(dict(context.obj["data"]))
    except ValueError as exc:
        raise typer.BadParameter(
            f"Validation of config file at {context.obj['path']} failed:\n{exc}"
        ) from exc

    try:
        ParsedCLIConfig.from_config(config)
    except ImportError as exc:
        raise typer.BadParameter(
            f"Config file at {context.obj['path']} is valid "
            f"but importing the objects failed:\n{exc}"
        ) from exc

    typer.echo("The configuration is valid.")

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import json
import typing

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from chango._utils.types import PathLike
from chango.config import get_chango_instance
from chango.constants import MarkupLanguage


class JsonValidator:
    """Validator that interprets the input as JSON data and loads it accordingly.
    The value must be a JSON-loadable value, not None.
    """

    def __init__(self, option_name: str) -> None:
        self.option_name = option_name

    def __call__(self, var: str | None) -> str | int | float | bool | dict | list | None:
        if var is None:
            raise ValueError(
                f"Option '{self.option_name}' must be a JSON-loadable value, not None"
            )

        try:
            return json.loads(var)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Option '{self.option_name}' must be a JSON-loadable value, not {var!r}"
            ) from exc

    def __repr__(self) -> str:  # pragma: no cover
        """So far only used for debugging."""
        return "<return json parsed data>"


def parse_function(func: typing.Callable) -> dict[str, typing.Callable[[str | None], typing.Any]]:
    """Parse a function's signature and annotations to create a dictionary of validators.
    Custom validators may be defined using the `typing.Annotated` type. Defaults are not -
    options are interpreted as kwargs and are always expected to carry a value.

    Example:
        >>> from typing import Annotated
        >>> from collections.abc import Sequence
        >>>
        >>> def custom_validator(x: str | None) -> Sequence[float]:
        ...     return tuple(map(float, x.split(","))) if x is not None else (1.0, 2.0, 3.0)
        >>>
        >>> def foo(
        >>>     arg1: str,
        >>>     arg2: int = 42,
        >>>     arg3: Annotated[Sequence[float], custom_validator] = (1, 2, 3),
        >>> ) -> None:
        ...     pass
        >>>
        >>> parse_function(foo)
        {'arg1': <return json parsed data>, 'arg2': <return json parsed data>, \
        'arg3': <function main.<locals>.custom_validator at 0x000001FB6F1D7100>}

    """
    # To get custom validator, we need to evaluate the annotations to detect `typing.Annotated`
    annotations = typing.get_type_hints(func, include_extras=True, localns=locals())
    return {
        name: typing.get_args(annotation)[1]
        if typing.get_origin(annotation) is typing.Annotated
        else JsonValidator(name)
        for name, annotation in annotations.items()
        # The return value is not a parameter
        if name != "return"
    }


def directive_factory(app: Sphinx) -> type[SphinxDirective]:
    """Create a directive class that uses the chango instance from the Sphinx app config.
    This approach is necessary because the `option_spec` attribute of a directive class can
    not be dynamically set.
    """
    if not isinstance(app.config.chango_pyproject_toml_path, PathLike | None):
        raise TypeError(
            f"Expected 'chango_pyproject_toml_path' to be a string or Path, "
            f"but got {type(app.config.chango_pyproject_toml_path)}"
        )
    chango_instance = get_chango_instance(app.config.chango_pyproject_toml_path)

    class ChangoDirective(SphinxDirective):
        has_content = True
        option_spec = parse_function(  # type: ignore[assignment]
            chango_instance.load_version_history
        )

        def run(self) -> list[Node]:
            title = " ".join(self.content)
            text = chango_instance.load_version_history(**self.options).render(
                MarkupLanguage.RESTRUCTUREDTEXT
            )
            if title:
                decoration = len(title) * "="
                text = f"{decoration}\n{title}\n{decoration}\n\n{text}"
            return self.parse_text_to_nodes(text, allow_section_headings=True)

    return ChangoDirective

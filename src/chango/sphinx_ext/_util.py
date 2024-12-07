#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import inspect
import typing

from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from chango.config import get_chango_instance
from chango.constants import MarkupLanguage


class NoChangeValidator:
    """Validator that does not change the input.
    Note that in contrast to `docutils.parsers.rst.directives.unchanged`, this function
    does not convert `None` to an empty string.
    """

    def __call__(self, var: str | None) -> str | None:
        return var

    def __repr__(self) -> str:
        return "<return unchanged>"


NO_CHANGE_VALIDATOR = NoChangeValidator()


class WithDefaultValidator[T]:
    """Validator-Wrapper that applies a default value if the input is `None`.
    Otherwise, the input is passed to the validator function.
    """

    def __init__(self, validator: typing.Callable[[str | None], T], default: T) -> None:
        self.validator: typing.Callable[[str | None], T] = validator
        self.default: T = default

    def apply_default(self, value: str | None) -> T:
        return self.default if value is None else self.validator(value)

    def __call__(self, value: str | None) -> T:
        return self.default if value is None else self.validator(value)

    def __repr__(self) -> str:
        return f"<return {self.default} if None else {self.validator}>"


def parse_function(func: typing.Callable) -> dict[str, typing.Callable[[str | None], typing.Any]]:
    """Parse a function's signature and annotations to create a dictionary of validators.
    Custom validators may be defined using the `typing.Annotated` type. Defaults are considered.

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
        {'arg1': <return unchanged>, 'arg2': <return 42 if None else <return unchanged>>, 'arg3': \
        <return (1, 2, 3) if None else <function custom_validator at 0x000001C89BEB80E0>>}

    """
    # We get the defaults via the inspect.signature API
    signature = inspect.signature(func)
    defaults = {
        param.name: param.default
        for param in signature.parameters.values()
        if param.default is not param.empty
    }

    # To get custom validator, we need to evaluate the annotations to detect `typing.Annotated`
    annotations = typing.get_type_hints(func, include_extras=True, localns=locals())
    validators = {
        name: typing.get_args(annotation)[1]
        if typing.get_origin(annotation) is typing.Annotated
        else NO_CHANGE_VALIDATOR
        for name, annotation in annotations.items()
        # The return value is not a parameter
        if name != "return"
    }

    # Combine the validators with the defaults
    return {
        name: WithDefaultValidator(validator, default)
        if (default := defaults.get(name))
        else validator
        for name, validator in validators.items()
    }


def directory_factory(app: Sphinx) -> type[SphinxDirective]:
    """Create a directive class that uses the chango instance from the Sphinx app config.
    This approach is necessary because the `option_spec` attribute of a directive class can
    not be dynamically set.
    """
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

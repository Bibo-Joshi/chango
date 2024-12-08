#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module contains functionality that allows automatically rendering changelogs in
`Sphinx <https://https://www.sphinx-doc.org/>`_ documentation using ``chango``.

.. seealso:: :ref:`sphinx_ext`
"""

import typing
from pathlib import Path
from types import NoneType

from sphinx.application import Sphinx

from chango import __version__

__all__ = ["setup"]

from ._util import directive_factory


def setup(app: Sphinx) -> dict[str, typing.Any]:
    """Sets up the ``chango`` Sphinx extension.
    This currently does two things:

    1. Adds the ``chango`` directive to Sphinx, which allows you to include changelogs in your
       documentation.
    2. Adds a configuration value ``chango_pyproject_toml_path`` to the Sphinx configuration, which
       allows you to specify the path to the ``pyproject.toml`` file that contains the chango
       configuration.

    Args:
        app (:class:`sphinx.application.Sphinx`): The Sphinx application object.

    Returns:
        dict[:class:`str`, :class:`typing.Any`]: A dictionary containing metadata about the
            extension.
    """
    app.add_config_value(
        "chango_pyproject_toml_path",
        None,
        rebuild="env",
        # Path & PurePath do not work well with how sphinx handles config value type checks
        types=(str, type(Path.cwd()), NoneType),
        description=(
            "Path to the pyproject.toml file to use for the chango configuration. Takes "
            "the same inputs as `chango.config.ChanGoConfig.load`."
        ),
    )
    app.add_directive("chango", directive_factory(app))

    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}

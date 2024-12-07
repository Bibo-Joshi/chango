#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module provides the functionality to load the configuration for the ChanGo CLI."""

__all__ = ["ChanGoConfig", "ChanGoInstanceConfig", "get_chango_instance"]

import functools
from typing import Any

from chango.abc import ChanGo

from .._utils.types import PathLike
from ._models import ChanGoConfig, ChanGoInstanceConfig


@functools.lru_cache(maxsize=256)
def get_chango_instance(path: PathLike | None = None) -> ChanGo[Any, Any, Any, Any]:
    """Get the :class:`~chango.abc.ChanGo` instance specified in the configuration file.
    Uses LRU caching to avoid reloading the configuration file multiple times.

    Args:
        path (:class:`~pathlib.Path` | :obj:`str` | :obj:`None`, optional): The path to the
            configuration file as passed to :meth:`ChanGoConfig.load`.

    Returns:
        :class:`~chango.abc.ChanGo`: The instance of the :class:`~chango.abc.ChanGo` class
            specified in the configuration file.
    """
    return ChanGoConfig.load(path).import_chango_instance()

# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
# SPDX-License-Identifier: MIT

__all__ = [
    "ChangeNoteInfo",
    "Version",
    "__version__",
    "abc",
    "action",
    "concrete",
    "config",
    "constants",
    "error",
    "helpers",
]

from . import __about__, abc, action, concrete, config, constants, error, helpers
from ._changenoteinfo import ChangeNoteInfo
from ._version import Version

#: :obj:`str`: The version of the ``chango`` library as string
__version__: str = __about__.__version__

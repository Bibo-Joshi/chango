#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import TYPE_CHECKING, Union

from .._version import Version

if TYPE_CHECKING:
    from ..abc._changenote import ChangeNote

VersionUID = str | None
VUIDInput = Version | str | None
CNUIDInput = Union["ChangeNote", str]
PathLike = str | Path

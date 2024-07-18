#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from chango import Version

    from ..abc._changenote import ChangeNote

VersionUID = str | None
VUIDInput = Union["Version", str] | None
VersionIO = Union["Version", None]
CNUIDInput = Union["ChangeNote", str]
PathLike = str | Path

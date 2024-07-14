#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from chango.abc._changenote import ChangeNote
    from chango.abc._version import Version

VersionUID = str | None
VUIDInput = Union["Version", str] | None
VersionIO = Union["Version", None]
CNUIDInput = Union["ChangeNote", str]
PathLike = str | Path

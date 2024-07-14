#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

from chango.abc._changenote import ChangeNote
from chango.abc._version import Version

VersionUID = str | None
VUIDInput = Version | str | None
VersionIO = Version | None
CNUIDInput = ChangeNote | str
PathLike = str | Path

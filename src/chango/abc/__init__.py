#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module contains abstract base classes defining the interfaces that the chango package
is build on.
"""

__all__ = ["ChanGo", "ChangeNote", "VersionHistory", "VersionNote", "VersionScanner"]

from ._changenote import ChangeNote
from ._chango import ChanGo
from ._versionhistory import VersionHistory
from ._versionnote import VersionNote
from ._versionscanner import VersionScanner

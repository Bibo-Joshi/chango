#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
from dataclasses import dataclass


@dataclass
class Version:
    """Objects of this type represent a released version of a software project.

    Args:
        uid: Unique identifier / version number of this version.
        date: Release date of this version.

    Attributes:
        uid: Unique identifier / version number of this version.
        date: Release date of this version.
    """

    uid: str
    date: dtm.date

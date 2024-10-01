#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm
from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    """Objects of this type represent a released version of a software project.

    Args:
        uid (:obj:`str`): Unique identifier / version number of this version.
        date (:class:`datetime.date`): Release date of this version.

    Attributes:
        uid (:obj:`str`): Unique identifier / version number of this version.
        date (:class:`datetime.date`): Release date of this version.
    """

    uid: str
    date: dtm.date

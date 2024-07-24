#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
from dataclasses import dataclass
from pathlib import Path

from ._version import Version


@dataclass
class ChangeNoteInfo:
    """Objects of this type represents metadata about a change note.

    Args:
        uid: Unique identifier of this change note.
        version: The version the change note belongs to. May be :obj:`None` if the change note is
            not yet released.
        path: The file path this change note is stored at.

    Attributes:
        uid: Unique identifier of this change note.
        version: The version the change note belongs to. May be :obj:`None` if the change note is
            not yet released.
        path: The file path this change note is stored at.
    """

    uid: str
    version: Version | None
    path: Path

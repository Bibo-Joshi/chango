#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from dataclasses import dataclass
from pathlib import Path

from ._version import Version


@dataclass(frozen=True)
class ChangeNoteInfo:
    """Objects of this type represents metadata about a change note.

    Args:
        uid (:obj:`str`): Unique identifier of this change note.
        version (:class:`~chango.Version` | :obj:`None`): The version the change note belongs to.
            May be :obj:`None` if the change note is not yet released.
        file_path (:class:`pathlib.Path`): The file path this change note is stored at.

    Attributes:
        uid (:obj:`str`): Unique identifier of this change note.
        version (:class:`~chango.Version` | :obj:`None`): The version the change note belongs to.
            May be :obj:`None` if the change note is not yet released.
        file_path (:class:`pathlib.Path`): The file path this change note is stored at.
    """

    uid: str
    version: Version | None
    file_path: Path

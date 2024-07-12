#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

from chango._utils.filename import FileName


def change_uid_from_file(file: str | Path) -> str:
    """Get the change note identifier from a file name or path.

    Args:
        file: The file name or path to get the identifier from.

    Returns:
        The :attr:`~chango.abc.ChangeNote.uid` of the change note.
    """
    if isinstance(file, Path):
        return change_uid_from_file(file.name)
    return FileName(file).uid

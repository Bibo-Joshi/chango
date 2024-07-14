#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from typing import Protocol, overload

from chango._utils.filename import FileName
from chango._utils.types import PathLike


def change_uid_from_file(file: PathLike) -> str:
    """Get the change note identifier from a file name or path.

    Args:
        file: The file name or path to get the identifier from.

    Returns:
        The :attr:`~chango.abc.ChangeNote.uid` of the change note.
    """
    if isinstance(file, Path):
        return change_uid_from_file(file.name)
    return FileName(file).uid


class _UIDProtocol(Protocol):
    uid: str


class _UIDPropProtocol(Protocol):
    @property
    def uid(self) -> str: ...


@overload
def ensure_uid(obj: _UIDProtocol | _UIDPropProtocol) -> str: ...


@overload
def ensure_uid(obj: None) -> None: ...


@overload
def ensure_uid(obj: str) -> str: ...


def ensure_uid(obj: _UIDProtocol | _UIDPropProtocol | str | None) -> str | None:
    """Extract the unique identifier of an object. Input of type :obj:`str` and :obj:`None`
    is returned unchanged.

    Args:
        obj: An object that either has a string attribute ``uid`` (e.g.
            :class:`~chango.abc.ChangeNote` or :class:`~chango.abc.Version`), is a :obj:`str` or
            is :obj:`None`.

    Returns:
        :obj:`str` | :obj:`None`: The extracted UID if available and :obj:`None` else.
    """
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    return obj.uid

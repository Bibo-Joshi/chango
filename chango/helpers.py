#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol, overload

from chango._utils.filename import FileName
from chango._utils.types import PathLike, VersionUID


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
    uid: VersionUID


@overload
def filter_released(sequence: Iterable[VersionUID], /) -> Iterable[str]: ...


@overload
def filter_released[T: _UIDProtocol](sequence: Iterable[T], /) -> Iterable[T]: ...


def filter_released[T: _UIDProtocol | VersionUID](sequence: Iterable[T], /) -> Iterable[T]:
    """Filter a sequence of objects to only contain released versions.

    Args:
        sequence: The sequence of objects to filter. The objects must either all have a
            :attr:`~chango.abc.VersionNote.uid` or be of type :obj:`str`/:obj:`None`, representing
            the version identifier.

    Returns:
        A list of objects that have/represent a released version identifier.
    """
    try:
        return filter(lambda obj: obj.uid is not None, sequence)  # type: ignore
    except AttributeError:
        return filter(lambda obj: obj is not None, sequence)

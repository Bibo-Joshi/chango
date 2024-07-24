#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
import datetime as dtm
import warnings
from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, overload

from .._utils.filename import FileName
from .._utils.files import UTF8
from .._utils.types import VersionIO
from ..abc._changenote import ChangeNote

if TYPE_CHECKING:
    from chango import Version


@dataclass
class VersionNote[CNT: ChangeNote, V: VersionIO](MutableMapping[str, CNT], abc.ABC):
    """Abstract base class for a version note describing the set of changes in a software project
    for a single version.

    Hint:
        Objects of this class can be used as :class:`~collections.abc.MutableMapping`, where the
        keys are the unique identifiers (or file names) of the change notes and the values are the
        change notes themselves.

    Warning:
        To ensure that the changes in this version are displayed in the correct order, the change
        notes should be added in the order they were made. Manual reordering of the change notes
        may interfere with the order in which they are displayed.

    Args:
        version: The version of the software project this note is for.
            May be :obj:`None` if the version is not yet released.

    Attributes:
        version: The version of the software project this note is for.
            May be :obj:`None` if the version is not yet released.
    """

    version: V
    _change_notes: dict[str, CNT] = field(default_factory=dict, init=False)

    def __delitem__(self, __key: str) -> None:
        try:
            del self._change_notes[__key]
        except KeyError:
            del self._change_notes[FileName.from_string(__key).uid]

    def __getitem__(self, __key: str) -> CNT:
        try:
            return self._change_notes[__key]
        except KeyError:
            return self._change_notes[FileName.from_string(__key).uid]

    def __iter__(self) -> Iterator[str]:
        return iter(self._change_notes)

    def __len__(self) -> int:
        return len(self._change_notes)

    def __setitem__(self, __key: str, __value: CNT) -> None:
        if __key != __value.uid:
            warnings.warn(
                f"Key {__key!r} does not match change note UID {__value.uid!r}. "
                "Using value the UID as key.",
                stacklevel=2,
            )
        self._change_notes[__value.uid] = __value

    @overload
    def uid(self: "VersionNote[CNT, Version]") -> str: ...

    @overload
    def uid(self: "VersionNote[CNT, None]") -> None: ...

    @property
    def uid(self) -> str | None:
        """Convenience property for the version UID.

        Returns:
            :obj:`str` | :obj:`None`: The UID of :attr:`version` if available, :obj:`None`
                otherwise.
        """
        if self.version is None:
            return None
        return self.version.uid

    @overload
    def date(self: "VersionNote[CNT, Version]") -> dtm.date: ...

    @overload
    def date(self: "VersionNote[CNT, None]") -> None: ...

    @property
    def date(self) -> dtm.date | None:
        """Convenience property for the version UID.

        Returns:
            :class:`datetime.date` | :obj:`None`: The release date of :attr:`version` if available,
                :obj:`None` otherwise.
        """
        if self.version is None:
            return None
        return self.version.date

    def add_change_note(self, change_note: CNT) -> None:
        """Add a change note to the version note.

        Args:
            change_note: The change note to add.
        """
        self[change_note.uid] = change_note

    def remove_change_note(self, change_note: CNT) -> None:
        """Remove a change note from the version note.

        Args:
            change_note: The change note to remove.
        """
        del self[change_note.uid]

    @abc.abstractmethod
    def render(self, markup: str, encoding: str = UTF8) -> str:
        """Render the version note as a string.

        Args:
            markup: The markup language to use for rendering. If the markup language
                is not supported, an :exc:`~chango.errors.UnsupportedMarkupError` should be raised.
            encoding: The encoding to use for rendering.

        Returns:
            :obj:`str`: The rendered version note.
        """
#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
import warnings
from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass, field

from chango._utils.files import UTF8
from chango.abc._versionnote import VersionNote


@dataclass
class VersionHistory[VNT: VersionNote](MutableMapping[str, VNT], abc.ABC):
    """Abstract base class for a version history describing the versions in a software project over
    several versions.

    Hint:
        Objects of this class can be used as mutable mappings, where the keys are the unique
        identifiers of the versions and the values are the version notes themselves.
    """

    _version_notes: dict[str, VNT] = field(default_factory=dict, init=False)

    def __delitem__(self, __key: str) -> None:
        del self._version_notes[__key]

    def __getitem__(self, __key: str) -> VNT:
        return self._version_notes[__key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._version_notes)

    def __len__(self) -> int:
        return len(self._version_notes)

    def __setitem__(self, __key: str, __value: VNT) -> None:
        if __key != __value.uid:
            warnings.warn(
                f"Key {__key!r} does not match version note UID {__value.uid!r}. "
                "Using value the version UID as key.",
                stacklevel=2,
            )
        self._version_notes[__value.uid] = __value

    def add_version_note(self, version_note: VNT) -> None:
        """Add a version note to the version note.

        Args:
            version_note: The version note to add.
        """
        self[version_note.uid] = version_note

    def remove_version_note(self, version_note: VNT) -> None:
        """Remove a version note from the version note.

        Args:
            version_note: The version note to remove.
        """
        del self[version_note.uid]

    @abc.abstractmethod
    def render(self, markup: str, encoding: str = UTF8) -> str:
        """Render the version note as a string. Must include information about all change notes
        contained in the version note.

        Hint:
            * Make use of :meth:`chango.abc.VersionNote.render` to render the change notes.
            * The change notes should be rendered in reverse chronological order. This needs to be
              handled by the implementation and can be achieved either by applying appropriate
              sorting the :attr:`~chango.abc.VersionNote.uid` or by sorting by
              :attr:`~chango.abc.VersionNote.date` if available.

        Args:
            markup: The markup language to use for rendering. If the markup language
                is not supported, an :exc:`~chango.errors.UnsupportedMarkupError` should be raised.
            encoding: The encoding to use for rendering.

        Returns:
            :obj:`str`: The rendered version note.
        """

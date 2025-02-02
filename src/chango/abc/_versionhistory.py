#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
import warnings
from collections.abc import Iterator, MutableMapping

from .._utils.types import VersionUID, VUIDInput
from ..abc._versionnote import VersionNote
from ..helpers import ensure_uid


class VersionHistory[VNT: VersionNote](MutableMapping[VersionUID, VNT], abc.ABC):
    """Abstract base class for a version history describing the versions in a software project over
    several versions.

    Hint:
        Objects of this class can be used as :class:`~collections.abc.MutableMapping`, where the
        keys are the unique identifiers of the versions and the values are the version notes
        themselves.
    """

    def __init__(self) -> None:
        self._version_notes: dict[VersionUID, VNT] = {}

    def __delitem__(self, key: VUIDInput, /) -> None:
        del self._version_notes[ensure_uid(key)]

    def __getitem__(self, key: VUIDInput, /) -> VNT:
        return self._version_notes[ensure_uid(key)]

    def __iter__(self) -> Iterator[VersionUID]:
        return iter(self._version_notes)

    def __len__(self) -> int:
        return len(self._version_notes)

    def __setitem__(self, key: VUIDInput, value: VNT, /) -> None:
        if ensure_uid(key) != value.uid:
            warnings.warn(
                f"Key {key!r} does not match version note UID {value.uid!r}. "
                "Using the version UID as key.",
                stacklevel=2,
            )
        self._version_notes[value.uid] = value  # type: ignore[index]

    def add_version_note(self, version_note: VNT) -> None:
        """Add a version note to the version note.

        Args:
            version_note (:class:`VNT <typing.TypeVar>`): The :class:`~chango.abc.VersionNote`
                note to add.
        """
        self[version_note.uid] = version_note  # type: ignore[index]

    def remove_version_note(self, version_note: VNT) -> None:
        """Remove a version note from the version note.

        Args:
            version_note (:class:`VNT <typing.TypeVar>`): The :class:`~chango.abc.VersionNote`
                note to remove.
        """
        del self[version_note.uid]  # type: ignore[arg-type]

    @abc.abstractmethod
    def render(self, markup: str) -> str:
        """Render the version note as a string. Must include information about all change notes
        contained in the version note.

        Hint:
            * Make use of :meth:`chango.abc.VersionNote.render` to render the change notes.
            * The change notes should be rendered in reverse chronological order. This needs to be
              handled by the implementation and can be achieved either by applying appropriate
              sorting the :attr:`~chango.abc.VersionNote.uid` or by sorting by
              :attr:`~chango.abc.VersionNote.date` if available.

        Args:
            markup (:obj:`str`): The markup language to use for rendering. If the markup language
                is not supported, an :exc:`~chango.error.UnsupportedMarkupError` should be raised.

        Returns:
            :obj:`str`: The rendered version note.
        """

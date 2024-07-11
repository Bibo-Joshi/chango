#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from pathlib import Path
from typing import Self

from chango._utils.filename import FileName


class ChangeNote(abc.ABC):
    """Abstract base class for a change note describing a single change in a software project.

    Args:
        slug (:obj:`str`): A short, human-readable identifier for the change note.
        uid (:obj:`str`, optional): A unique identifier for the change note. If not provided, a
            random identifier will be generated. Should be 8 characters long and consist of
            lowercase letters and digits.
    """

    def __init__(self, slug: str, uid: str | None = None):
        self._file_name = FileName(slug=slug, uid=uid) if uid else FileName(slug=slug)

    @property
    def slug(self) -> str:
        """The short, human-readable identifier for the change note."""
        return self._file_name.slug

    @property
    def uid(self) -> str:
        """The unique identifier for the change note."""
        return self._file_name.uid

    @property
    @abc.abstractmethod
    def file_extension(self) -> str:
        """The file extension to use when writing the change note to a file. The extension must
        *not* include the leading dot.
        """

    @property
    def file_name(self) -> str:
        """The file name to use when writing the change note to a file."""
        return self._file_name.to_string(self.file_extension)

    @classmethod
    def from_file(cls, file_path: str | Path) -> Self:
        """
        Read a change note from the specified file.

        Args:
            file_path (:obj:`str` | :class:`pathlib.Path)`: The path to the file to read from.

        Returns:
            The :class:`ChangeNote` object.

        Raises:
            :class:`chango.errors.ValidationError`: If the data is not a valid change note file.
        """
        return cls.from_bytes(Path(file_path).read_bytes())

    @classmethod
    @abc.abstractmethod
    def from_bytes(cls, data: bytes) -> Self:
        """
        Read a change note from the specified byte data. The data will be the raw binary content
        of a change note file. The implementation must be able to handle the case where the data
        is not a valid change note file and raise an :exc:`~chango.errors.ValidationError` in that
        case.

        Args:
            data (:obj:`bytes`): The bytes to read from.

        Returns:
            The :class:`ChangeNote` object.

        Raises:
            :class:`chango.errors.ValidationError`: If the data is not a valid change note file.
        """

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        """Write the change note to bytes. This binary data should be suitable for writing to a
        file and reading back in with :meth:`~chango.abc.ChangeNote.from_bytes`.

        Returns:
            The bytes data.
        """

    def to_file(self, file_path: str | Path | None = None) -> Path:
        """Write the change note to the specified file.

        Args:
            file_path (:obj:`str` | :class:`pathlib.Path)`: Optional. The path to the file to write
                to. Defaults to :attr:`file_name`.

        Returns:
            :class:`pathlib.Path`: The path to the file that was written.
        """
        path = Path(file_path or self.file_name)
        path.write_bytes(self.to_bytes())
        return path

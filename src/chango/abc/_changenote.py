#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from pathlib import Path
from typing import Self

from .._utils.filename import FileName
from .._utils.files import UTF8
from .._utils.types import PathLike


class ChangeNote(abc.ABC):
    """Abstract base class for a change note describing a single change in a software project.

    Args:
        slug: A short, human-readable identifier for the change note.
        uid: A unique identifier for the change note. If not provided, a
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

    @classmethod
    @abc.abstractmethod
    def build_template(cls, slug: str, uid: str | None = None) -> Self:
        """Build a template change note for the concrete change note type.

        Tip:
            This will be used to create a new change note in the CLI.

        Args:
            slug: The slug to use for the change note.
            uid: The unique identifier for the change note or :obj:`None` to generate a random one.

        Returns:
            The :class:`ChangeNote` object.
        """

    @property
    def file_name(self) -> str:
        """The file name to use when writing the change note to a file."""
        return self._file_name.to_string(self.file_extension)

    @classmethod
    def from_file(cls, file_path: PathLike, encoding: str = UTF8) -> Self:
        """
        Read a change note from the specified file.

        Tip:
            This convenience method calls :meth:`from_bytes` internally.

        Args:
            file_path: The path to the file to read from.
            encoding: The encoding to use for reading.

        Returns:
            The :class:`ChangeNote` object.

        Raises:
            :class:`chango.errors.ValidationError`: If the data is not a valid change note file.
        """
        path = Path(file_path)
        file_name = FileName.from_string(path.name)
        return cls.from_bytes(
            slug=file_name.slug, uid=file_name.uid, data=path.read_bytes(), encoding=encoding
        )

    @classmethod
    def from_bytes(cls, slug: str, uid: str, data: bytes, encoding: str = UTF8) -> Self:
        """
        Read a change note from the specified byte data. The data will be the raw binary content
        of a change note file.

        Tip:
            This convenience method calls :meth:`from_string` internally.

        Args:
            slug: The slug of the change note.
            uid: The UID of the change note.
            data: The bytes to read from.
            encoding: The encoding to use for reading.

        Returns:
            The :class:`ChangeNote` object.

        Raises:
            :class:`chango.errors.ValidationError`: If the data is not a valid change note file.
        """
        return cls.from_string(slug=slug, uid=uid, string=data.decode(encoding))

    @classmethod
    @abc.abstractmethod
    def from_string(cls, slug: str, uid: str, string: str) -> Self:
        """Read a change note from the specified string data. The implementation must be able to
        handle the case where the string is not a valid change note and raise an
        :exc:`~chango.errors.ValidationError` in that case.

        Args:
            slug: The slug of the change note.
            uid: The UID of the change note.
            string: The string to read from.

        Returns:
            The :class:`ChangeNote` object.

        Raises:
            :class:`chango.errors.ValidationError`: If the string is not a valid change note.
        """

    @abc.abstractmethod
    def to_bytes(self, encoding: str = UTF8) -> bytes:
        """Write the change note to bytes. This binary data should be suitable for writing to a
        file and reading back in with :meth:`from_bytes`.

        Tip:
            This convenience method calls :meth:`to_string` internally.

        Args:
            encoding: The encoding to use for writing.

        Returns:
            The bytes data.
        """
        return self.to_string().encode(encoding)

    @abc.abstractmethod
    def to_string(self, encoding: str = UTF8) -> str:
        """Write the change note to a string. This string should be suitable for writing to a file
        and reading back in with :meth:`from_string`.

        Args:
            encoding: The encoding to use for writing.

        Returns:
            The string data.
        """

    def to_file(self, directory: PathLike | None = None, encoding: str = UTF8) -> Path:
        """Write the change note to the directory.

        Hint:
            The file name will always be the :attr:`~chango.abc.ChangeNote.file_name`.

        Args:
            directory: Optional. The directory to write the file to. If not provided, the file
                will be written to the current working directory.
            encoding: The encoding to use for writing.

        Returns:
            :class:`pathlib.Path`: The path to the file that was written.
        """
        path = Path(directory) if directory else Path.cwd()
        write_path = path / self.file_name
        write_path.write_bytes(self.to_bytes(encoding=encoding))
        return write_path
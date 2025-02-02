#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import abc
from pathlib import Path
from typing import Any, Self

from .._utils.filename import FileName
from .._utils.files import UTF8
from .._utils.types import PathLike
from ..action import ChanGoActionData


class ChangeNote(abc.ABC):
    """Abstract base class for a change note describing a single change in a software project.

    Args:
        slug (:obj:`str`): A short, human-readable identifier for the change note.
        uid (:obj:`str`): A unique identifier for the change note. If not provided, a
            random identifier will be generated. Should be 8 characters long and consist of
            lowercase letters and digits.
    """

    def __init__(self, slug: str, uid: str | None = None):
        self._file_name = FileName(slug=slug, uid=uid) if uid else FileName(slug=slug)

    @property
    def slug(self) -> str:
        """:obj:`str`: The short, human-readable identifier for the change note."""
        return self._file_name.slug

    @property
    def uid(self) -> str:
        """:obj:`str`: The unique identifier for the change note."""
        return self._file_name.uid

    @property
    @abc.abstractmethod
    def file_extension(self) -> str:
        """:obj:`str`: The file extension to use when writing the change note to a file. The
        extension must *not* include the leading dot.
        """

    def update_uid(self, uid: str) -> None:
        """Update the UID of the change note.
        Use with caution.

        Args:
            uid (:obj:`str`): The new UID to use.
        """
        self._file_name = FileName(slug=self.slug, uid=uid)

    @classmethod
    @abc.abstractmethod
    def build_template(cls, slug: str, uid: str | None = None) -> Self:
        """Build a template change note for the concrete change note type.

        Tip:
            This will be used to create a new change note in the CLI.

        Args:
            slug (:obj:`str`): The slug to use for the change note.
            uid (:obj:`str`): The unique identifier for the change note or :obj:`None` to generate
                a random one.

        Returns:
            The :class:`ChangeNote` object.
        """

    @classmethod
    def build_from_github_event(
        cls, event: dict[str, Any], data: dict[str, Any] | ChanGoActionData | None = None
    ) -> Self:
        """Build a change note from a GitHub event.

        Important:
            This is an optional method and by default raises a :class:`NotImplementedError`.
            Implement this method if you want to automatically create change notes based on
            GitHub events.

        Tip:
            This method is useful for automatically creating change note drafts in GitHub actions
            to ensure that each pull request has documented changes.

            .. seealso:: :ref:`action`

        Args:
            event (Dict[:obj:`str`, :obj:`~typing.Any`]): The GitHub event data. This should be one
              of the `events that trigger workflows <ettw>`_. The event is represented as a
              JSON dictionary.
            data (Dict[:obj:`str`, :obj:`~typing.Any`] | :class:`chango.action.ChanGoActionData`, \
               optional): Additional data that may be required to build the change note.

        Returns:
            :class:`CNT <typing.TypeVar>`: The change note or :obj:`None`.

        Raises:
            NotImplementedError: If the method is not implemented.

        .. _ettw: https://docs.github.com/en/actions/writing-workflows/\
            choosing-when-your-workflow-runs/events-that-trigger-workflows
        """
        raise NotImplementedError

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
            file_path (:class:`pathlib.Path` | :obj:`str`): The path to the file to read from.
            encoding (:obj:`str`): The encoding to use for reading.

        Returns:
            :class:`ChangeNote`: The :class:`ChangeNote` object.

        Raises:
            :class:`chango.error.ValidationError`: If the data is not a valid change note file.
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
            slug (:obj:`str`): The slug of the change note.
            uid (:obj:`str`): The UID of the change note.
            data (:obj:`bytes`): The bytes to read from.
            encoding (:obj:`str`): The encoding to use for reading.

        Returns:
            :class:`ChangeNote`: The :class:`ChangeNote` object.

        Raises:
            :class:`chango.error.ValidationError`: If the data is not a valid change note file.
        """
        return cls.from_string(slug=slug, uid=uid, string=data.decode(encoding))

    @classmethod
    @abc.abstractmethod
    def from_string(cls, slug: str, uid: str, string: str) -> Self:
        """Read a change note from the specified string data. The implementation must be able to
        handle the case where the string is not a valid change note and raise an
        :exc:`~chango.error.ValidationError` in that case.

        Args:
            slug (:obj:`str`): The slug of the change note.
            uid (:obj:`str`): The UID of the change note.
            string (:obj:`str`): The string to read from.

        Returns:
            :class:`ChangeNote`: The :class:`ChangeNote` object.

        Raises:
            :class:`chango.error.ValidationError`: If the string is not a valid change note.
        """

    def to_bytes(self, encoding: str = UTF8) -> bytes:
        """Write the change note to bytes. This binary data should be suitable for writing to a
        file and reading back in with :meth:`from_bytes`.

        Tip:
            This convenience method calls :meth:`to_string` internally.

        Args:
            encoding (:obj:`str`): The encoding to use.

        Returns:
            :obj:`bytes`: The bytes data.
        """
        return self.to_string(encoding).encode(encoding)

    @abc.abstractmethod
    def to_string(self, encoding: str = UTF8) -> str:
        """Write the change note to a string. This string should be suitable for writing to a file
        and reading back in with :meth:`from_string`.

        Args:
            encoding (:obj:`str`): The encoding to use for writing.

        Returns:
            :obj:`str`: The string data.
        """

    def to_file(self, directory: PathLike | None = None, encoding: str = UTF8) -> Path:
        """Write the change note to the directory.

        Hint:
            The file name will always be the :attr:`~chango.abc.ChangeNote.file_name`.

        Args:
            directory: Optional. The directory to write the file to. If not provided, the file
                will be written to the current working directory.
            encoding (:obj:`str`): The encoding to use for writing.

        Returns:
            :class:`pathlib.Path`: The path to the file that was written.
        """
        path = Path(directory) if directory else Path.cwd()
        write_path = path / self.file_name
        write_path.write_bytes(self.to_bytes(encoding=encoding))
        return write_path

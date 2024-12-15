#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
#
#  SPDX-License-Identifier: MIT
import abc
import tomllib
from collections.abc import Collection
from typing import Any, ClassVar, Final, Self, override

import pydantic as pydt
import tomlkit

from chango._utils.files import UTF8
from chango.abc import ChangeNote
from chango.concrete.section_change_note._pullrequest import PullRequest
from chango.concrete.section_change_note._section import Section
from chango.constants import MarkupLanguage
from chango.error import ValidationError


class SectionChangeNote(pydt.BaseModel, ChangeNote, abc.ABC):
    """A change note that consists of multiple sections and includes references to pull requests
    that are related to the change.

    Uses the `toml <https://toml.io/>`_ format for specifying the content.

    Important:
        This class does not contain any specified sections by default and must not be instantiated
        directly. Use :meth:`with_sections` to create a suitable subclass with the desired
        sections.

    Args:
        pull_requests (tuple[:class:`PullRequest`], optional): The pull requests that are related
            to the change.

    Attributes:
        pull_requests (tuple[:class:`~chango.concrete.section_change_note.PullRequest`]): The pull
            requests that are related to the change
    """

    MARKUP: ClassVar[str] = MarkupLanguage.RESTRUCTUREDTEXT
    """:obj:`str`: The markup language used in the sections.
    """

    _SECTION_TITLES: Final[dict[str, str]] = pydt.PrivateAttr(default_factory=dict)
    """Mapping of section UIDs to section titles.
    This is set by the :meth:`with_sections` class method.
    """

    pull_requests: tuple[PullRequest, ...] = pydt.Field(default_factory=tuple)

    def __init__(self, slug: str, *args: Any, uid: str | None = None, **kwargs: Any) -> None:
        # Maxing pydantic with non-pydantic base classes is a bit tricky.
        # Unfortunately, we have to call the __init__ methods of both classes manually and also
        # don't get an overly nice signature. However, this class should rarely be instantiated
        # directly, so this should be acceptable.
        super().__init__(*args, **kwargs)
        ChangeNote.__init__(self, slug=slug, uid=uid)

    @pydt.model_validator(mode="after")
    def _validate_section_configuration(self) -> Self:
        # Runs after the pydantic validation. Adds some additional checks in case someone is
        # trying to manually build subclasses of SectionChangeNote.
        if self.__class__ is SectionChangeNote:
            raise TypeError(
                "SectionChangeNote must not be instantiated directly. Please use "
                "SectionChangeNote.with_sections to create a suitable subclass."
            )

        if not self._SECTION_TITLES:
            raise TypeError(
                "SectionChangeNote must not be subclassed manually Please use"
                "SectionChangeNote.with_sections to create a suitable subclass."
            )

        return self

    @classmethod
    def with_sections(cls, sections: Collection[Section], name: str | None = None) -> type[Self]:
        """Create a new subclass of :class:`SectionChangeNote` with the given sections.

        Args:
            sections (Collection[:class:`Section`]): The sections to include in the
                change note.
            name (:obj:`str`, optional): The name of the new class. Defaults to
                ``DynamicSectionChangeNote``.

        Returns:
            type[:class:`SectionChangeNote`]: The new subclass of :class:`SectionChangeNote`.

        """
        # This also covers the case of `sections` being an empty collection
        if not any(section.is_required for section in sections):
            raise ValueError("At least one section must be required.")

        config_fields = {
            section.uid: (str, pydt.Field(...)) if section.is_required else (str | None, None)
            for section in sections
        }

        doc_insert = ", ".join(f'"{x}"' for x in (section.title for section in sections))

        dynamic_model = pydt.create_model(  # type: ignore[call-overload]
            name or "DynamicSectionChangeNote",
            __base__=cls,
            __doc__=f"SectionChangeNote with sections {doc_insert}",
            **config_fields,
        )
        dynamic_model._SECTION_TITLES = {section.uid: section.title for section in sections}
        return dynamic_model

    @property
    @override
    def file_extension(self) -> str:
        return "toml"

    @classmethod
    @override
    def from_string(cls, slug: str, uid: str, string: str) -> Self:
        """Implementation of :meth:`~chango.abc.ChangeNote.from_string`.

        Args:
            slug (:obj:`str`): The slug of the change note.
            uid (:obj:`str`): The UID of the change note.
            string (:obj:`str`): The ``toml`` string to read from.

        Returns:
            :class:`~chango.abc.ChangeNote`: The :class:`~chango.abc.ChangeNote` object.

        Raises:
            :class:`chango.error.ValidationError`: If the string is not a valid change note.

        """
        try:
            return cls(slug=slug, uid=uid, **tomllib.loads(string))
        except (tomllib.TOMLDecodeError, pydt.ValidationError) as exc:
            raise ValidationError(f"Invalid TOML data: {exc}") from exc

    @override
    def to_string(self, encoding: str = UTF8) -> str:
        return tomlkit.dumps(
            {key: value for key, value in self.model_dump().items() if value is not None}
        )

    @classmethod
    @override
    def build_template(cls, slug: str, uid: str | None = None) -> Self:
        required_sections = {
            field_name: "Required Section Content"
            if field_info.is_required()
            else "Optional Section Content"
            for field_name, field_info in cls.model_fields.items()
            if field_name != "pull_requests"
        }
        pull_requests = (
            PullRequest(
                uid="pr-number-1", closes_threads=("thread1", "thread2"), author_uid="author1"
            ),
            PullRequest(uid="pr-number-2", closes_threads=("thread3",), author_uid="author2"),
        )
        return cls(slug=slug, uid=uid, pull_requests=pull_requests, **required_sections)

    @abc.abstractmethod
    def get_pull_request_url(self, pr_uid: str) -> str:
        """Get the URL of the pull request with the given UID.

        Args:
            pr_uid (:obj:`str`): The UID of the pull request as defined in
                :attr:`chango.concrete.section_change_note.PullRequest.uid`.

        Returns:
            :obj:`str`: The URL of the pull request.

        """

    @abc.abstractmethod
    def get_thread_url(self, thread_uid: str) -> str:
        """Get the URL of the thread with the given UID.

        Args:
            thread_uid (:obj:`str`): The UID of the thread as defined in
                :attr:`chango.concrete.section_change_note.PullRequest.closes_threads`.

        Returns:
            :obj:`str`: The URL of the thread.

        """

    @abc.abstractmethod
    def get_author_url(self, author_uid: str) -> str:
        """Get the URL of the author with the given UID.

        Args:
            author_uid (:obj:`str`): The UID of the author as defined in
                :attr:`chango.concrete.section_change_note.PullRequest.author_uid`.

        Returns:
            :obj:`str`: The URL of the author.

        """

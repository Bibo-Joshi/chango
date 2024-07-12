#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["UNRELEASED", "UNRELEASED_TYPE", "MarkupLanguage"]

import contextlib
from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

UNRELEASED = "unreleased-fx7cogka"
# we include a random suffix to avoid conflicts with other version names
"""A special object to indicate that a version has not been released yet."""

UNRELEASED_TYPE = Literal["unreleased-fx7cogka"]
"""A type hint for the :attr:`UNRELEASED` constant."""


class MarkupLanguage(StrEnum):
    """Commonly known markup languages"""

    ASCIIDOC = "asciidoc"
    """The `AsciiDoc <https://asciidoc.org>`_ markup language"""
    CREOLE = "creole"
    """The `Creole <https://www.wikicreole.org>`_ markup language"""
    HTML = "html"
    """The `HyperText Markup Language <https://html.spec.whatwg.org>`_"""
    MARKDOWN = "markdown"
    """The `Markdown <https://daringfireball.net/projects/markdown/>`_ markup language"""
    MEDIAWIKI = "mediawiki"
    """The `MediaWiki <https://www.mediawiki.org>`_ markup language"""
    ORG = "org"
    """The `Org-mode <https://orgmode.org>`_ markup language"""
    POD = "pod"
    """The `Plain Old Documentation <https://perldoc.perl.org/perlpod.html>`_ markup language"""
    RDOC = "rdoc"
    """The `RDoc <https://ruby.github.io/rdoc/>`_ markup language"""
    RESTRUCTUREDTEXT = "rst"
    """The `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ markup language"""
    TEXTILE = "textile"
    """The `Textile <https://textile-lang.com>`_ markup language"""
    TEXT = "txt"
    """Plain text"""

    @classmethod
    def from_string(
        cls, string: str, mapping: Mapping[str, "MarkupLanguage"] | None = None
    ) -> "MarkupLanguage":
        """Get the markup language enum member from a string by comparing against the members of
        this enum as well as commonly used file extensions. Case-insensitive. Leading dots are
        ignored.

        Args:
            string: The string to loop up.
            mapping: A mapping of file extensions to markup languages. If not provided, the
                default mapping will be used.

        Raises:
            ValueError: If the file extension can not be resolved to a markup language.
        """
        lookup = string.lower().lstrip(".")

        with contextlib.suppress(ValueError):
            return cls(lookup)

        with contextlib.suppress(KeyError):
            return cls[lookup.upper()]

        if mapping:
            if out := mapping[lookup]:
                return out
            raise ValueError(f"File extension `{string}` not found in provided mapping.")

        default_mapping = {
            "adoc": cls.ASCIIDOC,
            "htm": cls.HTML,
            "md": cls.MARKDOWN,
            "mkd": cls.MARKDOWN,
            "mdwn": cls.MARKDOWN,
            "mdown": cls.MARKDOWN,
            "mdtxt": cls.MARKDOWN,
            "mdtext": cls.MARKDOWN,
            "mediawiki": cls.MEDIAWIKI,
            "org": cls.ORG,
            "pod": cls.POD,
            "rdoc": cls.RDOC,
            "text": cls.TEXT,
        }

        with contextlib.suppress(KeyError):
            return default_mapping[lookup]

        raise ValueError(f"File extension `{string}` not found in default mapping.")

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pytest

from chango.constants import MarkupLanguage


class TestMarkupLanguage:
    def test_str_instance(self):
        for member in MarkupLanguage:
            assert isinstance(member, str)

    @pytest.mark.parametrize("leading_dot", [True, False])
    def test_from_string_members(self, leading_dot):
        for member in MarkupLanguage:
            string = member.value
            if leading_dot:
                string = "." + string
            assert MarkupLanguage.from_string(string) == member

    @pytest.mark.parametrize("leading_dot", [True, False])
    def test_from_string_default_mapping(self, leading_dot):
        default_mapping = {
            "adoc": MarkupLanguage.ASCIIDOC,
            "htm": MarkupLanguage.HTML,
            "md": MarkupLanguage.MARKDOWN,
            "mkd": MarkupLanguage.MARKDOWN,
            "mdwn": MarkupLanguage.MARKDOWN,
            "mdown": MarkupLanguage.MARKDOWN,
            "mdtxt": MarkupLanguage.MARKDOWN,
            "mdtext": MarkupLanguage.MARKDOWN,
            "mediawiki": MarkupLanguage.MEDIAWIKI,
            "org": MarkupLanguage.ORG,
            "pod": MarkupLanguage.POD,
            "rdoc": MarkupLanguage.RDOC,
            "text": MarkupLanguage.TEXT,
        }
        for ext, member in default_mapping.items():
            string = ext
            if leading_dot:
                string = "." + string
            assert MarkupLanguage.from_string(string) == member

    def test_from_string_invalid(self):
        with pytest.raises(
            ValueError, match="File extension `unknown` not found in default mapping."
        ):
            MarkupLanguage.from_string("unknown")
        with pytest.raises(
            ValueError, match="File extension `.unknown` not found in default mapping."
        ):
            MarkupLanguage.from_string(".unknown")

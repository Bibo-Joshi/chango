#  noqa: INP001
#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from chango.concrete import (
    CommentChangeNote,
    CommentVersionNote,
    DirectoryChanGo,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)
from chango.constants import MarkupLanguage


class RstChangeNote(CommentChangeNote):
    MARKUP = MarkupLanguage.RESTRUCTUREDTEXT


chango_instance = DirectoryChanGo(
    change_note_type=RstChangeNote,
    version_note_type=CommentVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=DirectoryVersionScanner(base_directory=".", unreleased_directory="unreleased"),
)

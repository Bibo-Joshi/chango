#  noqa: INP001
#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

from chango.concrete import (
    BackwardCompatibleChanGo,
    BackwardCompatibleVersionScanner,
    CommentChangeNote,
    CommentVersionNote,
    DirectoryChanGo,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)
from chango.concrete.sections import GitHubSectionChangeNote, Section, SectionVersionNote
from chango.constants import MarkupLanguage


class RstChangeNote(CommentChangeNote):
    MARKUP = MarkupLanguage.RESTRUCTUREDTEXT


legacy_version_scanner = DirectoryVersionScanner(
    base_directory="./legacy", unreleased_directory="unreleased"
)

legacy_chango_instance = DirectoryChanGo(
    change_note_type=RstChangeNote,
    version_note_type=CommentVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=legacy_version_scanner,
)

new_version_scanner = DirectoryVersionScanner(
    base_directory=".", unreleased_directory="unreleased"
)
ChangoSectionChangeNote = GitHubSectionChangeNote.with_sections(
    [
        Section(uid="highlights", title="Highlights", sort_order=0),
        Section(uid="breaking", title="Breaking Changes", sort_order=1),
        Section(uid="security", title="Security Changes", sort_order=2),
        Section(uid="deprecations", title="Deprecations", sort_order=3),
        Section(uid="features", title="New Features", sort_order=4),
        Section(uid="bugfixes", title="Bug Fixes", sort_order=5),
        Section(uid="dependencies", title="Dependencies", sort_order=6),
        Section(uid="other", title="Other Changes", sort_order=7),
        Section(uid="documentation", title="Documentation", sort_order=8),
        Section(uid="internal", title="Internal Changes", sort_order=9),
    ]
)
ChangoSectionChangeNote.OWNER = "Bibo-Joshi"
ChangoSectionChangeNote.REPOSITORY = "chango"

new_chango_instance = DirectoryChanGo(
    change_note_type=ChangoSectionChangeNote,
    version_note_type=SectionVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=new_version_scanner,
)

version_scanner = BackwardCompatibleVersionScanner(
    scanners=(new_version_scanner, legacy_version_scanner)
)
chango_instance = BackwardCompatibleChanGo(
    main_instance=new_chango_instance, legacy_instances=(legacy_chango_instance,)
)

if __name__ == "__main__":
    chango_instance.load_version_history().render(MarkupLanguage.RESTRUCTUREDTEXT)

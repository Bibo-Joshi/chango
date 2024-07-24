#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

from chango.concrete import (
    CommentChangeNote,
    CommentVersionNote,
    DirectoryIO,
    DirectoryVersionScanner,
    HeaderVersionHistory,
)

# get project description from pyproject.toml
chango_root = Path(__file__).parent.parent.parent.parent.resolve().absolute()
description = "CHANgelog GOvernor for Your Project"
data_root = Path(r"C:\Users\hinri\PycharmProjects\chango\data")

IO = DirectoryIO(
    change_note_type=CommentChangeNote,
    version_note_type=CommentVersionNote,
    version_history_type=HeaderVersionHistory,
    scanner=DirectoryVersionScanner(base_directory=data_root, unreleased_directory="unreleased"),
)

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

import pytest

from chango import ChangeNoteInfo, Version


class TestChangeNoteInfo:
    def test_init(self):
        v = Version("1.2.3", None)
        cni = ChangeNoteInfo(uid="123", version=v, file_path=Path("/path/to/file"))
        assert cni.uid == "123"
        assert cni.version == v
        assert cni.file_path == Path("/path/to/file")

    def test_frozen(self):
        v = Version("1.2.3", None)
        cni = ChangeNoteInfo(uid="123", version=v, file_path=Path("/path/to/file"))
        with pytest.raises(AttributeError):
            cni.uid = "124"
        with pytest.raises(AttributeError):
            cni.version = Version("1.2.4", None)
        with pytest.raises(AttributeError):
            cni.file_path = Path("/new/path/to/file")

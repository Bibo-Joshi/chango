#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

from chango.helpers import change_uid_from_file, ensure_uid


class TestHelpers:
    def test_ensure_uid_none(self):
        assert ensure_uid(None) is None

    def test_ensure_uid_str(self):
        assert ensure_uid("uid") == "uid"

    def test_ensure_uid_obj(self):
        class Obj:
            uid = "uid"

        assert ensure_uid(Obj()) == "uid"

    def test_ensure_uid_obj_prop(self):
        class Obj:
            @property
            def uid(self):
                return "uid"

        assert ensure_uid(Obj()) == "uid"

    def test_change_uid_from_file(self):
        assert change_uid_from_file("slug.uid.md") == "uid"
        assert change_uid_from_file(Path("slug.uid.md")) == "uid"

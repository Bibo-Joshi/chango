#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import datetime as dtm

import pytest

from chango import Version


class TestVersion:
    def test_init(self):
        v = Version("1.2.3", dtm.date(2024, 1, 1))
        assert v.uid == "1.2.3"
        assert v.date == dtm.date(2024, 1, 1)

    def test_frozen(self):
        v = Version("1.2.3", dtm.date(2024, 1, 1))
        with pytest.raises(AttributeError):
            v.uid = "1.2.4"
        with pytest.raises(AttributeError):
            v.date = dtm.date(2024, 1, 2)

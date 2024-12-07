#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from chango.config import ChanGoInstanceConfig


class TestChanGoInstanceConfig:
    def test_init(self):
        config = ChanGoInstanceConfig(name="name", module="module", package="package")
        assert config.name == "name"
        assert config.module == "module"
        assert config.package == "package"

    def test_init_required(self):
        config = ChanGoInstanceConfig(name="name", module="module")
        assert config.name == "name"
        assert config.module == "module"
        assert config.package is None

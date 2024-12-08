#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path
from types import SimpleNamespace

import pytest

from chango._utils.types import PathLike
from chango.config import ChanGoInstanceConfig, get_chango_instance
from tests.auxil.files import TEST_DATA_PATH

# INFO:
# Best reference for how use sphinx testing so far is
# https://github.com/sphinx-doc/sphinx/issues/7008


@pytest.fixture(scope="session")
def rootdir():
    return TEST_DATA_PATH / "sphinx_ext"


class MockStorage:
    def __init__(self):
        self.loaded_config: MockCGConfig | None = None

    def invalidate_storage(self):
        self.loaded_config = None

    def set_current_config(self, config: "MockCGConfig"):
        self.loaded_config = config

    def get(self) -> "MockCGConfig":
        if self.loaded_config is None:
            raise RuntimeError("No config loaded")
        return self.loaded_config

    @property
    def rendered_content(self):
        return self.loaded_config.chango.version_history.RENDERED_CONTENT


CG_CONFIG_STORAGE = MockStorage()


class MockVersionHistory(SimpleNamespace):
    RENDERED_CONTENT = "This is the rendered version history"

    def __init__(self):
        super().__init__()
        self.received_kwargs = None
        self.received_args = None

    def render(self, *args, **kwargs) -> str:
        self.received_args = args
        self.received_kwargs = kwargs
        return self.RENDERED_CONTENT


class MockChanGo(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.received_kwargs = None
        self.received_args = None
        self.version_history = MockVersionHistory()

    def load_version_history(
        self, *args, start_from: str | None = None, end_at: str | None = None, **kwargs
    ) -> MockVersionHistory:
        self.received_args = args
        self.received_kwargs = kwargs | {"start_from": start_from, "end_at": end_at}
        return self.version_history


class MockCGConfig(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chango = MockChanGo()

    @classmethod
    def load(cls, path: PathLike | None):
        out = cls(
            sys_path=None if path is None else Path(path),
            chango_instance=ChanGoInstanceConfig(name="name", module="module"),
        )
        CG_CONFIG_STORAGE.set_current_config(out)
        return out

    def import_chango_instance(self) -> MockChanGo:
        return self.chango


@pytest.fixture(autouse=True)
def cg_config_mock(monkeypatch):
    monkeypatch.setattr("chango.config.ChanGoConfig", MockCGConfig)
    yield CG_CONFIG_STORAGE
    get_chango_instance.cache_clear()
    CG_CONFIG_STORAGE.invalidate_storage()

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import os
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from chango.config import ChanGoConfig, get_chango_instance


@contextmanager
def temporary_chdir(path: Path):
    current_dir = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(current_dir)


class TestConfigModule:
    def test_get_chango_instance_caching(self, monkeypatch):
        call_count = 0

        def import_chango_instance():
            nonlocal call_count
            call_count += 1
            return call_count

        def load(*_, **__):
            return SimpleNamespace(import_chango_instance=import_chango_instance)

        monkeypatch.setattr(ChanGoConfig, "load", load)

        for _ in range(10):
            assert get_chango_instance() == 1, "The ChanGo instance should be cached!"

        # to ensure that other tests still pass
        get_chango_instance.cache_clear()

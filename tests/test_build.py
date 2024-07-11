# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
import os
import shutil
from pathlib import Path

import pytest


# To make the tests agnostic of the cwd
@pytest.fixture(autouse=True)
def _change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.config.rootdir)


def test_build():
    assert os.system("python -m build") == 0
    shutil.rmtree(Path("dist"))

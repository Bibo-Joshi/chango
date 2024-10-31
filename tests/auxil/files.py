#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
TEST_DATA_PATH = PROJECT_ROOT_PATH / "tests" / "data"


def data_file(filename: str) -> Path:
    return TEST_DATA_PATH / filename

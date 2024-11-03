#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from pathlib import Path

from chango._utils.types import PathLike

PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
TEST_DATA_PATH = PROJECT_ROOT_PATH / "tests" / "data"


def data_file(filename: PathLike) -> Path:
    return TEST_DATA_PATH / filename

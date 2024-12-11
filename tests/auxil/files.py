#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import os
from contextlib import contextmanager
from pathlib import Path

from chango._utils.types import PathLike

PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
TEST_DATA_PATH = PROJECT_ROOT_PATH / "tests" / "data"


def data_path(filename: PathLike) -> Path:
    return TEST_DATA_PATH / filename


def path_to_python_string(path: Path, output_type: type[str] | type[Path]) -> str:
    if output_type is str:
        return f"'{path.as_posix()}'"
    return f"Path(r'{path}')"


@contextmanager
def temporary_chdir(path: Path):
    current_dir = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(current_dir)

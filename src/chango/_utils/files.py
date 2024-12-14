#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import subprocess
from pathlib import Path

UTF8 = "utf-8"


class _GitMover:
    def __init__(self) -> None:
        self.git_available: bool | None = None

    def _git_move(self, src: Path, dst: Path) -> None:
        # Alternatives to using subprocess would be using pygit2 or dulwich.
        # However, that would add rather heavy dependencies for a very small part of this library.
        # Let's keep it in mind for a possible future improvement.
        subprocess.check_call(["git", "mv", str(src), str(dst)])

    def _pathlib_move(self, src: Path, dst: Path) -> None:
        src.rename(dst)

    def move(self, src: Path, dst: Path) -> None:
        if self.git_available is None:
            # We use try-except instead of first checking if git is available
            # because that way we can avoid calling git twice.
            try:
                self._git_move(src, dst)
                self.git_available = True
            except subprocess.CalledProcessError:
                self.git_available = False
                self._pathlib_move(src, dst)

        elif self.git_available:
            self._git_move(src, dst)
        else:
            self._pathlib_move(src, dst)


_GIT_MOVER = _GitMover()


def move_file(src: Path, dst: Path) -> None:
    _GIT_MOVER.move(src, dst)

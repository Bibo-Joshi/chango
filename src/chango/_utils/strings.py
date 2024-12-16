#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
def indent_multiline(text: str, indent: int = 2, newlines: int = 1) -> str:
    """Indent all lines of a multi-line string except the first one."""
    return (newlines * "\n").join(
        line if i == 0 else " " * indent + line for i, line in enumerate(text.splitlines())
    )

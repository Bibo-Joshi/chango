#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT

__all__ = ["UNRELEASED", "UNRELEASED_TYPE"]

from typing import Literal

UNRELEASED = "unreleased-fx7cogka"
# we include a random suffix to avoid conflicts with other version names
"""A special object to indicate that a version has not been released yet."""

UNRELEASED_TYPE = Literal["unreleased-fx7cogka"]
"""A type hint for the :attr:`UNRELEASED` constant."""

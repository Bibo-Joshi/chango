#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
"""This module contains error classes specific to the :mod:`chango` package."""

__all__ = ["ChanGoError", "UnsupportedMarkupError", "ValidationError"]


class ChanGoError(Exception):
    """Base class for all exceptions defined by the chango package."""


class ValidationError(ChanGoError):
    """Exception raised when a validation error occurs."""


class UnsupportedMarkupError(ChanGoError):
    """Exception raised when an unsupported markup is encountered."""

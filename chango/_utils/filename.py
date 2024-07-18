#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import random
import string as std_string
from dataclasses import dataclass, field
from typing import ClassVar, Self

from ..errors import ValidationError

_alphabet = std_string.ascii_lowercase + std_string.digits


def random_uid() -> str:
    return "".join(random.choices(_alphabet, k=8))


@dataclass
class FileName:
    slug: str
    uid: str = field(default_factory=random_uid)

    SEPARATOR: ClassVar[str] = "."

    def __post_init__(self) -> None:
        if self.SEPARATOR in self.slug:
            raise ValidationError(f"slug must not contain {self.SEPARATOR!r}")

    @classmethod
    def from_string(cls, string: str) -> Self:
        slug, uid, _ = string.split(cls.SEPARATOR)
        return cls(slug, uid)

    def to_string(self, extension: str) -> str:
        return self.SEPARATOR.join([self.slug, self.uid, extension])

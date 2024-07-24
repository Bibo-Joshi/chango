#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from dataclasses import dataclass, field
from typing import ClassVar, Self

import shortuuid

from ..errors import ValidationError

_short_uuid = shortuuid.ShortUUID()


def random_uid() -> str:
    return _short_uuid.uuid()


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
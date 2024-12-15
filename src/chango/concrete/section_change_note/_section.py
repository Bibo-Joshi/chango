#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import pydantic as pydt


class Section(pydt.BaseModel):
    """Configuration for a section in a :class:`SectionChangeNote`.

    Args:
        uid (:obj:`str`): The unique identifier for the section. This is used as the field name
            in the change note.
        title (:obj:`str`): The title of the section.
        is_required (:obj:`bool`, optional): Whether the section is required. Defaults
            to :obj:`False`.

            Tip:
                At least one section must be required.

        sort_order (:obj:`int`, optional): The sort order of the section. Defaults to ``0``.

    Attributes:
        uid (:obj:`str`): The unique identifier for the section.
        title (:obj:`str`): The title of the section.
        is_required (:obj:`bool`): Whether the section is required.
        sort_order (:obj:`int`): The sort order of the section.

    """

    model_config = pydt.ConfigDict(frozen=True)

    uid: str
    title: str
    is_required: bool = False
    sort_order: int = 0

#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
from typing import ClassVar

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
        render_pr_details (:obj:`bool`, optional): Whether to include details about the pull
            requests related to the change in the rendering for this section.
            Defaults to :obj:`True`.
        sort_order (:obj:`int`, optional): The sort order of the section. Defaults to ``0``.

    Attributes:
        uid (:obj:`str`): The unique identifier for the section.
        title (:obj:`str`): The title of the section.
        is_required (:obj:`bool`): Whether the section is required.
        render_pr_details (:obj:`bool`, optional): Whether to include details about the pull
            requests related to the change in the rendering for this section.
        sort_order (:obj:`int`): The sort order of the section.

    """

    model_config: ClassVar[pydt.ConfigDict] = pydt.ConfigDict(frozen=True)

    uid: str
    title: str
    is_required: bool = False
    render_pr_details: bool = True
    sort_order: int = 0

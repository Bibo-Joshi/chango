#  SPDX-FileCopyrightText: 2024-present Hinrich Mahler <chango@mahlerhome.de>
#
#  SPDX-License-Identifier: MIT
import importlib
import logging
from pathlib import Path
from types import ModuleType

from jinja2 import Template

logger = logging.getLogger(__name__)


CLASS_TEMPLATE = Template(
    """{{ class_name }}
{{ "=" * class_name|length }}

.. autoclass:: {{ fqn }}
    :members:
    :show-inheritance:
"""
)

MODULE_TEMPLATE = Template(
    """{{ module_name }}
{{ "=" * module_name|length }}

.. automodule:: {{ fqn }}

.. toctree::
    :titlesonly:

    {% for child in children -%}
    {{ child }}
    {% endfor -%}
"""
)


def write_text(file_path: Path, content: str) -> None:
    if file_path.exists():
        logger.debug("File %s already exists, skipping", file_path)
        return
    file_path.write_text(content, encoding="utf-8")


def write_class_rst_file(class_name: str, fqn: str, output_dir: Path) -> Path:
    file_name = f"{fqn.lower()}.rst"
    file_path = output_dir / file_name
    write_text(file_path, CLASS_TEMPLATE.render(class_name=class_name, fqn=fqn))

    return file_path


def write_module_rst_file(
    module_name: str, fqn: str, children: list[Path], output_dir: Path
) -> Path:
    file_name = f"{fqn.lower()}.rst"
    file_path = output_dir / file_name
    write_text(
        file_path,
        MODULE_TEMPLATE.render(
            module_name=module_name, fqn=fqn, children=sorted(child.stem for child in children)
        ),
    )

    return file_path


def create_rst_files(module_name: str, base_path: Path) -> list[Path]:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        logger.error("Could not import module %s", module_name)
        return []

    if not hasattr(module, "__all__"):
        return []

    created_files: list[Path] = []

    for name in module.__all__:
        fqn = f"{module_name}.{name}"
        try:
            member = getattr(module, name)
        except AttributeError:
            continue

        if not isinstance(member, type | ModuleType):
            # Rest is covered on module level
            continue

        if isinstance(member, type):
            created_files.append(write_class_rst_file(name, fqn, base_path))
        else:
            sub_files = create_rst_files(fqn, base_path)
            created_files.append(write_module_rst_file(name, fqn, sub_files, base_path))

    write_module_rst_file(module_name, module_name, created_files, base_path)
    return created_files


def main() -> None:
    output_dir = Path(__file__).parent / "source"
    output_dir.mkdir(exist_ok=True)

    create_rst_files("chango", output_dir)


if __name__ == "__main__":
    main()

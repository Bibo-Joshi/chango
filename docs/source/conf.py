import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path("../..").resolve().absolute()))

from chango import __version__

pyproject_toml = tomllib.loads(Path("../../pyproject.toml").read_text())

project = pyproject_toml["project"]["name"]
version = __version__
release = __version__
documentation_summary = pyproject_toml["project"]["description"]
author = pyproject_toml["project"]["authors"][0]["name"]
copyright = "2024, Hinrich Mahler"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_paramlinks",
]

html_theme = "furo"

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

nitpicky = True

# paramlinks options
paramlinks_hyperlink_param = "name"

# Don't show type hints in the signature - that just makes it hardly readable
# and we document the types anyway
autodoc_typehints = "none"

html_static_path = ["_static", "../../logo"]

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the documentation.
html_theme_options = {
    "light_logo": "chango_light_mode_1024.png",
    "dark_logo": "chango_dark_mode_1024.png",
    "navigation_with_keys": True,
    "footer_icons": [
        {  # Github logo
            "name": "GitHub",
            "url": "https://github.com/Bibo-Joshi/chango",
            "html": (
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
                'viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
                "2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.4"
                "9-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23"
                ".82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 "
                "0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.2"
                "7 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.5"
                "1.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 "
                '1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z">'
                "</path></svg>"
            ),
            "class": "",
        }
    ],
}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> <release> documentation".
html_title = f"chango {version}"

# Furo's default permalink icon is `#` which doesn't look great imo.
html_permalinks_icon = "¶"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "../../logo/chango_icon.ico"

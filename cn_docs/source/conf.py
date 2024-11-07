#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from importlib.metadata import version as get_version

from packaging.version import parse

# For our local_customization module
sys.path.insert(0, os.path.abspath("."))
# For trio itself
sys.path.insert(0, os.path.abspath("../../src"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinxcontrib_trio",  # 使 Sphinx 更好地记录 Python 函数和方法。特别是，它可以轻松记录异步函数。
    "local_customization",
    "typevars",
    "sphinx_inline_tabs",  # tabs
    "sphinx_copybutton",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "Trio"
copyright = "2017, Nathaniel J. Smith"  # noqa: A001 # Name shadows builtin
author = "Nathaniel J. Smith"

autodoc_member_order = "bysource"

autodoc_type_aliases = {
    # SSLListener.accept's return type is seen as trio._ssl.SSLStream
    "SSLStream": "trio.SSLStream",
}


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#


# General information about the project.


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# import trio

# version = trio.__version__
# # The full version, including alpha/beta/rc tags.
# release = version


##

v = parse(get_version("trio"))
version = v.base_version
release = v.public

language = "zh_CN"

highlight_language = "python3"

exclude_patterns = ["_build"]
pygments_style = "sphinx"
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_mock_imports = ["_typeshed"]
todo_include_todos = False

# html_theme = "sphinx_rtd_theme"
html_theme = "furo"
htmlhelp_basename = "Triodoc"

html_static_path = ["_static"]
html_favicon = "_static/favicon-32.png"
html_logo = "../../logo/wordmark-transparent.svg"


intersphinx_mapping = {
    "python": ("https://docs.python.org/zh-cn/3/", None),
    "outcome": ("https://outcome.readthedocs.io/en/latest/", None),
    "pyopenssl": ("https://www.pyopenssl.org/en/stable/", None),
    "sniffio": ("https://sniffio.readthedocs.io/en/latest/", None),
    "trio-util": ("https://trio-util.readthedocs.io/en/latest/", None),
    "flake8-async": ("https://flake8-async.readthedocs.io/en/latest/", None),
}

html_theme_options = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/hellowac/trio-zh-cn",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/hellowac/trio-zh-cn/",
    "source_branch": "sync-docs",
    "source_directory": "cn_docs/",
}

#!/usr/bin/env python3
from __future__ import annotations

import collections.abc
import os
import sys
import types
from importlib.metadata import version as get_version
from typing import TYPE_CHECKING, cast

from packaging.version import parse

if TYPE_CHECKING:
    from sphinx.application import Sphinx


# For our local_customization module
sys.path.insert(0, os.path.abspath("."))
# For trio itself
sys.path.insert(0, os.path.abspath("../../src"))

# Enable reloading with `typing.TYPE_CHECKING` being True
os.environ["SPHINX_AUTODOC_RELOAD_MODULES"] = "1"


# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-signature
def autodoc_process_signature(
    app: Sphinx,
    what: str,
    name: str,
    obj: object,
    options: object,
    signature: str,
    return_annotation: str,
) -> tuple[str, str]:
    """Modify found signatures to fix various issues."""
    if name == "trio.testing._raises_group._ExceptionInfo.type":
        # This has the type "type[E]", which gets resolved into the property itself.
        # That means Sphinx can't resolve it. Fix the issue by overwriting with a fully-qualified
        # name.
        assert isinstance(obj, property), obj
        assert isinstance(obj.fget, types.FunctionType), obj.fget
        assert (
            obj.fget.__annotations__["return"] == "type[MatchE]"
        ), obj.fget.__annotations__
        obj.fget.__annotations__["return"] = "type[~trio.testing._raises_group.MatchE]"
    if signature is not None:
        signature = signature.replace("~_contextvars.Context", "~contextvars.Context")
        if name == "trio.lowlevel.RunVar":  # Typevar is not useful here.
            signature = signature.replace(": ~trio._core._local.T", "")
        if "_NoValue" in signature:
            # Strip the type from the union, make it look like = ...
            signature = signature.replace(" | type[trio._core._local._NoValue]", "")
            signature = signature.replace("<class 'trio._core._local._NoValue'>", "...")
        if name in ("trio.testing.RaisesGroup", "trio.testing.Matcher") and (
            "+E" in signature or "+MatchE" in signature
        ):
            # This typevar being covariant isn't handled correctly in some cases, strip the +
            # and insert the fully-qualified name.
            signature = signature.replace("+E", "~trio.testing._raises_group.E")
            signature = signature.replace(
                "+MatchE",
                "~trio.testing._raises_group.MatchE",
            )
        if "DTLS" in name:
            signature = signature.replace("SSL.Context", "OpenSSL.SSL.Context")
        # Don't specify PathLike[str] | PathLike[bytes], this is just for humans.
        signature = signature.replace("StrOrBytesPath", "str | bytes | os.PathLike")

    return signature, return_annotation


def add_intersphinx(app: Sphinx) -> None:
    """Add some specific intersphinx mappings.

    Hooked up to builder-inited. app.builder.env.interpshinx_inventory is not an official API, so this may break on new sphinx versions.
    """

    def add_mapping(
        reftype: str,
        library: str,
        obj: str,
        version: str = "3.12",
        target: str | None = None,
    ) -> None:
        """helper function"""
        url_version = "3" if version == "3.12" else version
        if target is None:
            target = f"{library}.{obj}"

        # sphinx doing fancy caching stuff makes this attribute invisible
        # to type checkers
        inventory = app.builder.env.intersphinx_inventory  # type: ignore[attr-defined]
        assert isinstance(inventory, dict)
        inventory = cast("Inventory", inventory)

        inventory[f"py:{reftype}"][f"{target}"] = (
            "Python",
            version,
            f"https://docs.python.org/{url_version}/library/{library}.html/{obj}",
            "-",
        )

    # This has been removed in Py3.12, so add a link to the 3.11 version with deprecation warnings.
    add_mapping("method", "pathlib", "Path.link_to", "3.11")

    # defined in py:data in objects.inv, but sphinx looks for a py:class
    # see https://github.com/sphinx-doc/sphinx/issues/10974
    # to dump the objects.inv for the stdlib, you can run
    # python -m sphinx.ext.intersphinx http://docs.python.org/3/objects.inv
    add_mapping("class", "math", "inf")
    add_mapping("class", "types", "FrameType")

    # new in py3.12, and need target because sphinx is unable to look up
    # the module of the object if compiling on <3.12
    if not hasattr(collections.abc, "Buffer"):
        add_mapping("class", "collections.abc", "Buffer", target="Buffer")


# XX hack the RTD theme until
#   https://github.com/rtfd/sphinx_rtd_theme/pull/382
# is shipped (should be in the release after 0.2.4)
# ...note that this has since grown to contain a bunch of other CSS hacks too
# though.
def setup(app: Sphinx) -> None:
    app.add_css_file("hackrtd.css")
    app.connect("autodoc-process-signature", autodoc_process_signature)
    # After Intersphinx runs, add additional mappings.
    app.connect("builder-inited", add_intersphinx, priority=1000)


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinxcontrib_trio",  # 使 Sphinx 更好地记录 Python 函数和方法。特别是，它可以轻松记录异步函数。
    "sphinx_codeautolink",
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

autodoc_inherit_docstrings = False
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

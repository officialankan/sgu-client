# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

# Add the project root to sys.path for importing the package
sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sgu-client"
copyright = f"{datetime.now().year}, Anders Retzner"
author = "Anders Retzner"
release = "0.5.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_nb",
]

exclude_patterns = []

# typehints_fixup_module_name is a function, so the config cannot be pickled; harmless
suppress_warnings = ["config.cache"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Use a shorter title for the HTML pages
html_title = "sgu-client"
html_show_sourcelink = False

# Keep the page TOC to section headings; long class names overflow it
toc_object_entries = False

html_theme_options = {
    "logo": {"text": "sgu-client"},
    "navbar_align": "left",
    "header_links_before_dropdown": 4,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/officialankan/sgu-client",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/sgu-client/",
            "icon": "fa-brands fa-python",
        },
    ],
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "use_edit_page_button": True,
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version", "theme-version"],
}

html_context = {
    "github_user": "officialankan",
    "github_repo": "sgu-client",
    "github_version": "main",
    "doc_path": "docs/source",
}

# Landing and about pages have no section sidebar
html_sidebars = {
    "index": [],
    "about/**": [],
}

# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pydantic": ("https://pydantic.dev/docs/validation/latest/", None),
}

# Notebooks are committed with outputs; never run them (and hit the SGU API) at build time
nb_execution_mode = "off"
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3

# Strip prompts when copying code examples
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# Napoleon settings for Google and NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
add_module_names = False
autoclass_content = "class"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "exclude-members": "__weakref__, model_config, model_post_init",
}
autosummary_generate = False

# Type hints settings
typehints_fully_qualified = False
always_document_param_types = False
typehints_document_rtype = True


def typehints_fixup_module_name(module: str) -> str:
    """Link pandas types via their public names, which is what pandas' inventory lists."""
    return "pandas" if module.startswith("pandas.") else module


# autodoc-pydantic: show fields with their (Swedish) API aliases, hide internals
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_summary_list_order = "bysource"
autodoc_pydantic_model_member_order = "bysource"
autodoc_pydantic_model_hide_paramlist = True
autodoc_pydantic_model_undoc_members = True
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_field_show_alias = True
autodoc_pydantic_field_show_constraints = True
autodoc_pydantic_field_doc_policy = "description"
autodoc_pydantic_settings_show_json = False

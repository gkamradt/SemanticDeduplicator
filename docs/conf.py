"""Sphinx configuration."""
project = "Semantic Deduplicator"
author = "Greg Kamradt"
copyright = "2023, Greg Kamradt"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"

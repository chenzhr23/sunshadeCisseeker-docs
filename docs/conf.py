# sunshadeCisseeker documentation build configuration.
#
# Read the Docs theme (sphinx_rtd_theme): full-width layout, search box,
# light/dark modes and a mobile-friendly hamburger navigation, with content
# pages under content/.

project = "sunshadeCisseeker"
author = "sunshadeCisseeker developers"
copyright = "2026, sunshadeCisseeker developers"

# The short X.Y version and the full release version.
version = "v1.6.0"
release = "v1.6.0"

extensions = [
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "content/Changelog.rst"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Navigation: show the page list with only the CURRENT page's branch expanded
# down to its first-level section headings.
html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 2,
}

# The :red: text role used across the docs.
rst_prolog = ".. role:: red\n"

# sunshadeCisseeker documentation build configuration.
#
# Sphinx' built-in bizstyle theme with the same custom.css override, content
# pages under content/, and the
# "<page> — sunshadeCisseeker vX.Y.Z documentation" title pattern.

project = "sunshadeCisseeker"
author = "sunshadeCisseeker developers"
copyright = "2026, sunshadeCisseeker developers"

# The short X.Y version and the full release version.
version = "v1.3.45"
release = "v1.3.45"

extensions = [
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "content/Changelog.rst"]

html_theme = "bizstyle"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Sidebar layout: one "Table of Contents" list showing every page together
# with its section headings (3 levels), so the navigation is complete on
# every page; on phones the sidebar is kept visible above the content.
html_sidebars = {"**": ["globaltoc.html"]}
html_theme_options = {
    "globaltoc_maxdepth": 3,
    "globaltoc_collapse": False,
}

# The :red: text role used across the docs.
rst_prolog = ".. role:: red\n"

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

# Sidebar layout: one "Table of Contents" list of the top-level pages; only
# the CURRENT page's branch is expanded, and only to its first-level section
# headings (globaltoc_maxdepth 2 = page + its h2 sections).
html_sidebars = {"**": ["globaltoc.html"]}
html_theme_options = {
    "globaltoc_maxdepth": 2,
}

# The :red: text role used across the docs.
rst_prolog = ".. role:: red\n"

# sunshadeCisseeker documentation build configuration.
#
# The documentation follows the psiFinder style: Sphinx' built-in bizstyle
# theme with the same custom.css override, content pages under content/, and
# the "<page> — sunshadeCisseeker vX.Y.Z documentation" title pattern.

project = "sunshadeCisseeker"
author = "sunshadeCisseeker developers"
copyright = "2026, sunshadeCisseeker developers"

# The short X.Y version and the full release version.
version = "v1.3.16"
release = "v1.3.16"

extensions = [
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "bizstyle"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Sidebar layout exactly like psiFinder: one flat "Table of Contents" list of
# the top-level pages (no local toc, no relations, no source link, no search
# box), while the index body keeps the deep, fully expanded Contents tree.
html_sidebars = {"**": ["globaltoc.html"]}
html_theme_options = {
    "globaltoc_maxdepth": 1,
}

# The :red: text role used by the psiFinder docs.
rst_prolog = ".. role:: red\n"

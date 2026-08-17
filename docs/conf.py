# sunshadeCisseeker documentation build configuration.
#
# The documentation follows the psiFinder style: Sphinx' built-in bizstyle
# theme with the same custom.css override, content pages under content/, and
# the "<page> — sunshadeCisseeker vX.Y.Z documentation" title pattern.

project = "sunshadeCisseeker"
author = "sunshadeCisseeker developers"
copyright = "2026, sunshadeCisseeker developers"

# The short X.Y version and the full release version.
version = "v1.3.4"
release = "v1.3.4"

extensions = [
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "bizstyle"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# The :red: text role used by the psiFinder docs.
rst_prolog = ".. role:: red\n"

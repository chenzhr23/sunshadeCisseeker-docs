# sunshadeCisseeker documentation build configuration.

project = "sunshadeCisseeker"
author = "sunshadeCisseeker developers"
copyright = "2026, sunshadeCisseeker developers"

# The short X.Y version and the full release version.
version = "1.3.4"
release = "1.3.4"

extensions = [
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Read the Docs uses the classic RTD theme, in the same style as psiFinder.
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "sunshadeCisseeker"
html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
}
html_show_sourcelink = True

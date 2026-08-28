Credits
=======

sunshadeCisseeker is released under the **MIT** license.

Framework and interface
-----------------------

The desktop window is a native Qt 5.15 application: a flat tab widget with
page-change animation, a splash screen and a menu-bar main window
(``sunshadeCisseekerMainWindow`` / ``FlatTabWidget``). The page-change
animations come from the `Widget Animation Framework (WAF)
<https://github.com/dimkanovikov/WidgetAnimationFramework>`_, and the Qt 5.15
runtime is bundled from conda-forge.

R packages
----------

openxlsx, data.table, stringi, ggplot2, patchwork, scales, curl, xml2, dplyr,
rentrez, forcats, tidyr, magrittr — the XLSX outputs are written by openxlsx,
the CRE scan
runs the bundled C++ Aho-Corasick backend (``bin/cre_scan``) with an R
``stringi`` fallback, and all figures are made with ggplot2.

Tools
-----

bedtools and samtools (optional accelerators for linear
genomes); the bundled C++ engines ``bin/cre_scan`` (Aho-Corasick
cis-element scan), ``bin/promoter_extract`` (step 04 promoter extraction)
and ``bin/promoter_merge`` (step 05 merge) with automatic R fallbacks;
gzip for download integrity checks; Liberation Sans (bundled,
metric-compatible with Arial) for the interface font.

Data
----

Genome sequences and annotations are downloaded from NCBI (Assembly and
Nucleotide databases). The ecological grouping is user-supplied and never
inferred by the software.

Documentation
-------------

Built with `Sphinx <https://www.sphinx-doc.org/>`_ and the built-in
``bizstyle`` theme, hosted on Read the Docs.

Credits
=======

sunshadeCisseeker is released under the **MIT** license.

Framework and interface
-----------------------

The desktop window follows the **psiFinder framework and look**: the flat tab
widget with page-change animation, the splash screen, the menu-bar main
window (``pseudoTBMainWindow`` / ``FlatTabWidget``) and the psiFinder-style
path/process helpers are modelled on psiFinder. The
`Widget Animation Framework (WAF)
<https://github.com/dimkanovikov/WidgetAnimationFramework>`_ provides the
page-change animations, and the Qt 5.15 runtime is bundled from conda-forge.

R packages
----------

openxlsx, data.table, stringi, ggplot2, patchwork, scales, curl, xml2, dplyr,
rentrez, forcats, tidyr — the XLSX outputs are written by openxlsx, the CRE
scan uses stringi's C-level counting, and all figures are made with ggplot2.

Tools
-----

bedtools and samtools (optional accelerators for uncompressed linear
genomes); gzip for download integrity checks; Liberation Sans (bundled,
metric-compatible with Arial) for the interface font.

Data
----

Genome sequences and annotations are downloaded from NCBI (Assembly and
Nucleotide databases). The ecological grouping is user-supplied and never
inferred by the software.

Documentation
-------------

Built with `Sphinx <https://www.sphinx-doc.org/>`_ and the
`Read the Docs Sphinx theme <https://github.com/readthedocs/sphinx_rtd_theme>`_,
hosted on Read the Docs.

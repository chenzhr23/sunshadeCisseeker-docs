sunshadeCisseeker documentation
================================

**sunshadeCisseeker** quantifies and compares promoter **cis-regulatory
elements (CREs)** between three plant ecological groups — **sun (heliophyte)**,
**facultative (sun-shade generalist)** and **shade (sciophyte)** — across the
**nuclear**, **chloroplast** and **mitochondrial** genomes. Genomes come from
two merged sources: **NCBI** (located and downloaded automatically) and
**Custom** (user-collected FASTA + GFF3).

The software ships as a self-contained Linux bundle with a native Qt 5.15
desktop window (built in the same style as **psiFinder**) and a command-line
launcher that runs the exact same R/bash pipeline.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   installation
   quickstart
   command_line
   gui

.. toctree::
   :maxdepth: 2
   :caption: Analysis

   pipeline
   ecology
   configuration
   outputs

.. toctree::
   :maxdepth: 1
   :caption: Reference

   troubleshooting
   credits

Highlights
----------

* **Universal CRE identification** — a user-editable IUPAC motif library
  (``config/cis_element_motif_library.xlsx``), not limited to PlantCARE.
* **Manual ecology annotation** — ``config/species_ecology_labels.xlsx``
  drives the sun / facultative / shade grouping; the software never infers
  the groups itself.
* **One representative genome per species** — each species downloads exactly
  one most-representative FASTA + GFF3 pair (RefSeq preferred, complete
  annotation preferred, longest, most recent).
* **Fast promoter extraction** — ``bedtools getfasta`` + ``samtools faidx``
  for uncompressed linear genomes, a streaming R extractor for ``.gz`` files,
  and circular-aware R extraction for the organelle genomes.
* **Normalized cross-species metric** — ``element_density`` (sites per 1000
  promoters) makes species with very different gene numbers comparable.
* **Strict sequential steps** — every step reads the exact outputs of the
  previous one; each step writes its own ``.log`` and an XLSX workbook with a
  README sheet.
* **Publication-grade outputs** — multi-sheet XLSX tables plus PDF figures
  (volcano, PCA, heatmap, functional-group composition, key-element boxplots).
* **One-shot installer** — ``install.sh`` bootstraps a conda environment with
  every dependency, registers a self-activating launcher on ``PATH`` and
  verifies the installation end to end, without root rights.

.. note::

   This documentation covers the current release (``1.3.4``). The desktop
   window and the command line run the **same** scripts, so results are
   identical either way.

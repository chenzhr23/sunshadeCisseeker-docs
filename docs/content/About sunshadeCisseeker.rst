About sunshadeCisseeker
=======================

sunshadeCisseeker identifies, annotates and compares promoter
cis-regulatory elements across sun / facultative / shade plants.

The current release is **1.3.21**; see :doc:`Changelog` for what changed in
each version.

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

Contact us
----------

Issues, suggestions and pull requests are welcome at the project repository:
https://github.com/chenzhr23/sunshadeCisseeker-docs

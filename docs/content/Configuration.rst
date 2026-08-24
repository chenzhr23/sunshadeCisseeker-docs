Configuration
=============

Three user-editable files drive the whole analysis.

``quickstart_config.yml`` (run parameters)
------------------------------------------

.. list-table::
   :header-rows: 1

   * - Key
     - Default
     - Meaning
   * - ``promoter_len``
     - ``"2000"``
     - max promoter length extracted upstream of each TSS (bp)
   * - ``workers``
     - ``"6"``
     - parallel workers for the download / extraction pools and the step-01 URL validation
   * - ``cores``
     - ``"8"``
     - cores for the motif scan
   * - ``min_group_n``
     - ``"3"``
     - minimum species per ecology group for a statistical test
   * - ``max_genome_gb``
     - ``""``
     - skip genomes whose FASTA file exceeds this on-disk size (GB); empty or ``"0"`` = no limit. An oversized genome is recorded as ``skipped`` in the step-04 pair summary and never blocks the run (e.g. ``"2"`` skips a 2.7 GB archive)
   * - ``ncbi_api_key``
     - ``""``
     - optional NCBI API key (10 req/s instead of 3; far fewer throttling failures)
   * - ``run_nuclear`` / ``run_chloroplast`` / ``run_mitochondrial``
     - ``"true"``
     - which genome types to run
   * - ``run_ecology``
     - ``"true"``
     - run the cross-genome ecology comparison (07–09)
   * - ``ncbi_download``
     - ``"true"``
     - run NCBI steps 01–03; set ``"false"`` for custom-genome-only runs
   * - ``custom_download``
     - ``"true"``
     - run the Custom genome download step (the per-type lists ``Custom_genome_fa_gff/<type>/Custom_genome_fa_gff_<type>.xlsx``, plus the optional global table) before the per-genome steps; set ``"false"`` when you place custom files manually

``config/species_ecology_labels.xlsx`` (manual annotation)
----------------------------------------------------------

One row per species; edit it in Excel/LibreOffice or through the GUI's
**Tools → Ecology labels...** popup.

.. list-table::
   :header-rows: 1

   * - Column
     - Required
     - Description
   * - ``species``
     - yes
     - species key matching the pipeline name exactly (spaces → underscores, e.g. ``Arabidopsis_thaliana``); copy from the ``species`` column of any ``result/<type>/05_ciselement_input/all_species_<type>_id_map.xlsx``
   * - ``ecology``
     - yes
     - ``sun`` (heliophyte) / ``facultative`` / ``shade`` (sciophyte)
   * - ``note``
     - no
     - free-form note (e.g. ``Manual annotation``)

Only species listed here enter the ecology comparison (steps 07–09);
unlabelled species still appear in the general analysis (steps 01–06).
The shipped starter rows are *Sarcandra glabra* (``shade``), *Arabidopsis
thaliana* (``facultative``) and *Glycine max* (``sun``), all marked
``Manual annotation`` in the ``note`` column — replace or extend them with
your own annotations.

``config/cis_element_motif_library.xlsx`` (motif library)
----------------------------------------------------------

The universal CRE library used by step 06; edit through the GUI's
**Tools → Motif library...** popup.

* ``element`` — the CRE name (multiple rows with the same name are treated as
  sequence variants and summed per name);
* ``motif_sequence`` — IUPAC codes (``R Y M K S W B D H V N``) and ``(C/G)``
  notation are supported;
* ``functional_group`` — the classification used by the ecology figures
  (hormone / light / stress / development / core / ...).

Custom genomes
--------------

Two ways to bring your own genomes into the analysis:

Download from a URL list (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One download list per genome type, at the standard location
``Custom_genome_fa_gff/<genome_type>/Custom_genome_fa_gff_<genome_type>.xlsx``:

* ``species`` — species name; the downloaded file stem (spaces → underscores)
  and the species key for ecology labelling;
* ``genome_download_url`` — direct FASTA URL (``.fa/.fna/.fasta[.gz]``);
* ``annotation_download_url`` — direct GFF3 URL (``.gff/.gff3[.gz]``);
  http/https/file are accepted.

The folder decides the genome type, so the file itself has no type column
(existing lists with a plain ``Sheet1`` are read as-is). **Missing or empty
files are replaced by a header-only template** (``README`` + ``download_list``
sheets) on the first run, so nuclear / chloroplast / mitochondrial always
have a fillable, correctly named list; the chloroplast and mitochondrial
templates are also shipped in the bundle.

The optional global table ``config/custom_genome_download_list.xlsx`` (sheet
``download_list``, with a ``genome_type`` column) is still supported; rows
from both sources are merged and de-duplicated per stem.

The download runs as the first pipeline step (the ``custom`` scope, or
automatically before steps 01–06 when ``custom_download: "true"`` in
``quickstart_config.yml``). Files land in
``Custom_genome_fa_gff/<genome_type>/{fa,gff}/`` with **matching stems**, so
step 04 pairs them automatically. Re-runs skip already-complete files
(``skipped_complete``); delete a file to force a re-download.

Place files manually (offline)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Place your own genomes under ``Custom_genome_fa_gff/<genome_type>/``:

* FASTA in ``fa/``, GFF3 in ``gff/``;
* **basenames must match**, e.g. ``fa/Sarcandra_glabra.fa`` +
  ``gff/Sarcandra_glabra.gff3`` (extensions ``.fa/.fna/.fasta[.gz]`` and
  ``.gff/.gff3[.gz]`` are accepted);
* the basename (``Sarcandra_glabra``) is the species key matched against the
  ecology labels in the Label ecology step (06).

NCBI genomes need no manual placement: steps 01–03 download them into
``result/<type>/02_download/``.

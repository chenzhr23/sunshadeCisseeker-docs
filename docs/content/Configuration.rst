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
     - parallel workers for download/extraction
   * - ``cores``
     - ``"8"``
     - cores for the motif scan
   * - ``min_group_n``
     - ``"3"``
     - minimum species per ecology group for a statistical test
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
     - run the Custom genome download step (the ``config/custom_genome_download_list.xlsx`` URL list) before the per-genome steps; set ``"false"`` when you place custom files manually

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
   * - ``common_name``
     - no
     - common name (display only)
   * - ``genome_source``
     - no
     - ``NCBI`` / ``Custom`` / ``Both`` (record only)
   * - ``ecology``
     - yes
     - ``sun`` (heliophyte) / ``facultative`` / ``shade`` (sciophyte)
   * - ``note``
     - no
     - free-form note

Only species listed here enter the ecology comparison (steps 07–09);
unlabelled species still appear in the general analysis (steps 01–06).

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

Fill ``config/custom_genome_download_list.xlsx`` (created as a template on the
first run; sheet ``download_list``), one row per FASTA+GFF3 pair:

* ``organism`` — species name; the downloaded file stem unless ``file_stem`` is set;
* ``genome_type`` — ``nuclear_genome`` / ``chloroplast_genome`` /
  ``mitochondrial_genome`` (short forms accepted);
* ``genome_fasta_url`` / ``annotation_gff3_url`` — direct download URLs
  (``.fa/.fna/.fasta[.gz]`` and ``.gff/.gff3[.gz]``; http/https/file);
* ``assembly_accession`` (optional record), ``file_stem`` (optional stem
  override; if used, it is the species key for ecology labelling), ``notes``.

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

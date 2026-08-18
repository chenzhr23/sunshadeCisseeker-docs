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

Place your own genomes under ``Custom_genome_fa_gff/<genome_type>/``:

* FASTA in ``fa/``, GFF3 in ``gff/``;
* **basenames must match**, e.g. ``fa/Sarcandra_glabra.fa`` +
  ``gff/Sarcandra_glabra.gff3`` (extensions ``.fa/.fna/.fasta[.gz]`` and
  ``.gff/.gff3[.gz]`` are accepted);
* the basename (``Sarcandra_glabra``) is the species key matched against the
  ecology labels in the Label ecology step (06).

NCBI genomes need no manual placement: steps 01–03 download them into
``result/<type>/02_download/``.

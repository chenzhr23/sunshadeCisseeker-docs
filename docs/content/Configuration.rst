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
     - ``"2"``
     - skip genomes whose FASTA file exceeds this on-disk size (GB); empty or ``"0"`` = no limit. An oversized genome is recorded as ``skipped`` in the step-04 pair summary and never blocks the run (the default ``"2"`` skips oversized archives such as the ~2.7 GB *Tanacetum coccineum* genome). Editable in the GUI on the three genome pages and the Run Pipeline page. The ``2`` default applies only when the key is ABSENT from ``quickstart_config.yml`` (``run_all.sh`` applies it at launch); an explicitly empty value means no limit
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

One sheet per genome type — ``nuclear_genome`` / ``chloroplast_genome`` /
``mitochondrial_genome`` — each with one row per species; edit the sheets in
Excel/LibreOffice or through the GUI's **Tools → Ecology labels...** popup
(pick the sheet in the combo box, ``Reload``, edit, ``Save`` — the other
sheets are preserved).

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
     - ``sun`` (heliophyte) / ``shade`` (sciophyte)
   * - ``note``
     - no
     - free-form note (e.g. ``Manual annotation``)

Each genome type is labeled from its own sheet, so a species may carry
different labels in different compartments (or stay unlabeled in one).
Older single-sheet files (one sheet with the same three columns) still work
and apply to every genome type. The GUI's **Label ecology** page offers
checkboxes for the three genome types: unchecked types are skipped by the
labeling step. Only species listed here enter the ecology comparison (steps
07–09); unlabelled species still appear in the general analysis (steps
01–06).

``config/species_taxonomy.xlsx`` (optional; taxonomic strata, v1.8.0)
----------------------------------------------------------------------

Drop this file next to the other configs to make the Compare ecology
Box 4/G-box analysis additionally test the sun/shade signal **within
taxonomic strata** and with **fixed-effect models** — the reference-aligned
``box4_gbox_sunshade_results.xlsx`` sheets ``Order_stratified_tests`` /
``Family_stratified_tests`` / ``Genus_stratified_tests`` /
``Fixed_effect_models`` / ``Family_summary`` / ``Genus_summary`` and the
``box4_gbox_sunshade_relationship.pdf`` panels i/j/k. Without the file those
analyses are skipped.

.. list-table::
   :header-rows: 1

   * - Column
     - Required
     - Description
   * - ``species``
     - yes
     - species key matching the pipeline name exactly (spaces → underscores)
   * - ``order``
     - yes
     - taxonomic order, e.g. ``Malpighiales``
   * - ``family``
     - yes
     - taxonomic family, e.g. ``Euphorbiaceae``
   * - ``genus``
     - yes
     - taxonomic genus, e.g. ``Hevea``
   * - ``kingdom`` / ``phylum`` / ``tax_class``
     - no
     - higher ranks; reported in ``Species_annotated`` when present

Species are matched by name (the chromosome pipeline matches by NCBI
``tax_id``); a species missing from the table is marked ``unmatched`` and
stays out of the strata tests. Within-stratum Wilcoxon tests need ≥ 2 sun
AND ≥ 2 shade species in a stratum; fixed-effect models need ≥ 6 labeled
species with at least two strata — everything else is listed as
``insufficient_sun_or_shade`` / ``not_enough_data`` rather than dropped.

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
* ``taxid`` — **optional** NCBI taxonomy id of the species. When it matches
  the tax id of an NCBI genome of the same genome type, the NCBI genome is
  **preferred**: step 04 discards the custom pair (pair summary status
  ``skipped``, message ``custom genome discarded, NCBI preferred``) and no
  downstream analysis runs on it. **The custom download step fills this
  column in automatically** by looking the species name up on NCBI Taxonomy
  (rentrez; only an unambiguous single hit is written back — zero or
  multiple hits leave the cell empty, a ``.bak`` of the list is kept, and a
  failure to reach NCBI just logs a warning). Leave a cell empty to fall
  back to matching by the sanitized species name;
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

Outputs
=======

Everything is written under ``result/``. Each step produces a multi-sheet
XLSX workbook with a README sheet first, plus per-step ``.log`` files.

Per genome type
---------------

.. list-table::
   :header-rows: 1

   * - Location
     - Content
   * - ``result/<type>/01_species_info/<type>_info.xlsx``
     - NCBI metadata, taxonomy, per-species representative download URLs
   * - ``result/<type>/02_download/``
     - downloaded FASTA/GFF3 files, ``<type>_download_tasks.xlsx``, ``<type>_download_summary.xlsx``
   * - ``result/<type>/04_promoter/``
     - per-species promoter FASTA (``<species>__<accession>__<type>_promoter.fa``) + detail tables, combined FASTA, and three summary files: ``<type>_promoter_pair_summary.xlsx`` (one row per pair; the ``message`` column explains every per-pair outcome — ``ok (N promoters written)``, ``outputs up to date (skipped)``, ``missing input file``, ``corrupt GFF3 …``, ``bedtools getfasta failed …; used the streaming extractor``, ``excluded by max_genome_gb …``; a successful run also names its engine, ``C++ promoter_extract``), ``<type>_promoter_run_info.xlsx`` (parameters and totals, including ``excluded_pairs``) and ``<type>_promoter_summary.xlsx`` (``Pair_summary`` / ``File_sizes`` / ``Run_info`` sheets). The ``File_sizes`` sheet of ``<type>_promoter_summary.xlsx`` records each species' genome file sizes (``fasta_bytes`` / ``gff3_bytes`` / ``genome_total_bytes`` plus human-readable ``*_size`` columns), largest first.
   * - ``result/<type>/05_ciselement_input/``
     - ``all_species_<type>_ciselement_input.fa`` and ``all_species_<type>_id_map.xlsx``
   * - ``result/<type>/06_ciselement/<type>_ciselement_results.xlsx``
     - ``Element_stats`` / ``Species_element_counts`` / ``Species_summary``
   * - ``result/<type>/06_ciselement/<type>_ciselement_sites.xlsx``
     - full per-promoter × element site records
   * - ``result/<type>/06_ciselement/<type>_ciselement_summary.pdf``
     - six-panel CRE landscape figure

Ecology comparison outputs
--------------------------

.. list-table::
   :header-rows: 1

   * - Location
     - Content
   * - ``result/ecology_compare/06_label_ecology/species_ecology_assignment.xlsx``
     - ``Assignment`` / ``Group_counts`` / ``Unlabeled`` label tables (single label source for 07–09)
   * - ``result/ecology_compare/07_merge/ecology_master_dataset.xlsx``
     - ``Master_long`` / ``Species_summary`` / ``Element_species`` / ``Group_species_n``
   * - ``result/ecology_compare/08_statistics/ecology_differential_results.xlsx``
     - ``Kruskal_Wallis`` / ``Pairwise_Wilcoxon`` / ``Group_summary`` plus the Box 4 / G-box ratio analysis (``Box4_Gbox_species`` / ``Box4_Gbox_kruskal`` / ``Box4_Gbox_tests`` / ``Box4_Gbox_groups``), the v1.5.0 ratio-bin analysis (``Box4_Gbox_bin_by_group`` / ``Box4_Gbox_bin_tests`` / ``Box4_Gbox_bin_enrichment`` / ``Box4_Gbox_concentrated_bins`` / ``Box4_Gbox_relationship_tests`` / ``Box4_Gbox_stratified_tests`` / ``Box4_Gbox_fixed_effect_models``) and the publication-ready supplementary tables (``Publication_*``)
   * - ``result/ecology_compare/08_statistics/ecology_differential_volcano.pdf``
     - volcano of pairwise tests + top significant element boxplots
   * - ``result/ecology_compare/09_figures/ecology_figures.pdf``
     - single portrait A4 figure, panels (a) global differential landscape, (b) top differential elements with pairwise q-value brackets, (c) Box 4 / G-box ratio test, (d) Box 4 / G-box count decomposition
   * - ``result/ecology_compare/09_figures/box4_gbox_ratio.pdf``
     - portrait A4 multi-panel figure for the light-response hypothesis (ratio distributions, count balance, ratio-bin composition/enrichment, concentrated bins, raw bin count difference, optional order/family-stratified tests)
   * - ``result/ecology_compare/08_statistics/box4_gbox_sunshade_results.xlsx`` (v1.8.0)
     - reference-aligned Box 4/G-box × sun/shade workbook (same layout as the in-house chromosome pipeline's ``chromosome_promoter_Box4_Gbox_sunshade_results.xlsx``, one ``genome_type`` column added): ``Species_annotated`` (with ``tax_id`` + ``taxonomy_source``; v1.10.0) / ``Label_summary`` / ``Ratio_bin_by_label`` / ``Ratio_bin_enrichment`` / ``Concentrated_ratio_bins`` / ``Relationship_tests`` / ``Order_stratified_tests`` / ``Family_stratified_tests`` / ``Genus_stratified_tests`` / ``Fixed_effect_models`` / ``Family_summary`` / ``Genus_summary`` / ``Input_audit``. The taxonomy ranks come automatically from each type's ``01_species_info`` workbook (v1.9.0); species step 01 never saw are resolved from the custom-list taxid, the taxonomy cache and live NCBI lookups (v1.10.0); ``config/species_taxonomy.xlsx`` optionally overrides per species
   * - ``result/ecology_compare/08_statistics/taxonomy_cache.tsv`` (v1.10.0)
     - persistent taxid + taxonomy cache (species / tax_id / kingdom / phylum / tax_class / order / family / genus / source / resolved_on); resolved NCBI lookups are written back here and re-read on later runs, so re-runs stay offline and manually fixed rows are honoured
   * - ``result/ecology_compare/08_statistics/phylogenetic_tree.nwk`` (v1.11.0)
     - cached species tree (Open Tree of Life when available, otherwise an ultrametric classification tree from order/family/genus)
   * - ``result/ecology_compare/08_statistics/phylogenetic_comparative_results.xlsx`` (v1.11.0)
     - phylogenetic comparative results: ``Tree_species`` / ``Phylogenetic_signal`` (Blomberg K, Pagel lambda) / ``PGLS_models`` (OLS vs Brownian vs Pagel-lambda PGLS with AICc; ratio plus the two counts adjusted for log10 promoters) / ``phyloANOVA`` (999 Brownian simulations) / ``Input_audit``
   * - ``result/ecology_compare/09_figures/phylogenetic_comparative_figures.pdf`` (v1.11.0)
     - portrait A4 page: (a) tree with habitat-coloured tips, (b) ratio per habitat with phyloANOVA P, (c) PGLS coefficient forest, (d) phylogenetic signal, (e) Box 4 vs G-box count scatter, (f) delta-AICc model comparison; the tree panel is drawn as pure vector ggplot2 geometry
   * - ``result/ecology_compare/09_figures/phylogenetic_tree_figure.pdf`` (v1.11.0)
     - full-page vector tree figure, one page per genome type: ladderized phylogram with species tip labels (row spacing derived from the label size, so labels never overlap; page height grows with the tip count), order clade bars with vertical order names, a per-species log10(Box 4 / G-box) heat strip, and habitat-coloured tips (trees above 600 tips are deterministically subsampled for display)
   * - ``result/ecology_compare/08_statistics/within_clade_paired_contrasts.xlsx`` (v1.12.0)
     - phylogenetically paired within-clade contrasts: ``Summary`` (per genome type and clade level: paired-clade count, sun/shade-higher counts, mean/median difference, sign test and Wilcoxon signed-rank P for log10 ratio and the two log10 counts) / ``Per_genus`` / ``Per_family`` (one row per paired clade: sun and shade medians and their difference)
   * - ``result/ecology_compare/09_figures/within_clade_paired_contrasts.pdf`` (v1.12.0)
     - one A4 page per genome type: (a) per-genus waterfall of sun − shade differences, (b) per-family waterfall, (c) genus-level sun vs shade median scatter with the sign test / signed-rank summary in the subtitles
   * - ``result/ecology_compare/08_statistics/box4_gbox_sunshade_species_annotated.tsv`` (v1.8.0)
     - the annotated species table (Box 4 / G-box counts, ratio, ratio bin + sun/shade label + taxonomy ranks) as a flat TSV
   * - ``result/ecology_compare/09_figures/box4_gbox_sunshade_relationship.pdf`` (v1.8.0)
     - one page per genome type on the chromosome pipeline's 9.2 × 15.2 in canvas: panels (a) ratio violin/box/jitter, (b) motif count balance, (c) ratio-bin composition, (d) annotation coverage, (e) raw bin count difference, (f) raw labeled counts, (g) bin enrichment percentages, (h) concentrated bins, and (i/j/k) order- / family- / genus-stratified tests

Core metric
-----------

**``element_density`` = count / total_promoters × 1000** (sites per 1000
promoters) — the normalised metric used in every cross-group statistic, so
species with different gene numbers and the three compartments are directly
comparable. Related columns: ``total_sites`` (per species) and
``sites_per_gene`` (mean sites per gene that carries at least one site).

Very large tables are split into bounded parts
----------------------------------------------

R strings cannot exceed 2^31-1 bytes and openxlsx assembles a whole
workbook's text in memory, so a single XLSX cannot be written as one file
when the table holds either tens of millions of rows (nuclear promoter
details / id maps / site records) or fewer rows that carry long per-row
text. The large tables — ``<type>_promoter_detail.xlsx``,
``all_species_<type>_id_map.xlsx`` and ``<type>_ciselement_sites.xlsx`` — are
written automatically as **part files**, each part sized by row count and by
an estimated per-part character budget (sampled over the table), so the row
count is not the only limit:

* up to 1,000,000 rows (and within the per-part character budget): one
  classic workbook, exactly as before;
* beyond that: ``<name>.part01.xlsx``, ``<name>.part02.xlsx``, ... plus a
  small **index workbook** at the canonical ``<name>.xlsx`` path whose
  ``Parts`` sheet lists every part file and its row count. Join the parts
  (same columns, in order) to reconstruct the full table; stale parts from
  an earlier, larger run are removed automatically. Downstream steps (06, 07
  and the ecology comparison) read the parts back automatically.

The independent part files of the step-06 tables are written (and read back)
concurrently — up to 8 parts at a time, capped for shared-server memory
safety — which makes saving e.g. tens of millions of site records several
times faster; the part contents themselves are unchanged.

The same bound applies inside multi-sheet workbooks: sheets that would
exceed the 1,048,576-row Excel limit (e.g. ``Master_long`` in
``ecology_master_dataset.xlsx``) are split into ``<sheet>``, ``<sheet>_2``,
... — steps 08/09 read and recombine them automatically.

Logs
----

* ``log/sunshadeCisseeker_<scope>_<timestamp>_<pid>.log`` — the timestamped
  **master run log**. It holds the COMPLETE stdout+stderr of every pipeline
  step (``run_all.sh`` mirrors each step into it), so R errors such as
  ``Error: ID map is empty (no promoters to scan) …`` and external-tool
  messages always appear here — start troubleshooting with this file.
* each step also writes its own ``.log`` inside its result directory
  (``result/<genome_type>/<NN_step>/<NN>_<step>.log``). These carry the
  script's own progress lines (parameters, counts, warnings); stderr of
  external tools (gzip/samtools/bedtools) is recorded in step 04's pair
  summary ``message`` column instead.
* every parameter is recorded in the ``run_info`` sheet/table of each step.

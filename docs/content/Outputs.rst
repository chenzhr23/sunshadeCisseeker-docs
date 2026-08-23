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
     - per-species promoter FASTA (``<species>__<accession>__<type>_promoter.fa``) + detail tables, combined FASTA, pair summary. The pair summary and the summary workbook (``File_sizes`` sheet) record each species' genome file sizes: ``fasta_bytes`` / ``gff3_bytes`` / ``genome_total_bytes`` (on-disk sizes, plus human-readable ``*_size`` columns), largest first; ``Run_info`` carries the totals.
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
     - ``Kruskal_Wallis`` / ``Pairwise_Wilcoxon`` / ``Group_summary``
   * - ``result/ecology_compare/08_statistics/ecology_differential_volcano.pdf``
     - volcano of pairwise tests + top significant element boxplots
   * - ``result/ecology_compare/09_figures/ecology_figures.pdf``
     - PCA + heatmap + functional-group composition + key elements

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

* ``log/sunshadeCisseeker_*.log`` — the timestamped master run log;
* each step also writes its own ``.log`` inside its result directory;
* every parameter is recorded in the ``run_info`` sheet/table of each step.

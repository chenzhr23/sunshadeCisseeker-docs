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
     - per-species promoter FASTA (``<species>__<accession>__<type>_promoter.fa``) + detail tables, combined FASTA, pair summary
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

Logs
----

* ``log/sunshadeCisseeker_*.log`` — the timestamped master run log;
* each step also writes its own ``.log`` inside its result directory;
* every parameter is recorded in the ``run_info`` sheet/table of each step.

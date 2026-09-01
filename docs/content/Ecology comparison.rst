Ecology comparison
==================

The ecology comparison answers one question: **do the promoter
cis-regulatory elements of sun and shade plants differ
systematically?** The ecological assignment is a **manual annotation** from
``config/species_ecology_labels.xlsx``; the software never infers the groups.

Label ecology (step 06)
-----------------------

A standalone step between the per-genome pipelines and the comparison: it
reads ``config/species_ecology_labels.xlsx`` — one sheet per genome type
(``nuclear_genome`` / ``chloroplast_genome`` / ``mitochondrial_genome``;
older single-sheet files apply to every type) — and the 05 id maps of the
selected genome types, and writes ``species_ecology_assignment.xlsx``
(``Assignment`` / ``Group_counts`` / ``Unlabeled`` sheets) under
``result/ecology_compare/06_label_ecology/``. This assignment is the single
source of ecology labels for steps 07–09, so label changes only require
re-running this step and then 07–09. Unlabelled species are listed in the
``Unlabeled`` sheet and never enter the statistics.

The **Label ecology** GUI page offers checkboxes for the three genome types:
unchecked types are skipped (the run calls
``run_all.sh label_ecology --label-types=<comma list>``; the command line
accepts the same flag). Since v1.7.0 a species staged by **Tools → Run
local** (``result/local/<species>/<genome_type>/``) is labeled as part of
the genome type it was run under — its labels come from that type's sheet,
and a genome type whose only species are Run-local (no shared 05 output) is
still labeled. There is no ``local_genome`` sheet or pseudo-type.

Step 07 — merge
---------------

The **Compare ecology** GUI page offers the same genome-type checkboxes as
Label ecology (``run_all.sh ecology --ecology-types=<comma list>``): only
the checked types are merged, and steps 08–09 follow the types present in
the master table, so the comparison always matches the labeling selection.
Since v1.7.0 the isolated Run-local outputs under
``result/local/<species>/<genome_type>/`` are merged **into the genome type
they were run under**: a species present in both the shared set and the
local set is summed per element (counts and promoter totals scale together,
so the density metric is unchanged), and a genome type whose only outputs
are Run-local is still merged. Every staged species therefore joins the
comparison inside its physical type instead of a separate group.

1. For each selected genome type, merge the per-species element counts
   (``Species_element_counts``) with the per-species **total promoter
   number** (from the step-05 summary workbook's ``Per_species`` sheet —
   fast even for tens of millions of promoters).
2. Compute the normalised metric used everywhere downstream:

   ``element_density = count / total_promoters × 1000``

   (sites per 1000 promoters), so species with very different gene numbers
   and the three compartments are directly comparable.
3. Join the ``sun`` / ``shade`` label from the Label
   ecology assignment (by genome type + species).
4. Write the long-format ``Master_long`` table plus three auxiliary tables to
   ``ecology_master_dataset.xlsx``.

Step 08 — differential statistics
---------------------------------

For every "genome type × element" combination:

* **Filtering** — at least two ecology groups, each with ≥ ``min_group_n``
  species (default 3), must be present; otherwise the test is skipped.
* **Kruskal-Wallis** test across the two groups (overall difference).
* **Pairwise Wilcoxon** rank-sum test (sun vs shade) with the same
  group-size filter, plus
  ``log2FC = log2(median1 / median2)``.
* **Benjamini-Hochberg (BH)** correction of all p-values;
  ``bh_padj < 0.05`` is marked significant.

Outputs: ``Kruskal_Wallis``, ``Pairwise_Wilcoxon`` and ``Group_summary``
tables in ``ecology_differential_results.xlsx``, plus
``ecology_differential_volcano.pdf`` (volcano of pairwise tests + boxplots of
the top significant elements).

Publication-ready tables (v1.4.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same workbook additionally carries five export-ready sheets for a
paper's supplementary tables, with descriptive column names, rows ordered
by significance, rounded numerics and star-notation significance
(``*`` q < 0.05, ``**`` q < 0.01, ``***`` q < 0.001, ``n.s.``):

* ``Publication_Kruskal`` — Element, Functional group, Genome type,
  Kruskal-Wallis chi-squared, df, group/species counts, P value,
  BH-adjusted q, Significance;
* ``Publication_Pairwise`` — per group pair: medians of both groups,
  log2 fold change, Wilcoxon W, P value, BH-adjusted q, Significance;
* ``Publication_Groups`` — per-group medians/means and species counts;
* ``Publication_ratio_kruskal`` / ``Publication_ratio`` — the same layout
  for the Box 4 / G-box ratio tests.

The canonical sheets keep their full-precision machine-readable columns and
additionally carry ``q_value``, ``significance`` and formatted ``p_value_text``
/ ``q_value_text`` columns.

Box 4 / G-box ratio analysis (light-response hypothesis)
---------------------------------------------------------

To test whether **sun plants carry high Box 4 counts and low G-box counts**
while **shade plants show the opposite**, step 08 additionally computes, for
every labeled species, the ratio of the two Light-group elements of the motif
library (``Box 4`` motif ``ATTAAT`` and the ``G-box`` family of motifs):

``box4_gbox_ratio = Box 4 count / G-box count``

The same pipeline as the density tests — group-size filter,
Kruskal-Wallis, pairwise Wilcoxon with BH correction — is then run on the
ratio per genome type. Species without any G-box hit get an NA ratio and are
excluded from the tests (but remain visible in the per-species table).

* ``Box4_Gbox_species`` — per-species Box 4 count, G-box count, ratio and
  log2 ratio (per genome type);
* ``Box4_Gbox_kruskal`` — Kruskal-Wallis of the ratio across the ecology
  groups per genome type;
* ``Box4_Gbox_tests`` — pairwise Wilcoxon with BH correction and
  ``log2FC = log2(median1 / median2)``;
* ``Box4_Gbox_groups`` — per-group median/mean ratio and species counts;
* ``box4_gbox_ratio.pdf`` (step 09) — boxplots of the ratio per ecology
  group and genome type on a log10 scale.

A sun group median ratio clearly above the shade group median (significant
``bh_padj`` in the ``sun vs shade`` row) supports the hypothesis; the
direction and strength of the trend can be read directly from
``Box4_Gbox_groups``.

Step 09 — publication figures
-----------------------------

``ecology_figures.pdf`` is a single **portrait A4 figure** whose panels
follow a logical analytical progression (v1.4.0):

1. **(a) Global differential landscape** — a volcano plot of every pairwise
   test (log2 fold change vs ``-log10`` BH-adjusted q) with the significant
   tests highlighted and the significant/total count annotated.
2. **(b) Top differential elements** — boxplots of the up-to-six most
   significant elements (ordered by BH-adjusted q), with the pairwise
   Wilcoxon **q-value brackets and asterisks drawn on the panels** and the
   per-element Kruskal-Wallis P in each panel title.
3. **(c) Box 4 / G-box ratio test** — the per-species ratio per ecology
   group, with the ratio statistics (Kruskal-Wallis P, pairwise q brackets)
   drawn on the panel.
4. **(d) Box 4 / G-box count decomposition** — the per-species counts of the
   two elements, showing which of them drives the ratio, with per-element
   Kruskal-Wallis P values annotated.

``box4_gbox_ratio.pdf`` is a focused portrait A4 figure (v1.5.0) with the
ratio distributions, the Box 4 / G-box count balance, the ratio-bin
composition, the sun-vs-shade bin enrichment (Fisher tests with BH stars),
the concentrated bins and the raw bin count difference — plus order- and
family-stratified tests when ``config/species_taxonomy.xlsx`` exists.

Reference-aligned Box 4/G-box × sun/shade outputs (v1.8.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make the comparison directly comparable with the in-house chromosome
pipeline (``08_chromosome_promoter_Box4_Gbox_sunshade.r``), step 08 also
writes a second, reference-aligned workbook
``result/ecology_compare/08_statistics/box4_gbox_sunshade_results.xlsx``
with the same sheet layout as ``chromosome_promoter_Box4_Gbox_sunshade
_results.xlsx`` (one extra leading ``genome_type`` column, and species
matched by name). Every analyzed species gets a ``tax_id`` + taxonomy: the
per-type ``01_species_info`` NCBI tables are used first, then the per-type
custom download list ``taxid`` column, then the persistent
``result/ecology_compare/08_statistics/taxonomy_cache.tsv`` (v1.10.0), and
finally a live NCBI lookup whose results are cached back — with
``config/species_taxonomy.xlsx`` overriding per species):

* ``Species_annotated`` — per genome type × species: the resolved ``tax_id``
  and ``taxonomy_source`` (``config`` / ``ncbi_01_species_info`` /
  ``custom_download_list`` / ``taxonomy_cache`` / ``ncbi_lookup``),
  Box 4 / G-box counts, gene counts, ratio, log10 ratio, ratio status,
  ratio bin, total, the sun/shade label and the taxonomy ranks
  (``kingdom`` / ``phylum`` / ``tax_class`` when provided, ``order`` /
  ``family`` / ``genus``);
* ``Label_summary`` — per label: species counts plus ratio summary
  statistics (median / mean / Q25 / Q75 / median log10 / total counts);
* ``Ratio_bin_by_label`` / ``Ratio_bin_enrichment`` /
  ``Concentrated_ratio_bins`` — the distribution-level composition, the
  per-bin Fisher bin-vs-rest tests with BH adjustment, and the ranked
  concentrated bins;
* ``Relationship_tests`` — sun-vs-shade Wilcoxon, the binary-label Spearman
  correlation and the ratio-bin chi-square test, plus the fixed-effect
  model rows;
* ``Order_stratified_tests`` / ``Family_stratified_tests`` /
  ``Genus_stratified_tests`` — within-rank Wilcoxon tests (taxonomy comes
  automatically from each type's ``01_species_info`` workbook; the optional
  ``config/species_taxonomy.xlsx`` overrides per species);
* ``Fixed_effect_models`` — ``log10(ratio) ~ sunshade + order/family/genus``
  linear models adjusting for taxonomic structure;
* ``Family_summary`` / ``Genus_summary`` — order/family- and genus-level
  label coverage and ratio summaries;
* ``Input_audit`` — inputs, join-quality counts and headline p-values.

The matching ``box4_gbox_sunshade_species_annotated.tsv`` and the
``box4_gbox_sunshade_relationship.pdf`` figure (one 9.2 × 15.2 in page per
genome type; panels a–h mirror the chromosome figure and panels i/j/k show
the order- / family- / genus-stratified tested strata) complete the set.

Phylogenetic comparative analysis (v1.11.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The order/family/genus fixed-effect models correct taxonomy crudely, so
step 08 additionally runs proper **phylogenetic comparative methods** for
the Box 4 / G-box × light-habitat association:

* a species tree — **Open Tree of Life** via ``rotl`` (``tnrs_match_names``
  on the species binomials → ``tol_induced_subtree``) when installed and
  online, otherwise an ultrametric **classification tree** built from the
  resolved order/family/genus ranks; the tree is cached to
  ``result/ecology_compare/08_statistics/phylogenetic_tree.nwk``;
* **PGLS** (``nlme::gls`` with ``ape::corBrownian`` and a Pagel-lambda
  correlation estimated by maximum likelihood with lambda constrained to
  0–1) versus plain OLS for
  ``log10(Box4/G-box ratio)``, ``log10(Box 4 count)`` and
  ``log10(G-box count)`` — the count models adjust for log10 total
  promoters — with AICc model comparison; singular or failed fits (for
  example a constant covariate on a degenerate input) are skipped
  gracefully and reported in the log;
* **phylogenetic ANOVA** (``phytools::phylANOVA``, 999 Brownian
  simulations) of the ratio across sun/shade;
* **phylogenetic signal** (Blomberg K and Pagel lambda with tests) for the
  ratio and the two counts.

Everything lands in
``result/ecology_compare/08_statistics/phylogenetic_comparative_results.xlsx``
(``Tree_species`` / ``Phylogenetic_signal`` / ``PGLS_models`` /
``phyloANOVA`` / ``Input_audit``) and
``result/ecology_compare/09_figures/phylogenetic_comparative_figures.pdf``
(a portrait A4 page: tree with habitat-coloured tips, ratio per habitat
with the phyloANOVA P, the PGLS coefficient forest, the signal bars, the
count scatter and the delta-AICc comparison — fixed row heights keep every
panel complete and non-overlapping). The tree is drawn as pure vector
ggplot2 geometry, and a dedicated full-page figure
``result/ecology_compare/09_figures/phylogenetic_tree_figure.pdf`` shows
the same ladderized tree per genome type with species tip labels (the page
height is computed from the tip count, so labels never overlap), order
clade bars with vertical order names, a per-species log10(Box 4 / G-box)
heat strip, and habitat-coloured tips.

The block needs the R packages ``ape``, ``nlme`` and ``phytools`` (and
``rotl`` for the Open Tree of Life route); install them with
``conda install -c conda-forge r-ape r-nlme r-phytools r-rotl``. Without
them, with no taxonomy, or with fewer than six in-tree species, the block
is skipped with a warning and the rest of Compare ecology is unaffected.
When the block is skipped, the 08 log and the workbook README sheet state
the exact reason (which package is missing, whether the Box 4 / G-box
elements exist in the master table, whether the reference-aligned
annotation table is available).

Phylogenetically paired within-clade contrasts (v1.12.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To remove the lineage confounding *by design*, step 08 also pairs the
light-habitat comparison **inside clades**: every genus (and family) that
contains both sun- and shade-labeled species contributes one row with the
within-clade sun − shade difference of log10(Box 4 / G-box ratio). The
across-clade consistency of the direction is then tested with a two-sided
sign test and a Wilcoxon signed-rank test (the log10 Box 4 / G-box counts
are reported as supporting evidence). Results are written to
``result/ecology_compare/08_statistics/within_clade_paired_contrasts.xlsx``
(``Summary`` / ``Per_genus`` / ``Per_family``) and visualized in
``result/ecology_compare/09_figures/within_clade_paired_contrasts.pdf``
(one A4 page per genome type: per-genus and per-family waterfalls plus a
genus-level sun-vs-shade median scatter).

Ratio-bin analysis (v1.5.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Step 08 additionally bins every species' Box 4 / G-box ratio into nine
bins (``0``, ``0-0.5``, ``0.5-1``, ``1-2``, ``2-5``, ``5-10``, ``10-15``,
``>15`` and ``NA``; a species with G-box = 0 but Box 4 > 0 lands in
``>15``) and tests the sun/shade difference at the
*distribution* level: chi-square contingency tests (all groups and
sun-vs-shade), per-bin Fisher bin-vs-rest tests with BH correction,
percentages, odds ratios and sun/shade concentration ranking, plus a
Spearman trend test. The taxonomic strata for the within-order /
within-family / **within-genus** Wilcoxon tests and the fixed-effect linear
models come automatically from each genome type's ``01_species_info``
workbook (``species_summary`` sheet); an optional
``config/species_taxonomy.xlsx`` (``species`` / ``order`` / ``family`` /
``genus`` columns; optional ``kingdom`` / ``phylum`` / ``tax_class``)
overrides or supplements them per species.

Interpreting the results
------------------------

* ``Kruskal_Wallis`` — a small BH-adjusted p means the three ecology groups
  differ in that element's density.
* ``Pairwise_Wilcoxon`` — per group pair: ``median1``/``median2``,
  ``log2FC``, ``p_value``, ``bh_padj``/``q_value``, ``significant``
  (BH < 0.05) and the ``significance`` star column.
* The ``Publication_*`` sheets are the copy-paste-ready versions of those
  tables for a manuscript's supplementary tables.
* Raise ``min_group_n`` for stricter comparisons (fewer, more robust tests).
* ``element_density`` is a per-1000-promoter rate: values are comparable
  across species and compartments.

Reproducibility
---------------

* All parameters are recorded in each step's ``run_info`` sheet and ``.log``.
* Changing the motif library only affects steps 06–09: swap the library and
  rerun 06 for each genome type, then 07–09.
* Changing the ecology labels only requires re-running Label ecology (06)
  and then 07–09; the per-genome steps 01–06 are unaffected.

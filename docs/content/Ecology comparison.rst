Ecology comparison
==================

The ecology comparison answers one question: **do the promoter
cis-regulatory elements of sun, facultative and shade plants differ
systematically?** The ecological assignment is a **manual annotation** from
``config/species_ecology_labels.xlsx``; the software never infers the groups.

Label ecology (step 06)
-----------------------

A standalone step between the per-genome pipelines and the comparison: it
reads ``config/species_ecology_labels.xlsx`` — one sheet per genome type
(``nuclear_genome`` / ``chloroplast_genome`` / ``mitochondrial_genome`` and,
since v1.4.0, an optional ``local_genome`` sheet for the Run-local species;
older single-sheet files apply to every type) — and the 05 id maps of the
selected genome types, and writes ``species_ecology_assignment.xlsx``
(``Assignment`` / ``Group_counts`` / ``Unlabeled`` sheets) under
``result/ecology_compare/06_label_ecology/``. This assignment is the single
source of ecology labels for steps 07–09, so label changes only require
re-running this step and then 07–09. Unlabelled species are listed in the
``Unlabeled`` sheet and never enter the statistics.

The **Label ecology** GUI page offers checkboxes for the three genome types
plus **Local genome** (v1.4.0): unchecked types are skipped (the run calls
``run_all.sh label_ecology --label-types=<comma list>``; the command line
accepts the same flag). *Local genome* labels the species staged by
**Tools → Run local** (``result/local/<species>/``) as the pseudo genome
type ``local_genome``; give it labels by adding a ``local_genome`` sheet to
the label workbook. Without the flag, only the three physical types are
labeled.

Step 07 — merge
---------------

The **Compare ecology** GUI page offers the same genome-type checkboxes as
Label ecology, including **Local genome** (``run_all.sh ecology
--ecology-types=<comma list>``): only the checked types are merged, and
steps 08–09 follow the types present in the master table, so the comparison
always matches the labeling selection. *Local genome* merges the isolated
Run-local outputs under ``result/local/<species>/`` into the master table as
``local_genome`` rows — every staged species joins the comparison alongside
the NCBI/custom types.

1. For each selected genome type, merge the per-species element counts
   (``Species_element_counts``) with the per-species **total promoter
   number** (from the step-05 summary workbook's ``Per_species`` sheet —
   fast even for tens of millions of promoters).
2. Compute the normalised metric used everywhere downstream:

   ``element_density = count / total_promoters × 1000``

   (sites per 1000 promoters), so species with very different gene numbers
   and the three compartments are directly comparable.
3. Join the ``sun`` / ``facultative`` / ``shade`` label from the Label
   ecology assignment (by genome type + species).
4. Write the long-format ``Master_long`` table plus three auxiliary tables to
   ``ecology_master_dataset.xlsx``.

Step 08 — differential statistics
---------------------------------

For every "genome type × element" combination:

* **Filtering** — at least two ecology groups, each with ≥ ``min_group_n``
  species (default 3), must be present; otherwise the test is skipped.
* **Kruskal-Wallis** test across the three groups (overall difference).
* **Pairwise Wilcoxon** rank-sum tests (sun vs facultative, facultative vs
  shade, sun vs shade) with the same group-size filter, plus
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

``box4_gbox_ratio.pdf`` is a focused two-panel portrait A4 figure (panels
c + d) dedicated to the light-response hypothesis. Panels share one
colourblind-safe palette (sun orange, facultative blue, shade green), Arial
typography, and the asterisk thresholds are restated in each figure caption.
Count/density/ratio axes use a pseudo-log scale (linear below 1) so zero
values stay visible.

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

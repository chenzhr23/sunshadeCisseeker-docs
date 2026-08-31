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
accepts the same flag).

Step 07 — merge
---------------

The **Compare ecology** GUI page offers the same genome-type checkboxes as
Label ecology (``run_all.sh ecology --ecology-types=<comma list>``): only
the checked types are merged, and steps 08–09 follow the types present in
the master table, so the comparison always matches the labeling selection.

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

Step 09 — publication figures
-----------------------------

A four-panel figure (``ecology_figures.pdf``):

1. **PCA** of species × (compartment × element density) profiles
   (``log1p``-transformed, scaled) — do the three ecology groups separate
   along PC1/PC2?
2. **Heatmap** of the 40 most variable elements, species rows ordered by
   hierarchical clustering, values z-scored.
3. **Functional-group composition** — stacked fractions of element density
   per ecology group, using the ``functional_group`` column of the motif
   library (hormone / light / stress / development / core / ...).
4. **Key elements** — boxplots of the six elements with the smallest
   Kruskal-Wallis p-values.

Interpreting the results
------------------------

* ``Kruskal_Wallis`` — a small BH-adjusted p means the three ecology groups
  differ in that element's density.
* ``Pairwise_Wilcoxon`` — per group pair: ``median1``/``median2``,
  ``log2FC``, ``p_value``, ``bh_padj``, ``significant`` (BH < 0.05).
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

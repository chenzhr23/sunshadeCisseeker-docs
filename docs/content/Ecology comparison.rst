Ecology comparison
==================

The ecology comparison answers one question: **do the promoter
cis-regulatory elements of sun, facultative and shade plants differ
systematically?** The ecological assignment is a **manual annotation** from
``config/species_ecology_labels.xlsx``; the software never infers the groups.

Step 07 — merge and label
-------------------------

1. For each of the three genome types, merge the per-species element counts
   (``Species_element_counts``) with the per-species **total promoter
   number** (from the 05 id map).
2. Compute the normalised metric used everywhere downstream:

   ``element_density = count / total_promoters × 1000``

   (sites per 1000 promoters), so species with very different gene numbers
   and the three compartments are directly comparable.
3. Join the ``sun`` / ``facultative`` / ``shade`` label by species name.
   Unlabelled species stay in the summary tables but never enter the
   statistics.
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
* Changing the ecology labels only affects steps 07–09 (the id maps store the
  label at step 05, so rerun 05–09 for label changes to take effect).

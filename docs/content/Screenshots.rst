Screenshots
===========

This page walks through every part of the window, with a screenshot and a
short explanation for each.

Main window and sliding pages
-----------------------------

The window is organised as six sliding pages. Each analysis page runs the
matching pipeline scope and streams the full log live; **Run** starts it and
**Stop** interrupts it. A live progress bar above each log shows the overall
position (e.g. "Step 4/6 — promoter extraction — 46%"), and every started run
prints its run id as the first log line
(``run started | id=... | scope=...``) — each page tracks only its own run, so
several pages can run at the same time. The three genome pages additionally
have an **"NCBI API key (optional)" input** next to Run/Stop (it writes the
``ncbi_api_key`` entry of ``quickstart_config.yml``). The menu bar on top
(File / Tools / Global / Help) holds the parameter editor, the two XLSX table
editors and the remaining functions.

.. figure:: ../_static/screenshots/01-introduction.png
   :width: 1360

   The **Introduction** page: the workflow overview and the six pages of the
   window (Nuclear / Chloroplast / Mitochondrial / Label ecology / Compare
   ecology).

.. figure:: ../_static/screenshots/02-nuclear-genome.png
   :width: 1360

   The **Nuclear genome** page runs nuclear steps 01–06: NCBI species metadata
   and FASTA+GFF3 downloads (01–03, complete-safe with instant fail on dead
   URLs and bounded rate-limit probes), incremental promoter extraction (04),
   the NCBI + custom merge (05) and the universal cis-element scan (06).
   Results land under ``result/nuclear_genome/``.

.. figure:: ../_static/screenshots/03-chloroplast-genome.png
   :width: 1360

   The **Chloroplast genome** page runs the same six steps for the chloroplast
   compartment; step 04 is circular-aware, so promoters can wrap across the
   replication origin. Results land under ``result/chloroplast_genome/``.

.. figure:: ../_static/screenshots/04-mitochondrial-genome.png
   :width: 1360

   The **Mitochondrial genome** page runs the same six steps for the
   mitochondrial compartment. Results land under ``result/mitochondrial_genome/``.

.. figure:: ../_static/screenshots/05-label-ecology.png
   :width: 1360

   The **Label ecology** page (cross-genome step 06): assigns the
   ``sun`` / ``facultative`` / ``shade`` labels from
   ``config/species_ecology_labels.xlsx`` to the merged NCBI+custom datasets
   of all three genome types and writes
   ``result/ecology_compare/06_label_ecology/species_ecology_assignment.xlsx``
   (``Assignment`` / ``Group_counts`` / ``Unlabeled`` sheets) — the single
   label source for the comparison. Run it after the genome pages and before
   Compare ecology; re-run only this page after editing the label table.

.. figure:: ../_static/screenshots/06-compare-ecology.png
   :width: 1360

   The **Compare ecology** page runs steps 07–09: merge the three datasets
   into the ecology master table (07), differential statistics —
   Kruskal-Wallis plus pairwise Wilcoxon with Benjamini-Hochberg correction
   (08) — and the publication figures (09). It requires the Label ecology page
   to have run first. Results land under ``result/ecology_compare/``.

Menu-bar popup windows
----------------------

The three parameter/table editors open as popups from the **Tools** menu.

.. figure:: ../_static/screenshots/07-run-pipeline.png
   :width: 1040

   **Tools → Run pipeline…** — edit ``promoter_len``, ``workers``, ``cores``,
   ``min_group_n`` and the optional NCBI API key, tick the parts to run
   (nuclear / chloroplast / mitochondrial / ecology comparison, NCBI download
   steps, Custom genome download), pick a scope (all / nuclear / chloroplast
   / mitochondrial / custom / label_ecology / ecology) and start or stop the
   run. The same values are stored in ``quickstart_config.yml`` and are used
   by the command line identically.

.. figure:: ../_static/screenshots/08-ecology-labels.png
   :width: 1040

   **Tools → Ecology labels…** — the table editor for
   ``config/species_ecology_labels.xlsx``: add or remove species, assign each
   species its ``sun`` / ``facultative`` / ``shade`` label, reload or save.
   Changes take effect after re-running the Label ecology page.

.. figure:: ../_static/screenshots/09-motif-library.png
   :width: 1040

   **Tools → Motif library…** — the table editor for
   ``config/cis_element_motif_library.xlsx``: every CRE searched by the
   universal scan (06) with its IUPAC ``motif_sequence`` and
   ``functional_group`` classification (hormone / light / stress / development
   / core / …). On Linux the scan runs the bundled C++ Aho-Corasick backend
   (``bin/cre_scan``); motifs are matched as literal fixed text, and an R
   ``stringi`` fallback covers hosts without the binary.

Other windows and hints
-----------------------

* **File** — Save parameters, Open results folder (``result/``), Quit.
* **Global → Configuration** — the "Softwares checking and configuration"
  dialog, the same check the ``sunshadeCisseeker check`` command runs.
* **Help → About** — version, bundle path and attribution.

Every result mentioned above can also be produced headlessly with the command
line (``sunshadeCisseeker run <scope>``); the GUI and the CLI edit the same
configuration files and write the same outputs.

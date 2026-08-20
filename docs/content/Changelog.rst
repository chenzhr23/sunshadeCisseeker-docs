Changelog
=========

1.3.7 — content-aware part sizing for large tables
--------------------------------------------------

* **Fixed: step 05 crashed writing** ``*_id_map.xlsx`` **with** ``Error in
  stri_join ... CHARSXPs are limited to 2^31-1 bytes`` even though the
  table was written as bounded part files. Parts were sized by row count
  alone (1,000,000 rows each), but a part can hit the 2 GB string ceiling
  with far fewer rows when the rows themselves carry long text. Parts are
  now also sized by an estimated per-part character budget (sampled over
  the table), so any combination of row count and row width stays well
  below the limit.
* Circular promoter coordinates are now written in the compact
  ``start..end`` form (the same format the linear pipeline always used)
  instead of a per-position ``1;2;3;...`` list that cost roughly 7 bytes
  per base — the actual cause of the oversized id-map and detail rows.
  The information is identical; the columns are only smaller.

1.3.6 — bounded large-table writing and truthful progress bars
--------------------------------------------------------------

* **Fixed: runs died at the very end with** ``Error in stri_join ...
  CHARSXPs are limited to 2^31-1 bytes`` **when one giant XLSX was written**
  (nuclear step 04 combine, step 06 site records). openxlsx assembles a whole
  workbook's text in memory and R strings cannot exceed 2^31-1 bytes, so
  tables with tens of millions of rows could not be saved as one file. The
  large tables (``*_promoter_detail.xlsx``, ``*_id_map.xlsx``,
  ``*_ciselement_sites.xlsx``) are now written as **bounded part files** with
  an index workbook at the canonical path, and oversized sheets (e.g.
  ``Master_long``) are split and recombined automatically — see
  :doc:`Outputs`.
* **Fixed: after a run failed, the page's progress bar showed a stale
  mid-run value** (the reported 50% / 0% while the runs had already exited
  with an error). The bar is now monotonic within a run, and when the run
  ends it always shows a definitive terminal state: full green "Finished",
  full red "Failed (exit code N)", full orange "Stopped by user".
* Progress parsing now uses the most recent percentage / ``[n/total]`` after
  each step marker (previously the oldest one, which froze the bar at a
  stale mid-step fraction), and the last known step is carried forward when
  its marker scrolls out of the log tail.
* Step 04's incremental skip now keys on a separate per-pair extraction
  version marker, so an update that only changes the final combine does not
  force a full re-extraction of every genome on the next run.

1.3.5 — independent parallel pages
----------------------------------

* **Fixed: pages started together showed "100% finished" while the other
  runs were still going.** The run bookkeeping files were keyed by the GUI
  process id, so simultaneous runs (Nuclear + Chloroplast + Mitochondrial)
  overwrote each other's pid/status/output files: every page displayed the
  first run's exit state, the logs interleaved, and Stop killed whichever
  run had written the pid file last. Every started run now gets its own
  files ``/tmp/sunshadecisseeker-gui/run-<scope>-<pid>-<time>-<seq>.pid`` /
  ``.status`` / ``.out``, and the run id is the first line of each page's
  log (``run started | id=... | scope=...``). Logs, progress bars and
  Run/Stop buttons are now strictly per page.
* **Fixed: a run that died without an exit status was reported as
  success.** A run killed by a signal or the out-of-memory killer (common on
  shared servers) left no status file, which the GUI read as "exit code 0".
  Such runs are now reported as an abnormal end (exit code 137).
* **Fixed: per-run log collisions under ``log/``.** Two scopes started in
  the same second shared one timestamped log file; the name now includes the
  scope and the process id
  (``log/sunshadeCisseeker_<scope>_<date>_<pid>.log``).

1.3.4
-----

* Live Qt progress bar on every analysis page ("Step 4/6 — promoter
  extraction — 46%"), parsed from the pipeline's own step markers and
  percentage lines — no pipeline changes required.
* Standalone **Label ecology** step (cross-genome step 06) with its own GUI
  page: the NCBI+Custom merge (step 05) stays label-free, and labelling can
  be redone at any time without re-running the genome pipeline.
* Faster organelle promoter extraction — constant-time interval mathematics
  for circular genomes (byte-identical to the previous per-base walk) — plus
  a streaming, bounded-memory combiner for the per-pair tables and FASTA
  files, so very large runs no longer exhaust memory at the final combine.
* Hardened download retries in steps 02/03: deterministic HTTP 4xx errors
  fail immediately, NCBI 429 rate limiting is probed a bounded number of
  times (``--rate-retries=``), and every kept file passes a FASTA/GFF3
  format check before being accepted.

Earlier versions
----------------

Initial releases: the six-step per-genome pipeline (NCBI species metadata,
FASTA+GFF3 download, promoter extraction, NCBI+Custom merge, universal CRE
scan), the cross-genome ecology comparison (steps 06–09), the Qt 5.15
psiFinder-style desktop interface, and the one-shot conda installer.

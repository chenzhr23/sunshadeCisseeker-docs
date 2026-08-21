Changelog
=========

1.3.14 — drop the unused NCBI_genome_fa_gff directory
------------------------------------------------------

* **Cleanup: the bundle no longer ships the ``NCBI_genome_fa_gff/``
  directory.** No pipeline step ever reads it - NCBI genomes are downloaded
  by steps 01–03 into ``result/<type>/02_download/`` and step 04 takes its
  NCBI pairs from the step-02 task table - so the empty directory only
  caused confusion (the manual even claimed steps 01–03 fill it, which was
  wrong). The manual and bundle README/INSTALL have been corrected.
* Re-installing still **preserves** an existing ``NCBI_genome_fa_gff/`` in
  case an old installation holds manually placed files there; nothing is
  deleted, the directory is simply no longer created or shipped.

1.3.13 — per-genome-type Custom download lists
----------------------------------------------

* **New: one download list per genome type.** The Custom download step now
  reads ``Custom_genome_fa_gff/<type>/Custom_genome_fa_gff_<type>.xlsx``
  (standardized columns ``species | genome_download_url |
  annotation_download_url``; the folder decides the genome type, so one file
  per nuclear / chloroplast / mitochondrial type). Existing files in that
  shape - including a plain ``Sheet1`` - are read as-is, so current lists
  keep working unchanged; rows are merged with the optional global table
  ``config/custom_genome_download_list.xlsx`` and de-duplicated per stem.
* **Missing or empty per-type files are replaced by a header-only template**
  (``README`` + ``download_list`` sheets with the three standardized
  columns) in the standard location, so every genome type always has a
  fillable, correctly named list after the first run. The chloroplast and
  mitochondrial templates are also shipped in the bundle.
* Downloaded files still land in ``Custom_genome_fa_gff/<type>/{fa,gff}/``
  with matching stems (species name with spaces replaced by underscores),
  and step 04 picks the pairs up automatically - no analysis-side changes
  are needed.

1.3.12 — no more orphaned workers after an interrupted run
----------------------------------------------------------

* **Fixed: interrupted runs could leave R worker processes behind**, keeping
  result files open so that deleting or replacing the installation failed
  with ``rm: cannot remove .../.nfsXXXX...: Device or resource busy`` (NFS
  silly-rename files). The pipeline launcher (``run_all.sh``) now cleans up
  its whole process tree on interrupt: it traps INT/TERM/HUP and stops every
  R step, PSOCK worker and helper it started.
* A **watchdog** is armed for GUI-launched runs: if the GUI window is closed,
  crashes, or loses its connection while the pipeline runs, the closing of
  the output pipe triggers the same tree-wide stop — workers are no longer
  orphaned and no ``.nfs`` files are left pinning the installation directory.
* Terminal runs (``bash run_all.sh ...`` with Ctrl+C) keep working as
  before, and normally finished runs are unaffected (the watchdog disarms
  itself on completion). The GUI's Stop button already performed a
  process-group kill; the new logic covers every other way a run can die.

1.3.11 — Custom genome download from a URL list
-----------------------------------------------

* **New: Custom genomes can now be downloaded by the pipeline.** Fill
  ``config/custom_genome_download_list.xlsx`` (one row per FASTA+GFF3 pair:
  ``organism``, ``genome_type``, ``genome_fasta_url``,
  ``annotation_gff3_url``; optional ``assembly_accession`` / ``file_stem``),
  and the new first pipeline step downloads the files into
  ``Custom_genome_fa_gff/<type>/{fa,gff}/`` with matching file stems, so step
  04 picks them up automatically — no manual file placement needed.
* The step reuses the hardened download machinery of steps 02/03 (resume from
  partial files, bounded retries with backoff, HTTP 429 handling, error-page
  detection, fork-free PSOCK worker pool with launch pacing) and skips
  already-complete files on re-run (``skipped_complete``); duplicate file
  stems for one genome type are refused with a clear ``failed`` record
  instead of overwriting.
* The config table is created as an empty template (README + header row) on
  the first run when it is missing; a row may also carry only one of the two
  URLs (the missing file is recorded as ``failed``).
* **Pipeline integration:** a new ``custom`` scope runs only this download;
  with the new ``custom_download: "true"`` key in ``quickstart_config.yml``
  (checkbox in the GUI) the download also runs automatically before the
  per-genome steps (01–06) of every run. The progress panel understands the
  new step in both ``all`` and ``custom`` scopes.
* The previous manual placement under ``Custom_genome_fa_gff/`` keeps working
  unchanged; both sources are merged by step 04 as before.

1.3.10 — fork-free parallel workers for the download/extraction steps
-----------------------------------------------------------------------

* **Fixed: long runs could abort with the** ``mcfork`` **error**
  ``unable to fork, possible reason: Cannot allocate memory`` **after hours
  of work** (observed in step 02 at ~75% of downloads). Steps 02/03/04
  previously ran their worker pool with fork-based ``mcparallel``; once the
  parent R process had grown on a shared, cgroup/process-count-limited
  server, ``fork()`` started failing and killed the whole run. The pools now
  use a **PSOCK worker cluster** (separate ``Rscript`` processes started at
  the beginning of the run, so new workers never depend on the parent's
  address size).
* The launch pacing (one download launch every 0.4 s, ~2.5 requests/s vs.
  NCBI's 3/s limit), the 429 rate-limit backoff, the
  ``ok/skip/fail`` accounting and every output file, column and status
  value are unchanged. Re-running after an abort still skips every
  already-complete file (``skipped_complete``), so the failed chloroplast
  run only downloads the remaining ~25%.
* **Graceful degradation:** if the worker cluster cannot be started (e.g.
  the server forbids spawning child processes) or a worker dies mid-run, the
  remaining tasks are processed sequentially in the running session with a
  clear warning — the run always finishes instead of aborting.
* The same protection was added to the remaining fork-based paths: the
  step-06 R fallback scan (unused when ``bin/cre_scan`` runs, which remains
  the default on Linux) and the parallel part-file xlsx reader/writer now
  fall back to sequential processing with a warning instead of failing.

1.3.9 — step 06 cis-element scan rewritten as a C++ program
------------------------------------------------------------

* **Step 06 (cis-element identification) is now performed by a bundled C++
  program** (``bin/cre_scan``) instead of the R stringi loop. The scanner
  builds an Aho-Corasick multi-pattern automaton from the motif library and
  reads the combined FASTA **once** for the whole motif set (previously one
  full pass per motif), splitting the file across threads (up to 64,
  defaulting to the machine's core count minus one as configured by the
  pipeline). On multi-core servers this makes the scan several times faster
  and removes the largest CPU cost of the step.
* The counting semantics are **bit-identical** to the R backend: literal
  fixed matching (degenerate IUPAC motifs keep their 1.3.0–1.3.8 behaviour),
  non-overlapping occurrences counted greedily per record, repeated
  (element, motif) rows counted with their multiplicity, and the per-record
  site table sorted by promoter then element (the R backend now applies the
  same deterministic sort, so both backends produce identical tables).
* The R stringi backend is kept as an automatic fallback and is used when
  ``bin/cre_scan`` is absent or not executable; the ``scan_method`` note in
  the results workbook records which backend ran. Results are identical
  either way (verified against the R reference on synthetic data plus 200
  randomized adversarial cases).
* ``cre_scan`` is built with the same conda toolchain and glibc 2.17 target
  as the GUI, links only libc/libm/libpthread, and ships pre-built inside
  the bundle — no new server-side dependencies.

1.3.8 — faster step 06 cis-element scan
---------------------------------------

* Step 06 (cis-element scan) is faster with byte-identical results: the
  per-record FASTA assembly is now a single vectorized pass per batch
  instead of an R loop over every record, header detection uses a
  vectorized prefix test, and the default read batch is larger (500,000
  lines, still tunable with ``--batch-lines=``).
* The step-06 id map and site-records tables are read and written with
  bounded part files **in parallel** (up to 8 concurrent parts, capped for
  shared-server memory safety); every part is produced by the exact same
  writer call as before, so the files contain the same data in the same
  order.
* Step 06 keeps only the columns it needs before joining the (potentially
  hundreds of millions of rows) hit table, lowering peak memory and join
  time.
* **Fixed: step 06 could abort in the PDF stage with**
  ``factor level [N] is duplicated`` **when a species has genomes from both
  NCBI and Custom.** The per-species summary plots now aggregate to species
  level first; datasets without such duplicates produce the same plots as
  before.
* **Note (no behaviour change):** the motif library's degenerate IUPAC
  motifs are currently detected as exact and matched as literal text (same
  as 1.3.0–1.3.7); this release preserves that behaviour bit-for-bit. A
  future release can switch them to true IUPAC matching; get in touch if
  you want that.

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

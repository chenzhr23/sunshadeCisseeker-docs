Changelog
=========

1.3.60 — installer: R-free fast self test
------------------------------------------

* The installer's step 3/3 now runs the new **``--selftest-fast``** mode of
  the interface: it never starts R, so the probe finishes in seconds
  regardless of how slow ``Rscript`` / ``openxlsx`` start on the host (the
  config round-trips remain verified in step 2/3, which now checks both
  workbooks in ONE ``Rscript`` process instead of two). ``timeout 120``
  still bounds the probe.
* The full ``--selftest`` mode (with the R round-trips, used by tests and
  development) is unchanged.

1.3.59 — installer self test: bounded and non-destructive
----------------------------------------------------------

* The installer's **3/3 GUI self test (offscreen)** is now wrapped in a
  hard ``timeout 240`` and pins ``SUNSHADE_RSCRIPT`` to the R interpreter the
  dependency check just verified, so a stalled probe can no longer hang
  ``install.sh`` (a slow network filesystem could previously keep it busy
  indefinitely on the large per-genome-type label table).
* The Ecology labels and Motif library self tests now round-trip their
  **save through a temp copy** (local temp dir, ``--keep`` semantics): the
  real config workbooks are never rewritten by the installer — the previous
  plain save would have dropped the chloroplast/mitochondrial label sheets
  of a three-sheet ``species_ecology_labels.xlsx``.

1.3.58 — per-genome-type ecology labels + Label ecology checkboxes
------------------------------------------------------------------

* ``config/species_ecology_labels.xlsx`` now uses **one sheet per genome
  type** — ``nuclear_genome`` / ``chloroplast_genome`` /
  ``mitochondrial_genome`` (columns unchanged: ``species | ecology |
  note``) — so each compartment carries its own label table and a species
  may be labeled differently (or stay unlabeled) per compartment. Older
  single-sheet files keep working and apply to every type.
* The **Label ecology** GUI page offers three **genome-type checkboxes**
  (Nuclear / Chloroplast / Mitochondrial, all checked by default): the
  labeling step only processes the checked types
  (``run_all.sh label_ecology --label-types=<comma list>``; the command
  line accepts the same flag), and its output and run info record exactly
  the analyzed types.
* The **Tools → Ecology labels…** editor matches the new layout: a
  **Genome type sheet** combo selects the sheet to edit, ``Save`` preserves
  every other sheet, and older single-sheet files load their first sheet
  automatically.

1.3.57 — robustness: gene-name sanitizing + self-healing step 04
----------------------------------------------------------------

* A GFF3 attribute value carrying raw **tab or newline characters** (for
  example ``Name=trnK-UUU <TAB> trnK`` in a custom annotation) used to be
  written verbatim into the per-pair detail table and the promoter FASTA
  headers. ``data.table::fread`` then stopped early on such a row and
  silently dropped every following row — the merged detail/id-map tables
  lost hundreds of thousands of records and step 06 aborted with a
  ``cre_scan record count mismatch``. The C++ tools (``promoter_extract``,
  ``promoter_merge``) and the R fallbacks now collapse every run of
  tabs/newlines inside gene names, gene IDs and the original FASTA header to
  a single space and strip the surrounding spaces, identically in both
  implementations (byte-parity is preserved).
* Step 04 now **validates cached outputs before skipping** a pair: the
  per-pair FASTA headers must be free of raw tabs and the detail workbook
  must be readable and hold at least as many rows as the FASTA has records.
  Pairs whose cached outputs fail either check are re-extracted
  automatically (reported as ``cached ... (pair regenerated)`` in the pair
  summary), so upgrading an existing install heals the affected files on the
  next run without any manual cleanup.
* The step 04 C++ fast path proves the per-pair detail TSV row structure
  before parsing it, and the step 06 mismatch error now explains the cause
  and the remedy instead of just printing the counts.

1.3.56 — server-scale hardening: bounded C++ merge + C++ xlsx writer
----------------------------------------------------------------------

* Step 05's C++ merge writes the id map as **bounded part files** (500,000
  rows each, plus a manifest) instead of one giant TSV: the R side reads the
  parts one at a time, so the 10M+ record id maps of a server-scale run no
  longer blow up memory (the previous single ``fread`` fell back to the slow
  R merge on the 24.8M-promoter dataset).
* New C++ tool **``bin/xlsx_fast``**: a minimal spec-conformant XLSX writer
  (streamed worksheet XML + zlib zip) used automatically by every big table
  write (04 detail, 05 id map, 06 sites, pair summaries) with openxlsx as
  the fallback. Cell values and column types are identical to openxlsx
  (verified cell-by-cell, including NA-vs-empty-string and boolean
  columns); on the benchmark it writes 200,000 rows in 0.7 s — the 6M-row
  chloroplast sites table that took ~70 minutes now takes a few minutes,
  and the same applies to the 24.3M-row nuclear detail table.
  ``SUNSHADE_NO_CXX=1`` disables both new tools.

1.3.55 — documentation update: screenshots of the new Tools dialogs
---------------------------------------------------------------------

* The headless screenshot capture now also renders the **Run local** dialog
  and the **Custom genome lists** editor, and the Screenshots page documents
  both (``10-run-local.png``, ``11-custom-genome-lists.png``), together with
  the updated menu-bar description (Run local, Custom genome lists,
  ellipsized dialog entries).

1.3.54 — shipped custom download lists carry the new header
-------------------------------------------------------------

* The per-type custom download lists bundled in the archive
  (``Custom_genome_fa_gff/<type>/Custom_genome_fa_gff_<type>.xlsx``) are
  upgraded to the new header ``species | taxid | genome_download_url |
  annotation_download_url`` (the ``taxid`` cells start empty and are filled
  in automatically by the step-01 lookup). Upgrading an existing install
  keeps the on-disk lists untouched — run the Custom download step once to
  add the column there.

1.3.53 — automatic NCBI taxid lookup for custom species
--------------------------------------------------------

* The Custom genome download step (01) now fills the ``taxid`` column of the
  per-type download lists **automatically**: species names with an empty
  taxid are looked up on NCBI Taxonomy through rentrez, and only an
  unambiguous single hit is written back (zero or multiple hits stay empty
  and fall back to name-based de-duplication; a ``.bak`` of each list is
  kept, the README sheet is preserved, and NCBI being unreachable only logs
  a warning). ``SUNSHADE_TAXID_MOCK_FILE`` provides an offline name→taxid
  table (used by the new end-to-end test).

1.3.52 — menu-label consistency (dialog-opening items carry an ellipsis)
-------------------------------------------------------------------------

* ``Check environment`` and ``Global → Configuration`` open dialog windows,
  so they now follow the standard menu convention and read
  ``Check environment...`` / ``Configuration...`` — every Tools/Global item
  that opens a window for further input carries the ``...`` ellipsis.

1.3.51 — GUI editor for the custom genome download lists
---------------------------------------------------------

* New **Tools → Custom genome lists...** table editor for the three per-type
  custom download lists (``Custom_genome_fa_gff/<type>/Custom_genome_fa_gff_<type>.xlsx``,
  ``download_list`` sheet): edit ``species`` / ``taxid`` / the two URL columns
  per genome type (a selector switches nuclear / chloroplast /
  mitochondrial), add or remove rows, and save back — the workbook's README
  sheet is preserved. The XLSX helper now supports loading a named sheet and
  saving a single sheet in place (``--keep``); both are covered by a new
  round-trip test.

1.3.50 — new feature: species de-duplication (NCBI preferred over Custom)
---------------------------------------------------------------------------

* When a Custom genome (a species the user provided a download link for) is
  the **same species** as an NCBI genome of the same genome type, the NCBI
  genome is now **preferred and the custom pair is discarded**: it is not
  extracted, merged or scanned. The decision is made in step 04 by the
  **NCBI tax id** when both sides carry one (steps 02 now record ``tax_id``
  in the download tasks; the custom download list gained an optional
  ``taxid`` column) and otherwise falls back to matching the sanitized
  species name — the rule used is named in the pair-summary ``message``
  (``custom genome discarded, NCBI preferred``, status ``skipped``), the
  matching pairs are logged, and the run info records
  ``deduplicated_pairs``. Custom files stay on disk untouched.

1.3.49 — C++ promoter engines: ~2x faster steps 04–06, byte-identical outputs
------------------------------------------------------------------------------

* Two new C++ accelerators replace the two biggest R hotspots of the
  per-genome pipeline (profiled on a 60-species / 120,000-promoter benchmark;
  on the server's 17.5-million-promoter dataset the saving is proportionally
  larger):
  - **``bin/promoter_extract``** — one process per pair replaces the
    gzip/samtools/bedtools spawns, the R GFF3 parse and the per-gene interval
    loop of step 04 (plain and gzipped FASTA, linear and circular genomes).
  - **``bin/promoter_merge``** — one pass renumbers and merges every per-pair
    FASTA and emits the id-map/per-file tables of step 05 (the previous
    biggest bottleneck: ~49 s → ~5 s in the benchmark, ~10×).
* Both tools produce **byte-identical outputs** to the R implementations
  (verified against the bedtools path AND the pure-R streaming path for
  linear, gzipped and circular fixtures, including the id map and detail
  tables). When a tool is missing or fails, the pipeline transparently falls
  back to the previous R path (``SUNSHADE_NO_CXX=1`` disables both
  accelerators entirely).
* Benchmark (WSL2, 60 species × 4 Mb × 2000 genes, 243 MB FASTA, 4 workers):
  steps 04–06 total **97.4 s → 47.6 s (2.05×)** with identical results;
  step 06 remains scan-bound on the C++ Aho-Corasick backend + the XLSX
  packaging.

1.3.48 — Run local becomes a truly isolated single-species analysis
--------------------------------------------------------------------

* ``Tools → Run local...`` now stages the two files into
  ``result/local/<species>/input/`` and writes every 04–06 output under
  ``result/local/<species>/<type>_genome/NN_step/`` — the **same file names
  and column layouts** as a normal run, so the tables merge row by row with
  other results. The shared ``result/<type>`` trees, the NCBI task lists and
  ``Custom_genome_fa_gff`` are **never read or modified**: only the chosen
  species is analyzed, other species are not re-extracted, and later normal
  runs are unaffected. Re-running the same species starts from a clean
  workspace.
* Steps 04–06 honor the new ``SUNSHADE_LOCAL_SPECIES/FA/GFF/OUT``
  environment contract (single-pair input + redirected output root), driven
  by the same ``SUNSHADE_RUN_LOCAL=1`` flag as before.
* New e2e verifies the isolation: exactly one pair processed, outputs in
  the local tree, shared result and custom directories untouched, size cap
  lifted.

1.3.47 — fix: installer verifies the old installation is really gone
---------------------------------------------------------------------

* On NFS, wiping the previous installation can partially fail: a running GUI
  keeps ``lib/fonts`` open and killed workers leave unremovable ``.nfsXXXX``
  files. The installer used to continue anyway, and ``cp -a`` then nested the
  new bundle inside the half-removed directory (the installed tree was
  broken — missing ``script/shell``, missing GUI binary). The installer now
  **verifies the removal**: when anything survives it prints the surviving
  entries, explains the likely cause (running GUI / ``.nfs*`` leftovers on
  NFS), restores the preserved user data and stops instead of installing a
  broken tree. Re-running after closing the GUI and deleting the ``.nfs*``
  files completes normally. Covered by a new installer e2e that simulates an
  undeletable directory.

1.3.46 — new feature: Tools → Run local (single-species analysis)
------------------------------------------------------------------

* New **Tools → Run local...** dialog: enter a species name, pick a local
  genome **FASTA** + annotation **GFF3**, tick the genome type(s) to analyze
  (**nuclear / chloroplast / mitochondrial** — at least one must be ticked)
  and press Run. The files are staged into
  ``Custom_genome_fa_gff/<type>/{fa,gff}/<species>.<ext>`` and the standard
  steps **04–06** run for each ticked type, sequentially, with the live log
  shown in the dialog (Stop interrupts the run and the queue).
* Local runs set ``SUNSHADE_RUN_LOCAL=1`` for ``run_all.sh``: NCBI and the
  download steps are forced off and the **genome-size cap is lifted** for
  the explicitly chosen file, regardless of ``quickstart_config.yml`` — a
  large local genome is analyzed instead of silently skipped. The staged
  species becomes part of the custom set and is reused by later runs.
* New end-to-end test covers the whole flow (staging → 04–06 → results)
  including the size-cap lift.

1.3.45 — fix: installer heals environments that dropped individual files
--------------------------------------------------------------------------

* The broken-environment repair now verifies that R actually RUNS with every
  package loadable, not just that ``Rscript`` exists. When individual files
  have vanished from the environment (e.g. the ``sed`` that R's wrapper
  needs, after an NFS/quota incident) a reinstall of r-base alone does not
  restore them — the installer now escalates to a force-reinstall of every
  package the environment contains (enumerated explicitly, from the local
  package cache) and only gives up with a disk/NFS hint if R is still broken
  after that.
* The mirror-reachability probes are wrapped in ``timeout`` so a wedged
  resolver can never hang the installer.
* The repair e2e now covers both layers: a missing ``Rscript`` and a missing
  tool link (``sed``) with R present but unrunnable.

1.3.44 — one command fixes a broken R environment; verified end-to-end
------------------------------------------------------------------------

* ``bash install.sh`` now handles the full broken-environment cycle on its
  own: it detects a missing ``Rscript``, **force-reinstalls r-base and all R
  packages automatically**, then hard-verifies the fix — if conda reports
  success but ``Rscript`` is still missing (e.g. the filesystem dropped the
  package links), the install fails with a disk/quota hint instead of
  finishing with a pipeline that cannot start. No manual conda commands
  needed. The repair path is covered by a new end-to-end test that clones a
  working environment, deletes its ``Rscript``, and runs the installer.

1.3.43 — fix: installer repairs a broken R installation automatically
------------------------------------------------------------------------

* If conda's metadata says the environment is complete but ``Rscript`` itself
  is missing (a broken or partially-linked transaction, e.g. an interrupted
  package update), a plain ``conda install`` reports "all requested packages
  already installed" and leaves the environment unusable. The installer now
  detects this state and **force-reinstalls r-base and the R packages**
  instead, and the dependency self-check names the exact condition.

1.3.42 — fix: installer resolves the conda environment through conda itself
-------------------------------------------------------------------------------

* The dependency self-check and the post-install verification used to derive
  the environment's path from the conda binary's directory — which breaks
  when the environment lives in a non-default ``envs_dirs`` location
  (``Rscript not found at .../miniconda3/envs/...``). The installer now asks
  conda for the real ``R.home()`` (``conda run -n <env> Rscript``) and puts
  the resolved bin directory first on PATH for every check, so both the
  auto-skip decision and the live verification work regardless of where the
  environment physically lives. When the environment cannot be resolved at
  all, the installer prints the full ``conda env list`` for diagnosis.

1.3.41 — fix: installer conda-CLI compatibility + self-diagnosing dependency check
-------------------------------------------------------------------------------------

* The conda ``install``/``create`` calls no longer pass
  ``--repodata-timeout-secs`` (rejected as an unrecognized argument by
  conda 26.x, which aborted the repair before it even reached the network).
  Unreachable sources are still bounded by the installer's own quick probes.
* The dependency self-check now PRINTS exactly which R package is missing
  (or that Rscript itself is missing) instead of failing silently.
* bedtools/samtools are now treated as the optional accelerators they are:
  when they are absent the installer skips the network step anyway (the
  pipeline falls back to its built-in streaming extractor), with a note.
* (v1.3.40) When the environment already satisfies every requirement the
  installer skips the dependency step entirely; unreachable conda mirrors
  fail fast with ``-s`` guidance; and the GUI self-test no longer rewrites
  ``quickstart_config.yml``.

1.3.40 — fix: installer no longer hangs on unreachable conda mirrors
------------------------------------------------------------------------

* When the target conda environment already satisfies every requirement
  (R, all R packages, bedtools/samtools/gzip), the installer now **skips the
  dependency step entirely** — re-installs on a fully provisioned machine
  never touch the network and can no longer hang on unreachable mirrors.
* If a network source is needed but both ``conda.anaconda.org`` and the TUNA
  mirror are unreachable, the installer now fails fast (a quick 10-second
  probe) with instructions to re-run with ``-s`` instead of letting conda
  retry repodata downloads for minutes.
* ``conda install/create`` runs are bounded with ``--repodata-timeout-secs``,
  and the failure messages point to the ``-s`` escape hatch.
* The installer's GUI self-test no longer rewrites
  ``quickstart_config.yml`` (it writes a throwaway probe file instead), so an
  upgrade can never replace your edited configuration with bundle defaults.

1.3.39 — complete audit pass: nothing fails silently, logs tell the whole story
----------------------------------------------------------------------------------

* **The master run log now captures everything.** ``run_all.sh`` pipes every
  step through ``tee -a`` into ``log/sunshadeCisseeker_<scope>_<timestamp>_<pid>.log``,
  so the full stdout+stderr of each R step — including ``stop()`` errors such
  as ``Error: ID map is empty (no promoters to scan)`` — is always on disk,
  even when the GUI window or terminal is gone. A failed step also logs
  ``ERROR: the step failed (exit N)`` with the reason above it.
* **External tools report their own errors.** Step 04 captures the stderr of
  gzip/samtools/bedtools and writes a trimmed snippet into the pair-summary
  ``message`` column (e.g. ``bedtools getfasta failed (exit 1: Unrecognized
  parameter ...); used the streaming extractor``), instead of discarding it.
  Step 06 does the same for ``cre_scan``.
* **Worker failures carry their real message.** Parallel workers now pass the
  actual error text into the summary (``worker error: could not find function
  ...``) instead of an opaque "worker error".
* **Pair statuses reflect reality.** Step 04 counts the records actually
  written to each per-pair FASTA and reports ``ok (N promoters written)`` /
  ``ok (N of M requested ...)`` / ``no_promoters_written`` — a failed
  extraction can never again be reported as "ok".
* **Step 04 parallel path repaired** — the per-pair detail workbook writer was
  missing from the worker export list (every parallel pair failed after doing
  its extraction); the xlsx helpers are now exported.
* **The first motif in the library is no longer silently dropped** in the R
  fallback scan (a ``cut()`` boundary made motif row 1 land in an ``NA``
  group that ``split()`` discarded).
* **Nuclear step 01 URL pre-validation repaired** — batch results were
  unnamed, so the validation cache was never filled and the step could abort;
  results are now named by URL and looked up defensively.
* **Downloads react to HTTP status codes again** — the regex only matched
  ``error: NNN`` while curl reports ``HTTP error NNN.``, leaving the fatal-4xx
  and 429 rate-limit branches dead code.
* **Partial samtools indexes can no longer silently drop genes** — step 04
  verifies every GFF contig is present in the ``.fai`` (missing contigs fall
  back to the R length scan with a note).
* **Ecology merge fixed** — ``Species_summary`` (one row per species × source)
  is aggregated by species before joining, so species with both an NCBI and a
  Custom assembly no longer double every row and inflate the statistics.
* **Taxonomy fetch failures are logged** (with the error text) instead of
  silently marking whole batches ``missing_or_failed``.
* **Installer hardened further:** the bundle copy is error-checked, the backup
  directory name carries the installer PID and rejects collisions, a prefix
  inside the bundle directory (and vice versa) is refused up front, dangling
  symlinks are backed up too, and the ``-s`` skip-deps path warns when
  Rscript is missing.
* **GUI:** an unwritable ``quickstart_config.yml`` now shows a warning and
  aborts the launch (previously the run silently used stale parameters); a
  possible null header item in the xlsx table export is guarded.
* **Resume logic hardened:** skip checks require non-empty outputs; download
  renames verify success; completeness checks no longer error on empty
  decompressed content; part-file readers validate row counts against the
  index.
* **Process handling:** GUI runs make ``run_all.sh`` a session/group leader so
  one group kill stops the whole tree (including R workers reparented after a
  crash), the GUI Stop button forwards into that group, and the dead stdin
  watchdog code was removed.
* **Test coverage for the previously untested paths.** New end-to-end tests
  force the bedtools path with gzipped genomes (the exact NCBI scenario), run
  the whole ecology chain (label → merge → statistics → figures) with
  under-sized groups, verify that R error text lands in the master log, and
  exercise the installer's preserve/rollback paths.

1.3.38 — fix: installer backup can no longer destroy user data
--------------------------------------------------------------------

* The installer used to back user data up into a ``mktemp`` directory (often
  ``/tmp``, a different filesystem): moving ``result/`` and the genome
  directories was a GB-scale cross-device copy, and if a later item then
  failed to copy, the abort path **deleted the backup directory** — together
  with the data already moved into it. The backup now lives **next to the
  installation directory** (``<prefix>.bak.<timestamp>``) on the same
  filesystem, so every move is an atomic rename: it cannot run out of space,
  a failed item rolls everything back before anything is deleted, and the
  backup is only removed after a fully successful restore. The backup
  location is printed, and it can be deleted once the run is verified.
* (v1.3.37) Step 04 bedtools extraction fixed: the FASTA path for
  uncompressed genomes was replaced by ``NULL`` so ``bedtools getfasta`` got
  no ``-fi`` value and silently wrote empty promoter FASTA files (step 05
  then merged 0 promoters and step 06 stopped with "ID map is empty"). The
  path is only swapped when a temp decompressed file exists, ``-name``
  headers are parsed with a leading-integer regex, and a failed bedtools run
  falls back to the built-in streaming extractor instead of writing an empty
  file.

1.3.37 — fix: bedtools promoter extraction silently produced empty output
-----------------------------------------------------------------------------

* Step 04 calls ``bedtools getfasta`` for plain (uncompressed) FASTA files.
  A refactoring slip left ``idx_fa <- tmp_fa`` outside the gzip branch, so
  the FASTA path was replaced by ``NULL`` for every non-gzipped genome:
  the ``-fi`` argument vanished from the command line, bedtools failed with
  "Unrecognized parameter", its error output was discarded, and the pair was
  reported as "ok" while writing an **empty** promoter FASTA. Step 05 then
  merged 0 promoters and step 06 stopped with "ID map is empty". The path is
  now only swapped when a temp decompressed file actually exists.
* ``bedtools getfasta -name`` output headers are parsed with a
  leading-integer regex instead of assuming a bare ``>1`` header (bedtools
  writes ``>1::chr1:0-4(+)``), so the re-alignment by record id works with
  every bedtools version.
* Fail-safe: if bedtools exits non-zero or returns no usable records, the
  pair now falls back to the built-in streaming extractor (recorded in the
  pair summary) instead of silently writing an empty FASTA.
* Added a regression test that forces the bedtools code path — the previous
  test environment had no bedtools on PATH, which is why the suite missed
  this. Empty per-pair FASTA files left by v1.3.36 re-extract automatically
  on the next run; no manual cleanup is needed.

1.3.36 — robustness sweep across the whole pipeline
--------------------------------------------------------------------

* A full audit of every step fixed the following issues:

  * **Downloads now truly resume** — a failed attempt previously deleted the
    partial ``.part`` file, so every retry restarted multi-GB genomes from
    byte 0; partial data is now kept (only genuine NCBI error pages are
    discarded) and ``resume_from`` actually resumes.
  * **Step 03 retries work in parallel** — the retry workers were missing one
    helper from the worker export list, so every parallel retry task failed
    with "worker error"; the helper is now exported.
  * **Compressed files are content-checked, not just integrity-checked** — a
    validly-gzipped NCBI error page can no longer pass as a genome; the first
    decompressed line must look like FASTA/GFF3, and a missing ``gzip`` binary
    no longer forces needless re-downloads.
  * **A gzip-decompression failure inside a worker now falls back to the
    streaming extractor** (the warning was previously sent to a logger the
    workers do not have, which aborted the pair); the fallback is recorded in
    the pair's summary message instead.
  * **bedtools output is re-aligned by record id** — a record skipped by
    bedtools can no longer shift the sequence/header pairing.
  * **The id map is built in bounded chunks** (no more full 17 M-row matrix in
    memory), and the combined detail table merges with ``data.table`` for
    lower peak memory.
  * **Empty tables round-trip correctly** — the "no data" placeholder is no
    longer read back as a bogus data row, and step 06 stops with a clear
    message when the id map is empty instead of a misleading record-mismatch
    error.
  * **Ecology figures: row-wise element selection** (no more spurious
    type × element combinations in the top-element panels), groups smaller
    than ``min_group_n`` no longer enter the statistics, per-species counts
    are used instead of row counts, NA densities can no longer crash the PCA,
    and single-species inputs degrade to an explanatory empty panel instead
    of aborting.
  * **Motif library validation** — empty ``element`` / ``functional_group``
    values are rejected, and an element mapped to several functional groups
    warns and uses the first (previously its hits were silently duplicated).
  * **install.sh can no longer destroy user data on a failed upgrade** — the
    old tree is deleted only after the backup is verified, and a failed
    restore keeps the backup instead of deleting it.
  * **GUI polish** — clearing "Max genome size (GB)" now really persists
    "no limit"; saving parameters keeps user-added config keys; run-pipeline
    slot connections are created once; the launcher QProcess is reset between
    runs; the quit-watchdog uses static storage; ``run_all.sh`` parses the
    config robustly (CRLF, indented keys, comments) and defaults
    ``max_genome_gb`` to ``2`` only when the key is absent; the stall
    detector no longer aborts when worker PIDs are unavailable; the bounded
    xlsx part files are actually written/read in parallel (``parallel::``
    prefix was missing).

1.3.35 — fix: several excluded genomes crashed step 04's summary
------------------------------------------------------------------

* **Fixed: step 04 crashed right after the last pair when more than one
  genome was excluded by the size cap** (``Error in if (!file.exists(path))
  ... the condition has length > 1``). The summary builder passed the whole
  vector of excluded FASTA paths to a single-path helper; ``file_bytes`` is
  now vectorized, so any number of excluded pairs is recorded correctly. The
  per-pair outputs are written before this point, so a crashed run loses
  nothing — a re-run skips the finished pairs and only redoes the summary.

1.3.34 — default genome-size cap skips Tanacetum
------------------------------------------------

* **The default ``max_genome_gb`` is now ``2``** (was ``10``), so a fresh
  install skips any genome whose FASTA file exceeds 2 GB on disk — in
  particular the ~2.7 GB *Tanacetum coccineum* archive that previously
  stalled step 04 for hours. The GUI fields (three genome pages + Run
  Pipeline window) are pre-filled with the new default; raise, lower or clear
  the value at any time (empty/``0`` = no limit). Note: an upgrade preserves
  an already-existing ``quickstart_config.yml``, so on an existing
  installation set the field to ``2`` (or the desired threshold) once in the
  GUI.

1.3.33 — genome-size cap in the GUI
-----------------------------------

* **The genome-size upper limit is now a GUI setting.** The three genome pages
  (Nuclear / Chloroplast / Mitochondrial) and the Run Pipeline window each
  show a **Max genome size (GB)** input next to the other parameters; it is
  pre-filled with the default ``10`` and saved to ``quickstart_config.yml``
  when the field loses focus and before every run starts. Genomes whose FASTA
  file exceeds the value (on-disk size, GB) are skipped by step 04 as
  ``skipped`` and never block the run; clear the field (or set ``0``) for no
  limit.

1.3.32 — genome-size cap replaces the exclusion list
----------------------------------------------------

* **The species exclusion list is replaced by a configurable genome-size
  cap.** The ``max_genome_gb`` key in ``quickstart_config.yml`` skips every
  pair whose genome FASTA file exceeds that on-disk size (GB; empty or
  ``"0"`` = no limit): oversized pairs are recorded as ``skipped`` in the
  step-04 pair summary (message ``excluded by max_genome_gb …``) and the run
  always completes — a single oversized genome can no longer stall or crash
  it. The compared size is the FASTA file's on-disk size (the same
  ``fasta_bytes`` shown in the summary's ``File_sizes`` sheet). Set the key
  once (e.g. ``"2"``) instead of maintaining a species blacklist; lower or
  clear it to process those genomes again.

1.3.31 — species exclusion list for step 04
-------------------------------------------

* **New: an optional species exclusion list bypasses problematic genomes.**
  ``config/species_exclude_list.xlsx`` (sheet 1, column ``species``) lists
  species keys that step 04 must skip: matching pairs are recorded in the
  pair summary as ``skipped`` (message ``excluded by
  config/species_exclude_list.xlsx``) instead of being processed, so a single
  oversized/problematic genome can no longer stall or crash the whole run —
  the run always finishes. The file is optional (missing/empty = nothing
  excluded); remove a row to process that species again. The shipped file
  pre-excludes ``Tanacetum_coccineum`` (oversized genome) as an example, and
  the run log/summary report the excluded count.

1.3.30 — ecology labels: species / ecology / note only (English)
------------------------------------------------------------------

* ``config/species_ecology_labels.xlsx`` is simplified to three columns —
  ``species``, ``ecology`` and ``note`` (``common_name`` and ``genome_source``
  are no longer needed) — and all shipped text is English: the starter rows
  are *Sarcandra glabra* (``shade``), *Arabidopsis thaliana*
  (``facultative``) and *Glycine max* (``sun``), each noted ``Manual
  annotation``. The label reader only ever used the two required columns, so
  existing files with the old extra columns keep working unchanged. Note: an
  upgrade preserves an already-existing labels file on the server — edit it
  through **Tools → Ecology labels…** or in Excel to match.

1.3.29 — starter ecology labels: Sarcandra / Arabidopsis / Soybean
-----------------------------------------------------------------------

* The shipped ``config/species_ecology_labels.xlsx`` now contains only the
  three study species: **Sarcandra** (*Sarcandra glabra*, ``shade``),
  **Arabidopsis** (*Arabidopsis thaliana*, ``facultative``) and **Soybean**
  (*Glycine max*, ``sun``); the ``note`` column is filled with
  ``manually annotated`` instead of the old placeholder text. The common
  names live in the ``common_name`` column while ``species`` keeps the Latin
  pipeline key (the label matcher compares sanitized names, so the key must
  stay Latin).
  Note: an upgrade preserves an already-existing labels file on the server —
  edit it through **Tools → Ecology labels…** or in Excel to match.
* The GUI now bundles **Noto Sans CJK SC**, so CJK text (the labels
  table's common names and notes included) renders correctly even on hosts
  without any system CJK fonts.

1.3.28 — ultra-large genome performance
---------------------------------------

* **Step 04 now processes ultra-large genomes (multi-GB FASTA, hundreds of
  thousands of contigs) dramatically faster.** The hot paths were rewritten
  with vectorized ``stringi`` C-level calls: FASTA length scanning and
  interval extraction process whole chunks instead of one line per R loop
  iteration, gene attribute parsing runs one regex pass per key instead of
  one per gene, and 80-character FASTA wrapping no longer loops per output
  line. The BED file for the bedtools path is written with
  ``data.table::fwrite`` (seconds instead of minutes for millions of rows).
* **Fixed: promoter sequences could be attached to the wrong gene header.**
  The streaming extractor sorted its internal request order but returned the
  sequences in that sorted order, so whenever the request order differed from
  sorted order the sequence/header pairing in the output FASTA could shift.
  Sequences are now returned in the original request order (verified
  byte-for-byte against the genome substring), and chunk-boundary handling
  was hardened (adjacent-line spans, a trailing FASTA header exactly at a
  chunk edge).
* The ``samtools`` index (``.fai``) next to a custom FASTA is now reused on
  re-runs while it is still fresh (and regenerated automatically when the
  FASTA changed), so indexing a huge genome happens only once.
* A gzip-to-temp decompression failure now logs a clear warning and falls
  back to the streaming extractor instead of failing silently.

1.3.27 — per-species genome file sizes
--------------------------------------

* **New: every genome type now records the file size of each species' genome
  files.** Step 04 adds ``fasta_bytes`` / ``gff3_bytes`` /
  ``genome_total_bytes`` (on-disk sizes of the genome FASTA, the GFF3
  annotation and their sum) plus human-readable ``fasta_size`` / ``gff3_size``
  / ``total_size`` columns to the per-species pair summary, and the step's
  summary workbook gains a dedicated **``File_sizes``** sheet (one row per
  species, largest genomes first). The ``Run_info`` sheet also reports the
  totals, and the final log line prints them (e.g. ``FASTA 1.20 TB + GFF3
  45.61 GB``).

1.3.26 — no more false stall aborts on giant genomes
----------------------------------------------------

* **Fixed: step 04 could abort at the very end of a run ("no worker finished
  for over 2400 s") even though the workers were fine.** Some pairs
  legitimately take longer than the stall timeout (multi-GB FASTA
  decompression plus ``samtools faidx`` plus ``bedtools`` extraction of tens
  of thousands of genes). The stall check now confirms the hang first: it
  only aborts when the worker processes **and their children** have also
  stopped consuming CPU; workers that are still computing are reported (with
  the names of the running pairs) and the run simply continues. Truly stuck
  workers are still aborted, now with a list of the pairs that were in
  flight.

1.3.25 — refreshed documentation screenshots
--------------------------------------------

* The Screenshots page now shows the current interface: every capture was
  regenerated with the built-in offscreen screenshot mode at the same pixel
  sizes as before. The new images include the live progress bar, the NCBI
  API key input on the three genome pages, and the updated Introduction
  workflow diagram.

1.3.24 — documentation refresh
------------------------------

* The bundled guides (``INSTALL.md``, the analysis manual and the workflow
  reference) now describe the current behavior: the parallel step-01 URL
  validation, the crash-proof GFF3 handling and stall detection in step 04,
  the NCBI API key input on the genome pages, the never-lost live log, and
  the printed log locations (panel log copy, master run log path on success
  and failure).

1.3.23 — updated Introduction workflow diagram
-----------------------------------------------

* The Introduction page's workflow diagram now matches the current pipeline:
  the **Custom genome download pre-step** (per-type URL lists) is shown
  feeding the three genome types, step 05 no longer mentions ecology labels
  (they are assigned by the standalone Label ecology step), and the
  cross-genome row shows **label ecology → 07 merge → 08 differential
  statistics → 09 figures**.

1.3.22 — crash-proof GFF3 parsing and a clearer run record
----------------------------------------------------------

* **Fixed: step 04 could crash the whole run with a segfault (exit 139).**
  A single corrupt GFF3 (binary NUL content that still passes the download
  checks) made ``data.table::fread``'s C parser segfault: the worker crashed,
  the pool's sequential fallback then read the same file and killed the main
  R process. GFF3 files are now stream-checked for binary garbage before any
  parser sees them, and the fast parse path reads a normalised
  exactly-9-column awk stream instead of arbitrary lines. A corrupt file
  fails its pair cleanly (clear message) and is **removed automatically** so
  step 02 re-downloads it on the next run — the run itself always continues.
* **Fixed: after a successful run the genome pages could leave the log panel
  scrolled onto blank space** (the finished view looked empty until you
  scrolled back up). The final scroll now runs after the layout has settled,
  so the panel always ends on the last log line.
* **The run record is now easy to find:** every finished run prints in the
  panel itself the panel log path (a copy is kept under
  ``log/gui_<run-id>.log``), the master run log path and the per-step log
  location; the master log path is now printed even when a run ends
  abnormally (previously only successful runs printed it).

1.3.21 — fast, visible representative-assembly selection (step 01)
------------------------------------------------------------------

* **Fixed: Nuclear step 01 "[3/5] Selecting representative assemblies" looked
  frozen at 0% and could run for hours.** The step validated every candidate
  FASTA/GFF3 download URL one at a time (up to ~5000 HEAD requests, each
  bounded by a 20-second timeout) and never updated its progress bar, so the
  GUI showed 0% the entire time while the process slowly checked URLs. All
  candidate URLs are now validated once, up front, in parallel (the same
  fork-free PSOCK worker pool used by the download steps, 32 URLs per batch),
  and both that pass and the selection loop now report progress. The step
  takes minutes instead of hours and stays visibly alive throughout.

1.3.20 — complete log updates on the genome pages
--------------------------------------------------

* **Fixed: the genome pages froze their log while another page was on
  screen.** Log lines produced while a page was not visible were silently
  dropped, so switching back showed stale progress. New lines are now
  buffered (bounded) and flushed when the page is shown again, including
  before the final "process finished" line; the status-bar mode refreshes on
  the next show as well. The progress bar itself always kept updating.

1.3.19 — NCBI API key field on the genome pages
-----------------------------------------------

* **New: the Nuclear / Chloroplast / Mitochondrial genome pages each have an
  "NCBI API key (optional)" input** next to the Run/Stop buttons. The key is
  written to ``quickstart_config.yml`` when the field loses focus and before
  every run starts (the Run Pipeline window keeps its own field; both edit
  the same configuration entry). A free NCBI API key raises the request limit
  from 3 to 10 requests/second and removes the HTTP 429 throttling on shared
  IPs.

1.3.18 — patient NCBI rate-limit handling in step 01
----------------------------------------------------

* **Fixed: step 01 could abort after five quick retries during an NCBI HTTP
  429 storm** on a shared IP without an API key. The NCBI queries now retry
  up to 10 times with much longer waits when the error is rate-limiting
  (up to 2 minutes per attempt) and the final error message tells the user
  to set ``ncbi_api_key`` (a free NCBI API key raises the limit from 3 to 10
  requests/second and removes the throttling entirely).

1.3.17 — stall detection and crash cleanup for parallel steps
--------------------------------------------------------------

* **Fixed: step 04 could hang silently and then crash (exit 139) during long
  runs.** The worker pool no longer blocks on one socket read: it polls all
  workers, and step 04 aborts with a clear message after 40 minutes without
  any finished job (``stall_timeout``) instead of freezing for an hour and
  dying with a segfault when a worker was killed on a broken connection. A
  torn worker socket is now handled as an R error and triggers the existing
  sequential fallback. Re-running the scope resumes the step (finished pairs
  are skipped), so an aborted run costs almost nothing.
* **Crashed runs no longer leave orphaned workers behind.** ``run_all.sh``
  now reaps the whole process tree whenever the run ends abnormally (a step
  failed or crashed with a signal) and logs a clear warning, so a segfaulting
  step can no longer pin result files.

1.3.16 — clearer run records and pruned documentation
-----------------------------------------------------

* **Run records:** step 03's per-file log line no longer carries a
  ``completeness=NN%`` percentage (the GUI progress bar misread it as the
  intra-step progress, shadowing the real ``[done/total]`` value). Steps
  01/02/03 and the Custom download now log their full parameters (retries,
  timeouts, batches, search settings), and every step logs the path of its
  summary workbook when it finishes.
* **Documentation cleanup:** outdated and historical content was removed from
  the manual, INSTALL/README, the workflow reference and the online docs —
  old bug workarounds, stale version notes, the removed
  ``NCBI_genome_fa_gff`` directory and references to the previous R-only
  motif scan. The pipeline order, the run scopes (including ``custom`` and
  ``label_ecology``), the configuration keys (``custom_download``) and the
  per-type Custom download lists are now described consistently everywhere.

1.3.15 — unified per-type download-list format
----------------------------------------------

* **The shipped nuclear download list now uses the same standard format as
  the chloroplast and mitochondrial lists** (``README`` + ``download_list``
  sheets with the ``species | genome_download_url | annotation_download_url``
  columns) instead of a plain ``Sheet1``. All 527 rows are preserved
  value-for-value. The download step still reads both formats, so existing
  installations with the old ``Sheet1`` file keep working unchanged.

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
desktop interface, and the one-shot conda installer.

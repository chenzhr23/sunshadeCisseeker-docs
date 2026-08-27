GUI
===

The interface is organised as a flat tab widget with page-change animation,
a splash screen and a menu-bar main window. It is a native Qt 5.15 C++
application; the archive ships the compiled binary together with its own Qt
runtime (``lib/``, ``plugins/``, ``qt.conf``), so **no Qt or X11 package has
to be installed** on the host.

Start it with:

.. code-block:: bash

   sunshadeCisseeker gui

The window only assembles arguments and edits the same files the command line
uses, so results are identical either way.

Sliding pages
-------------

There are exactly six sliding pages, in this order:

.. list-table::
   :header-rows: 1

   * - Page
     - What it does
   * - **Introduction**
     - workflow diagram
   * - **Nuclear genome**
     - runs the nuclear part (steps 01-06) with the log streamed live; Run/Stop buttons
   * - **Chloroplast genome**
     - runs the chloroplast part (steps 01-06)
   * - **Mitochondrial genome**
     - runs the mitochondrial part (steps 01-06)
   * - **Label ecology**
     - assigns the sun/facultative/shade labels to the three merged datasets (cross-genome step 06)
   * - **Compare ecology**
     - runs the cross-genome ecology comparison (steps 07-09; requires Label ecology first)

Each analysis page shows the step description, the result directory hint and
a live log panel. The three genome pages additionally offer an **NCBI API key
(optional)** input and a **Max genome size (GB)** input: both are written to
``quickstart_config.yml`` when the field loses focus and before every run
starts (same entries as the Run Pipeline window). The genome-size cap skips
genomes whose FASTA file exceeds that on-disk size (GB). The field shows the
value from ``quickstart_config.yml``; when the key is absent it pre-fills
with ``2`` (skips oversized archives such as the ~2.7 GB *Tanacetum
coccineum* genome). Clearing the field means no limit (the empty value
persists), while a *missing* key defaults to ``2`` again on the next
``run_all.sh`` launch. A screenshot of every
page and popup, with explanations, is on the :doc:`Screenshots` page.

Menu bar
--------

Functionality lives in the menu bar only (no duplicated toolbar):

* **File** — Save parameters, Open results folder, Quit.
* **Tools** — ``Run pipeline...`` opens the full parameter/run window as a
  popup; ``Run local...`` analyzes one local species (see below);
  ``Ecology labels...`` and ``Motif library...`` open the two XLSX
  table editors as popups; ``Check environment`` opens the "Softwares
  checking and configuration" dialog.
* **Global → Configuration** — the same checking/configuration dialog.
* **Help** — About, About Qt.

Run local (single-species analysis)
-----------------------------------

**Tools → Run local...** analyzes **one species on your disk** without
touching NCBI or the download lists. Enter a species name, pick its genome
**FASTA** and annotation **GFF3**, tick the genome type(s) to analyze
(**nuclear / chloroplast / mitochondrial** — at least one must be ticked)
and press **Run**:

* The two files are copied into
  ``Custom_genome_fa_gff/<type>/{fa,gff}/<species>.<ext>`` (the original
  ``.fa/.fasta/.gz`` suffixes are kept, so gzipped inputs stay compressed).
  They become part of the custom set and are reused by later normal runs.
* For each ticked type the standard steps **04–06** run sequentially
  (promoter extraction → merge → CRE scan) with the live log shown in the
  dialog. NCBI and download steps are forced off and the **genome-size cap
  is lifted** for the explicitly chosen file, whatever
  ``quickstart_config.yml`` says — a huge local genome is analyzed, not
  skipped.
* Ticking several types runs them one after another; **Stop** interrupts
  the current run and the queue.

Fonts and remote displays
-------------------------

* The whole interface is rendered in **Arial**. Hosts without Arial
  automatically get the bundled, metrically identical **Liberation Sans**
  through the bundle's fontconfig alias (``lib/fonts/``). CJK text the
  user enters into the config tables (species names, notes) renders through
  the bundled **Noto Sans CJK SC** font on hosts without system CJK fonts.
* On X-forwarded connections (``DISPLAY`` contains a host) the page-change
  animations are switched off automatically to keep the window responsive;
  ``SUNSHADE_ANIM=1`` forces them back on.
* **Live log everywhere**: the run panels show the full live log on local
  and remote displays alike (the run itself is detached and the display is
  polled once per second, so forwarded sessions stay responsive). Log lines
  produced while another page is on screen are **buffered, never dropped**,
  and are flushed (in order) when the page is shown again, so switching
  back always shows the complete history up to "process finished". At the
  end of every run the panel prints where the logs live: a copy of the
  panel log is kept under ``log/gui_<run-id>.log``, the master run log is
  ``log/sunshadeCisseeker_<scope>_*.log``, and every step writes its own
  ``.log`` under ``result/``. The full
  output also flows into ``log/sunshadeCisseeker_*.log`` and each step's own
  ``.log`` file. For very constrained links a compact status bar (one status
  line per second) is available with
  ``SUNSHADE_LOG=status sunshadeCisseeker gui``.
* **Live progress bar**: every analysis page shows a Qt progress bar above
  the log with the overall position (e.g. "Step 4/6 — promoter extraction —
  46%"). The panel parses the pipeline's step markers
  (``===== NN_name.log started =====``) and its percentage / ``[n/total]``
  log lines once per second, so no pipeline changes were needed. The bar is
  **monotonic** within a run (it never moves backwards, even while a long
  step's marker scrolls out of the visible log tail) and always ends in a
  definitive terminal state: full **green** "Finished — all steps completed",
  full **red** "Failed (exit code N) — see the log below", or full
  **orange** "Stopped by user". A page therefore never lingers on a stale
  mid-run percentage after its run has ended.
* **Runs are independent per page**: every started run gets its own
  bookkeeping files, so several pages may run at the same time and each page
  tracks only its own run — see the next section for details.
* Startup never blocks: the two XLSX label tables load in the background, all
  notices are non-modal, and a watchdog guarantees the process exits after
  the window closes even on broken remote displays.
* **Open results** on hosts without a file manager/browser shows a copyable
  path dialog instead of calling ``xdg-open``.

Running several pages at the same time
--------------------------------------

Every started run is fully independent, so the three genome pages (and the
ecology pages) can be run **at the same time**:

* Each page gets its own run id and its own bookkeeping files
  ``/tmp/sunshadecisseeker-gui/run-<scope>-<pid>-<time>-<seq>.pid`` /
  ``.status`` / ``.out``. The run id is the first line of the page's log
  (``run started | id=... | scope=...``). The page's log, progress bar and
  Run/Stop buttons therefore track **only that page's run**: one page
  finishing never marks another page as finished, and **Stop** terminates
  only the selected run.
* The pipeline writes separate result directories and separate run logs per
  scope (``log/sunshadeCisseeker_<scope>_<date>_<pid>.log``), so parallel
  runs cannot corrupt each other's data.
* To double-check which page is doing what on the server, compare the first
  log line of each page (``scope=...``) with ``top``/``ps``: the R command
  lines show the active step (``02_..._download_fagff.r``,
  ``04_..._promoter_sequence.r``, ...). A page shows "Finished" only when
  its own run really exited.
* Concurrent runs share one IP address for NCBI, so expect more HTTP 429
  rate-limit retries (absorbed automatically). If you want faster downloads,
  set ``ncbi_api_key`` in ``quickstart_config.yml`` or run the
  download-heavy pages one after another.

Rebuilding the interface
------------------------

On hosts where the prebuilt binary does not run (needs conda; sources ship in
``src/``):

.. code-block:: bash

   bash build_on_host.sh -s src -b .

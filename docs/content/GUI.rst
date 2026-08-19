GUI
===

The interface follows the **psiFinder framework and look**: the same flat tab
widget with page-change animation, the same splash screen and the same
menu-bar main window. It is a native Qt 5.15 C++ application; the archive
ships the compiled binary together with its own Qt runtime
(``lib/``, ``plugins/``, ``qt.conf``), so **no Qt or X11 package has to be
installed** on the host.

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
a live log panel. A screenshot of every page and popup, with explanations, is
on the :doc:`Screenshots` page.

Menu bar
--------

Functionality lives in the menu bar only (no duplicated toolbar):

* **File** — Save parameters, Open results folder, Quit.
* **Tools** — ``Run pipeline...`` opens the full parameter/run window as a
  popup; ``Ecology labels...`` and ``Motif library...`` open the two XLSX
  table editors as popups; ``Check environment`` opens the "Softwares
  checking and configuration" dialog.
* **Global → Configuration** — the same checking/configuration dialog.
* **Help** — About, About Qt.

Fonts and remote displays
-------------------------

* The whole interface is rendered in **Arial**. Hosts without Arial
  automatically get the bundled, metrically identical **Liberation Sans**
  through the bundle's fontconfig alias (``lib/fonts/``).
* On X-forwarded connections (``DISPLAY`` contains a host) the page-change
  animations are switched off automatically to keep the window responsive;
  ``SUNSHADE_ANIM=1`` forces them back on.
* **Live log everywhere**: the run panels show the full live log on local
  and remote displays alike (the run itself is detached and the display is
  polled once per second, so forwarded sessions stay responsive). The full
  output also flows into ``log/sunshadeCisseeker_*.log`` and each step's own
  ``.log`` file. For very constrained links a compact status bar (one status
  line per second) is available with
  ``SUNSHADE_LOG=status sunshadeCisseeker gui``.
* **Live progress bar**: every analysis page shows a Qt progress bar above
  the log with the overall position (e.g. "Step 4/6 — promoter extraction —
  46%"). The panel parses the pipeline's step markers
  (``===== NN_name.log started =====``) and its percentage / ``[n/total]``
  log lines once per second, so no pipeline changes were needed.
* **Runs are independent per page**: every started run gets its own bookkeeping
  files (``/tmp/sunshadecisseeker-gui/run-<scope>-<pid>-<time>-<seq>.pid/.status/.out``),
  so several pages may run at the same time and each page's log, progress bar
  and Run/Stop buttons track only its own run — one page finishing never
  affects the others. The data directories per genome type are separate too,
  so concurrent runs cannot corrupt each other's results. Note that concurrent
  NCBI downloads share one IP address, so expect more 429 rate-limit retries
  (the pipeline retries them automatically).
* Startup never blocks: the two XLSX label tables load in the background, all
  notices are non-modal, and a watchdog guarantees the process exits after
  the window closes even on broken remote displays.
* **Open results** on hosts without a file manager/browser shows a copyable
  path dialog instead of calling ``xdg-open``.

Rebuilding the interface
------------------------

On hosts where the prebuilt binary does not run (needs conda; sources ship in
``src/``):

.. code-block:: bash

   bash build_on_host.sh -s src -b .

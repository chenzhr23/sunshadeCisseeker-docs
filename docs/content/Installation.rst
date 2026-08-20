Installation
============

.. note::

   Remember – currently, sunshadeCisseeker is available only for Unix-based
   systems (Linux x86_64; WSL2 counts as Linux)!

Requirements
------------

.. list-table::
   :header-rows: 1

   * - Item
     - Requirement
     - Notes
   * - Operating system
     - Linux x86_64
     - WSL2 works as well
   * - R + R packages
     - installed by ``install.sh``
     - openxlsx, data.table, stringi, ggplot2, patchwork, scales, curl, xml2, dplyr, rentrez, forcats, tidyr
   * - bedtools / samtools
     - installed by ``install.sh``
     - optional accelerators for uncompressed linear genomes
   * - gzip
     - installed by ``install.sh``
     - required for download integrity checks
   * - Qt runtime (GUI)
     - bundled
     - the archive ships Qt 5.15 in ``lib/`` + ``plugins/``; glibc >= 2.17
   * - Display (GUI only)
     - WSLg, X11 or ``ssh -X/-Y``
     - the pipeline itself runs without a display

sunshadeCisseeker download
--------------------------

.. code-block:: bash

   sha256sum -c SHA256SUMS.txt
   tar -xzf sunshadeCisseeker-latest-linux-x86_64.tar.gz
   cd sunshadeCisseeker-latest

Unpack
------

The archive contains the launcher, the compiled Qt interface with its own Qt
runtime (``lib/`` + ``plugins/`` + ``qt.conf``), the installer, all analysis
scripts (``script/``), the two XLSX configuration templates (``config/``),
the interface sources (``src/``) and this documentation.

Install
-------

One command installs everything, without root rights:

.. code-block:: bash

   bash install.sh -y

What ``install.sh`` does:

1. **Conda detection/bootstrapping** — finds an existing
   conda/mamba/micromamba, or installs Miniconda into ``~/miniconda3`` when
   none exists. When ``conda.anaconda.org`` is unreachable it falls back to
   the TUNA mirror automatically (``-m`` forces the mirror).
2. **Dependency environment** — creates the dedicated ``sunshadecisseeker``
   conda environment with R, all 12 R packages and ``bedtools``,
   ``samtools``, ``gzip``.
3. **Bundle installation** — copies the bundle to
   ``~/.local/opt/sunshadeCisseeker``, makes every script executable and
   creates the writable directories. Re-installing **preserves** your
   ``result/``, ``log/``, custom genomes, the two configuration XLSX files and
   ``quickstart_config.yml``.
4. **Self-activating launcher** — registers ``~/.local/bin/sunshadeCisseeker``
   which activates the dependency environment itself, so
   ``sunshadeCisseeker gui`` / ``run`` / ``check`` work in any fresh terminal
   without manual ``conda activate``.
5. **Desktop menu entry** — registers a ``sunshadeCisseeker`` entry when a
   desktop is present.
6. **End-to-end verification** — runs the environment check, reads both
   configuration tables through the GUI's own R helper and runs the GUI self
   test.

Options:

.. code-block:: bash

   bash install.sh -p /opt/sunshadeCisseeker   # custom install directory
   bash install.sh -e myenv                    # custom conda environment name
   bash install.sh -y                          # do not prompt, accept the defaults
   bash install.sh -m                          # force the TUNA conda mirror
   bash install.sh -s                          # skip the dependency step
   bash install.sh -h                          # help

With ``-y`` the installer never waits for input — in particular the
"*target already exists, overwrite it?*" question is answered automatically,
so the command is safe for scripts and remote sessions. Your results and
configuration are still preserved. Without ``-y`` the installer asks for
confirmation before overwriting an existing installation (answering anything
but ``y`` aborts). Note that the conda calls inside the installer always use
conda's own ``-y`` regardless of this flag, so the dependency phase never
prompts either way.

Ways to start sunshadeCisseeker
-------------------------------

A machine with its own display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sunshadeCisseeker gui

A remote server, through X11 forwarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reconnect with ``ssh -Y user@server`` and run ``sunshadeCisseeker gui``. On
forwarded displays the interface switches off the page-change animations
automatically, and the run panels show the same full live log as on a local
display (the run is detached and polled once per second, so the tunnel stays
usable). ``SUNSHADE_LOG=status sunshadeCisseeker gui`` switches the panels to
a compact status bar for very constrained links. For heavier usage on
servers, X2Go / TigerVNC / MobaXterm are still preferable to raw X11
forwarding.

No display at all, run the pipeline directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   nohup sunshadeCisseeker run > run.out 2>&1 &
   tail -f log/sunshadeCisseeker_*.log

Global configuration
--------------------

See :doc:`Configuration` for ``quickstart_config.yml``, the two XLSX
templates and custom-genome placement.

Running from the command line
-----------------------------

.. code-block:: text

   Usage: sunshadeCisseeker <command> [options]

   Commands:
     run [all|nuclear|chloroplast|mitochondrial|ecology]
                    run the pipeline; defaults to "all".
     gui            open the Qt desktop window.
     check [--install] [--yes]
                    check the environment; --install also installs missing pieces.
     config [get KEY|list]
                    inspect quickstart_config.yml.
     version        print the version.
     help           show this help.

.. code-block:: bash

   sunshadeCisseeker run               # all genome types + ecology comparison
   sunshadeCisseeker run nuclear       # nuclear only (01-06)
   sunshadeCisseeker run chloroplast   # chloroplast only (01-06)
   sunshadeCisseeker run mitochondrial # mitochondrial only (01-06)
   sunshadeCisseeker run ecology       # cross-genome comparison only (07-09)

Minimal working sequence
------------------------

.. code-block:: bash

   # 1. verify and unpack
   sha256sum -c SHA256SUMS.txt
   tar -xzf sunshadeCisseeker-latest-linux-x86_64.tar.gz
   cd sunshadeCisseeker-latest

   # 2. install everything (dependencies + launcher), no questions
   bash install.sh -y

   # 3. configure (edit these two XLSX + the yml)
   #    config/species_ecology_labels.xlsx
   #    config/cis_element_motif_library.xlsx
   #    quickstart_config.yml

   # 4. custom-genome-only smoke test (no network, no NCBI)
   #    place FASTA+GFF3 pairs in Custom_genome_fa_gff/*/fa and gff/
   sed -i 's/ncbi_download: "true"/ncbi_download: "false"/' quickstart_config.yml
   sunshadeCisseeker run

   # 5. full run with NCBI downloads (set your API key first)
   sed -i 's/ncbi_download: "false"/ncbi_download: "true"/' quickstart_config.yml
   nohup sunshadeCisseeker run > run.out 2>&1 &
   tail -f log/sunshadeCisseeker_*.log

Troubleshooting
---------------

1. **Missing R package(s)** — run ``sunshadeCisseeker check --install --yes``.
2. **``Cannot locate pipeline root (.pipeline_root marker)``** — do not delete
   the root ``.pipeline_root``; run scripts from inside the bundle tree.
3. **02/03 download failures** — step 03 retries across HTTPS/FTP/datasets
   mirrors. If downloads keep failing, set ``ncbi_api_key`` in
   ``quickstart_config.yml`` (the single most effective fix — unauthenticated
   eutils access is limited to 3 requests/second) and rerun.
4. **``retry ... lexical error: invalid character inside string`` /
   ``Unable to retrieve history data``** — historic NCBI web_history server
   failures; current releases no longer use web_history, and transient
   network errors are retried with exponential backoff automatically.
5. **Custom genomes not analyzed** — check that the FASTA/GFF3 basenames
   match exactly under ``Custom_genome_fa_gff/<type>/``.
6. **Ecology comparison empty** — check that the ``species`` values in
   ``config/species_ecology_labels.xlsx`` match the id_map ``species`` values
   exactly, and that at least two ecology groups have ``min_group_n`` or more
   species.
7. **Changing the motif library has no effect on ecology figures** — rerun
   step 06 for each genome type and then the ecology steps 07–09.
8. **Windows paths / Excel file locking (WSL)** — close the XLSX in Excel
   before a step rewrites it.
9. **GUI: ``qt.glx: qglx_findConfig`` warnings on startup** — harmless; the
   interface does not use OpenGL and the launcher disables the GLX
   integration by default (the same treatment as in psiFinder).
   ``SUNSHADE_KEEP_GL=1`` re-enables it.
10. **GUI: ``Fontconfig error: Cannot load default config file``** — the
    bundle ships its own fonts and generates a fontconfig configuration for
    the installed path at start-up. If it persists, run
    ``SUNSHADE_DEBUG=1 sunshadeCisseeker gui``.
11. **The interface still refuses to start** — the launcher prints the
    reason: no ``DISPLAY``/``WAYLAND_DISPLAY`` (headless — reconnect with
    ``ssh -Y`` or use ``sunshadeCisseeker run``); interface binary missing
    (rebuild with ``bash build_on_host.sh -s src -b .``); or ``could not
    connect to display`` / ``Authorization required`` (X11 forwarding not
    enabled — use ``ssh -Y``).
12. **"Open results" shows a path dialog / xdg-open error spam** — on remote
    servers without a file manager or browser the window cannot open folders
    by itself; it detects the remote display and shows the copyable path plus
    a "Try to open anyway" button.
13. **The window freezes after clicking Run on a remote server** — the run
    panels switch to the status-bar mode on forwarded displays
    (``SUNSHADE_LOG=full`` forces the live log). If it still freezes, the X
    tunnel itself is congested: use ``nohup sunshadeCisseeker run`` on the
    server, or switch to X2Go/TigerVNC/MobaXterm.
14. **Re-installing wipes my results?** — no: ``install.sh`` preserves
    ``result/``, ``log/``, custom genomes, the two configuration XLSX files
    and ``quickstart_config.yml`` across re-installs.
15. **Several pages started together all show "100% finished" while ``top``
    still shows R processes running** — fixed in version 1.3.5. Older releases
    keyed the per-run status files by the GUI process id, so simultaneous runs
    (Nuclear + Chloroplast + Mitochondrial) overwrote each other's files and
    every page displayed the first run's exit state. From 1.3.5 each started
    run owns a separate file set
    ``/tmp/sunshadecisseeker-gui/run-<scope>-<pid>-<time>-<seq>.{pid,status,out}``
    (the run id is printed as the first line of each page's log), and the run
    logs under ``log/`` are named per scope, so the pages, their logs and
    their progress bars are fully independent. If you still see the symptom,
    check the log line ``scope=...`` at the top of the page and compare it
    with the R processes in ``top``.
16. **A run fails at the very end with ``CHARSXPs are limited to 2^31-1
    bytes`` / ``stri_join``** — fixed in version 1.3.6: very large result
    tables (promoter details, id maps, site records) are now written as
    bounded part files (``<name>.partNN.xlsx`` plus an index workbook at the
    canonical path, see :doc:`Outputs`). Simply re-run the same scope: the
    already-extracted promoters are skipped as up to date and only the table
    writing is redone.

Uninstall
---------

.. code-block:: bash

   rm -rf ~/.local/opt/sunshadeCisseeker
   rm -f ~/.local/bin/sunshadeCisseeker
   rm -f ~/.local/share/applications/sunshadeCisseeker.desktop
   conda env remove -n sunshadecisseeker

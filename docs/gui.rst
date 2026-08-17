Desktop window (GUI)
====================

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

There are exactly five sliding pages, in this order:

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
   * - **Compare ecology**
     - runs the cross-genome ecology comparison (steps 07-09)

Each analysis page shows the step description, the result directory hint and a
live log panel.

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
* Startup never blocks: the two XLSX label tables load in the background, all
  notices are non-modal, and a watchdog guarantees the process exits after the
  window closes even on broken remote displays.
* **Open results** on hosts without a file manager/browser shows a copyable
  path dialog instead of calling ``xdg-open``.

Display requirements
--------------------

* **WSL2 on Windows 11** — WSLg shows the window directly; with an older
  setup, start VcXsrv or Xming on Windows first.
* **Remote server** — reconnect with ``ssh -Y user@server``, then run
  ``sunshadeCisseeker gui``.
* **No display** — the launcher refuses to start with a clear message; use
  ``sunshadeCisseeker run`` instead.

Rebuilding the interface
------------------------

On hosts where the prebuilt binary does not run (needs conda; sources ship in
``src/``):

.. code-block:: bash

   bash build_on_host.sh -s src -b .

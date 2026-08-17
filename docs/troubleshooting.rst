Troubleshooting
===============

1. **Missing R package(s)** — run ``sunshadeCisseeker check --install --yes``.
2. **``Cannot locate pipeline root (.pipeline_root marker)``** — do not delete
   the root ``.pipeline_root``; run scripts from inside the bundle tree.
3. **02/03 download failures** — step 03 retries across HTTPS/FTP/datasets
   mirrors. If downloads keep failing: set ``ncbi_api_key`` in
   ``quickstart_config.yml`` (the single most effective fix — unauthenticated
   eutils access is limited to 3 requests/second) and rerun; or place the
   files manually in ``result/<type>/02_download/<species>/``.
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
9. **GUI: ``qt.glx: qglx_findConfig`` warnings** — harmless; the interface
   does not use OpenGL and the launcher disables the GLX integration by
   default (same treatment as psiFinder). ``SUNSHADE_KEEP_GL=1`` re-enables
   it.
10. **GUI: ``Fontconfig error: Cannot load default config file``** — the
    bundle ships its own fonts and generates a fontconfig configuration for
    the installed path at start-up. If it persists, run
    ``SUNSHADE_DEBUG=1 sunshadeCisseeker gui`` and check that ``lib/fonts/``
    and ``lib/fontconfig/fonts.conf.in`` exist.
11. **GUI does not open** — the launcher prints the reason: no
    ``DISPLAY``/``WAYLAND_DISPLAY`` (headless — reconnect with ``ssh -Y`` or
    use ``sunshadeCisseeker run``); interface binary missing (rebuild with
    ``bash build_on_host.sh -s src -b .``); or a library error such as
    ``libxcb-cursor.so.0`` (the bundle is incomplete — never copy
    ``sunshadeCisseeker-bin`` away from ``lib/``, ``plugins/`` and
    ``qt.conf``).
12. **"Open results" shows a path dialog / xdg-open error spam** — on remote
    servers without a file manager or browser the window cannot open folders
    by itself; it detects the remote display and shows the copyable path plus
    a "Try to open anyway" button. On WSLg and normal desktops the default
    file manager opens as before.
13. **Re-installing wipes my results?** — no: ``install.sh`` preserves
    ``result/``, ``log/``, custom genomes, the two configuration XLSX files
    and ``quickstart_config.yml`` across re-installs.

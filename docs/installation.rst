Installation
============

sunshadeCisseeker runs on **Linux x86_64** (WSL2 counts as Linux) and needs no
root rights. One command installs everything:

.. code-block:: bash

   # 1. verify and unpack
   sha256sum -c SHA256SUMS.txt
   tar -xzf sunshadeCisseeker-latest-linux-x86_64.tar.gz
   cd sunshadeCisseeker-latest

   # 2. one-shot install (dependencies + launcher + verification)
   bash install.sh -y

What ``install.sh`` does
------------------------

Following the psiFinder approach, the installer works without root and is
safe to re-run:

1. **Conda detection/bootstrapping** — finds an existing
   conda/mamba/micromamba, or installs Miniconda into ``~/miniconda3`` when
   none exists. When ``conda.anaconda.org`` is unreachable it falls back to
   the TUNA mirror automatically (``-m`` forces the mirror).
2. **Dependency environment** — creates the dedicated ``sunshadecisseeker``
   conda environment with R and all 12 R packages used by the pipeline and the
   GUI helper (``openxlsx``, ``data.table``, ``stringi``, ``ggplot2``,
   ``patchwork``, ``scales``, ``curl``, ``xml2``, ``dplyr``, ``rentrez``,
   ``forcats``, ``tidyr``) plus ``bedtools``, ``samtools`` and ``gzip``.
3. **Bundle installation** — copies the bundle to
   ``~/.local/opt/sunshadeCisseeker``, makes every script executable and
   creates the writable directories. Re-installing **preserves** your
   ``result/``, ``log/``, custom genomes, the two configuration XLSX files and
   ``quickstart_config.yml``.
4. **Self-activating launcher** — registers ``~/.local/bin/sunshadeCisseeker``
   which activates the dependency environment itself, so
   ``sunshadeCisseeker gui`` / ``run`` / ``check`` work in any fresh terminal
   without manual ``conda activate``. ``~/.local/bin`` is added to your
   ``.bashrc``/``.zshrc``/``.profile`` if needed.
5. **Desktop menu entry** — registers a ``sunshadeCisseeker`` entry when a
   desktop is present.
6. **End-to-end verification** — runs the environment check, reads both
   configuration tables through the GUI's own R helper and runs the GUI self
   test.

Options:

.. code-block:: bash

   bash install.sh -p /opt/sunshadeCisseeker   # custom install directory
   bash install.sh -e myenv                    # custom conda environment name
   bash install.sh -m                          # force the TUNA conda mirror
   bash install.sh -s                          # skip the dependency step
   bash install.sh -h                          # help

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
     - the 12 packages listed above
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

Dependency check
----------------

At any time you can inspect or repair the environment:

.. code-block:: bash

   sunshadeCisseeker check                  # report what is missing
   sunshadeCisseeker check --install --yes  # install missing pieces

The checker prefers the conda route (the ``sunshadecisseeker`` environment)
and falls back to ``install.packages()`` from CRAN when no conda exists.

Uninstall
---------

.. code-block:: bash

   rm -rf ~/.local/opt/sunshadeCisseeker
   rm -f ~/.local/bin/sunshadeCisseeker
   rm -f ~/.local/share/applications/sunshadeCisseeker.desktop
   conda env remove -n sunshadecisseeker

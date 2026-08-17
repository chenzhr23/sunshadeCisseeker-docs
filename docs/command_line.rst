Command line
============

``sunshadeCisseeker`` is a single launcher with subcommands. The registered
``PATH`` launcher activates the ``sunshadecisseeker`` environment
automatically, so no manual ``conda activate`` is needed.

.. code-block:: text

   Usage: sunshadeCisseeker <command> [options]

   Commands:
     run [all|nuclear|chloroplast|mitochondrial|ecology]
                    run the pipeline; defaults to "all". Reads quickstart_config.yml.
     gui            open the Qt desktop window (WSLg or X forwarding needed).
     check [--install] [--yes]
                    check the environment; --install also installs missing pieces.
     config [get KEY|list]
                    inspect quickstart_config.yml.
     version        print the version.
     help           show this help.

``run``
-------

Runs the pipeline in strict order (see :doc:`pipeline`):

.. code-block:: bash

   sunshadeCisseeker run               # all genome types + ecology comparison
   sunshadeCisseeker run nuclear       # nuclear only (01-06)
   sunshadeCisseeker run chloroplast   # chloroplast only (01-06)
   sunshadeCisseeker run mitochondrial # mitochondrial only (01-06)
   sunshadeCisseeker run ecology       # cross-genome comparison only (07-09)

Every run writes a timestamped master log
(``log/sunshadeCisseeker_YYYYMMDD_HHMMSS.log``) and each step writes its own
``.log`` under its result directory. For long runs, detach:

.. code-block:: bash

   nohup sunshadeCisseeker run > run.out 2>&1 &
   tail -f log/sunshadeCisseeker_*.log

``check``
---------

.. code-block:: bash

   sunshadeCisseeker check                  # report
   sunshadeCisseeker check --install --yes  # install what is missing

Verifies R, every R package and the optional accelerators
(``bedtools``/``samtools``/``gzip``), and reports whether the GUI binary is
present.

``config``
----------

.. code-block:: bash

   sunshadeCisseeker config list          # show quickstart_config.yml
   sunshadeCisseeker config get workers   # one key

``gui``
-------

.. code-block:: bash

   sunshadeCisseeker gui

Opens the desktop window; see :doc:`gui`. Without a display the launcher
prints a clear message and exits (use ``run`` instead on headless hosts).

Running scripts directly
------------------------

Every analysis step is a plain script and can be run directly (the
``sunshadecisseeker`` environment must be active if you bypass the launcher):

.. code-block:: bash

   cd ~/.local/opt/sunshadeCisseeker
   conda activate sunshadecisseeker
   Rscript script/nuclear_genome/01_nuclear_genome_species_info.r
   bash run_all.sh                       # same as the launcher's "run all"

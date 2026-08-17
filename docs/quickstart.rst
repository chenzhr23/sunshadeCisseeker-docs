Quick start
===========

Five minutes from archive to first results:

.. code-block:: bash

   # 1. verify and unpack
   sha256sum -c SHA256SUMS.txt
   tar -xzf sunshadeCisseeker-latest-linux-x86_64.tar.gz
   cd sunshadeCisseeker-latest

   # 2. install everything (dependencies + launcher), no questions
   bash install.sh -y

   # 3. open the desktop window
   sunshadeCisseeker gui

   # 4. run the pipeline (or a single genome type)
   sunshadeCisseeker run            # everything enabled in quickstart_config.yml
   sunshadeCisseeker run nuclear
   sunshadeCisseeker run chloroplast
   sunshadeCisseeker run mitochondrial
   sunshadeCisseeker run ecology    # only the comparison (after 01-06 are done)

Custom-genome-only smoke test (no network, no NCBI)
----------------------------------------------------

Place your own FASTA + GFF3 pairs under
``Custom_genome_fa_gff/<genome_type>/fa`` and ``gff`` (matching basenames,
e.g. ``fa/Sarcandra_glabra.fa`` + ``gff/Sarcandra_glabra.gff3``), then:

.. code-block:: bash

   sed -i 's/ncbi_download: "true"/ncbi_download: "false"/' quickstart_config.yml
   sunshadeCisseeker run

Full run with NCBI downloads
----------------------------

Set your NCBI API key first (recommended: 10 requests/second instead of 3,
and far fewer throttling failures):

.. code-block:: bash

   sed -i 's/ncbi_download: "false"/ncbi_download: "true"/' quickstart_config.yml
   # put your key in quickstart_config.yml: ncbi_api_key: "your_key"
   nohup sunshadeCisseeker run > run.out 2>&1 &
   tail -f log/sunshadeCisseeker_*.log

.. note::

   The NCBI steps are large by design: for example the chloroplast part
   prepares one representative FASTA + GFF3 pair for every plant species in
   RefSeq (tens of thousands of files). If you only need a subset of species,
   list them in ``config/species_ecology_labels.xlsx`` and contact us for the
   species-filtering option, or simply place the genomes you need under
   ``Custom_genome_fa_gff/`` and disable ``ncbi_download``.

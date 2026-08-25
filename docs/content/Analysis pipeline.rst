Analysis pipeline
=================

The pipeline is built from eleven strict step roles — one Custom genome
download step, six per-genome steps (run for each of nuclear / chloroplast /
mitochondrial, i.e. steps 01–06 × 3) and four cross-genome steps (label
ecology plus the ecology comparison) — for 23 step executions in the ``all``
scope.

.. code-block:: text

   custom genomes:
     01 download Custom FASTA+GFF3 (per-type URL lists)

   per genome type:
     01 species metadata -> 02 download FASTA+GFF3 -> 03 retry failed
     -> 04 promoter extraction -> 05 merge NCBI+Custom -> 06 universal CRE scan

   cross-genome:
     06 label ecology -> 07 merge -> 08 differential statistics -> 09 figures

Each step reads the exact outputs of the previous one and writes a multi-sheet
XLSX workbook (README sheet first) plus its own ``.log``.

Step 00 — Custom genome download
--------------------------------

Before the per-genome steps, the Custom download step reads the per-type URL
lists ``Custom_genome_fa_gff/<type>/Custom_genome_fa_gff_<type>.xlsx``
(columns ``species | genome_download_url | annotation_download_url``; the
folder decides the genome type; missing or empty files are replaced by
header-only templates) plus the optional global table
``config/custom_genome_download_list.xlsx``, and downloads every FASTA/GFF3
pair into ``Custom_genome_fa_gff/<type>/{fa,gff}/`` with matching file stems
(species name, spaces → underscores). Step 04 then pairs them automatically.
Downloads are resumable (``.part``), retried with backoff, paced, and skipped
when already complete; the summary is
``result/custom_genome/01_custom_download/custom_download_summary.xlsx``. The
``custom`` scope runs this step alone, and the ``custom_download`` switch in
``quickstart_config.yml`` controls whether it runs automatically before the
genome steps.

Running scopes in parallel
--------------------------

The genome scopes and the ecology scope write to separate result directories
and separate run logs, so they can be started in parallel — from several GUI
pages at once (each page tracks only its own run, see :doc:`GUI`) or from
several terminals with ``sunshadeCisseeker run nuclear`` /
``sunshadeCisseeker run chloroplast`` /
``sunshadeCisseeker run mitochondrial`` (equivalently
``bash run_all.sh <scope>``). The only
shared resource is the NCBI rate limit (one IP address): parallel download
phases simply see more 429 retries, which the pipeline absorbs automatically.
For cleaner downloads, run the download-heavy scopes one after another or
configure ``ncbi_api_key``.

Step 01 — species metadata
--------------------------

Queries NCBI (Assembly for the nuclear compartment, Nucleotide for the
organelles), retrieves taxonomy, and writes ``<type>_info.xlsx``. The IDs are
fetched directly and summarised in per-id batches (the fragile NCBI
web_history server is not used). For every species the **single most
representative record** is chosen deterministically:

1. RefSeq records first,
2. "complete genome" annotations first,
3. longest genome,
4. most recently updated,
5. accession as the final tie-breaker.

The nuclear part additionally validates that the FASTA and GFF3 URLs really
exist before selecting the representative pair. Since 1.3.21 every candidate
URL is checked once, up front, **in parallel** (the same fork-free PSOCK
worker pool the download steps use, 32 URLs per batch), and both that
validation pass and the selection loop report live progress — the step takes
minutes instead of the hours a serial check needed. The download URLs carry
the ``api_key`` parameter automatically when ``ncbi_api_key`` is configured.

Step 02 — download FASTA + GFF3
-------------------------------

Builds exactly **one FASTA + one GFF3 task per species** from the
representative URLs and downloads them in parallel (paced to respect the NCBI
rate limit, with ``failonerror``, error-page detection, clean retries with
jitter and resumable ``.part`` files). Deterministic HTTP 4xx errors fail
immediately and NCBI rate limiting (429) is probed a bounded number of times
(``--rate-retries=``), so a dead URL never burns the whole retry budget.
Completed files are skipped on re-runs, and every kept file passes a cheap
format check (FASTA starts with ``>``, GFF3 with ``#``; ``gzip -t`` for
``.gz``), so incomplete or mislabelled content is re-downloaded.

Step 03 — retry failed
----------------------

Re-reads the task list and retries failed downloads across alternative URL
mirrors with exponential backoff. Deterministic client errors (HTTP 4xx
except 429, e.g. a malformed or removed URL) fail immediately instead of
burning all retries, and NCBI rate limiting (HTTP 429) is probed a bounded
number of times with short waits before being recorded cleanly — so the step
finishes in minutes rather than hours and can simply be re-run later once the
throttle clears. Files that exist but fail the FASTA/GFF3 format check are
re-downloaded as well. Extra flags: ``--retries=``, ``--rate-retries=``,
``--timeout=``, ``--workers=``, ``--check-all=true``.

Step 04 — promoter extraction
-----------------------------

For every gene (fallback: CDS/tRNA/rRNA) the transcription start site (TSS)
is the 5' end on the ``+`` strand or the 3' end on the ``-`` strand. Up to
``promoter_len`` bp upstream of the TSS are extracted; the interval is
clipped at the nearest upstream gene and at the sequence boundary so gene
bodies are never included.

The extraction engine is chosen per genome:

* **Chloroplast / mitochondrial (circular)** — constant-time interval
  extraction per gene (the same blocker-interval mathematics as the linear
  path), so a full organelle run takes minutes instead of hours; the output
  is byte-identical to the previous per-base walk.
* **Nuclear (linear)** — ``bedtools getfasta`` + ``samtools faidx`` whenever
  both tools exist: the gzipped NCBI FASTA is decompressed once into a
  temporary file (``gzip -dc``), indexed with ``samtools faidx`` (sequence
  lengths come straight from the index, no R pass over the genome) and
  extracted with ``bedtools``; the temp file is removed afterwards. Without
  the tools, a streaming R extractor reads ``.gz`` directly (identical
  results).
* **GFF3 parsing** — ``data.table::fread`` (C-level parser, native ``.gz``
  support, stops at the ``##FASTA`` section) with an automatic fallback to
  the pure-R parser. Every GFF3 is first stream-checked for binary content
  (a corrupt download once crashed the parser and, through the sequential
  fallback, the whole run with a segfault); a corrupt file fails its pair
  cleanly and is removed so step 02 re-downloads it on the next run.

Re-runs are incremental: a species whose promoter FASTA and detail table are
newer than its inputs (and the requested ``promoter_len`` is unchanged, as
recorded in the ``.promoter_len`` marker written at start-up) is skipped, so
a re-run only processes new or changed genomes — even a run that was
interrupted late resumes cheaply. Long parallel steps are additionally
protected by **CPU-confirmed stall detection**: when no pair has finished
for 40 minutes the pool reports which species are still running and checks
whether the worker processes (and their ``gzip``/``samtools``/``bedtools``
children) are still consuming CPU. Pairs that keep computing — typically
multi-GB genomes — are left to finish, with a progress warning every
confirmation window; only a worker tree that has *also* stopped consuming
CPU is treated as truly stuck and aborted, with the in-flight species named
(a crashed run never leaves orphaned workers behind). The next re-run
simply resumes from the completed pairs.

A configurable **genome-size cap** (``max_genome_gb`` in
``quickstart_config.yml``, editable in the GUI on the three genome pages and
the Run Pipeline window, default ``2``) skips any pair whose genome FASTA
file exceeds that on-disk size (GB): the pair is recorded as ``skipped`` in
the pair summary (message ``excluded by max_genome_gb …``) and never blocks
the run — for genomes that are simply too large for the machine (the default
``2`` skips oversized archives such as the ~2.7 GB *Tanacetum coccineum*
genome). Empty or
``0`` = no limit; the compared size is the same ``fasta_bytes`` reported in
the summary's ``File_sizes`` sheet.

Every pair's summary row also records the **on-disk genome file sizes**:
``fasta_bytes`` / ``gff3_bytes`` / ``genome_total_bytes`` plus the
human-readable ``fasta_size`` / ``gff3_size`` / ``total_size`` columns, and
the summary workbook carries a dedicated **``File_sizes``** sheet with one
row per species, largest genomes first (totals in ``Run_info``). The
per-pair detail tables and the combined
FASTA are assembled at the end by a streaming, bounded-memory combiner that
tolerates unreadable files instead of aborting; a combined detail table with
more than 1,000,000 rows is written as bounded part files (see
:doc:`Outputs`).

Step 05 — input merge
---------------------

Merges NCBI and Custom promoters (no ecology labels here), gives every
promoter a short unique ID (``N/C/M`` + 9 digits) and writes the ID map
(``all_species_<type>_id_map.xlsx``) with species, source, gene, strand and
coordinates. Ecology labels are attached separately by the Label ecology
step. The combined FASTA is written through a large buffer, so merging
hundreds of thousands of promoters stays fast. The merge is skipped when its
outputs are already newer than every input and the script itself.

Step 06 — universal CRE scan
----------------------------

Searches every motif of ``config/cis_element_motif_library.xlsx`` in every
promoter. On Linux the scan runs the bundled **C++ Aho-Corasick backend**
(``bin/cre_scan``): it builds a multi-pattern automaton from the whole motif
set and reads the combined FASTA once, splitting the file across threads (up
to 64, defaulting to the configured core count). The R ``stringi`` backend is
kept as an automatic fallback when ``bin/cre_scan`` is absent or not
executable; both backends produce identical tables (the ``scan_method`` note
in the results workbook records which one ran). All motifs are matched as
literal fixed text — degenerate IUPAC codes keep their literal behaviour —
and occurrences are counted non-overlapping per promoter. Outputs:

* ``<type>_ciselement_results.xlsx`` — ``Element_stats`` /
  ``Species_element_counts`` / ``Species_summary``;
* ``<type>_ciselement_sites.xlsx`` — full per-promoter × element records
  (written as bounded part files when they exceed 1,000,000 rows);
* ``<type>_ciselement_summary.pdf`` — the six-panel summary figure.

Steps 06–09 — label ecology and ecology comparison
--------------------------------------------------

Step 06 (Label ecology) attaches the ``sun`` / ``facultative`` / ``shade``
labels to the merged datasets and steps 07–09 run the comparison.
See :doc:`Ecology comparison` for the full business logic.

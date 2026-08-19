Analysis pipeline
=================

The pipeline runs ten strict steps: six per genome type (nuclear /
chloroplast / mitochondrial) and four cross-genome steps (label ecology plus
the ecology comparison).

.. code-block:: text

   per genome type:
     01 species metadata -> 02 download FASTA+GFF3 -> 03 retry failed
     -> 04 promoter extraction -> 05 merge NCBI+Custom -> 06 universal CRE scan

   cross-genome:
     06 label ecology -> 07 merge -> 08 differential statistics -> 09 figures

Each step reads the exact outputs of the previous one and writes a multi-sheet
XLSX workbook (README sheet first) plus its own ``.log``.

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
exist before selecting the representative pair. The download URLs carry the
``api_key`` parameter automatically when ``ncbi_api_key`` is configured.

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
  the pure-R parser.

Re-runs are incremental: a species whose promoter FASTA and detail table are
newer than its inputs (and the requested ``promoter_len`` is unchanged, as
recorded in the ``.promoter_len`` marker written at start-up) is skipped, so
a re-run only processes new or changed genomes — even a run that was
interrupted late resumes cheaply. The per-pair detail tables and the combined
FASTA are assembled at the end by a streaming, bounded-memory combiner that
tolerates unreadable files instead of aborting.

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
promoter. Exact motifs use fixed-string counting and degenerate IUPAC motifs
use regular expressions, both through the C-level ``stringi`` library,
parallelised across cores with streaming batches, so arbitrarily many
promoters can be scanned in bounded memory. Outputs:

* ``<type>_ciselement_results.xlsx`` — ``Element_stats`` /
  ``Species_element_counts`` / ``Species_summary``;
* ``<type>_ciselement_sites.xlsx`` — full per-promoter × element records;
* ``<type>_ciselement_summary.pdf`` — the six-panel summary figure.

Steps 06–09 — label ecology and ecology comparison
--------------------------------------------------

Step 06 (Label ecology) attaches the ``sun`` / ``facultative`` / ``shade``
labels to the merged datasets and steps 07–09 run the comparison.
See :doc:`Ecology comparison` for the full business logic.

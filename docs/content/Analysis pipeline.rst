Analysis pipeline
=================

The pipeline runs nine strict steps: six per genome type (nuclear /
chloroplast / mitochondrial) and three cross-genome ecology steps.

.. code-block:: text

   per genome type:
     01 species metadata -> 02 download FASTA+GFF3 -> 03 retry failed
     -> 04 promoter extraction -> 05 merge NCBI+Custom + ecology labels
     -> 06 universal CRE scan

   cross-genome:
     07 merge -> 08 differential statistics -> 09 publication figures

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
jitter and resumable ``.part`` files). Completed files are skipped on re-runs.

Step 03 — retry failed
----------------------

Re-reads the task list and retries failed downloads across alternative URL
mirrors with exponential backoff.

Step 04 — promoter extraction
-----------------------------

For every gene (fallback: CDS/tRNA/rRNA) the transcription start site (TSS)
is the 5' end on the ``+`` strand or the 3' end on the ``-`` strand. Up to
``promoter_len`` bp upstream of the TSS are extracted; the interval is
clipped at the nearest upstream gene and at the sequence boundary so gene
bodies are never included.

The extraction engine is chosen per genome:

* **Chloroplast / mitochondrial (circular)** — pure R, circular-aware:
  promoters may wrap across the replication origin.
* **Nuclear (linear)** — ``bedtools getfasta`` + ``samtools faidx`` when both
  tools exist and the FASTA is uncompressed; otherwise a streaming R
  extractor that reads ``.gz`` files directly (identical results).

Step 05 — input merge
---------------------

Merges NCBI and Custom promoters, gives every promoter a short unique ID
(``N/C/M`` + 9 digits) and writes the ID map
(``all_species_<type>_id_map.xlsx``) with species, source, gene, strand,
coordinates and the ecology label.

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

Steps 07–09 — ecology comparison
--------------------------------

See :doc:`Ecology comparison` for the full business logic.

# Architecture

Gov Assist AI uses an agentic RAG architecture because government scheme data changes over time and cannot be trusted if the system only reads static PDFs.

## Source Strategy

The primary source is `https://www.myscheme.gov.in/`. myScheme was selected because it is an official Government of India discovery portal that aggregates scheme information across ministries, states, categories, eligibility criteria, benefits, required documents, and application routes.

## Pipeline

```text
Web Crawler
  -> Page Discovery
  -> Content Extraction
  -> Data Cleaning
  -> Metadata Extraction
  -> Chunking
  -> Embedding
  -> Vector Storage
  -> Hybrid Retrieval
  -> Agentic Answering
```

## Components

- `crawler/`: discovers myScheme scheme URLs, extracts structured data, cleans HTML, captures metadata, and schedules refreshes.
- `models/`: defines the canonical `Scheme` data model and source references.
- `retrieval/`: chunks structured scheme records and retrieves with BM25 plus vector similarity.
- `agents/`: LangGraph-compatible nodes for profile, intent, planning, research, retrieval, eligibility, action planning, and grounding.
- `storage/`: JSONL store for structured scheme data with hash-based change detection and versioning.
- `evaluation/`: metrics for precision, recall, faithfulness, freshness, eligibility accuracy, and source coverage.

## Dynamic Knowledge

Each crawl calculates a content hash. If the hash changes for the same source URL, the system increments the scheme version and updates `last_updated`. This supports incremental refresh instead of full rebuilds for every run.

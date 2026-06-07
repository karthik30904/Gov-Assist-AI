# Project Flow

## User Query Flow

```text
User Query
  -> Profile Agent
  -> Intent Agent
  -> Research Planner Agent
  -> Existing Knowledge or Fresh Web Research
  -> Hybrid Retrieval Agent
  -> Eligibility Reasoning Agent
  -> Action Plan Agent
  -> Grounding Agent
  -> Answer with Sources
```

## Research Planner Decision

The planner checks whether local chunks exist and whether retrieval quality is high enough.

- If local knowledge is sufficient, it uses the vector and BM25 indexes.
- If local knowledge is missing, stale, or low quality, it triggers the Web Research Agent.
- If retrieval still returns weak evidence after fresh crawl, the answer is grounded with a warning instead of pretending certainty.

## Knowledge Refresh Flow

```text
Daily Scheduler
  -> Crawl myScheme
  -> Extract Scheme Records
  -> Compare Content Hash
  -> Update Version Metadata
  -> Rechunk
  -> Re-embed Changed Chunks
  -> Update Vector Store
```

`retrieval/indexer.py` contains the indexing handoff from structured `Scheme` records to chunks, embeddings, and local vector storage.

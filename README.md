# Gov Assist AI

Agentic RAG for Indian government scheme discovery and eligibility guidance.

The project uses [myScheme](https://www.myscheme.gov.in/) as the primary source and is designed to refresh knowledge from the web instead of relying only on static PDFs.

## Core Capabilities

- Web crawling and scraping for scheme data.
- Structured scheme extraction with source references.
- Dynamic knowledge-base refresh with change detection.
- Agentic retrieval that decides when local knowledge is enough and when fresh research is required.
- LangGraph-oriented agents for profile extraction, intent detection, research planning, hybrid retrieval, eligibility reasoning, action planning, and grounding.

## Layout

```text
crawler/                 Web crawling and extraction pipeline
agents/                  LangGraph-compatible agent nodes
models/                  Shared Pydantic data models
retrieval/               Hybrid BM25 + vector retrieval interfaces
evaluation/              RAG and eligibility evaluation metrics
storage/                 Structured JSONL storage and version metadata
```

## Quick Start

```bash
uv sync
uv run playwright install
ollama pull qwen2.5:14b
uv run python scripts/check_qwen.py
uv run python scripts/ingest_myscheme.py --query "student scholarship" --limit 50
```

Run the Chainlit app:

```bash
uv run chainlit run chainlit_app.py -w
```

Read `ARCHITECTURE.md`, `PROJECT_FLOW.md`, `CRAWLING_ARCHITECTURE.md`, `AGENT_DESIGN.md`, and `DECISIONS.md` for the full design.

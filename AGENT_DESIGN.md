# Agent Design

Gov Assist AI uses LangGraph because the workflow is stateful, conditional, and benefits from explicit graph edges. A linear chain is not enough because the system must decide whether to use existing knowledge, perform fresh crawling, or ask retrieval to try again.

## Agents

1. **Profile Agent**
   Extracts citizen attributes from the query, such as age, occupation, and category signals.

2. **Intent Agent**
   Detects whether the user wants scheme discovery, eligibility checking, or application guidance.

3. **Research Planner Agent**
   Decides whether existing indexed knowledge is sufficient or fresh web research is needed.

4. **Web Research Agent**
   Crawls myScheme, extracts structured scheme data, creates temporary knowledge, and passes chunks to retrieval.

5. **Hybrid Retrieval Agent**
   Uses BM25 for exact keyword matching and vector search for semantic matching.

6. **Eligibility Reasoning Agent**
   Determines whether the user appears eligible, partially eligible, or not eligible from grounded evidence.

7. **Action Plan Agent**
   Generates recommended actions, required documents, and application steps.

8. **Grounding Agent**
   Validates that generated answers are backed by retrieved source references.

## Agentic Features

- Dynamic crawl decisions.
- Retrieval quality checks.
- Freshness-aware knowledge refresh.
- Grounded final answers with source URLs.
- Temporary knowledge injection from live research.

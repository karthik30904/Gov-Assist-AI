# Decisions

## Why Crawling Is Needed

Government scheme data changes frequently. Eligibility rules, benefits, document requirements, application links, and ministry ownership can change without warning. A system that only relies on static PDFs risks stale or incomplete guidance.

## Why Agentic Retrieval Is Used

Agentic retrieval lets the system decide whether local knowledge is enough for the current query. If retrieval quality is weak or the local index is stale, the system can trigger fresh web research from myScheme before answering.

## Why LangGraph Was Chosen

LangGraph provides explicit state and conditional routing. This is useful for a workflow where the next step depends on retrieval quality, freshness, intent, and whether sources were found.

## Why Hybrid Retrieval Was Chosen

BM25 is strong for exact matches such as scheme names, ministries, caste categories, document names, and state names. Vector search is strong for semantic matches where users describe their situation naturally. Combining them improves recall and precision.

## Why myScheme Was Selected

myScheme is the primary official discovery portal for Indian government schemes. It provides a central entry point for schemes across ministries, states, categories, benefits, eligibility, documents, and application processes.

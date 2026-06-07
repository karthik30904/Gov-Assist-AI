# Crawling Architecture

## Modules

- `crawler/crawler.py`: orchestrates discovery, fetching, extraction, and storage.
- `crawler/page_discovery.py`: finds scheme URLs from myScheme seed pages and search pages.
- `crawler/content_extractor.py`: extracts scheme name, category, state, ministry, benefits, eligibility, documents, application process, links, and references.
- `crawler/html_cleaner.py`: removes noisy HTML and normalizes text.
- `crawler/metadata_extractor.py`: extracts page metadata, canonical URLs, timestamps, and content hashes.
- `crawler/scheduler.py`: runs daily refresh jobs.
- `crawler/dynamic_fetcher.py`: uses crawl4ai or Playwright when static HTML does not contain enough scheme evidence.

## Frameworks

- `aiohttp` and `asyncio` support fast concurrent HTTP crawling.
- `beautifulsoup4` supports stable HTML parsing and extraction.
- `playwright` is included for dynamic pages where content is rendered client-side.
- `crawl4ai` is included for deeper crawling and LLM-ready extraction where regular HTML parsing is insufficient.

## Incremental Update Strategy

Each extracted scheme has:

- `source_url`
- `content_hash`
- `last_updated`
- `version`
- `source_references`

When a page changes, the structured record version increments. Downstream indexing can then re-embed only changed chunks.

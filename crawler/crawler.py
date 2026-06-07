from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import aiohttp

from models import Scheme
from retrieval.chunking import chunk_scheme
from storage.json_store import JsonSchemeStore

from .content_extractor import ContentExtractor
from .dynamic_fetcher import DynamicFetcher
from .page_discovery import PageDiscovery


class MySchemeCrawler:
    def __init__(self, store: JsonSchemeStore | None = None) -> None:
        self.discovery = PageDiscovery()
        self.extractor = ContentExtractor()
        self.dynamic_fetcher = DynamicFetcher()
        self.store = store or JsonSchemeStore(Path("data/schemes.jsonl"))

    async def crawl(self, query: str | None = None, limit: int = 100) -> list[Scheme]:
        pages = await self.discovery.discover(query=query, limit=limit)
        schemes: list[Scheme] = []
        async with aiohttp.ClientSession(headers={"User-Agent": "GovAssistAI/0.1"}) as session:
            for page in pages:
                html = await self._fetch(session, page.url)
                if not html:
                    continue
                scheme = self.extractor.extract_scheme(html, page.url)
                self.store.upsert(scheme)
                schemes.append(scheme)
        return schemes

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> str | None:
        try:
            async with session.get(url, timeout=30) as response:
                if response.status >= 400:
                    return None
                html = await response.text()
                if self._looks_complete(html):
                    return html
        except aiohttp.ClientError:
            html = None

        html = await self.dynamic_fetcher.fetch_with_crawl4ai(url)
        if html and self._looks_complete(html):
            return html
        return await self.dynamic_fetcher.fetch_with_playwright(url)

    def _looks_complete(self, html: str | None) -> bool:
        if not html:
            return False
        lowered = html.lower()
        return any(marker in lowered for marker in ["eligibility", "benefit", "documents", "how to apply"])


async def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl myScheme and store structured scheme data.")
    parser.add_argument("--query", default=None, help="Optional scheme search keyword.")
    parser.add_argument("--limit", type=int, default=25, help="Maximum scheme pages to crawl.")
    args = parser.parse_args()

    crawler = MySchemeCrawler()
    schemes = await crawler.crawl(query=args.query, limit=args.limit)
    chunks = [chunk.model_dump() for scheme in schemes for chunk in chunk_scheme(scheme)]
    print(json.dumps({"schemes": len(schemes), "chunks": len(chunks)}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from .dynamic_fetcher import DynamicFetcher


MYSCHEME_BASE_URL = "https://www.myscheme.gov.in/"


@dataclass(frozen=True)
class DiscoveredPage:
    url: str
    title: str | None = None
    depth: int = 0


class PageDiscovery:
    def __init__(self, base_url: str = MYSCHEME_BASE_URL) -> None:
        self.base_url = base_url
        self.allowed_domain = urlparse(base_url).netloc
        self.dynamic_fetcher = DynamicFetcher()

    async def discover(self, query: str | None = None, limit: int = 100) -> list[DiscoveredPage]:
        seeds = self._seed_urls(query)
        seen: set[str] = set()
        results: list[DiscoveredPage] = []

        async with aiohttp.ClientSession(headers={"User-Agent": "GovAssistAI/0.1"}) as session:
            for seed in seeds:
                if len(results) >= limit:
                    break
                pages = await self._extract_links(session, seed)
                if not pages:
                    pages = await self._extract_rendered_links(seed)
                for page in pages:
                    if page.url not in seen:
                        seen.add(page.url)
                        results.append(page)
                    if len(results) >= limit:
                        break

        return results

    def _seed_urls(self, query: str | None) -> Iterable[str]:
        yield self.base_url
        yield urljoin(self.base_url, "search")
        yield urljoin(self.base_url, "schemes")
        if query:
            slug = self._slugify(query)
            yield urljoin(self.base_url, f"schemes/{slug}")
            yield urljoin(self.base_url, f"search?keyword={query}")
            yield urljoin(self.base_url, f"search?q={query}")

    async def _extract_links(self, session: aiohttp.ClientSession, url: str) -> list[DiscoveredPage]:
        try:
            async with session.get(url, timeout=30) as response:
                if response.status >= 400:
                    return []
                html = await response.text()
        except aiohttp.ClientError:
            return []

        soup = BeautifulSoup(html, "html.parser")
        pages: list[DiscoveredPage] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            absolute = urljoin(url, href)
            parsed = urlparse(absolute)
            if parsed.netloc != self.allowed_domain:
                continue
            if "/schemes/" not in parsed.path and "/scheme/" not in parsed.path:
                continue
            pages.append(
                DiscoveredPage(
                    url=absolute.split("#", 1)[0],
                    title=anchor.get_text(" ", strip=True) or None,
                    depth=1,
                )
            )
        return pages

    async def _extract_rendered_links(self, url: str) -> list[DiscoveredPage]:
        html = await self.dynamic_fetcher.fetch_with_playwright(url)
        if not html:
            return []
        return self._extract_links_from_html(html, url)

    def _extract_links_from_html(self, html: str, base_url: str) -> list[DiscoveredPage]:
        soup = BeautifulSoup(html, "html.parser")
        pages: list[DiscoveredPage] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)
            if parsed.netloc != self.allowed_domain:
                continue
            if "/schemes/" not in parsed.path and "/scheme/" not in parsed.path:
                continue
            pages.append(
                DiscoveredPage(
                    url=absolute.split("#", 1)[0],
                    title=anchor.get_text(" ", strip=True) or None,
                    depth=1,
                )
            )
        return pages

    def _slugify(self, query: str) -> str:
        return "-".join(part for part in query.lower().split() if part)

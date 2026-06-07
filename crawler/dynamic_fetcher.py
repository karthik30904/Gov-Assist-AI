from __future__ import annotations


class DynamicFetcher:
    async def fetch_with_playwright(self, url: str) -> str | None:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return None

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=45000)
            html = await page.content()
            await browser.close()
            return html

    async def fetch_with_crawl4ai(self, url: str) -> str | None:
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            return None

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            return getattr(result, "html", None) or getattr(result, "cleaned_html", None)

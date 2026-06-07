from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from .crawler import MySchemeCrawler


class DailyCrawlerScheduler:
    def __init__(self, crawler: MySchemeCrawler | None = None, hour_utc: int = 2) -> None:
        self.crawler = crawler or MySchemeCrawler()
        self.hour_utc = hour_utc

    async def run_forever(self) -> None:
        while True:
            await asyncio.sleep(self._seconds_until_next_run())
            await self.crawler.crawl(limit=500)

    def _seconds_until_next_run(self) -> float:
        now = datetime.now(timezone.utc)
        next_run = now.replace(hour=self.hour_utc, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return (next_run - now).total_seconds()

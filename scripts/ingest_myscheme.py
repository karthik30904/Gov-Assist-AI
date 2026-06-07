from __future__ import annotations

import argparse
import asyncio

from services import SchemeRagService


async def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape myScheme and index scheme chunks into ChromaDB.")
    parser.add_argument("--query", default=None, help="Optional search query, such as 'student scholarship'.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum scheme pages to scrape.")
    args = parser.parse_args()

    service = SchemeRagService()
    count = await service.ingest(query=args.query, limit=args.limit)
    print(f"Scraped and indexed {count} schemes into ChromaDB.")


if __name__ == "__main__":
    asyncio.run(main())

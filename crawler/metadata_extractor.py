from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_metadata(soup: BeautifulSoup, source_url: str) -> dict:
    parsed = urlparse(source_url)
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    description_node = soup.select_one("meta[name='description']")
    description = description_node.get("content") if description_node else None
    canonical_node = soup.select_one("link[rel='canonical']")
    canonical_url = canonical_node.get("href") if canonical_node else source_url

    return {
        "title": title,
        "description": description,
        "domain": parsed.netloc,
        "path": parsed.path,
        "canonical_url": canonical_url,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }

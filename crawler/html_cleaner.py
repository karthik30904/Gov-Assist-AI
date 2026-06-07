from __future__ import annotations

import re

from bs4 import BeautifulSoup


NOISE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "footer",
    "nav",
    "[aria-hidden='true']",
]


def clean_html(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    for selector in NOISE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()
    return soup


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def list_texts(nodes: list) -> list[str]:
    values: list[str] = []
    for node in nodes:
        text = normalize_text(node.get_text(" ", strip=True))
        if text and text not in values:
            values.append(text)
    return values

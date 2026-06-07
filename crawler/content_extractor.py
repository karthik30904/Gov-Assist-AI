from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import Scheme, SourceReference

from .html_cleaner import clean_html, list_texts, normalize_text
from .metadata_extractor import content_hash, extract_metadata


SECTION_ALIASES = {
    "benefits": ["benefit", "benefits"],
    "eligibility": ["eligibility", "eligible"],
    "required_documents": ["documents required", "required documents", "documents"],
    "application_process": ["application process", "how to apply", "process"],
}


class ContentExtractor:
    def extract_scheme(self, html: str, source_url: str) -> Scheme:
        soup = clean_html(html)
        text = normalize_text(soup.get_text(" ", strip=True))
        metadata = extract_metadata(soup, source_url)
        sections = self._extract_sections(soup)
        if not any(sections.values()):
            sections = self._extract_sections_from_text(text)

        scheme_name = self._first_text(
            soup,
            ["h1", "[data-testid*='scheme-title']", ".scheme-title", "title"],
            fallback=metadata.get("title") or "Unknown Scheme",
        )

        application_link = self._extract_application_link(soup, source_url)
        source_ref = SourceReference(
            title=scheme_name,
            url=source_url,
            section="scheme-page",
            extracted_at=datetime.now(timezone.utc),
        )

        return Scheme(
            scheme_name=scheme_name,
            category=self._metadata_value(soup, ["category", "scheme category"]),
            state=self._metadata_value(soup, ["state"]),
            ministry=self._metadata_value(soup, ["ministry", "department"]),
            benefits=sections["benefits"],
            eligibility=sections["eligibility"],
            required_documents=sections["required_documents"],
            application_process=sections["application_process"],
            application_link=application_link,
            source_url=source_url,
            source_references=[source_ref],
            metadata=metadata,
            content_hash=content_hash(text),
        )

    def _extract_sections(self, soup: BeautifulSoup) -> dict[str, list[str]]:
        sections = {key: [] for key in SECTION_ALIASES}
        headings = soup.find_all(re.compile("^h[1-6]$"))

        for heading in headings:
            heading_text = normalize_text(heading.get_text(" ", strip=True)).lower()
            target = self._section_key(heading_text)
            if not target:
                continue
            collected = []
            for sibling in heading.find_next_siblings():
                if sibling.name and re.match(r"h[1-6]", sibling.name):
                    break
                if sibling.name in {"ul", "ol"}:
                    collected.extend(list_texts(sibling.find_all("li")))
                elif sibling.name in {"p", "div", "section"}:
                    value = normalize_text(sibling.get_text(" ", strip=True))
                    if value:
                        collected.append(value)
            sections[target] = self._dedupe(collected)

        return sections

    def _section_key(self, heading_text: str) -> str | None:
        for key, aliases in SECTION_ALIASES.items():
            if any(alias in heading_text for alias in aliases):
                return key
        return None

    def _first_text(self, soup: BeautifulSoup, selectors: list[str], fallback: str) -> str:
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                value = normalize_text(node.get_text(" ", strip=True))
                if value:
                    return value
        return fallback

    def _metadata_value(self, soup: BeautifulSoup, labels: list[str]) -> str | None:
        label_pattern = re.compile("|".join(re.escape(label) for label in labels), re.I)
        for node in soup.find_all(string=label_pattern):
            parent = node.parent
            if not parent:
                continue
            text = normalize_text(parent.get_text(" ", strip=True))
            parts = re.split(r":|-", text, maxsplit=1)
            if len(parts) == 2 and parts[1].strip():
                return parts[1].strip()
        return None

    def _extract_application_link(self, soup: BeautifulSoup, source_url: str) -> str | None:
        for anchor in soup.select("a[href]"):
            label = normalize_text(anchor.get_text(" ", strip=True)).lower()
            if "apply" in label or "application" in label:
                href = anchor.get("href")
                return urljoin(source_url, href) if href else None
        return source_url

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        output = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                output.append(value)
        return output

    def _extract_sections_from_text(self, text: str) -> dict[str, list[str]]:
        sections = {key: [] for key in SECTION_ALIASES}
        labels = {
            "benefits": r"benefits?",
            "eligibility": r"eligibility|eligible",
            "required_documents": r"documents required|required documents|documents",
            "application_process": r"application process|how to apply|process",
        }
        ordered = list(labels.items())
        lowered = text.lower()

        for index, (section, pattern) in enumerate(ordered):
            match = re.search(pattern, lowered)
            if not match:
                continue
            end = len(text)
            for _, next_pattern in ordered[index + 1 :]:
                next_match = re.search(next_pattern, lowered[match.end() :])
                if next_match:
                    end = match.end() + next_match.start()
                    break
            snippet = text[match.end() : end].strip(" :-")
            if snippet:
                sections[section] = self._dedupe(self._split_sentences(snippet))
        return sections

    def _split_sentences(self, text: str) -> list[str]:
        pieces = re.split(r"(?<=[.;])\s+|\s+[•]\s+|\n+", text)
        return [normalize_text(piece) for piece in pieces if len(normalize_text(piece)) > 20]

from __future__ import annotations

import hashlib

from models import Scheme, SchemeChunk


def chunk_scheme(scheme: Scheme) -> list[SchemeChunk]:
    sections = {
        "benefits": scheme.benefits,
        "eligibility": scheme.eligibility,
        "required_documents": scheme.required_documents,
        "application_process": scheme.application_process,
    }
    chunks: list[SchemeChunk] = []
    for section, values in sections.items():
        text = "\n".join(values).strip()
        if not text:
            continue
        chunk_id = hashlib.sha1(f"{scheme.source_url}:{section}:{text}".encode("utf-8")).hexdigest()
        chunks.append(
            SchemeChunk(
                chunk_id=chunk_id,
                scheme_name=scheme.scheme_name,
                text=text,
                source_url=scheme.source_url,
                section=section,
                metadata={
                    "category": scheme.category,
                    "state": scheme.state,
                    "ministry": scheme.ministry,
                    "version": scheme.version,
                    "last_updated": scheme.last_updated.isoformat(),
                },
            )
        )
    return chunks

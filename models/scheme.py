from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class SourceReference(BaseModel):
    title: str | None = None
    url: HttpUrl | str
    section: str | None = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Scheme(BaseModel):
    scheme_name: str
    category: str | None = None
    state: str | None = None
    ministry: str | None = None
    benefits: list[str] = Field(default_factory=list)
    eligibility: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    application_process: list[str] = Field(default_factory=list)
    application_link: HttpUrl | str | None = None
    source_url: HttpUrl | str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_references: list[SourceReference] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    content_hash: str | None = None
    version: int = 1


class SchemeChunk(BaseModel):
    chunk_id: str
    scheme_name: str
    text: str
    source_url: HttpUrl | str
    section: str
    metadata: dict[str, Any] = Field(default_factory=dict)

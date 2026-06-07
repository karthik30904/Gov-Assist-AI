from __future__ import annotations

import json
from pathlib import Path

from models import Scheme


class JsonSchemeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> list[Scheme]:
        if not self.path.exists():
            return []
        schemes = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                schemes.append(Scheme.model_validate_json(line))
        return schemes

    def upsert(self, scheme: Scheme) -> bool:
        schemes = self.all()
        updated = False
        output = []
        for existing in schemes:
            if str(existing.source_url) == str(scheme.source_url):
                if existing.content_hash == scheme.content_hash:
                    output.append(existing)
                else:
                    scheme.version = existing.version + 1
                    output.append(scheme)
                    updated = True
            else:
                output.append(existing)

        if not any(str(item.source_url) == str(scheme.source_url) for item in schemes):
            output.append(scheme)
            updated = True

        self.path.write_text(
            "\n".join(item.model_dump_json() for item in output) + ("\n" if output else ""),
            encoding="utf-8",
        )
        return updated

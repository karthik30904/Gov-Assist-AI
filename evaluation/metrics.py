from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class EvaluationMetrics:
    retrieval_precision: float
    retrieval_recall: float
    faithfulness: float
    freshness_score: float
    eligibility_accuracy: float
    source_coverage: float


def freshness_score(last_updated: datetime, max_age_days: int = 30) -> float:
    age_days = (datetime.now(timezone.utc) - last_updated).days
    return max(0.0, 1.0 - (age_days / max_age_days))

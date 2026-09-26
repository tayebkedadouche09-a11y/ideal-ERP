"""Dependency-free baseline cost matching.

The matcher is intentionally pluggable: exact/token matching works offline,
while a future embedding provider can implement the same interface without
creating a second cost catalog.
"""

from dataclasses import dataclass
import re


_TOKEN_RE = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class CostCandidate:
    item_code: str
    description: str
    score: float


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(value or "")}


def match_cost(query: str, catalog: list[dict], limit: int = 5) -> list[CostCandidate]:
    q = _tokens(query)
    if not q:
        return []

    candidates: list[CostCandidate] = []
    for row in catalog:
        description = str(row.get("description") or row.get("name") or "")
        code = str(row.get("item_code") or row.get("code") or "")
        terms = _tokens(description)
        if not terms:
            continue
        overlap = len(q & terms)
        score = overlap / len(q | terms)
        if query.strip().lower() in description.lower():
            score = max(score, 0.95)
        if score > 0:
            candidates.append(
                CostCandidate(item_code=code, description=description, score=round(score, 4))
            )

    candidates.sort(key=lambda item: (-item.score, item.item_code))
    return candidates[: max(1, limit)]

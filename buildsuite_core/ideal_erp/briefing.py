"""Deterministic daily briefing and priority ordering over existing ERP signals."""

from __future__ import annotations

from typing import Any

_TONE_SCORE = {
    "danger": 100,
    "warning": 70,
    "info": 45,
    "brand": 35,
    "success": 15,
    "muted": 0,
}


def prioritize_actions(alerts: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Rank existing alert signals; never invents a new business metric."""
    ranked = []
    for index, alert in enumerate(alerts or []):
        score = _TONE_SCORE.get(str(alert.get("tone") or "muted"), 0)
        value = float(alert.get("value") or 0)
        active = str(alert.get("tone") or "muted") != "muted"
        ranked.append(
            (
                -(100000 if active else 0) - score * 1000 - min(value, 999999),
                index,
                {
                    **alert,
                    "priority_score": score,
                    "priority_rank": 0,
                },
            )
        )

    ranked.sort(key=lambda row: (row[0], row[1]))
    out = []
    for rank, (_, _, item) in enumerate(ranked[: max(0, limit)], start=1):
        item["priority_rank"] = rank
        out.append(item)
    return out


def build_daily_briefing(
    *,
    role: str,
    greeting_sub: str,
    alerts: list[dict[str, Any]],
    cta: dict[str, Any] | None,
    active_projects: int = 0,
    at_risk_projects: int = 0,
) -> dict[str, Any]:
    priority = prioritize_actions(alerts)
    active = [a for a in priority if a.get("tone") != "muted"]
    summary = []

    if at_risk_projects:
        summary.append(f"{at_risk_projects} active project(s) need risk attention.")
    if active_projects:
        summary.append(f"{active_projects} active project(s) are in scope.")
    if active:
        summary.append(f"{len(active)} actionable signal(s) are open today.")
    if not summary:
        summary.append("No active priority signal is raised right now.")

    return {
        "role": role,
        "headline": greeting_sub,
        "summary": summary,
        "priority": priority,
        "primary_action": cta,
    }

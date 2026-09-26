"""Deterministic business intelligence primitives used by IDEAIL project snapshots."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from statistics import mean, pstdev
from typing import Any, Iterable


def forecast_series(values: Iterable[float], periods: int = 1) -> dict[str, Any]:
    data = [float(x) for x in values]
    if periods < 1:
        raise ValueError("periods must be at least 1")
    if not data:
        return {"history": [], "forecast": [0.0] * periods, "slope": 0.0, "intercept": 0.0}

    if len(data) == 1:
        return {
            "history": data,
            "forecast": [round(data[0], 4)] * periods,
            "slope": 0.0,
            "intercept": data[0],
        }

    x = list(range(1, len(data) + 1))
    x_mean = mean(x)
    y_mean = mean(data)
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    slope = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, data)) / denominator
    intercept = y_mean - slope * x_mean
    forecast = [max(0.0, slope * (len(data) + step) + intercept) for step in range(1, periods + 1)]
    return {
        "history": data,
        "forecast": [round(v, 4) for v in forecast],
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
    }


def detect_anomalies(values: Iterable[float], z_threshold: float = 2.5) -> list[dict[str, float | int | bool]]:
    data = [float(x) for x in values]
    if not data:
        return []
    if z_threshold <= 0:
        raise ValueError("z_threshold must be greater than zero")
    center = mean(data)
    spread = pstdev(data)
    result = []
    for index, value in enumerate(data):
        z = 0.0 if spread == 0 else (value - center) / spread
        result.append(
            {
                "index": index,
                "value": value,
                "z_score": round(z, 6),
                "anomaly": abs(z) >= z_threshold,
            }
        )
    return result


def lessons_learned(observations: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        category = str(row.get("category") or "general")
        grouped[category].append(dict(row))

    lessons = []
    for category, rows in sorted(grouped.items()):
        occurrences = len(rows)
        impact = sum(float(row.get("impact", 0)) for row in rows)
        root_causes = Counter(str(row.get("root_cause")) for row in rows if row.get("root_cause"))
        recommendations = Counter(str(row.get("recommendation")) for row in rows if row.get("recommendation"))
        lessons.append(
            {
                "category": category,
                "occurrences": occurrences,
                "impact": round(impact, 2),
                "top_root_causes": root_causes.most_common(3),
                "top_recommendations": recommendations.most_common(3),
                "evidence_count": sum(1 for row in rows if row.get("evidence")),
            }
        )
    return lessons


def project_anomaly_summary(
    *,
    cost_values: Iterable[float] = (),
    material_values: Iterable[float] = (),
    progress_values: Iterable[float] = (),
) -> dict[str, Any]:
    return {
        "cost": detect_anomalies(cost_values),
        "material": detect_anomalies(material_values),
        "progress": detect_anomalies(progress_values),
    }

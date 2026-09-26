"""Evidence-first Company Intelligence rule engine.

This is intentionally deterministic at the foundation. LLMs can later sit
behind the same result contract, but the ERP gets useful, explainable signals
without making an external model a system-of-record.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectSignal:
    project: str
    baseline_cost: float = 0.0
    actual_cost: float = 0.0
    planned_progress_pct: float = 0.0
    actual_progress_pct: float = 0.0
    baseline_end_days: float = 0.0
    forecast_end_days: float = 0.0
    material_variance_pct: float = 0.0


@dataclass(frozen=True, slots=True)
class Insight:
    project: str
    kind: str
    severity: str
    message: str
    evidence: tuple[str, ...]


def _pct_delta(actual: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (actual - baseline) / baseline * 100


def analyze_project(signal: ProjectSignal) -> list[Insight]:
    insights: list[Insight] = []
    cost_delta = _pct_delta(signal.actual_cost, signal.baseline_cost)
    progress_delta = signal.actual_progress_pct - signal.planned_progress_pct
    schedule_delta = signal.forecast_end_days - signal.baseline_end_days

    if cost_delta >= 10:
        insights.append(
            Insight(
                project=signal.project,
                kind="cost_overrun",
                severity="high" if cost_delta >= 20 else "medium",
                message=f"Actual cost is {cost_delta:.1f}% above the project baseline.",
                evidence=("baseline_cost", "actual_cost"),
            )
        )

    if progress_delta <= -10:
        insights.append(
            Insight(
                project=signal.project,
                kind="progress_gap",
                severity="high" if progress_delta <= -20 else "medium",
                message=f"Actual progress is {abs(progress_delta):.1f} percentage points behind plan.",
                evidence=("planned_progress_pct", "actual_progress_pct"),
            )
        )

    if schedule_delta >= 7:
        insights.append(
            Insight(
                project=signal.project,
                kind="schedule_risk",
                severity="high" if schedule_delta >= 21 else "medium",
                message=f"Forecast completion is {schedule_delta:.0f} days later than baseline.",
                evidence=("baseline_end_days", "forecast_end_days"),
            )
        )

    if signal.material_variance_pct >= 10:
        insights.append(
            Insight(
                project=signal.project,
                kind="material_variance",
                severity="medium",
                message=f"Material usage/cost is {signal.material_variance_pct:.1f}% above the expected baseline.",
                evidence=("material_variance_pct",),
            )
        )

    return insights


def analyze_projects(signals: list[ProjectSignal]) -> list[Insight]:
    result: list[Insight] = []
    for signal in signals:
        result.extend(analyze_project(signal))
    return result

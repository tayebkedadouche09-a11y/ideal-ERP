"""Integrated IDEAIL project flow.

The functions in this module deliberately operate on shared project facts:
project -> BOQ/estimate -> materials -> schedule -> actual cost -> billing
-> EVM -> risk/change intelligence.

They are pure Python so they can be tested without a running Frappe site and
called by Frappe APIs/DocTypes as one connected capability layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

from buildsuite_core.ideal_erp.industry.resin_epoxy import (
    EpoxyEstimateInput,
    estimate_epoxy_job,
)
from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
    ProjectSignal,
    analyze_project,
)
from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost


def _pct_delta(actual: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (actual - baseline) / baseline * 100.0


def _money(value: float) -> float:
    return round(float(value), 2)


@dataclass(frozen=True, slots=True)
class BillingLine:
    description: str
    contract_qty: float
    contract_rate: float
    previous_qty: float
    current_qty: float


@dataclass(frozen=True, slots=True)
class BillingResult:
    gross_current: float
    cumulative_before: float
    cumulative_after: float
    retention_amount: float
    advance_recovery: float
    other_deductions: float
    net_payable: float
    total_retention_held: float
    lines: tuple[dict[str, Any], ...]


def calculate_ipc(
    lines: Iterable[dict[str, Any] | BillingLine],
    *,
    previous_cumulative_amount: float = 0.0,
    retention_percent: float = 10.0,
    advance_recovery_amount: float = 0.0,
    other_deductions: float = 0.0,
    previous_retention_held: float = 0.0,
) -> BillingResult:
    """Calculate an IPC/progress billing certificate before posting an invoice."""
    if retention_percent < 0:
        raise ValueError("retention_percent cannot be negative")

    normalized: list[dict[str, Any]] = []
    gross = 0.0

    for raw in lines:
        item = raw if isinstance(raw, BillingLine) else BillingLine(
            description=str(raw.get("description") or raw.get("boq_item_ref") or "Item"),
            contract_qty=float(raw.get("contract_qty", 0)),
            contract_rate=float(raw.get("contract_rate", 0)),
            previous_qty=float(raw.get("previous_qty", 0)),
            current_qty=float(raw.get("current_qty", 0)),
        )
        if item.contract_qty < 0 or item.previous_qty < 0 or item.current_qty < 0:
            raise ValueError(f"Negative quantity is invalid for {item.description}")
        cumulative_qty = item.previous_qty + item.current_qty
        if cumulative_qty > item.contract_qty + 1e-9:
            raise ValueError(
                f"Cumulative quantity exceeds contract quantity for {item.description}"
            )
        contract_amount = item.contract_qty * item.contract_rate
        current_amount = item.current_qty * item.contract_rate
        cumulative_amount = cumulative_qty * item.contract_rate
        percent_complete = (
            cumulative_amount / contract_amount * 100 if contract_amount else 0.0
        )
        gross += current_amount
        normalized.append(
            {
                "description": item.description,
                "contract_qty": item.contract_qty,
                "contract_rate": item.contract_rate,
                "contract_amount": _money(contract_amount),
                "previous_qty": item.previous_qty,
                "current_qty": item.current_qty,
                "cumulative_qty": cumulative_qty,
                "current_amount": _money(current_amount),
                "cumulative_amount": _money(cumulative_amount),
                "percent_complete": round(percent_complete, 4),
            }
        )

    retention = gross * retention_percent / 100.0
    net = gross - retention - advance_recovery_amount - other_deductions
    if net < -1e-9:
        raise ValueError("Deductions cannot exceed the current gross amount")

    return BillingResult(
        gross_current=_money(gross),
        cumulative_before=_money(previous_cumulative_amount),
        cumulative_after=_money(previous_cumulative_amount + gross),
        retention_amount=_money(retention),
        advance_recovery=_money(advance_recovery_amount),
        other_deductions=_money(other_deductions),
        net_payable=_money(max(0.0, net)),
        total_retention_held=_money(previous_retention_held + retention),
        lines=tuple(normalized),
    )


def calculate_retention_release(
    *,
    total_retention_held: float,
    amount_requested: float,
    already_released: float = 0.0,
) -> dict[str, float]:
    """Return the remaining retention balance and validate a release request."""
    available = max(0.0, total_retention_held - already_released)
    if amount_requested < 0:
        raise ValueError("amount_requested cannot be negative")
    if amount_requested > available + 1e-9:
        raise ValueError("Retention release exceeds the available retained balance")
    return {
        "total_retention_held": _money(total_retention_held),
        "already_released": _money(already_released),
        "release_amount": _money(amount_requested),
        "balance_after_release": _money(available - amount_requested),
    }


@dataclass(frozen=True, slots=True)
class MaterialPlanLine:
    item_code: str
    planned_qty: float
    waste_pct: float
    required_qty: float
    consumed_qty: float
    available_qty: float
    ordered_qty: float
    qty_to_order: float
    estimated_rate: float
    estimated_value: float
    status: str
    required_by: str | None = None


def build_material_plan(rows: Iterable[dict[str, Any]]) -> tuple[MaterialPlanLine, ...]:
    """Calculate project material requirement against consumption, stock and POs."""
    result: list[MaterialPlanLine] = []
    for raw in rows:
        planned = float(raw.get("planned_qty", raw.get("boq_qty", 0)))
        waste = float(raw.get("waste_pct", raw.get("waste_factor", 0)))
        consumed = float(raw.get("consumed_qty", 0))
        available = float(raw.get("available_qty", 0))
        ordered = float(raw.get("ordered_qty", raw.get("already_ordered_qty", 0)))
        rate = float(raw.get("estimated_rate", 0))
        required = max(0.0, planned * (1.0 + waste / 100.0))
        remaining = max(0.0, required - consumed)
        to_order = max(0.0, remaining - available - ordered)
        if to_order <= 1e-9:
            status = "covered"
        elif available + ordered > 0:
            status = "partial_shortage"
        else:
            status = "shortage"
        result.append(
            MaterialPlanLine(
                item_code=str(raw.get("item_code") or ""),
                planned_qty=planned,
                waste_pct=waste,
                required_qty=_money(required),
                consumed_qty=consumed,
                available_qty=available,
                ordered_qty=ordered,
                qty_to_order=_money(to_order),
                estimated_rate=rate,
                estimated_value=_money(to_order * rate),
                status=status,
                required_by=raw.get("required_by"),
            )
        )
    return tuple(result)


def draft_estimate(
    lines: Iterable[dict[str, Any]],
    catalog: Iterable[dict[str, Any]],
    *,
    margin_percent: float = 20.0,
) -> dict[str, Any]:
    """Produce a traceable estimate draft from the canonical cost catalog.

    This is the deterministic baseline behind the future AI provider. It never
    mutates a BOQ, quote or accounting record on its own.
    """
    catalog_list = list(catalog)
    result_lines: list[dict[str, Any]] = []
    total_cost = 0.0
    total_price = 0.0

    for raw in lines:
        description = str(raw.get("description") or raw.get("name") or "")
        quantity = float(raw.get("quantity", raw.get("qty", 0)))
        matches = match_cost(description, catalog_list, 1)
        match = matches[0] if matches else None
        rate = float(raw.get("rate", match.score and raw.get("fallback_rate", 0) or 0))
        if match and "rate" in (catalog_list and catalog_list[0] or {}):
            rate = float(next(
                (row.get("rate", 0) for row in catalog_list if row.get("item_code") == match.item_code),
                rate,
            ))
        line_cost = quantity * rate
        line_price = line_cost * (1.0 + margin_percent / 100.0)
        total_cost += line_cost
        total_price += line_price
        result_lines.append(
            {
                "description": description,
                "quantity": quantity,
                "item_code": match.item_code if match else None,
                "matched_description": match.description if match else None,
                "match_score": match.score if match else 0.0,
                "rate": _money(rate),
                "cost": _money(line_cost),
                "sell_price": _money(line_price),
                "needs_human_confirmation": match is None,
            }
        )

    return {
        "lines": result_lines,
        "total_cost": _money(total_cost),
        "total_sell_price": _money(total_price),
        "gross_margin_percent": margin_percent,
        "requires_human_confirmation": True,
        "source_of_truth_after_confirmation": "canonical BOQ + rate master",
    }


def estimate_industry_job(profile: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize construction finishing profiles onto one technical estimator."""
    normalized = profile.strip().lower()
    if normalized not in {
        "epoxy",
        "resin",
        "industrial_flooring",
        "waterproofing",
        "decorative_concrete",
        "technical_coatings",
    }:
        raise ValueError("Unsupported industry profile")

    if normalized in {"epoxy", "resin", "industrial_flooring", "technical_coatings"}:
        result = estimate_epoxy_job(EpoxyEstimateInput(**payload))
        return {
            "profile": normalized,
            "technical": {
                "coating_mix_kg": result.coating_mix_kg,
                "resin_kg": result.resin_kg,
                "hardener_kg": result.hardener_kg,
                "primer_kg": result.primer_kg,
                "labor_hours": result.labor_hours,
            },
            "cost": {
                "material": _money(result.material_cost),
                "labor": _money(result.labor_cost),
                "equipment": _money(result.equipment_cost),
                "total": _money(result.total_cost),
            },
        }

    # Waterproofing/decorative concrete can use the same commercial flow even
    # when the technical recipe is supplied by the BOQ/rate master.
    quantity = float(payload.get("quantity", payload.get("area_m2", 0)))
    unit_cost = float(payload.get("unit_cost", 0))
    labor = float(payload.get("labor_cost", 0))
    return {
        "profile": normalized,
        "technical": {"quantity": quantity},
        "cost": {
            "material": _money(quantity * unit_cost),
            "labor": _money(labor),
            "equipment": _money(float(payload.get("equipment_cost", 0))),
            "total": _money(quantity * unit_cost + labor + float(payload.get("equipment_cost", 0))),
        },
    }


def build_project_snapshot(
    *,
    project: str,
    project_signal: dict[str, Any],
    billing_lines: Iterable[dict[str, Any]] = (),
    billing_context: dict[str, Any] | None = None,
    material_rows: Iterable[dict[str, Any]] = (),
    evm_rows: Iterable[dict[str, Any]] = (),
    tasks: Iterable[dict[str, Any]] = (),
    change_orders: Iterable[dict[str, Any]] = (),
    risk_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the whole connected project intelligence flow from shared facts."""
    billing_context = billing_context or {}
    material = build_material_plan(material_rows)
    evm = calculate_evm(evm_rows)
    schedule = analyze_schedule(tasks)
    changes = analyze_change_orders(change_orders)

    signal = ProjectSignal(
        project=project,
        baseline_cost=float(project_signal.get("baseline_cost", 0)),
        actual_cost=float(project_signal.get("actual_cost", evm["actual_cost"])),
        planned_progress_pct=float(project_signal.get("planned_progress_pct", 0)),
        actual_progress_pct=float(project_signal.get("actual_progress_pct", 0)),
        baseline_end_days=float(project_signal.get("baseline_end_days", schedule["planned_duration_days"])),
        forecast_end_days=float(project_signal.get("forecast_end_days", schedule["forecast_duration_days"])),
        material_variance_pct=float(project_signal.get("material_variance_pct", 0)),
    )
    insights = analyze_project(signal)

    risk = assess_project_risk(
        evm=evm,
        schedule=schedule,
        material=list(material),
        change_orders=changes,
        extra=risk_context or {},
    )

    billing = calculate_ipc(
        billing_lines,
        previous_cumulative_amount=float(billing_context.get("previous_cumulative_amount", 0)),
        retention_percent=float(billing_context.get("retention_percent", 10)),
        advance_recovery_amount=float(billing_context.get("advance_recovery_amount", 0)),
        other_deductions=float(billing_context.get("other_deductions", 0)),
        previous_retention_held=float(billing_context.get("previous_retention_held", 0)),
    )

    return {
        "project": project,
        "billing": {
            "gross_current": billing.gross_current,
            "cumulative_after": billing.cumulative_after,
            "retention_amount": billing.retention_amount,
            "net_payable": billing.net_payable,
            "total_retention_held": billing.total_retention_held,
            "lines": list(billing.lines),
        },
        "materials": [
            {
                "item_code": x.item_code,
                "required_qty": x.required_qty,
                "qty_to_order": x.qty_to_order,
                "estimated_value": x.estimated_value,
                "status": x.status,
            }
            for x in material
        ],
        "evm": evm,
        "schedule": schedule,
        "changes": changes,
        "risk": risk,
        "insights": [
            {
                "kind": x.kind,
                "severity": x.severity,
                "message": x.message,
                "evidence": list(x.evidence),
            }
            for x in insights
        ],
        "single_source_flow": [
            "project",
            "boq_estimate",
            "materials",
            "schedule",
            "actual_cost",
            "billing",
            "evm",
            "risk_change_intelligence",
        ],
    }


def calculate_project_finance(
    *,
    contract_value: float,
    invoiced_net: float,
    outstanding_gross: float,
    actual_cost: float,
    open_commitment: float = 0.0,
) -> dict[str, Any]:
    """Reconcile commercial value, receivable, recognised cost and open commitments.

    Accounting remains in ERPNext; this helper only derives project-management metrics.
    """
    contract = max(0.0, float(contract_value))
    invoiced = max(0.0, float(invoiced_net))
    outstanding = max(0.0, float(outstanding_gross))
    cost = max(0.0, float(actual_cost))
    commitment = max(0.0, float(open_commitment))

    earned = min(contract, invoiced) if contract else invoiced
    unbilled = max(0.0, contract - invoiced)
    gross_profit = invoiced - cost
    margin_pct = gross_profit / invoiced * 100.0 if invoiced else 0.0
    projected_cost = cost + commitment

    return {
        "earned_commercial_value": _money(earned),
        "unbilled_contract_value": _money(unbilled),
        "invoiced_net": _money(invoiced),
        "outstanding": _money(outstanding),
        "estimated_cash_collected": _money(max(0.0, invoiced - outstanding)),
        "actual_cost": _money(cost),
        "gross_profit_on_invoiced": _money(gross_profit),
        "margin_percent_on_invoiced": round(margin_pct, 4),
        "open_commitment": _money(commitment),
        "projected_cost_position": _money(projected_cost),
        "projected_profit_position": _money(invoiced - projected_cost),
    }


def calculate_evm(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Calculate EVM/5D metrics without becoming an accounting ledger."""
    bac = pv = ev = ac = 0.0
    for row in rows:
        budget = float(row.get("budget", row.get("bac", 0)))
        planned_pct = max(0.0, min(100.0, float(row.get("planned_pct", 0))))
        actual_pct = max(0.0, min(100.0, float(row.get("actual_pct", 0))))
        actual_cost = float(row.get("actual_cost", row.get("ac", 0)))
        bac += budget
        pv += budget * planned_pct / 100.0
        ev += budget * actual_pct / 100.0
        ac += actual_cost

    cpi = ev / ac if ac else 0.0
    spi = ev / pv if pv else 0.0
    eac = ac + (bac - ev) / cpi if cpi > 0 else ac
    etc = max(0.0, eac - ac)
    vac = bac - eac

    return {
        "bac": _money(bac),
        "planned_value": _money(pv),
        "earned_value": _money(ev),
        "actual_cost": _money(ac),
        "cpi": round(cpi, 4),
        "spi": round(spi, 4),
        "estimate_at_completion": _money(eac),
        "estimate_to_complete": _money(etc),
        "variance_at_completion": _money(vac),
    }


def analyze_schedule(tasks: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Topologically calculate the canonical task network and critical path."""
    nodes = {str(t["id"]): t for t in tasks if t.get("id")}
    if not nodes:
        return {
            "planned_duration_days": 0.0,
            "forecast_duration_days": 0.0,
            "critical_tasks": [],
            "task_offsets": {},
            "cycle_detected": False,
        }

    start: dict[str, float] = {}
    finish: dict[str, float] = {}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> float:
        if node_id in visiting:
            raise ValueError("Task dependency cycle detected")
        if node_id in visited:
            return finish[node_id]
        visiting.add(node_id)
        raw = nodes[node_id]
        preds = [str(x) for x in raw.get("predecessors", raw.get("depends_on", []))]
        predecessor_finish = 0.0
        for pred in preds:
            if pred not in nodes:
                raise ValueError(f"Unknown predecessor {pred} for task {node_id}")
            predecessor_finish = max(predecessor_finish, visit(pred))
        start[node_id] = predecessor_finish
        duration = max(0.0, float(raw.get("duration_days", raw.get("duration", 0))))
        finish[node_id] = predecessor_finish + duration
        visiting.remove(node_id)
        visited.add(node_id)
        return finish[node_id]

    for node_id in nodes:
        visit(node_id)

    planned = max(finish.values(), default=0.0)
    delay_days = max(
        [float(x.get("delay_days", 0)) for x in nodes.values()] + [0.0]
    )
    forecast = planned + delay_days
    critical = [
        node_id
        for node_id, end in finish.items()
        if end >= planned - 1e-9
    ]
    return {
        "planned_duration_days": _money(planned),
        "forecast_duration_days": _money(forecast),
        "critical_tasks": critical,
        "task_offsets": {
            task_id: {"start": _money(start[task_id]), "finish": _money(finish[task_id])}
            for task_id in nodes
        },
        "cycle_detected": False,
    }


def analyze_change_orders(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate scope-change impacts while preserving approval status."""
    total_cost = 0.0
    total_days = 0.0
    pending = 0
    approved = 0
    evidence_gaps = 0

    for row in rows:
        status = str(row.get("status", "Pending Approval"))
        cost = float(row.get("cost_impact", row.get("impact", 0)))
        days = float(row.get("days_impact", 0))
        evidence_complete = bool(row.get("evidence_complete", row.get("evidence", True)))
        if status == "Approved":
            approved += 1
            total_cost += cost
            total_days += days
        else:
            pending += 1
        if not evidence_complete:
            evidence_gaps += 1

    return {
        "approved_count": approved,
        "pending_count": pending,
        "approved_cost_impact": _money(total_cost),
        "approved_days_impact": _money(total_days),
        "evidence_gaps": evidence_gaps,
        "requires_action": pending > 0 or evidence_gaps > 0,
    }


def assess_project_risk(
    *,
    evm: dict[str, Any],
    schedule: dict[str, Any],
    material: Iterable[MaterialPlanLine],
    change_orders: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Explainable project risk score based only on project execution evidence."""
    extra = extra or {}
    score = 0.0
    drivers: list[str] = []

    if evm["cpi"] and evm["cpi"] < 0.9:
        score += 30
        drivers.append("cost_efficiency")
    if evm["spi"] and evm["spi"] < 0.9:
        score += 30
        drivers.append("schedule_efficiency")
    shortages = sum(1 for item in material if item.status != "covered")
    if shortages:
        score += min(20.0, shortages * 5.0)
        drivers.append("material_shortage")
    if schedule["forecast_duration_days"] > schedule["planned_duration_days"] + 7:
        score += 15
        drivers.append("schedule_delay")
    if change_orders["pending_count"]:
        score += min(15.0, change_orders["pending_count"] * 5.0)
        drivers.append("pending_change_orders")
    if change_orders["evidence_gaps"]:
        score += min(10.0, change_orders["evidence_gaps"] * 2.5)
        drivers.append("evidence_gaps")
    score += float(extra.get("risk_points", 0))

    score = min(100.0, score)
    level = "high" if score >= 70 else "medium" if score >= 40 else "low"
    return {
        "score": round(score, 2),
        "level": level,
        "drivers": drivers,
        "explainable": True,
    }

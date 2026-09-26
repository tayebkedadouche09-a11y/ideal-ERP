"""Whitelisted entry points for the unified IDEAIL capability layer."""

import frappe

from buildsuite_core.ideal_erp.industry.resin_epoxy import (
    EpoxyEstimateInput,
    estimate_epoxy_job,
)
from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
    ProjectSignal,
    analyze_projects,
)
from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost
from buildsuite_core.ideal_erp.registry import get_registry


@frappe.whitelist()
def capabilities() -> dict:
    return get_registry()


@frappe.whitelist()
def estimate_resin_job(**payload) -> dict:
    result = estimate_epoxy_job(EpoxyEstimateInput(**payload))
    return {
        "coating_mix_kg": result.coating_mix_kg,
        "resin_kg": result.resin_kg,
        "hardener_kg": result.hardener_kg,
        "primer_kg": result.primer_kg,
        "labor_hours": result.labor_hours,
        "material_cost": result.material_cost,
        "labor_cost": result.labor_cost,
        "equipment_cost": result.equipment_cost,
        "total_cost": result.total_cost,
    }


@frappe.whitelist()
def analyze_company_projects(records: list[dict]) -> list[dict]:
    signals = [ProjectSignal(**row) for row in records]
    return [
        {
            "project": item.project,
            "kind": item.kind,
            "severity": item.severity,
            "message": item.message,
            "evidence": list(item.evidence),
        }
        for item in analyze_projects(signals)
    ]


@frappe.whitelist()
def semantic_match(query: str, catalog: list[dict], limit: int = 5) -> list[dict]:
    return [
        {
            "item_code": item.item_code,
            "description": item.description,
            "score": item.score,
        }
        for item in match_cost(query, catalog, int(limit))
    ]

from math import isclose

from buildsuite_core.ideal_erp.industry.resin_epoxy import EpoxyEstimateInput, estimate_epoxy_job
from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
    ProjectSignal,
    analyze_project,
)
from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost


def test_epoxy_estimate_is_deterministic():
    result = estimate_epoxy_job(
        EpoxyEstimateInput(
            area_m2=100,
            thickness_mm=2,
            density_kg_per_l=1.5,
            waste_pct=5,
            primer_kg_per_m2=0.2,
            material_cost_per_kg=100,
            primer_cost_per_kg=60,
            labor_hours_per_10m2=0.5,
            labor_rate_per_hour=500,
            equipment_cost=1000,
        )
    )
    assert isclose(result.coating_mix_kg, 315.0)
    assert isclose(result.primer_kg, 21.0)
    assert isclose(result.labor_hours, 5.0)


def test_company_intelligence_explains_cost_and_progress():
    insights = analyze_project(
        ProjectSignal(
            project="P-001",
            baseline_cost=100000,
            actual_cost=125000,
            planned_progress_pct=60,
            actual_progress_pct=35,
        )
    )
    kinds = {item.kind for item in insights}
    assert "cost_overrun" in kinds
    assert "progress_gap" in kinds
    assert all(item.evidence for item in insights)


def test_semantic_cost_match_ranks_relevant_items():
    result = match_cost(
        "epoxy primer industrial floor",
        [
            {"item_code": "MAT-01", "description": "industrial epoxy primer"},
            {"item_code": "MAT-02", "description": "cement plaster"},
        ],
    )
    assert result[0].item_code == "MAT-01"

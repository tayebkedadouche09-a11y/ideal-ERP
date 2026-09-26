from math import isclose

from buildsuite_core.ideal_erp.analytics import (
    detect_anomalies,
    forecast_series,
    lessons_learned,
)
from buildsuite_core.ideal_erp.field_and_digital import (
    approval_gate,
    inventory_variance,
    normalize_cad_bim_takeoff,
    normalize_document,
    normalize_site_diary,
    parse_voice_capture,
)
from buildsuite_core.ideal_erp.industry.resin_epoxy import (
    EpoxyEstimateInput,
    estimate_epoxy_job,
)
from buildsuite_core.ideal_erp.integrated_flow import (
    analyze_change_orders,
    analyze_schedule,
    assess_project_risk,
    build_material_plan,
    build_project_snapshot,
    calculate_evm,
    calculate_ipc,
    calculate_retention_release,
    draft_estimate,
)
from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
    ProjectSignal,
    analyze_project,
)
from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost
from buildsuite_core.ideal_erp.registry import validate_dependency_graph


def test_dependency_graph_is_closed():
    assert validate_dependency_graph() == []


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


def test_ipc_and_retention_are_one_flow():
    result = calculate_ipc(
        [
            {
                "description": "flooring",
                "contract_qty": 100,
                "contract_rate": 1000,
                "previous_qty": 20,
                "current_qty": 30,
            }
        ],
        retention_percent=10,
        previous_retention_held=5000,
    )
    assert result.gross_current == 30000
    assert result.retention_amount == 3000
    assert result.net_payable == 27000

    released = calculate_retention_release(
        total_retention_held=result.total_retention_held,
        amount_requested=2000,
    )
    assert released["balance_after_release"] == 6000


def test_ipc_rejects_overclaim():
    try:
        calculate_ipc(
            [
                {
                    "description": "flooring",
                    "contract_qty": 10,
                    "contract_rate": 100,
                    "previous_qty": 9,
                    "current_qty": 2,
                }
            ]
        )
    except ValueError as exc:
        assert "exceeds contract quantity" in str(exc)
    else:
        raise AssertionError("overclaim should fail")


def test_material_plan_connects_boq_consumption_stock_and_procurement():
    lines = build_material_plan(
        [
            {
                "item_code": "RESIN",
                "planned_qty": 100,
                "waste_pct": 5,
                "consumed_qty": 20,
                "available_qty": 10,
                "ordered_qty": 30,
                "estimated_rate": 200,
            }
        ]
    )
    assert lines[0].required_qty == 105
    assert lines[0].qty_to_order == 45
    assert lines[0].status == "partial_shortage"


def test_evm_and_schedule():
    evm = calculate_evm(
        [
            {
                "budget": 100000,
                "planned_pct": 60,
                "actual_pct": 40,
                "actual_cost": 50000,
            }
        ]
    )
    assert evm["bac"] == 100000
    assert evm["planned_value"] == 60000
    assert evm["earned_value"] == 40000
    assert evm["cpi"] == 0.8

    schedule = analyze_schedule(
        [
            {"id": "A", "duration_days": 5, "predecessors": []},
            {"id": "B", "duration_days": 7, "predecessors": ["A"]},
        ]
    )
    assert schedule["planned_duration_days"] == 12
    assert schedule["critical_tasks"] == ["B"]


def test_schedule_rejects_cycles():
    try:
        analyze_schedule(
            [
                {"id": "A", "duration_days": 1, "predecessors": ["B"]},
                {"id": "B", "duration_days": 1, "predecessors": ["A"]},
            ]
        )
    except ValueError as exc:
        assert "cycle" in str(exc).lower()
    else:
        raise AssertionError("cycle should fail")


def test_change_risk_and_project_snapshot_are_connected():
    changes = analyze_change_orders(
        [
            {
                "status": "Approved",
                "cost_impact": 10000,
                "days_impact": 4,
                "evidence_complete": True,
            },
            {
                "status": "Pending Approval",
                "cost_impact": 5000,
                "days_impact": 2,
                "evidence_complete": False,
            },
        ]
    )
    assert changes["approved_cost_impact"] == 10000
    assert changes["pending_count"] == 1
    assert changes["evidence_gaps"] == 1

    snapshot = build_project_snapshot(
        project="P-001",
        project_signal={
            "baseline_cost": 100000,
            "actual_cost": 95000,
            "planned_progress_pct": 50,
            "actual_progress_pct": 45,
        },
        billing_lines=[
            {
                "description": "coating",
                "contract_qty": 100,
                "contract_rate": 500,
                "previous_qty": 10,
                "current_qty": 20,
            }
        ],
        material_rows=[
            {
                "item_code": "MAT",
                "planned_qty": 100,
                "waste_pct": 5,
                "consumed_qty": 20,
                "available_qty": 0,
                "ordered_qty": 10,
                "estimated_rate": 100,
            }
        ],
        evm_rows=[
            {
                "budget": 100000,
                "planned_pct": 50,
                "actual_pct": 45,
                "actual_cost": 95000,
            }
        ],
        tasks=[
            {"id": "A", "duration_days": 5, "predecessors": [], "delay_days": 0}
        ],
        change_orders=[
            {
                "status": "Pending Approval",
                "cost_impact": 1000,
                "days_impact": 1,
                "evidence_complete": True,
            }
        ],
    )
    assert snapshot["billing"]["net_payable"] == 9000
    assert snapshot["risk"]["level"] in {"low", "medium", "high"}
    assert "evm" in snapshot
    assert "materials" in snapshot
    assert "schedule" in snapshot
    assert "changes" in snapshot


def test_estimation_document_voice_and_takeoff_are_connected():
    draft = draft_estimate(
        [{"description": "industrial epoxy primer", "quantity": 10}],
        [{"item_code": "MAT-01", "description": "industrial epoxy primer", "rate": 120}],
    )
    assert draft["lines"][0]["item_code"] == "MAT-01"
    assert draft["lines"][0]["rate"] == 120
    assert draft["requires_human_confirmation"] is True

    doc = normalize_document(
        document_id="DOC-1",
        project="P-001",
        title="Method Statement",
        status="Approved",
        required=True,
        approvals=["engineer"],
    )
    assert doc["ready_for_use"] is True

    voice = parse_voice_capture(
        "P-001",
        "Retard: commander matériau et prendre une photo",
        "fr",
    )
    assert voice.action_type in {"delay", "purchase", "photo"}
    assert voice.requires_approval is True

    takeoff = normalize_cad_bim_takeoff(
        project="P-001",
        source="BIM",
        rows=[{"description": "epoxy primer", "quantity": 20, "uom": "Kg"}],
        cost_catalog=[{"item_code": "MAT-01", "description": "industrial epoxy primer"}],
    )
    assert takeoff["items"][0]["item_code"] == "MAT-01"
    assert takeoff["requires_human_confirmation"] is True


def test_field_diary_photo_approval_inventory():
    diary = normalize_site_diary(
        project="P-001",
        entry_date="2026-09-26",
        narrative="Floor preparation completed",
        workers=4,
        photos=["FILE-1"],
        issues=["minor surface crack"],
    )
    assert diary["project"] == "P-001"
    assert diary["requires_approval"] is True

    approval = approval_gate(
        status="Draft",
        action="submit",
        required_role="Projects Manager",
    )
    assert approval["status"] == "Pending Approval"

    variance = inventory_variance(100, 108)
    assert variance["variance_qty"] == 8
    assert variance["variance_pct"] == 8


def test_forecasting_anomalies_and_lessons():
    forecast = forecast_series([10, 12, 14, 16], periods=2)
    assert forecast["forecast"] == [18.0, 20.0]

    anomalies = detect_anomalies([10, 10, 10, 100], z_threshold=1.0)
    assert anomalies[-1]["anomaly"] is True

    lessons = lessons_learned(
        [
            {
                "category": "procurement",
                "impact": 10,
                "root_cause": "late supplier",
                "recommendation": "dual-source",
                "evidence": "PO-1",
            },
            {
                "category": "procurement",
                "impact": 5,
                "root_cause": "late supplier",
                "recommendation": "dual-source",
                "evidence": "PO-2",
            },
        ]
    )
    assert lessons[0]["occurrences"] == 2
    assert lessons[0]["top_root_causes"][0][0] == "late supplier"


def test_project_risk_uses_connected_evidence():
    risk = assess_project_risk(
        evm={"cpi": 0.8, "spi": 0.8},
        schedule={
            "planned_duration_days": 10,
            "forecast_duration_days": 20,
        },
        material=[],
        change_orders={
            "pending_count": 1,
            "evidence_gaps": 1,
        },
    )
    assert risk["level"] in {"medium", "high"}
    assert risk["drivers"]

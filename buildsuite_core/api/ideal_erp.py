"""Whitelisted entry points for the connected IDEAIL capability layer."""

import frappe

from buildsuite_core.ideal_erp.analytics import (
    detect_anomalies,
    forecast_series,
    lessons_learned,
    project_anomaly_summary,
)
from buildsuite_core.ideal_erp.field_and_digital import (
    approval_gate,
    inventory_variance,
    normalize_cad_bim_takeoff,
    normalize_document,
    normalize_site_diary,
    normalize_takeoff,
    parse_voice_capture,
    photo_evidence,
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
    estimate_industry_job,
)
from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
    ProjectSignal,
    analyze_projects,
)
from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost
from buildsuite_core.ideal_erp.localization import (
    commercial_total,
    format_amount,
    resolve_localization,
)
from buildsuite_core.ideal_erp.registry import get_registry, validate_dependency_graph
from buildsuite_core.ideal_erp.project_finance import calculate_project_finance


def _plain(value):
    if hasattr(value, "__dataclass_fields__"):
        return {k: _plain(getattr(value, k)) for k in value.__dataclass_fields__}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


@frappe.whitelist()
def capabilities() -> dict:
    return get_registry()


@frappe.whitelist()
def validate_integration_graph() -> dict:
    errors = validate_dependency_graph()
    return {"ok": not errors, "errors": errors}


@frappe.whitelist()
def estimate_resin_job(**payload) -> dict:
    return _plain(estimate_epoxy_job(EpoxyEstimateInput(**payload)))


@frappe.whitelist()
def estimate_industry(profile: str, payload: dict) -> dict:
    return estimate_industry_job(profile, payload)


@frappe.whitelist()
def analyze_company_projects(records: list[dict]) -> list[dict]:
    return _plain(analyze_projects([ProjectSignal(**row) for row in records]))


@frappe.whitelist()
def semantic_match(query: str, catalog: list[dict], limit: int = 5) -> list[dict]:
    return _plain(match_cost(query, catalog, int(limit)))


@frappe.whitelist()
def calculate_ipc_preview(lines: list[dict], context: dict | None = None) -> dict:
    return _plain(calculate_ipc(lines, **(context or {})))


@frappe.whitelist()
def calculate_retention_preview(
    total_retention_held: float,
    amount_requested: float,
    already_released: float = 0,
) -> dict:
    return calculate_retention_release(
        total_retention_held=total_retention_held,
        amount_requested=amount_requested,
        already_released=already_released,
    )


@frappe.whitelist()
def material_plan(rows: list[dict]) -> list[dict]:
    return _plain(build_material_plan(rows))


@frappe.whitelist()
def ai_estimate(lines: list[dict], catalog: list[dict], margin_percent: float = 20) -> dict:
    return draft_estimate(lines, catalog, margin_percent=margin_percent)


@frappe.whitelist()
def schedule_analysis(tasks: list[dict]) -> dict:
    return analyze_schedule(tasks)


@frappe.whitelist()
def evm_snapshot(rows: list[dict]) -> dict:
    return calculate_evm(rows)


@frappe.whitelist()
def change_intelligence(rows: list[dict]) -> dict:
    return analyze_change_orders(rows)


@frappe.whitelist()
def risk_assessment(
    evm: dict,
    schedule: dict,
    material_rows: list[dict],
    changes: dict,
    extra: dict | None = None,
) -> dict:
    material_lines = build_material_plan(material_rows)
    return assess_project_risk(
        evm=evm,
        schedule=schedule,
        material=material_lines,
        change_orders=changes,
        extra=extra,
    )


@frappe.whitelist()
def project_snapshot(
    project: str,
    project_signal: dict,
    billing_lines: list[dict],
    billing_context: dict | None = None,
    material_rows: list[dict] | None = None,
    evm_rows: list[dict] | None = None,
    tasks: list[dict] | None = None,
    change_orders: list[dict] | None = None,
    risk_context: dict | None = None,
) -> dict:
    return build_project_snapshot(
        project=project,
        project_signal=project_signal,
        billing_lines=billing_lines,
        billing_context=billing_context,
        material_rows=material_rows or [],
        evm_rows=evm_rows or [],
        tasks=tasks or [],
        change_orders=change_orders or [],
        risk_context=risk_context,
    )


@frappe.whitelist()
def voice_capture(project: str, transcript: str, language: str = "auto") -> dict:
    return _plain(parse_voice_capture(project, transcript, language))


@frappe.whitelist()
def site_diary(
    project: str,
    entry_date: str,
    narrative: str,
    weather: str | None = None,
    workers: int = 0,
    photos: list[str] | None = None,
    issues: list[str] | None = None,
    measurements: list[dict] | None = None,
    actions: list[str] | None = None,
) -> dict:
    return normalize_site_diary(
        project=project,
        entry_date=entry_date,
        narrative=narrative,
        weather=weather,
        workers=workers,
        photos=photos or [],
        issues=issues or [],
        measurements=measurements or [],
        actions=actions or [],
    )


@frappe.whitelist()
def approval(
    status: str,
    action: str,
    required_role: str,
    approved_by: str | None = None,
) -> dict:
    return approval_gate(
        status=status,
        action=action,
        required_role=required_role,
        approved_by=approved_by,
    )


@frappe.whitelist()
def field_photo(
    project: str,
    file_ref: str,
    caption: str = "",
    captured_at: str | None = None,
    source: str = "mobile",
    task: str | None = None,
) -> dict:
    return photo_evidence(
        project=project,
        file_ref=file_ref,
        caption=caption,
        captured_at=captured_at,
        source=source,
        task=task,
    )


@frappe.whitelist()
def inventory_delta(planned_qty: float, actual_qty: float) -> dict:
    return inventory_variance(planned_qty, actual_qty)


@frappe.whitelist()
def document_metadata(
    document_id: str,
    project: str,
    title: str,
    version: str = "1.0",
    status: str = "Draft",
    required: bool = False,
    approvals: list[str] | None = None,
) -> dict:
    return normalize_document(
        document_id=document_id,
        project=project,
        title=title,
        version=version,
        status=status,
        required=required,
        approvals=approvals or [],
    )


@frappe.whitelist()
def takeoff_normalize(
    rows: list[dict],
    catalog: list[dict],
    source_type: str = "takeoff",
) -> list[dict]:
    return normalize_takeoff(rows, catalog, source_type=source_type)


@frappe.whitelist()
def cad_bim_takeoff(
    project: str,
    source: str,
    rows: list[dict],
    catalog: list[dict],
) -> dict:
    return normalize_cad_bim_takeoff(
        project=project,
        source=source,
        rows=rows,
        cost_catalog=catalog,
    )


@frappe.whitelist()
def forecast(values: list[float], periods: int = 3) -> dict:
    return forecast_series(values, periods=periods)


@frappe.whitelist()
def anomalies(values: list[float], z_threshold: float = 2.5) -> list[dict]:
    return detect_anomalies(values, z_threshold=z_threshold)


@frappe.whitelist()
def anomaly_summary(
    cost_values: list[float] | None = None,
    material_values: list[float] | None = None,
    progress_values: list[float] | None = None,
) -> dict:
    return project_anomaly_summary(
        cost_values=cost_values or [],
        material_values=material_values or [],
        progress_values=progress_values or [],
    )


@frappe.whitelist()
def lessons(rows: list[dict]) -> list[dict]:
    return lessons_learned(rows)


@frappe.whitelist()
def localize_amount(
    value: float,
    language: str = "fr",
    currency: str = "DZD",
) -> dict:
    loc = resolve_localization(language, currency)
    return {
        "formatted": format_amount(value, loc),
        "rtl": loc.rtl,
        "currency": loc.currency,
    }


@frappe.whitelist()
def commercial_calculation(
    net_amount: float,
    tax_rate_percent: float = 0,
    discount_percent: float = 0,
) -> dict:
    return commercial_total(
        net_amount=net_amount,
        tax_rate_percent=tax_rate_percent,
        discount_percent=discount_percent,
    )


def _live_approved_contract_value(project: str) -> float:
    rows = frappe.get_all(
        "BOQ",
        filters={"project": project, "status": "Approved"},
        fields=["planned_amount"],
        order_by="creation desc",
        limit=1,
    )
    if rows:
        return float(rows[0].planned_amount or 0)
    return float(frappe.db.get_value("Project", project, "estimated_costing") or 0)


def _live_invoice_totals(project: str) -> dict:
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"project": project, "docstatus": 1},
        fields=["name", "net_total", "grand_total", "outstanding_amount"],
    )
    return {
        "count": len(rows),
        "net_invoiced": sum(float(r.net_total or 0) for r in rows),
        "gross_invoiced": sum(float(r.grand_total or 0) for r in rows),
        "outstanding": sum(float(r.outstanding_amount or 0) for r in rows),
        "names": [r.name for r in rows],
    }


def _live_payment_totals(invoice_names: list[str]) -> dict:
    if not invoice_names:
        return {"count": 0, "allocated": 0.0}
    refs = frappe.get_all(
        "Payment Entry Reference",
        filters={
            "reference_doctype": "Sales Invoice",
            "reference_name": ["in", invoice_names],
            "docstatus": 1,
        },
        fields=["parent", "allocated_amount"],
    )
    payment_names = list({r.parent for r in refs})
    if not payment_names:
        return {"count": 0, "allocated": 0.0}
    valid = set(
        frappe.get_all(
            "Payment Entry",
            filters={
                "name": ["in", payment_names],
                "docstatus": 1,
                "payment_type": "Receive",
            },
            pluck="name",
        )
    )
    return {
        "count": len(valid),
        "allocated": sum(
            float(r.allocated_amount or 0) for r in refs if r.parent in valid
        ),
    }


def _live_open_commitments(project: str) -> dict:
    po_rows = frappe.get_all(
        "Purchase Order",
        filters={
            "project": project,
            "docstatus": 1,
            "status": ["not in", ["Completed", "Closed", "Cancelled"]],
        },
        fields=["grand_total"],
    )
    subcontract_rows = (
        frappe.get_all(
            "Subcontractor Work Order",
            filters={"project": project, "docstatus": 1},
            fields=["total_value"],
        )
        if frappe.db.exists("DocType", "Subcontractor Work Order")
        else []
    )
    po_value = sum(float(r.grand_total or 0) for r in po_rows)
    subcontract_value = sum(float(r.total_value or 0) for r in subcontract_rows)
    return {
        "purchase_orders": len(po_rows),
        "purchase_order_value": po_value,
        "subcontract_work_orders": len(subcontract_rows),
        "subcontract_committed_value": subcontract_value,
        "total_open_commitment": po_value + subcontract_value,
    }


@frappe.whitelist()
def project_financial_snapshot(project: str) -> dict:
    """Reconcile a project's commercial value, cash, actual cost and commitments."""
    if not project:
        frappe.throw("Project is required.")
    project_row = frappe.db.get_value(
        "Project",
        project,
        ["project_name", "company", "customer", "estimated_costing"],
        as_dict=True,
    )
    if not project_row:
        frappe.throw(f"Project {project} does not exist.")

    from buildsuite_core.api import boq_actuals

    contract_value = _live_approved_contract_value(project)
    invoices = _live_invoice_totals(project)
    payments = _live_payment_totals(invoices["names"])
    actuals = boq_actuals.get_actuals_summary(project)
    commitments = _live_open_commitments(project)
    finance = calculate_project_finance(
        contract_value=contract_value,
        invoiced_net=invoices["net_invoiced"],
        outstanding_gross=invoices["outstanding"],
        actual_cost=float(actuals["total"]),
        open_commitment=commitments["total_open_commitment"],
        invoiced_gross=float(invoices["gross_invoiced"]),
    )
    invoices.pop("names", None)

    return {
        "project": project,
        "project_name": project_row.project_name or project,
        "company": project_row.company,
        "customer": project_row.customer,
        "contract_value": contract_value,
        "invoices": invoices,
        "payments": payments,
        "actual_cost": actuals["total"],
        "actual_cost_by_type": {
            code: row.get("by_cost_type", {})
            for code, row in actuals.get("by_group", {}).items()
        },
        "commitments": commitments,
        "finance": finance,
        "source_of_truth": {
            "commercial": "ERPNext Sales Invoice",
            "cash": "ERPNext Payment Entry + Payment Entry Reference",
            "actual_cost": "BuildSuite BOQ Actuals",
            "commitments": "ERPNext Purchase Order + Subcontractor Work Order",
        },
    }


@frappe.whitelist(methods=["POST"])
def create_material_request_from_forecast(name: str) -> dict:
    """Create/reuse the canonical ERPNext Material Request for forecast shortages."""
    doc = frappe.get_doc("Material Forecast", name)
    doc.check_permission("write")
    return doc.create_material_request()


@frappe.whitelist()
def project_360(project: str) -> dict:
    """Return one live project view assembled from canonical module sources."""
    if not project:
        frappe.throw("Project is required.")

    from buildsuite_core.api import boq_actuals, cost_report, project_dashboard
    from buildsuite_core.ideal_erp.intelligence.company_intelligence import (
        ProjectSignal,
        analyze_project,
    )

    dashboard = project_dashboard.get_project_dashboard(project)
    cost = cost_report.cost_vs_budget_by_cost_code(project)
    actuals = boq_actuals.get_actuals_summary(project)
    finance = project_financial_snapshot(project)

    forecast_rows = frappe.get_all(
        "Material Forecast",
        filters={"project": project},
        fields=[
            "name",
            "status",
            "procurement_status",
            "material_request_ref",
            "total_forecast_qty_value",
            "modified",
        ],
        order_by="modified desc",
        limit=1,
    )
    forecast = forecast_rows[0] if forecast_rows else None

    project_row = frappe.db.get_value(
        "Project",
        project,
        ["expected_start_date", "expected_end_date"],
        as_dict=True,
    )
    health = (dashboard.get("health") or [{}])[0]
    baseline_days = 0.0
    if project_row and project_row.expected_start_date and project_row.expected_end_date:
        baseline_days = max(
            0.0,
            (project_row.expected_end_date - project_row.expected_start_date).days,
        )
    delayed_days = float(health.get("delayed") or 0)
    insights = analyze_project(
        ProjectSignal(
            project=project,
            baseline_cost=float(finance["contract_value"] or 0),
            actual_cost=float(finance["actual_cost"] or 0),
            planned_progress_pct=float(health.get("expected") or 0),
            actual_progress_pct=float(health.get("progress") or 0),
            baseline_end_days=baseline_days,
            forecast_end_days=baseline_days + delayed_days,
            material_variance_pct=0.0,
        )
    )

    return {
        "project": project,
        "dashboard": dashboard,
        "finance": finance,
        "cost_control": cost,
        "actuals": actuals,
        "material_forecast": forecast,
        "intelligence": [
            {
                "kind": item.kind,
                "severity": item.severity,
                "message": item.message,
                "evidence": list(item.evidence),
            }
            for item in insights
        ],
        "connected_sources": [
            "Project",
            "BOQ",
            "Tasks",
            "Material Forecast",
            "Material Request",
            "Purchase Order",
            "Material Consumption / Stock Entry",
            "Sales Invoice",
            "Payment Entry",
            "Scope Change Order",
            "Project Finance",
            "Company Intelligence",
        ],
    }

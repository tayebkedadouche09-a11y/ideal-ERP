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

    from frappe.utils import date_diff, flt, getdate, nowdate
    from buildsuite_core.api import boq_actuals, cost_report, project_dashboard, schedule
    from buildsuite_core.ideal_erp.integrated_flow import (
        MaterialPlanLine,
        analyze_change_orders,
        analyze_schedule,
        assess_project_risk,
        calculate_evm,
    )
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

    forecast_items = []
    material_lines = []
    shortage_value = 0.0
    if forecast:
        forecast_items = frappe.get_all(
            "Material Forecast Item",
            filters={"parent": forecast.name, "parenttype": "Material Forecast"},
            fields=[
                "item_code",
                "boq_qty",
                "waste_factor",
                "net_qty_required",
                "already_ordered_qty",
                "qty_to_order",
                "estimated_rate",
                "required_by_date",
            ],
            order_by="idx asc",
        )
        for row in forecast_items:
            qty_to_order = flt(row.qty_to_order)
            ordered = flt(row.already_ordered_qty)
            required = flt(row.net_qty_required) or flt(row.boq_qty)
            rate = flt(row.estimated_rate)
            shortage_value += qty_to_order * rate
            status = "covered"
            if qty_to_order > 0:
                status = "partial_shortage" if ordered > 0 else "shortage"
            material_lines.append(
                MaterialPlanLine(
                    item_code=row.item_code,
                    planned_qty=flt(row.boq_qty),
                    waste_pct=flt(row.waste_factor),
                    required_qty=required,
                    consumed_qty=0.0,
                    available_qty=max(0.0, required - ordered - qty_to_order),
                    ordered_qty=ordered,
                    qty_to_order=qty_to_order,
                    estimated_rate=rate,
                    estimated_value=qty_to_order * rate,
                    status=status,
                    required_by=row.required_by_date,
                )
            )

    project_row = frappe.db.get_value(
        "Project",
        project,
        ["expected_start_date", "expected_end_date"],
        as_dict=True,
    )
    health = (dashboard.get("health") or [{}])[0]

    schedule_data = schedule.get_project_schedule(project)
    schedule_tasks = []
    today = getdate(nowdate())
    for task_row in schedule_data.get("tasks", []):
        duration = 0.0
        if task_row.get("exp_start_date") and task_row.get("exp_end_date"):
            duration = max(
                0,
                date_diff(task_row.exp_end_date, task_row.exp_start_date) + 1,
            )
        delay_days = 0.0
        if (
            task_row.get("exp_end_date")
            and task_row.get("task_status") != "Completed"
            and getdate(task_row.exp_end_date) < today
        ):
            delay_days = max(0, date_diff(today, task_row.exp_end_date))
        schedule_tasks.append(
            {
                "id": task_row.name,
                "duration_days": duration,
                "delay_days": delay_days,
                "predecessors": [item["task"] for item in (task_row.get("predecessors") or [])],
            }
        )

    try:
        schedule_snapshot = analyze_schedule(schedule_tasks)
    except ValueError as exc:
        schedule_snapshot = {
            "planned_duration_days": 0.0,
            "forecast_duration_days": 0.0,
            "critical_tasks": [],
            "task_offsets": {},
            "cycle_detected": True,
            "error": str(exc),
        }

    contract_value = flt(finance["contract_value"])
    planned_progress = flt(health.get("expected"))
    actual_progress = flt(health.get("progress"))
    evm = calculate_evm(
        [
            {
                "budget": contract_value,
                "planned_pct": planned_progress,
                "actual_pct": actual_progress,
                "actual_cost": flt(finance["actual_cost"]),
            }
        ]
    )

    change_rows = frappe.get_all(
        "Scope Change Order",
        filters={"project": project},
        fields=["status", "impact", "recoverable", "reason"],
        order_by="raised_date desc, modified desc",
        limit_page_length=500,
    )
    changes = analyze_change_orders(
        [
            {
                "status": row.status,
                "cost_impact": flt(row.impact),
                "days_impact": 0,
                "evidence_complete": bool(row.reason) or row.status == "Approved",
            }
            for row in change_rows
        ]
    )
    risk = assess_project_risk(
        evm=evm,
        schedule=schedule_snapshot,
        material=material_lines,
        change_orders=changes,
    )

    baseline_days = 0.0
    if project_row and project_row.expected_start_date and project_row.expected_end_date:
        baseline_days = max(
            0.0,
            date_diff(project_row.expected_end_date, project_row.expected_start_date),
        )
    delayed_days = float(health.get("delayed") or 0)
    material_variance_pct = (
        shortage_value / flt(forecast.total_forecast_qty_value) * 100.0
        if forecast and flt(forecast.total_forecast_qty_value)
        else 0.0
    )
    insights = analyze_project(
        ProjectSignal(
            project=project,
            baseline_cost=contract_value,
            actual_cost=flt(finance["actual_cost"]),
            planned_progress_pct=planned_progress,
            actual_progress_pct=actual_progress,
            baseline_end_days=baseline_days,
            forecast_end_days=baseline_days + delayed_days,
            material_variance_pct=material_variance_pct,
        )
    )

    return {
        "project": project,
        "dashboard": dashboard,
        "finance": finance,
        "cost_control": cost,
        "actuals": actuals,
        "material_forecast": forecast,
        "evm": evm,
        "schedule": schedule_snapshot,
        "changes": changes,
        "risk": risk,
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


@frappe.whitelist(methods=["POST"])
def create_material_forecast_from_boq(boq: str, waste_pct: float = 5) -> dict:
    """Create a draft Material Forecast from the approved BOQ's material lines."""
    doc = frappe.get_doc("BOQ", boq)
    doc.check_permission("read")
    if not frappe.has_permission("Material Forecast", "create"):
        frappe.throw("You are not allowed to create a Material Forecast.", frappe.PermissionError)
    from buildsuite_core.ideal_erp.doctype.material_forecast.material_forecast import MaterialForecast

    return MaterialForecast.from_approved_boq(boq, waste_pct=float(waste_pct))


@frappe.whitelist(methods=["POST"])
def create_quotation_from_resin_estimate(customer: str, estimate: dict, project: str | None = None, title: str = "Resin / Epoxy Works", validity_days: int = 30, margin_percent: float = 20) -> dict:
    """Create a native ERPNext Quotation draft from a confirmed resin estimate."""
    if not customer:
        frappe.throw("Customer is required.")
    if not frappe.has_permission("Quotation", "create"):
        frappe.throw("You are not allowed to create quotations.", frappe.PermissionError)

    from buildsuite_core.api.invoice import ensure_invoice_item
    from buildsuite_core.utils.project import default_company
    from frappe.utils import add_days, nowdate, flt

    company = (
        frappe.db.get_value("Project", project, "company")
        if project
        else default_company()
    ) or default_company()

    quote = frappe.new_doc("Quotation")
    quote.quotation_to = "Customer"
    quote.party_name = customer
    quote.company = company
    quote.project = project or None
    quote.title = title
    quote.transaction_date = nowdate()
    quote.valid_till = add_days(nowdate(), max(0, int(validity_days)))
    quote.currency = frappe.db.get_value("Company", company, "default_currency")

    service_item = ensure_invoice_item()
    total_cost = flt(estimate.get("total_cost"))
    material_cost = flt(estimate.get("material_cost"))
    labor_cost = flt(estimate.get("labor_cost"))
    equipment_cost = flt(estimate.get("equipment_cost"))
    margin = flt(margin_percent)
    if margin < 0:
        frappe.throw("Margin cannot be negative.")
    total_price = total_cost * (1 + margin / 100)

    if total_price <= 0:
        frappe.throw("The estimate must produce a quotation amount greater than zero.")

    quote.append(
        "items",
        {
            "item_code": service_item,
            "item_name": title,
            "description": (
                f"Area {flt(estimate.get('area_m2')):g} m² · "
                f"Thickness {flt(estimate.get('thickness_mm')):g} mm · "
                f"Material {material_cost:,.2f} · Labour {labor_cost:,.2f} · Equipment {equipment_cost:,.2f}"
            ),
            "qty": 1,
            "rate": total_price,
        },
    )
    quote.insert()
    return {
        "name": quote.name,
        "customer": customer,
        "project": project,
        "total_cost": total_cost,
        "quoted_total": total_price,
        "margin_percent": margin,
        "source": "resin_epoxy_estimator",
    }


@frappe.whitelist()
def approval_center(limit: int = 100) -> dict:
    """Return actionable approval/workflow records for the current user."""
    from frappe.model.workflow import get_transitions, get_workflow, get_workflow_name
    from urllib.parse import quote

    specs = [
        ("Stage Planning", "workflow_state", {"Pending Approval"}),
        ("Scope Change Order", "status", {"Pending Approval"}),
        ("Material Request", "workflow_state", {"Pending Approval"}),
        ("Retention Release", "status", {"Draft"}),
        ("Sales Invoice", "workflow_state", {"Pending Approval"}),
        ("Purchase Order", "workflow_state", {"Pending Approval"}),
        ("Subcontractor Bill", "workflow_state", {"Pending Approval"}),
    ]

    items = []
    max_rows = max(1, min(int(limit), 250))

    for doctype, fallback_state_field, fallback_states in specs:
        if not frappe.db.exists("DocType", doctype):
            continue

        workflow_name = get_workflow_name(doctype)
        if workflow_name:
            workflow = get_workflow(doctype)
            state_field = workflow.workflow_state_field
            rows = frappe.get_list(
                doctype,
                fields=["name", state_field, "modified"],
                order_by="modified desc",
                limit_page_length=max_rows,
            )
            for row in rows:
                try:
                    doc = frappe.get_doc(doctype, row.name)
                    doc.check_permission("read")
                    transitions = get_transitions(doc, workflow)
                except Exception:
                    continue
                if not transitions:
                    continue
                actions = [
                    {
                        "action": transition.get("action"),
                        "next_state": transition.get("next_state"),
                    }
                    for transition in transitions
                ]
                items.append(
                    {
                        "doctype": doctype,
                        "name": row.name,
                        "state": row.get(state_field),
                        "title": row.get("title")
                        or row.get("project_name")
                        or row.get("subject")
                        or row.name,
                        "modified": row.modified,
                        "actions": actions,
                        "route": f"/records/{quote(doctype)}/{quote(row.name)}",
                        "source": "workflow",
                    }
                )
            continue

        if not frappe.get_meta(doctype).has_field(fallback_state_field):
            continue

        rows = frappe.get_list(
            doctype,
            filters={fallback_state_field: ["in", list(fallback_states)]},
            fields=["name", fallback_state_field, "modified"],
            order_by="modified desc",
            limit_page_length=max_rows,
        )
        for row in rows:
            title = (
                row.get("title")
                or row.get("project_name")
                or row.get("subject")
                or row.name
            )
            items.append(
                {
                    "doctype": doctype,
                    "name": row.name,
                    "state": row.get(fallback_state_field),
                    "title": title,
                    "modified": row.modified,
                    "actions": [],
                    "route": f"/records/{quote(doctype)}/{quote(row.name)}",
                    "source": "document_state",
                }
            )

    items.sort(key=lambda item: str(item.get("modified") or ""), reverse=True)
    return {
        "total": len(items),
        "items": items[:max_rows],
        "supported": [doctype for doctype, _, _ in specs if frappe.db.exists("DocType", doctype)],
    }


@frappe.whitelist(methods=["POST"])
def voice_to_work(
    project: str,
    transcript: str,
    language: str = "auto",
    confirm: int = 0,
    priority: str = "Medium",
) -> dict:
    """Turn a reviewed transcript into a real draft work item.

    Speech recognition happens outside this endpoint; this function receives the
    transcript and converts it into an explainable action. It never posts stock,
    accounting or purchasing automatically.
    """
    from buildsuite_core.ideal_erp.field_and_digital import parse_voice_capture

    if not project or not transcript:
        frappe.throw("Project and transcript are required.")

    action = parse_voice_capture(project, transcript, language)
    proposal = {
        "project": project,
        "action_type": action.action_type,
        "text": action.text,
        "confidence": action.confidence,
        "requires_confirmation": True,
        "supported_actions": ["delay", "inspection", "note"],
    }

    if not int(confirm):
        return {"proposal": proposal, "created": False}

    if action.action_type in {"delay", "inspection", "note"}:
        if not frappe.has_permission("ToDo", "create"):
            frappe.throw("You are not allowed to create work items.", frappe.PermissionError)

        subject = {
            "delay": "Site delay: ",
            "inspection": "Inspection required: ",
            "note": "Site note: ",
        }.get(action.action_type, "Site note: ")
        todo = frappe.new_doc("ToDo")
        todo.description = subject + action.text
        todo.priority = priority if priority in {"Low", "Medium", "High"} else "Medium"
        todo.reference_type = "Project"
        todo.reference_name = project
        todo.status = "Open"
        todo.insert()
        return {
            "proposal": proposal,
            "created": True,
            "doctype": "ToDo",
            "name": todo.name,
            "route": f"/todo/{frappe.utils.quote(todo.name)}",
        }

    if action.action_type == "purchase":
        return {
            "proposal": {
                **proposal,
                "supported_actions": ["purchase"],
                "next_step": "Provide the item and quantity, then create a Material Request draft.",
            },
            "created": False,
        }

    if action.action_type == "photo":
        return {
            "proposal": {
                **proposal,
                "supported_actions": ["photo"],
                "next_step": "Attach a photo File to the Project or Task Progress Entry.",
            },
            "created": False,
        }

    return {"proposal": proposal, "created": False}


@frappe.whitelist()
def company_intelligence_live(limit: int = 100) -> dict:
    """Build evidence-first Company Intelligence from live project records."""
    from frappe.utils import date_diff, flt, getdate, nowdate
    from buildsuite_core.api import boq_actuals
    from buildsuite_core.ideal_erp.intelligence.company_intelligence import ProjectSignal, analyze_projects

    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        companies = frappe.get_all("Company", filters={"is_group": 0}, pluck="name", limit=1)
        company = companies[0] if companies else None

    projects = frappe.get_all(
        "Project",
        filters={"company": company, "status": ["!=", "Cancelled"]} if company else {"status": ["!=", "Cancelled"]},
        fields=[
            "name",
            "project_name",
            "percent_complete",
            "expected_start_date",
            "expected_end_date",
            "estimated_costing",
        ],
        order_by="modified desc",
        limit_page_length=max(1, min(int(limit), 200)),
    )

    today = getdate(nowdate())
    signals = []
    project_rows = []
    for project_row in projects:
        contract = _live_approved_contract_value(project_row.name)
        actuals = boq_actuals.get_actuals_summary(project_row.name)
        forecast = frappe.get_all(
            "Material Forecast",
            filters={"project": project_row.name},
            fields=["name", "total_forecast_qty_value"],
            order_by="modified desc",
            limit=1,
        )
        shortage_value = 0.0
        forecast_value = flt(forecast[0].total_forecast_qty_value) if forecast else 0.0
        if forecast:
            forecast_items = frappe.get_all(
                "Material Forecast Item",
                filters={"parent": forecast[0].name, "parenttype": "Material Forecast"},
                fields=["qty_to_order", "estimated_rate"],
            )
            shortage_value = sum(flt(row.qty_to_order) * flt(row.estimated_rate) for row in forecast_items)

        planned_progress = 0.0
        if project_row.expected_start_date and project_row.expected_end_date:
            total_days = max(1, date_diff(project_row.expected_end_date, project_row.expected_start_date))
            elapsed = date_diff(today, project_row.expected_start_date)
            planned_progress = max(0.0, min(100.0, elapsed / total_days * 100.0))

        forecast_days = 0.0
        baseline_days = 0.0
        if project_row.expected_start_date and project_row.expected_end_date:
            baseline_days = max(0.0, float(date_diff(project_row.expected_end_date, project_row.expected_start_date)))
            if project_row.expected_end_date and getdate(project_row.expected_end_date) < today and flt(project_row.percent_complete) < 100:
                forecast_days = baseline_days + max(0, date_diff(today, project_row.expected_end_date))

        material_variance_pct = shortage_value / forecast_value * 100.0 if forecast_value else 0.0
        signals.append(
            ProjectSignal(
                project=project_row.name,
                baseline_cost=contract,
                actual_cost=flt(actuals["total"]),
                planned_progress_pct=planned_progress,
                actual_progress_pct=flt(project_row.percent_complete),
                baseline_end_days=baseline_days,
                forecast_end_days=forecast_days or baseline_days,
                material_variance_pct=material_variance_pct,
            )
        )
        project_rows.append(
            {
                "project": project_row.name,
                "project_name": project_row.project_name or project_row.name,
                "contract_value": contract,
                "actual_cost": flt(actuals["total"]),
                "planned_progress_pct": round(planned_progress, 1),
                "actual_progress_pct": flt(project_row.percent_complete),
                "material_variance_pct": round(material_variance_pct, 1),
            }
        )

    insights = analyze_projects(signals)
    return {
        "company": company,
        "project_count": len(project_rows),
        "projects": project_rows,
        "insights": [
            {
                "project": item.project,
                "kind": item.kind,
                "severity": item.severity,
                "message": item.message,
                "evidence": list(item.evidence),
            }
            for item in insights
        ],
    }

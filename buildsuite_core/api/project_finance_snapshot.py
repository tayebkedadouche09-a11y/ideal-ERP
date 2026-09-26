"""Live project-finance reconciliation over ERPNext's canonical ledgers.

This module does not create a second accounting ledger. It reads submitted Sales
Invoices / Payment Entry references and BuildSuite's derived BOQ actuals so the
project view can reconcile commercial value, cash and recognised project cost.
"""

from __future__ import annotations

import frappe
from frappe.utils import flt

from buildsuite_core.api import boq_actuals
from buildsuite_core.ideal_erp.integrated_flow import calculate_project_finance
from buildsuite_core.utils.project import default_company


def _approved_contract_value(project: str) -> float:
    rows = frappe.get_all(
        "BOQ",
        filters={"project": project, "status": "Approved"},
        fields=["planned_amount"],
        order_by="creation desc",
        limit=1,
    )
    if not rows:
        return flt(frappe.db.get_value("Project", project, "estimated_costing"))
    return flt(rows[0].planned_amount)


def _invoice_totals(project: str) -> dict[str, float | int]:
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"project": project, "docstatus": 1},
        fields=[
            "name",
            "net_total",
            "grand_total",
            "outstanding_amount",
            "posting_date",
        ],
    )
    return {
        "count": len(rows),
        "net_invoiced": sum(flt(row.net_total) for row in rows),
        "gross_invoiced": sum(flt(row.grand_total) for row in rows),
        "outstanding": sum(flt(row.outstanding_amount) for row in rows),
    }


def _payment_totals(project: str, invoice_names: list[str]) -> dict[str, float | int]:
    if not invoice_names:
        return {"count": 0, "allocated": 0.0}

    refs = frappe.get_all(
        "Payment Entry Reference",
        filters={
            "reference_doctype": "Sales Invoice",
            "reference_name": ["in", invoice_names],
            "docstatus": 1,
        },
        fields=["parent", "reference_name", "allocated_amount"],
    )
    payments = {
        row.name: row
        for row in frappe.get_all(
            "Payment Entry",
            filters={
                "name": ["in", [ref.parent for ref in refs]] if refs else ["in", ["__none__"]],
                "docstatus": 1,
                "payment_type": "Receive",
            },
            fields=["name"],
        )
    }
    allocated = sum(
        flt(ref.allocated_amount)
        for ref in refs
        if ref.parent in payments
    )
    return {"count": len(payments), "allocated": allocated}


def _open_commitments(project: str) -> dict[str, float | int]:
    po_rows = frappe.get_all(
        "Purchase Order",
        filters={
            "project": project,
            "docstatus": 1,
            "status": ["not in", ["Completed", "Closed", "Cancelled"]],
        },
        fields=["grand_total"],
    )
    subcontract_rows = []
    if frappe.db.exists("DocType", "Subcontractor Work Order"):
        subcontract_rows = frappe.get_all(
            "Subcontractor Work Order",
            filters={"project": project, "docstatus": 1},
            fields=["total_value"],
        )
    po_value = sum(flt(row.grand_total) for row in po_rows)
    subcontract_value = sum(flt(row.total_value) for row in subcontract_rows)
    return {
        "purchase_orders": len(po_rows),
        "purchase_order_value": po_value,
        "subcontract_work_orders": len(subcontract_rows),
        "subcontract_committed_value": subcontract_value,
        "total_open_commitment": po_value + subcontract_value,
    }


@frappe.whitelist()
def get_project_financial_snapshot(project: str) -> dict:
    """Reconcile one project's commercial and cost position from canonical ERPNext data."""
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

    contract_value = _approved_contract_value(project)
    invoices = _invoice_totals(project)
    invoice_names = frappe.get_all(
        "Sales Invoice",
        filters={"project": project, "docstatus": 1},
        pluck="name",
    )
    payments = _payment_totals(project, invoice_names)
    actuals = boq_actuals.get_actuals_summary(project)
    commitments = _open_commitments(project)

    finance = calculate_project_finance(
        contract_value=contract_value,
        invoiced_net=float(invoices["net_invoiced"]),
        outstanding_gross=float(invoices["outstanding"]),
        actual_cost=float(actuals["total"]),
        open_commitment=float(commitments["total_open_commitment"]),
    )

    return {
        "project": project,
        "project_name": project_row.project_name or project,
        "company": project_row.company or default_company(),
        "customer": project_row.customer,
        "contract_value": contract_value,
        "invoices": {
            **invoices,
            "names": invoice_names,
        },
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

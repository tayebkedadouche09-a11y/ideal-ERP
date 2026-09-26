import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from buildsuite_core.ideal_erp.integrated_flow import calculate_ipc
from buildsuite_core.api import invoice as invoice_api
from buildsuite_core.api.workflow import workflow_active


class InterimPaymentCertificate(Document):
    def validate(self):
        self._recalculate()

    def _recalculate(self):
        result = calculate_ipc(
            [
                {
                    "description": row.description,
                    "contract_qty": row.contract_qty,
                    "contract_rate": row.contract_rate,
                    "previous_qty": row.previous_qty_claimed,
                    "current_qty": row.qty_this_period,
                }
                for row in self.items
            ],
            previous_cumulative_amount=flt(self.previous_cumulative_amount),
            retention_percent=flt(self.retention_percent),
            advance_recovery_amount=flt(self.advance_recovery_amount),
            other_deductions=flt(self.other_deductions),
            previous_retention_held=self._previous_retention(),
        )
        for source, target in zip(self.items, result.lines):
            source.contract_amount = target["contract_amount"]
            source.cumulative_qty = target["cumulative_qty"]
            source.amount_this_period = target["current_amount"]
            source.cumulative_amount = target["cumulative_amount"]
            source.percent_complete = target["percent_complete"]
        self.gross_amount_this_period = result.gross_current
        self.cumulative_amount_to_date = result.cumulative_after
        self.retention_amount = result.retention_amount
        self.net_payable_this_period = result.net_payable
        self.total_retention_held = result.total_retention_held

    def _previous_retention(self):
        if not self.project:
            return 0
        rows = frappe.db.sql(
            """
            SELECT COALESCE(SUM(retention_amount), 0) AS total
            FROM `tabInterim Payment Certificate`
            WHERE project = %s AND docstatus = 1 AND name != %s
            """,
            (self.project, self.name or ""),
            as_dict=True,
        )
        return flt((rows[0] if rows else {}).get("total"))

    def before_submit(self):
        self._recalculate()
        if not self.client:
            frappe.throw("Client is required before submitting an IPC")
        self.submitted_by = frappe.session.user
        self.submission_date = nowdate()
        self.status = "Submitted"

    def on_submit(self):
        self._create_sales_invoice()

    def on_cancel(self):
        self._cancel_sales_invoice()
        self.db_set("status", "Draft")

    def _create_sales_invoice(self):
        if self.sales_invoice_ref and frappe.db.exists("Sales Invoice", self.sales_invoice_ref):
            return self.sales_invoice_ref

        result = invoice_api.save_invoice(
            frappe.as_json(
                {
                    "customer": self.client,
                    "project": self.project,
                    "date": nowdate(),
                    "due_date": nowdate(),
                    "items": [
                        {
                            "description": f"Progress Billing — {self.ipc_title}",
                            "qty": 1,
                            "rate": flt(self.net_payable_this_period),
                        }
                    ],
                }
            )
        )
        invoice_name = result["name"]
        self.db_set("sales_invoice_ref", invoice_name)

        if workflow_active("Sales Invoice"):
            self.db_set("status", "Invoice Pending")
            return invoice_name

        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        try:
            invoice.check_permission("submit")
        except frappe.PermissionError:
            self.db_set("status", "Invoice Pending")
            return invoice_name

        invoice.submit()
        self.db_set("status", "Invoiced")
        return invoice_name

    def _cancel_sales_invoice(self):
        if not self.sales_invoice_ref or not frappe.db.exists("Sales Invoice", self.sales_invoice_ref):
            return
        invoice = frappe.get_doc("Sales Invoice", self.sales_invoice_ref)
        if invoice.docstatus == 1:
            invoice.cancel()
        elif invoice.docstatus == 0:
            frappe.delete_doc("Sales Invoice", invoice.name, ignore_permissions=True)
        self.db_set("sales_invoice_ref", None)

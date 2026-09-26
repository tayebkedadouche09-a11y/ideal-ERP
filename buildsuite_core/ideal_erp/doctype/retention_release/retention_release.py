import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from buildsuite_core.ideal_erp.integrated_flow import calculate_retention_release
from buildsuite_core.api import invoice as invoice_api
from buildsuite_core.api.workflow import workflow_active


class RetentionRelease(Document):
    def _already_released(self):
        if not self.project:
            return 0
        rows = frappe.db.sql(
            """
            SELECT COALESCE(SUM(release_amount), 0) AS total
            FROM `tabRetention Release`
            WHERE project = %s AND docstatus = 1 AND name != %s
            """,
            (self.project, self.name or ""),
            as_dict=True,
        )
        return flt((rows[0] if rows else {}).get("total"))

    def validate(self):
        result = calculate_retention_release(
            total_retention_held=flt(self.total_retention_held),
            amount_requested=flt(self.release_amount),
            already_released=self._already_released(),
        )
        self.balance_retention = result["balance_after_release"]

    def before_submit(self):
        if not self.client:
            frappe.throw("Client is required before submitting a retention release")
        if flt(self.release_amount) <= 0:
            frappe.throw("Release amount must be greater than zero")
        released = self._already_released()
        available = flt(self.total_retention_held) - released
        if flt(self.release_amount) > available:
            frappe.throw(
                f"Release amount exceeds available retention balance ({available:g})"
            )
        self.status = "Approved"
        self.requested_by = self.requested_by or frappe.session.user
        self.request_date = self.request_date or nowdate()
        self.approved_by = frappe.session.user
        self.approval_date = nowdate()

    def on_submit(self):
        self._create_sales_invoice()

    def _create_sales_invoice(self):
        if self.sales_invoice_ref and frappe.db.exists("Sales Invoice", self.sales_invoice_ref):
            return self.sales_invoice_ref

        result = invoice_api.save_invoice(
            frappe.as_json(
                {
                    "customer": self.client,
                    "project": self.project,
                    "date": self.release_date or nowdate(),
                    "due_date": self.release_date or nowdate(),
                    "items": [
                        {
                            "description": f"Retention release ({self.release_type}) for project {self.project}",
                            "qty": 1,
                            "rate": flt(self.release_amount),
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

    def on_cancel(self):
        if self.sales_invoice_ref and frappe.db.exists("Sales Invoice", self.sales_invoice_ref):
            invoice = frappe.get_doc("Sales Invoice", self.sales_invoice_ref)
            if invoice.docstatus == 1:
                invoice.cancel()
            elif invoice.docstatus == 0:
                frappe.delete_doc("Sales Invoice", invoice.name, ignore_permissions=True)
        self.db_set("sales_invoice_ref", None)
        self.db_set("status", "Cancelled")

import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class RetentionRelease(Document):
    def validate(self):
        self.balance_retention = max(
            0,
            flt(self.total_retention_held) - flt(self.release_amount),
        )

    def before_submit(self):
        if not self.client:
            frappe.throw("Client is required before submitting a retention release")
        if flt(self.release_amount) <= 0:
            frappe.throw("Release amount must be greater than zero")
        if flt(self.release_amount) > flt(self.total_retention_held):
            frappe.throw("Release amount exceeds total retention held")
        self.status = "Approved"
        self.requested_by = self.requested_by or frappe.session.user
        self.request_date = self.request_date or nowdate()

    def on_submit(self):
        if self.sales_invoice_ref:
            return
        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = self.client
        invoice.company = self.company
        invoice.currency = self.currency
        if hasattr(invoice, "project"):
            invoice.project = self.project
        invoice.append(
            "items",
            {
                "item_name": f"Retention Release — {self.project}",
                "description": f"Retention release ({self.release_type}) for project {self.project}",
                "qty": 1,
                "rate": flt(self.release_amount),
                "uom": "Nos",
            },
        )
        invoice.insert(ignore_permissions=True)
        self.db_set("sales_invoice_ref", invoice.name)
        self.db_set("approval_date", nowdate())
        self.db_set("approved_by", frappe.session.user)

    def on_cancel(self):
        if self.sales_invoice_ref:
            invoice = frappe.get_doc("Sales Invoice", self.sales_invoice_ref)
            if invoice.docstatus == 1:
                invoice.cancel()
        self.db_set("status", "Cancelled")

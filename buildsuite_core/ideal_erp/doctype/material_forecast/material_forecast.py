import frappe
from frappe.model.document import Document
from frappe.utils import flt

from buildsuite_core.ideal_erp.integrated_flow import build_material_plan


class MaterialForecast(Document):
    def validate(self):
        plan = build_material_plan(
            [
                {
                    "item_code": row.item_code,
                    "planned_qty": flt(row.boq_qty),
                    "waste_pct": flt(row.waste_factor),
                    "consumed_qty": self._consumed(row.item_code),
                    "available_qty": self._available(row.item_code, row.warehouse),
                    "ordered_qty": self._ordered(row.item_code),
                    "estimated_rate": flt(row.estimated_rate),
                    "required_by": row.required_by_date,
                }
                for row in self.items
            ]
        )
        for row, calculated in zip(self.items, plan):
            row.net_qty_required = calculated.required_qty
            row.already_ordered_qty = calculated.ordered_qty
            row.qty_to_order = calculated.qty_to_order
            row.estimated_value = calculated.estimated_value

        self.total_forecast_qty_value = sum(
            flt(row.estimated_value) for row in self.items
        )
        shortages = sum(1 for row in self.items if flt(row.qty_to_order) > 0)
        if shortages == 0:
            self.status = "Fully Procured"
        elif any(
            flt(row.already_ordered_qty) > 0 or flt(row.qty_to_order) < flt(row.net_qty_required)
            for row in self.items
        ):
            self.status = "Partially Procured"
        else:
            self.status = "Draft"

    def before_submit(self):
        if any(
            flt(row.boq_qty) < 0 or flt(row.waste_factor) < 0
            for row in self.items
        ):
            frappe.throw("Material quantities and waste cannot be negative")
        if self.status not in {"Fully Procured", "Partially Procured", "Draft"}:
            self.status = "Draft"

    def _ordered(self, item_code):
        if not self.project or not frappe.get_meta("Purchase Order").has_field("project"):
            return 0
        q = frappe.db.sql(
            """
            SELECT COALESCE(SUM(poi.qty), 0) AS total
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po ON po.name = poi.parent
            WHERE poi.item_code = %s
              AND po.project = %s
              AND po.docstatus = 1
              AND po.status NOT IN ('Completed', 'Cancelled')
            """,
            (item_code, self.project),
            as_dict=True,
        )
        return flt((q[0] if q else {}).get("total"))

    def _available(self, item_code, warehouse=None):
        if warehouse:
            q = frappe.db.sql(
                """
                SELECT COALESCE(SUM(actual_qty), 0) AS total
                FROM `tabBin`
                WHERE item_code = %s AND warehouse = %s
                """,
                (item_code, warehouse),
                as_dict=True,
            )
        else:
            q = frappe.db.sql(
                """
                SELECT COALESCE(SUM(actual_qty), 0) AS total
                FROM `tabBin`
                WHERE item_code = %s
                """,
                (item_code,),
                as_dict=True,
            )
        return max(0.0, flt((q[0] if q else {}).get("total")))

    def _consumed(self, item_code):
        if not self.project:
            return 0
        try:
            q = frappe.db.sql(
                """
                SELECT COALESCE(SUM(mci.qty), 0) AS total
                FROM `tabMaterial Consumption Item` mci
                JOIN `tabMaterial Consumption Entry` mc ON mc.name = mci.parent
                WHERE mci.item_code = %s
                  AND mc.project = %s
                  AND mc.docstatus = 1
                """,
                (item_code, self.project),
                as_dict=True,
            )
        except Exception:
            return 0
        return flt((q[0] if q else {}).get("total"))

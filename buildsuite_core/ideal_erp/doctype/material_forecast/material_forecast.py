import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from buildsuite_core.ideal_erp.integrated_flow import build_material_plan


class MaterialForecast(Document):
    @classmethod
    def from_approved_boq(cls, boq_name, waste_pct=5):
        boq = frappe.get_doc("BOQ", boq_name)
        if boq.status != "Approved":
            frappe.throw("Only an Approved BOQ can create a material forecast.")

        item_rows = frappe.get_all(
            "BOQ Item",
            filters={"boq": boq_name, "cost_head": "Material"},
            fields=["description", "unit", "planned_qty", "rate", "code"],
            order_by="code asc",
        )
        catalog_rows = frappe.get_all(
            "Item",
            fields=["name", "item_name", "description", "stock_uom"],
            filters={"disabled": 0, "is_stock_item": 1},
            limit_page_length=5000,
        )
        catalog = [
            {
                "item_code": item.name,
                "description": f"{item.item_name or ''} {item.description or ''}".strip(),
            }
            for item in catalog_rows
        ]

        from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost

        forecast = frappe.new_doc("Material Forecast")
        forecast.forecast_title = f"Material Forecast — {boq.title or boq.name}"
        forecast.project = boq.project
        forecast.boq_ref = boq.name
        forecast.company = boq.company or frappe.db.get_value("Project", boq.project, "company")
        forecast.status = "Draft"

        unresolved = []
        matched = []
        for row in item_rows:
            candidates = match_cost(row.description or row.code, catalog, limit=3)
            best = candidates[0] if candidates else None
            if not best or best.score < 0.20:
                unresolved.append(
                    {
                        "boq_code": row.code,
                        "description": row.description,
                        "candidates": [
                            {
                                "item_code": candidate.item_code,
                                "description": candidate.description,
                                "score": candidate.score,
                            }
                            for candidate in candidates
                        ],
                    }
                )
                continue

            item = next((candidate for candidate in catalog_rows if candidate.name == best.item_code), None)
            if not item:
                unresolved.append(
                    {"boq_code": row.code, "description": row.description, "candidates": []}
                )
                continue

            forecast.append(
                "items",
                {
                    "item_code": item.name,
                    "item_name": item.item_name,
                    "uom": row.unit or item.stock_uom,
                    "boq_qty": row.planned_qty,
                    "waste_factor": waste_pct,
                    "estimated_rate": row.rate,
                },
            )
            matched.append(
                {
                    "boq_code": row.code,
                    "item_code": item.name,
                    "score": best.score,
                }
            )

        if not forecast.items:
            frappe.throw("No BOQ material lines could be matched to stock Items.")

        forecast.insert()
        return {
            "name": forecast.name,
            "project": forecast.project,
            "boq": forecast.boq_ref,
            "matched": matched,
            "unresolved": unresolved,
            "requires_human_confirmation": bool(unresolved),
        }

    def validate(self):
        self._recalculate_plan()

    def _recalculate_plan(self):
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

        self.total_forecast_qty_value = sum(flt(row.estimated_value) for row in self.items)
        shortages = [row for row in self.items if flt(row.qty_to_order) > 0]

        if not shortages:
            self.status = "Fully Procured"
            self.procurement_status = "Fully Ordered"
        elif self.material_request_ref and frappe.db.exists("Material Request", self.material_request_ref):
            mr = frappe.get_cached_doc("Material Request", self.material_request_ref)
            self.procurement_status = (
                "Fully Ordered" if flt(mr.per_ordered) >= 100 else "Requested"
            )
            self.status = "Partially Procured" if any(
                flt(row.already_ordered_qty) > 0 for row in self.items
            ) else "Approved"
        else:
            self.status = "Partially Procured" if any(
                flt(row.already_ordered_qty) > 0 for row in self.items
            ) else "Draft"
            self.procurement_status = "Draft"

    def before_submit(self):
        self._recalculate_plan()
        if any(flt(row.boq_qty) < 0 or flt(row.waste_factor) < 0 for row in self.items):
            frappe.throw("Material quantities and waste cannot be negative")
        if self.status not in {"Fully Procured", "Partially Procured"}:
            self.status = "Approved"

    def create_material_request(self):
        if not self.project:
            frappe.throw("Project is required before creating procurement.")
        self._recalculate_plan()
        rows = [
            row for row in self.items
            if flt(row.qty_to_order) > 0 and row.item_code
        ]
        if not rows:
            frappe.throw("There is no material shortage to procure.")

        if self.material_request_ref and frappe.db.exists("Material Request", self.material_request_ref):
            return {"name": self.material_request_ref, "reused": True}

        from buildsuite_core.api import procurement_docs

        payload = [
            {
                "item_code": row.item_code,
                "qty": flt(row.qty_to_order),
                "uom": row.uom,
                "rate": flt(row.estimated_rate),
                "description": f"Project {self.project} — Material Forecast {self.name}",
                "schedule_date": row.required_by_date or self.to_date or nowdate(),
            }
            for row in rows
        ]
        result = procurement_docs.save_material_request(
            project=self.project,
            schedule_date=self.to_date or nowdate(),
            items=frappe.as_json(payload),
        )
        self.material_request_ref = result["name"]
        self.status = "Partially Procured" if any(flt(row.already_ordered_qty) > 0 for row in self.items) else "Approved"
        self.procurement_status = "Request Draft"
        self.db_set("material_request_ref", result["name"])
        self.db_set("status", self.status)
        self.db_set("procurement_status", "Request Draft")
        return {"name": result["name"], "reused": False}

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
                SELECT COALESCE(SUM(sed.qty), 0) AS total
                FROM `tabStock Entry Detail` sed
                JOIN `tabStock Entry` se ON se.name = sed.parent
                WHERE sed.item_code = %s
                  AND se.project = %s
                  AND se.purpose = 'Material Issue'
                  AND se.docstatus = 1
                """,
                (item_code, self.project),
                as_dict=True,
            )
        except Exception:
            return 0
        return flt((q[0] if q else {}).get("total"))


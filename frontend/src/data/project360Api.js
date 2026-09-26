import { frappeRequest } from "frappe-ui-frappe-request";
import { parseFrappeError } from "@/utils/frappeError";

// Project 360 — one live read across Project, BOQ actuals, procurement, stock,
// Sales Invoices/Payments and Company Intelligence.
export async function getProject360(project) {
	if (!project) return null;
	try {
		return await frappeRequest({
			url: "buildsuite_core.api.ideal_erp.project_360",
			params: { project },
		});
	} catch (err) {
		throw new Error(parseFrappeError(err).summary || "Failed to load Project 360.");
	}
}

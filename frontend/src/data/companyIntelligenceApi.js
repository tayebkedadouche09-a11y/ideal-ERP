import { frappeRequest } from "frappe-ui-frappe-request";
import { parseFrappeError } from "@/utils/frappeError";

export async function getCompanyIntelligence(limit = 100) {
	try {
		return await frappeRequest({
			url: "buildsuite_core.api.ideal_erp.company_intelligence_live",
			params: { limit },
		});
	} catch (err) {
		throw new Error(parseFrappeError(err).summary || "Failed to load Company Intelligence.");
	}
}

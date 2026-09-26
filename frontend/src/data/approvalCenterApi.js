import { frappeRequest } from "frappe-ui-frappe-request";
import { parseFrappeError } from "@/utils/frappeError";

export async function getApprovalCenter(limit = 100) {
	try {
		return await frappeRequest({
			url: "buildsuite_core.api.ideal_erp.approval_center",
			params: { limit },
		});
	} catch (err) {
		throw new Error(parseFrappeError(err).summary || "Failed to load Approval Center.");
	}
}

export async function applyApprovalAction(doctype, name, action) {
	try {
		return await frappeRequest({
			url: "buildsuite_core.api.workflow.apply_action",
			params: { doctype, name, action },
		});
	} catch (err) {
		throw new Error(parseFrappeError(err).summary || "Failed to apply workflow action.");
	}
}

<script setup>
// Stub used by the 12 workspace landing routes (and the 4 legacy placeholders) until
// a proper Desk-styled workspace page lands. When `links` is non-empty, renders a row
// of shortcut tiles below the description — used by workspaces whose underlying list
// views already exist (Site Execution → Projects / WP / Tasks / Schedule, etc.) so the
// sidebar isn't a dead end. Workspaces with no backing screens omit `links` and show
// just the "Coming next" panel.

import { RouterLink } from "vue-router";
import WorkspaceShortcut from "@/components/WorkspaceShortcut.vue";
import { computed } from "vue";
import { getWorkspaceIconPath, resolveWorkspaceIconSlug } from "@/utils/workspaceIcons";

const props = defineProps({
	title: { type: String, required: true },
	icon: { type: String, default: "📄" },
	desc: { type: String, default: "" },
	// Optional explicit links from legacy routes. When omitted, the landing hub
	// derives shortcuts from the real routes already available in this app.
	links: { type: Array, default: () => [] },
});

const REAL_MODULE_LINKS = {
	Buying: [
		{ label: "Material Requests", to: "/procurement/material-requests", icon: "clipboard-list", desc: "Raise, approve and convert project material requests." },
		{ label: "Purchase Orders", to: "/procurement/purchase-orders", icon: "shopping-cart", desc: "Create and manage supplier purchase orders." },
		{ label: "Purchase Receipts", to: "/procurement/receipts", icon: "package-check", desc: "Receive ordered materials into project stock." },
		{ label: "Suppliers", to: "/suppliers", icon: "users", desc: "Manage supplier masters and purchasing parties." },
	],
	Stock: [
		{ label: "Items", to: "/items", icon: "package", desc: "Item master, units and stock configuration." },
		{ label: "Material Consumption", to: "/material-consumption", icon: "layers", desc: "Issue materials from the project store and recognise actual cost." },
		{ label: "Warehouses", to: "/records/Warehouse", icon: "warehouse", desc: "Open the native ERPNext warehouse register." },
		{ label: "Material Forecasts", to: "/records/Material%20Forecast", icon: "forecast", desc: "Calculate shortages from BOQ, stock and consumption." },
	],
	Assets: [
		{ label: "Equipment", to: "/equipment", icon: "settings", desc: "Equipment register and project assignment." },
		{ label: "Machinery", to: "/machinery", icon: "truck", desc: "Machines, plant and asset details." },
		{ label: "Machinery Usage", to: "/machinery-usage", icon: "gauge", desc: "Log machine hours, quantities and fuel cost." },
	],
	HR: [
		{ label: "Field Employees", to: "/field-employees", icon: "users", desc: "Worker records and field profiles." },
		{ label: "Field Attendance", to: "/field-attendance", icon: "calendar", desc: "Daily field attendance linked to site workforce." },
		{ label: "Attendance Summary", to: "/workforce/attendance-summary", icon: "chart", desc: "Workforce reporting and attendance summaries." },
		{ label: "Users", to: "/settings/users", icon: "user", desc: "Manage system users and roles." },
	],
	Subcontractor: [
		{ label: "Subcontractors", to: "/subcontractors", icon: "users", desc: "Subcontractor master and trade information." },
		{ label: "Work Orders", to: "/subcontractor-work-orders", icon: "clipboard", desc: "Issue and manage subcontract work orders." },
		{ label: "Measurement Books", to: "/measurement-books", icon: "ruler", desc: "Measure work before certification and billing." },
		{ label: "Subcontractor Bills", to: "/subcontractor-bills", icon: "receipt", desc: "Certify bills, retention and downstream payment." },
	],
	Labour: [
		{ label: "Field Employees", to: "/field-employees", icon: "users", desc: "Worker register." },
		{ label: "Field Attendance", to: "/field-attendance", icon: "calendar", desc: "Daily attendance and site workforce." },
		{ label: "Labour Attendance", to: "/labour-attendance", icon: "clock", desc: "Labour attendance register." },
		{ label: "Overtime", to: "/overtime-attendance", icon: "timer", desc: "Overtime attendance register." },
	],
	Financials: [
		{ label: "Project Finance", to: "/project-finance", icon: "wallet", desc: "Invoices, payments, supplier bills and project financials." },
		{ label: "Finance Reports", to: "/project-finance/report/cash-flow", icon: "chart", desc: "Finance reporting over ERPNext accounting data." },
		{ label: "Cost vs Budget", to: "/reports/cost-vs-budget", icon: "chart", desc: "Planned, committed and actual project cost by code." },
		{ label: "Interim Payment Certificates", to: "/records/Interim%20Payment%20Certificate", icon: "receipt", desc: "Certify progress billing and generate ERPNext customer invoices." },
		{ label: "Retention Releases", to: "/records/Retention%20Release", icon: "lock-open", desc: "Approve and invoice contractual retention release." },
		{ label: "Accounting", to: "/accounting", icon: "calculator", desc: "ERPNext accounting workspace and ledgers." },
	],
	Reports: [
		{ label: "Project Dashboard", to: "/project-dashboard", icon: "layout-dashboard", desc: "Live projects, schedule, cost, decisions and commitments." },
		{ label: "Delay Analysis", to: "/reports/delay-analysis", icon: "clock", desc: "Schedule and delay analysis." },
		{ label: "Cost vs Budget", to: "/reports/cost-vs-budget", icon: "chart", desc: "BOQ planned vs committed vs actual." },
		{ label: "Insights", to: "/insights", icon: "sparkles", desc: "Connected project intelligence and reporting." },
	],
};

const resolvedLinks = computed(() => {
	if (props.links.length) return props.links;
	return REAL_MODULE_LINKS[props.title] || [];
});

const moduleLabel = computed(() =>
	resolvedLinks.value.length ? "Live module shortcuts" : "No shortcuts available"
);
</script>

<template>
	<div class="px-6 py-10">
		<div class="max-w-3xl mx-auto">
			<div class="flex items-start gap-4 mb-6">
				<div
					class="w-12 h-12 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center flex-shrink-0"
				>
					<svg
						class="w-6 h-6"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						v-html="getWorkspaceIconPath(resolveWorkspaceIconSlug(icon))"
					/>
				</div>
				<div class="min-w-0 flex-1">
					<h1 class="text-xl font-semibold text-ink-900">{{ title }}</h1>
					<p class="text-sm text-ink-500 mt-1 leading-relaxed">{{ desc }}</p>
				</div>
			</div>

			<!-- Shortcut tiles — only when `links` is provided. -->
			<div v-if="resolvedLinks.length" class="mb-6">
				<div class="text-[11px] uppercase tracking-wider text-ink-500 font-semibold mb-2">
					{{ moduleLabel }}
				</div>
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
					<WorkspaceShortcut
						v-for="l in resolvedLinks"
						:key="l.to"
						:to="l.to"
						:icon="l.icon"
						:label="l.label"
						:description="l.desc || ''"
					/>
				</div>
			</div>

			<div
				v-if="!resolvedLinks.length"
				class="px-4 py-3 bg-ink-50 border border-ink-200 text-xs text-ink-600"
				style="border-radius: 6px"
			>
				<div class="font-medium text-ink-700 mb-1">No shortcuts available</div>
				<p class="leading-relaxed">
					There are no shortcuts configured for this workspace yet.
				</p>
			</div>
		</div>
	</div>
</template>

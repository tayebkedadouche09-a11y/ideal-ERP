<script setup>
// Estimation workspace — date + title, BOQ shortcut, and a "Setup" group.
// Setup has Rate Master + Assembly for now (Estimate Templates come later).

import { computed } from "vue";
import WorkspaceShortcut from "@/components/WorkspaceShortcut.vue";
import WorkspaceRecordsSection from "@/components/workspaces/WorkspaceRecordsSection.vue";
import WorkspaceReportsSection from "@/components/workspaces/WorkspaceReportsSection.vue";

const today = computed(() =>
	new Date().toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" }),
);



const ESTIMATES = [
	{ to: "/boq", icon: "chart-bar", label: "BOQ", cap: "boq" },
	{ to: "/quotations", icon: "file-text", label: "Quotations" },
	{ to: "/tenders", icon: "clipboard-list", label: "Tenders" },
];
const SETUP = [
	{
		to: "/rate-master",
		icon: "tag",
		label: "Rate Master",
		description: "Price book for materials, labour, and equipment.",
		cap: "rateMaster",
	},
	{
		to: "/assembly",
		icon: "layout-grid",
		label: "Assembly",
		description: "Rate-analysis recipes built from rate-master resources.",
		cap: "assembly",
	},
	{
		to: "/estimate-template",
		icon: "file-text",
		label: "Estimate Template",
		description: "Reusable BOQ skeletons of assemblies and resources.",
		cap: "estimateTemplate",
	},
];
</script>

<template>
	<div class="bg-white min-h-full">
		<div class="max-w-6xl mx-auto px-6 py-8">
			<div class="mb-6">
				<div class="text-xs text-ink-500 mb-1">{{ today }}</div>
				<h1 class="text-2xl font-semibold text-ink-900">Estimation</h1>
			</div>

			<div class="mb-8 border border-brand-200 bg-brand-50/40 rounded-xl overflow-hidden">
				<button type="button" class="w-full px-4 py-3 flex items-center justify-between text-left" @click="resinOpen = !resinOpen">
					<div>
						<div class="text-sm font-semibold text-ink-900">Resin / Epoxy Estimator</div>
						<div class="text-[11px] text-ink-500 mt-0.5">Site measurements → material quantity → cost → quotation draft.</div>
					</div>
					<span class="text-xs text-brand-700">{{ resinOpen ? "Hide" : "Open" }}</span>
				</button>
				<div v-if="resinOpen" class="border-t border-brand-200 bg-white p-4">
					<div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
						<DeskField label="Customer" required><DeskSearchableSelect v-model="resinForm.customer" :options="customerOptions" placeholder="Pick customer…" search-placeholder="Search customers…" /></DeskField>
						<DeskField label="Project"><DeskSearchableSelect v-model="resinForm.project" :options="projectOptions" allow-clear placeholder="Optional project" search-placeholder="Search projects…" /></DeskField>
						<div class="lg:col-span-2"><DeskField label="Work title"><DeskInput v-model="resinForm.title" /></DeskField></div>
					</div>
					<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-4">
						<DeskField label="Area (m²)"><DeskInput v-model="resinForm.area_m2" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Thickness (mm)"><DeskInput v-model="resinForm.thickness_mm" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Density (kg/L)"><DeskInput v-model="resinForm.density_kg_per_l" type="number" min="0.01" step="any" /></DeskField>
						<DeskField label="Volume solids"><DeskInput v-model="resinForm.volume_solids" type="number" min="0.01" max="1" step="0.01" /></DeskField>
						<DeskField label="Waste %"><DeskInput v-model="resinForm.waste_pct" type="number" min="0" step="0.1" /></DeskField>
						<DeskField label="Primer kg/m²"><DeskInput v-model="resinForm.primer_kg_per_m2" type="number" min="0" step="any" /></DeskField>
					</div>
					<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mt-4">
						<DeskField label="Material DA/kg"><DeskInput v-model="resinForm.material_cost_per_kg" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Primer DA/kg"><DeskInput v-model="resinForm.primer_cost_per_kg" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Labour h/10m²"><DeskInput v-model="resinForm.labor_hours_per_10m2" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Labour DA/h"><DeskInput v-model="resinForm.labor_rate_per_hour" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Equipment DA"><DeskInput v-model="resinForm.equipment_cost" type="number" min="0" step="any" /></DeskField>
						<DeskField label="Margin %"><DeskInput v-model="resinForm.margin_percent" type="number" min="0" step="0.1" /></DeskField>
					</div>
					<div v-if="resinError" class="mt-4 px-3 py-2 rounded-md bg-danger-50 border border-danger-200 text-xs text-danger-700">{{ resinError }}</div>
					<div class="mt-4 flex flex-wrap items-center gap-2">
						<button type="button" class="desk-save-btn text-xs" :disabled="resinLoading" @click="runResinEstimate">{{ resinLoading ? "Calculating…" : "Calculate estimate" }}</button>
						<button v-if="resinResult" type="button" class="text-xs px-3 py-1.5 border border-brand-300 text-brand-700 bg-brand-50 rounded-md" :disabled="quotationLoading" @click="createResinQuotation">{{ quotationLoading ? "Creating quotation…" : "Create quotation draft" }}</button>
						<button type="button" class="text-xs px-3 py-1.5 text-ink-600 hover:text-ink-900" @click="closeResin">Close</button>
					</div>
					<div v-if="resinResult" class="mt-5 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Mix kg</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinResult.coating_mix_kg || 0).toFixed(2) }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Resin kg</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinResult.resin_kg || 0).toFixed(2) }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Hardener kg</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinResult.hardener_kg || 0).toFixed(2) }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Primer kg</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinResult.primer_kg || 0).toFixed(2) }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Labour h</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinResult.labor_hours || 0).toFixed(2) }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Cost</div><div class="font-semibold text-ink-900 mt-1">{{ fmtCurrency(resinResult.total_cost, "DZD") }}</div></div>
						<div class="border border-ink-200 rounded-lg p-3"><div class="text-[10px] text-ink-500 uppercase">Margin</div><div class="font-semibold text-ink-900 mt-1">{{ Number(resinForm.margin_percent || 0).toFixed(1) }}%</div></div>
						<div class="border border-brand-200 bg-brand-50 rounded-lg p-3"><div class="text-[10px] text-brand-700 uppercase">Quote</div><div class="font-semibold text-brand-900 mt-1">{{ fmtCurrency(resinResult.quoted_total, "DZD") }}</div></div>
					</div>
				</div>
			</div>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-8">
				<WorkspaceShortcut
					v-for="sc in ESTIMATES"
					:key="sc.to"
					:to="sc.to"
					:icon="sc.icon"
					:label="sc.label"
					:cap="sc.cap"
				/>
			</div>

			<h2 class="text-[11px] font-semibold uppercase tracking-wider text-ink-700 mb-2">
				Setup
			</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
				<WorkspaceShortcut
					v-for="sc in SETUP"
					:key="sc.to"
					:to="sc.to"
					:icon="sc.icon"
					:label="sc.label"
					:description="sc.description"
					:cap="sc.cap"
				/>
			</div>

			<WorkspaceRecordsSection workspace="estimation" />

			<WorkspaceReportsSection workspace="estimation" />
		</div>
	</div>
</template>

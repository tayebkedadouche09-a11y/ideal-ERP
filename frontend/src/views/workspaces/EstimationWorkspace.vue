<script setup>
// Estimation workspace — date + title, BOQ shortcut, and a "Setup" group.
// Setup has Rate Master + Assembly for now (Estimate Templates come later).

import { computed, reactive, ref } from "vue";
import WorkspaceShortcut from "@/components/WorkspaceShortcut.vue";
import WorkspaceRecordsSection from "@/components/workspaces/WorkspaceRecordsSection.vue";
import WorkspaceReportsSection from "@/components/workspaces/WorkspaceReportsSection.vue";
import DeskField from "@/components/desk/DeskField.vue";
import DeskInput from "@/components/desk/DeskInput.vue";
import DeskSearchableSelect from "@/components/desk/DeskSearchableSelect.vue";
import { useCustomerOptions } from "@/composables/useCustomerOptions";
import { useProjectOptions } from "@/composables/useProjectOptions";
import { showToast } from "@/utils/appToast";
import { fmtCurrency } from "@/utils/format";
import { frappeRequest } from "frappe-ui-frappe-request";

const { customerOptions } = useCustomerOptions();
const { projectOptions } = useProjectOptions();

const resinOpen = ref(false);
const resinLoading = ref(false);
const quotationLoading = ref(false);
const resinResult = ref(null);
const resinError = ref("");
const resinForm = reactive({
  customer: "",
  project: "",
  title: "Industrial Epoxy Flooring",
  area_m2: 100,
  thickness_mm: 2,
  density_kg_per_l: 1.5,
  volume_solids: 1,
  waste_pct: 5,
  primer_kg_per_m2: 0,
  resin_share: 0.7,
  hardener_share: 0.3,
  material_cost_per_kg: 0,
  primer_cost_per_kg: 0,
  labor_hours_per_10m2: 0,
  labor_rate_per_hour: 0,
  equipment_cost: 0,
  margin_percent: 20,
  validity_days: 30,
});

function closeResin() {
  resinOpen.value = false;
  resinError.value = "";
}

async function runResinEstimate() {
  resinError.value = "";
  resinLoading.value = true;
  try {
    const payload = {
      area_m2: Number(resinForm.area_m2),
      thickness_mm: Number(resinForm.thickness_mm),
      density_kg_per_l: Number(resinForm.density_kg_per_l),
      volume_solids: Number(resinForm.volume_solids),
      waste_pct: Number(resinForm.waste_pct),
      primer_kg_per_m2: Number(resinForm.primer_kg_per_m2),
      resin_share: Number(resinForm.resin_share),
      hardener_share: Number(resinForm.hardener_share),
      material_cost_per_kg: Number(resinForm.material_cost_per_kg),
      primer_cost_per_kg: Number(resinForm.primer_cost_per_kg),
      labor_hours_per_10m2: Number(resinForm.labor_hours_per_10m2),
      labor_rate_per_hour: Number(resinForm.labor_rate_per_hour),
      equipment_cost: Number(resinForm.equipment_cost),
    };
    const result = await frappeRequest({
      url: "buildsuite_core.api.ideal_erp.estimate_resin_job",
      params: payload,
    });
    resinResult.value = {
      ...payload,
      ...result,
      quoted_total: Number(result.total_cost || 0) * (1 + Number(resinForm.margin_percent || 0) / 100),
    };
  } catch (err) {
    resinError.value = err?.message || "Could not calculate the resin estimate.";
  } finally {
    resinLoading.value = false;
  }
}

async function createResinQuotation() {
  if (!resinResult.value) return;
  if (!resinForm.customer) {
    showToast("Pick a customer before creating the quotation.", "error");
    return;
  }
  quotationLoading.value = true;
  try {
    const result = await frappeRequest({
      url: "buildsuite_core.api.ideal_erp.create_quotation_from_resin_estimate",
      params: {
        customer: resinForm.customer,
        project: resinForm.project || null,
        title: resinForm.title || "Industrial Epoxy Flooring",
        validity_days: Number(resinForm.validity_days || 30),
        estimate: resinResult.value,
      },
    });
    showToast(`Quotation ${result.name} created as a draft.`);
    window.location.href = `/quotations/${encodeURIComponent(result.name)}`;
  } catch (err) {
    showToast(err?.message || "Could not create quotation.", "error");
  } finally {
    quotationLoading.value = false;
  }
}

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

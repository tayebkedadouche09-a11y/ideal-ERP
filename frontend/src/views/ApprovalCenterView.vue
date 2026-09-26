<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import DeskPage from "@/components/desk/DeskPage.vue";
import DeskSelect from "@/components/desk/DeskSelect.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { showToast } from "@/utils/appToast";
import { applyApprovalAction, getApprovalCenter } from "@/data/approvalCenterApi";

const items = ref([]);
const loading = ref(true);
const error = ref("");
const filter = ref("all");
const busyKey = ref("");

async function load() {
	loading.value = true;
	error.value = "";
	try {
		const result = await getApprovalCenter();
		items.value = result?.items || [];
	} catch (err) {
		error.value = err?.message || "Could not load approvals.";
		items.value = [];
	} finally {
		loading.value = false;
	}
}

onMounted(load);

const doctypeOptions = computed(() => [
	"all",
	...Array.from(new Set(items.value.map((item) => item.doctype))).sort(),
]);

const visibleItems = computed(() =>
	filter.value === "all"
		? items.value
		: items.value.filter((item) => item.doctype === filter.value)
);

async function applyAction(item, action) {
	const key = item.doctype + ":" + item.name + ":" + action;
	busyKey.value = key;
	try {
		await applyApprovalAction(item.doctype, item.name, action);
		showToast(item.name + " → " + action);
		await load();
	} catch (err) {
		showToast(err?.message || "Could not apply workflow action.", "error");
	} finally {
		busyKey.value = "";
	}
}
</script>

<template>
	<DeskPage
		title="Approval Center"
		subtitle="One inbox over the same native Frappe documents and workflows used by each module."
		:breadcrumbs="[{ label: 'BuildSuite Core', to: '/' }, { label: 'Approval Center' }]"
	>
		<template #actions>
			<div class="flex items-center gap-2">
				<DeskSelect v-model="filter" class="!w-52">
					<option v-for="value in doctypeOptions" :key="value" :value="value">
						{{ value === "all" ? "All document types" : value }}
					</option>
				</DeskSelect>
				<button
					type="button"
					class="text-xs px-3 py-1.5 border border-ink-200 bg-white hover:bg-ink-50 rounded-md"
					@click="load"
				>
					Refresh
				</button>
			</div>
		</template>

		<div v-if="loading" class="py-16 text-center text-sm text-ink-400">
			Loading approval queue…
		</div>

		<div v-else-if="error" class="border border-danger-200 bg-danger-50 rounded-lg px-4 py-6 text-sm text-danger-700">
			{{ error }}
		</div>

		<div v-else class="space-y-3">
			<div class="flex items-center justify-between">
				<div class="text-sm text-ink-700">
					{{ visibleItems.length }} item{{ visibleItems.length === 1 ? "" : "s" }} waiting
				</div>
				<div class="text-[11px] text-ink-400">
					Actions are still governed by native workflow permissions.
				</div>
			</div>

			<div v-for="item in visibleItems" :key="item.doctype + ':' + item.name" class="bg-white border border-ink-200 rounded-lg p-4">
				<div class="flex items-start gap-4">
					<div class="w-9 h-9 rounded-lg bg-warning-50 text-warning-700 flex items-center justify-center flex-shrink-0">
						✓
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 flex-wrap">
							<span class="text-sm font-semibold text-ink-900 truncate">{{ item.title }}</span>
							<StatusBadge :status="item.state || 'Pending'" />
							<span class="text-[10px] text-ink-400">{{ item.doctype }}</span>
						</div>
						<div class="text-[11px] text-ink-500 mt-1 font-mono">{{ item.name }}</div>
					</div>
					<RouterLink :to="item.route" class="text-xs text-brand-700 hover:underline flex-shrink-0">
						Open →
					</RouterLink>
				</div>

				<div v-if="item.actions?.length" class="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-ink-100">
					<button
						v-for="transition in item.actions"
						:key="transition.action"
						type="button"
						class="text-xs px-3 py-1.5 border border-brand-200 bg-brand-50 text-brand-700 hover:bg-brand-100 rounded-md"
						:disabled="busyKey === item.doctype + ':' + item.name + ':' + transition.action"
						@click="applyAction(item, transition.action)"
					>
						{{ busyKey === item.doctype + ":" + item.name + ":" + transition.action ? "Applying…" : transition.action }}
					</button>
				</div>
			</div>

			<div v-if="!visibleItems.length" class="border border-ink-200 rounded-lg px-4 py-10 text-center bg-white">
				<div class="text-sm text-success-700 font-medium">Nothing is waiting for approval.</div>
				<p class="text-xs text-ink-500 mt-1">The queue is clear for the current user.</p>
			</div>
		</div>
	</DeskPage>
</template>

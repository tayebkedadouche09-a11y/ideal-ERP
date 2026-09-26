<script setup>
import { ref, computed, watch } from "vue";
import { RouterLink } from "vue-router";
import { useDataStore } from "@/stores";
import StatusBadge from "@/components/StatusBadge.vue";
import UserAvatar from "@/components/UserAvatar.vue";
import { fmtDate, fmtCompactINR } from "@/utils/format";
import { getWorkspaceIconPath } from "@/utils/workspaceIcons";
import { usePermissions } from "@/composables/usePermissions";
import { getProject360 } from "@/data/project360Api";

const { canEdit } = usePermissions();

const props = defineProps({
	project: { type: Object, required: true },
	pmName: { type: String, default: "" },
	activeBoq: { type: Object, default: null },
	projectReports: { type: Array, default: () => [] },
	delayedDays: { type: Number, default: 0 },
	scheduleSummary: { type: Object, default: null },
	progressBarColor: { type: Function, required: true },
});

const emit = defineEmits(["edit"]);

const live360 = ref(null);
const live360Loading = ref(false);
const live360Error = ref("");

async function loadProject360(projectId) {
	if (!projectId) {
		live360.value = null;
		return;
	}
	live360Loading.value = true;
	live360Error.value = "";
	try {
		live360.value = await getProject360(projectId);
	} catch (err) {
		live360Error.value = err?.message || "Project 360 is unavailable.";
	} finally {
		live360Loading.value = false;
	}
}

watch(() => props.project?.id, loadProject360, { immediate: true });

const liveFinance = computed(() => live360.value?.finance?.finance || {});
const liveInvoices = computed(() => live360.value?.finance?.invoices || {});
const liveForecast = computed(() => live360.value?.material_forecast || null);
const liveInsights = computed(() => (live360.value?.intelligence || []).slice(0, 3));


// The Progress Report is the one in-app report (its own project-scoped route). Every other
// tile links to the report in its owning workspace with `?project=<id>` so the report opens
// pre-filtered to this project — the report-view renderer seeds filters from the URL query,
// Delay Analysis reads route.query.project, and the finance P&L is project-scoped. Tiles with
// no report yet (cost-vs-budget) fall through to the /reports/<slug> stub, still project-carrying.
function reportLink(rt) {
	const project = props.project?.id;
	if (rt.routeName === "project-progress-report") {
		return {
			name: "project-progress-report",
			params: { id: project },
			query: { period: "weekly" },
		};
	}
	if (rt.to) {
		return { ...rt.to, query: { ...(rt.to.query || {}), project } };
	}
	return { path: `/reports/${rt.slug}`, query: { project } };
}

// S271 — four tiles show by default (fills the two-column grid); the `more` tiles sit
// behind Show more.
const reportsShowMore = ref(false);
const visibleReports = computed(() =>
	reportsShowMore.value ? props.projectReports : props.projectReports.filter((r) => !r.more)
);

const store = useDataStore();

function plannedCost() {
	if (props.activeBoq) return props.activeBoq.totals?.planned || 0;
	return props.project?.budget || 0;
}
function actualCost() {
	if (props.activeBoq) return props.activeBoq.totals?.actual || 0;
	return 0;
}
function costDeviation() {
	return actualCost() - plannedCost();
}
function costDeviationPct() {
	return plannedCost() ? (costDeviation() / plannedCost()) * 100 : 0;
}
function deviationColor(pct) {
	if (Math.abs(pct) < 0.5) return "text-ink-500";
	return pct > 0 ? "text-danger-700" : "text-success-700";
}
</script>

<template>
	<div class="pt-5">
		<!-- Live Project 360 — one server-side source joining execution, commercial, stock/procurement and intelligence. -->
		<section
			class="bg-white border border-ink-200 overflow-hidden mb-5"
			style="border-radius: 10px"
		>
			<header
				class="px-5 py-3 bg-gradient-to-r from-brand-50 to-white border-b border-ink-100 flex items-center gap-2"
			>
				<svg
					class="w-4 h-4 text-ink-700"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.8"
					stroke-linecap="round"
					stroke-linejoin="round"
					aria-hidden="true"
					v-html="getWorkspaceIconPath('activity')"
				/>
				<div>
					<h3 class="text-sm font-semibold text-ink-900">Live Project 360</h3>
					<p class="text-[11px] text-ink-500">One connected view of execution, money, supply and intelligence.</p>
				</div>
			</header>

			<div v-if="live360Loading" class="px-5 py-5 text-xs text-ink-400">
				Loading live project data…
			</div>
			<div v-else-if="live360Error" class="px-5 py-5 text-xs text-danger-700">
				{{ live360Error }}
			</div>
			<div v-else-if="live360" class="p-4">
				<div class="grid grid-cols-2 md:grid-cols-5 gap-3">
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500">Contract</div>
						<div class="text-sm font-semibold text-ink-900 mt-1 tabular-nums">{{ fmtCompactINR(live360.finance?.contract_value || 0) }}</div>
					</div>
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500">Actual cost</div>
						<div class="text-sm font-semibold text-ink-900 mt-1 tabular-nums">{{ fmtCompactINR(live360.finance?.actual_cost || 0) }}</div>
					</div>
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500">Invoiced</div>
						<div class="text-sm font-semibold text-ink-900 mt-1 tabular-nums">{{ fmtCompactINR(liveInvoices.gross_invoiced || 0) }}</div>
					</div>
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500">Outstanding</div>
						<div class="text-sm font-semibold text-ink-900 mt-1 tabular-nums">{{ fmtCompactINR(liveInvoices.outstanding || 0) }}</div>
					</div>
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500">Projected profit</div>
						<div class="text-sm font-semibold mt-1 tabular-nums" :class="liveFinance.projected_profit_position >= 0 ? 'text-success-700' : 'text-danger-700'">
							{{ fmtCompactINR(liveFinance.projected_profit_position || 0) }}
						</div>
					</div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500 mb-2">Material & procurement</div>
						<div v-if="liveForecast" class="text-xs text-ink-700">
							<div class="flex items-center justify-between gap-3">
								<span>Forecast</span><span class="font-medium">{{ liveForecast.status }}</span>
							</div>
							<div class="flex items-center justify-between gap-3 mt-1.5">
								<span>Procurement</span><span class="font-medium">{{ liveForecast.procurement_status }}</span>
							</div>
							<div v-if="liveForecast.material_request_ref" class="text-[11px] text-brand-700 mt-2">
								Material Request: {{ liveForecast.material_request_ref }}
							</div>
						</div>
						<div v-else class="text-xs text-ink-400">No material forecast created yet.</div>
					</div>

					<div class="border border-ink-100 rounded-lg p-3">
						<div class="text-[10px] uppercase tracking-wider text-ink-500 mb-2">Control signals</div>
						<div class="grid grid-cols-2 gap-3">
							<div>
								<div class="text-[10px] text-ink-500 uppercase">CPI</div>
								<div class="text-sm font-semibold text-ink-900">{{ Number(live360.evm?.cpi || 0).toFixed(2) }}</div>
							</div>
							<div>
								<div class="text-[10px] text-ink-500 uppercase">SPI</div>
								<div class="text-sm font-semibold text-ink-900">{{ Number(live360.evm?.spi || 0).toFixed(2) }}</div>
							</div>
							<div>
								<div class="text-[10px] text-ink-500 uppercase">Risk</div>
								<div class="text-sm font-semibold capitalize" :class="live360.risk?.level === 'high' ? 'text-danger-700' : live360.risk?.level === 'medium' ? 'text-warning-700' : 'text-success-700'">
									{{ live360.risk?.level || "low" }} · {{ Number(live360.risk?.score || 0).toFixed(0) }}
								</div>
							</div>
							<div>
								<div class="text-[10px] text-ink-500 uppercase">Critical tasks</div>
								<div class="text-sm font-semibold text-ink-900">{{ (live360.schedule?.critical_tasks || []).length }}</div>
							</div>
						</div>
						<div v-if="live360.changes" class="mt-3 text-[11px] text-ink-500">
							{{ live360.changes.pending_count }} pending change{{ live360.changes.pending_count === 1 ? "" : "s" }} · {{ fmtCompactINR(live360.changes.approved_cost_impact || 0) }} approved impact
						</div>
					</div>
				</div>

				<div class="border border-ink-100 rounded-lg p-3 mt-4">
					<div class="text-[10px] uppercase tracking-wider text-ink-500 mb-2">Company Intelligence</div>
					<div v-if="liveInsights.length" class="space-y-2">
						<div v-for="item in liveInsights" :key="item.kind + item.message" class="text-xs text-ink-700">
							<span class="font-medium text-ink-900">{{ item.kind }}</span> · {{ item.message }}
						</div>
					</div>
					<div v-else class="text-xs text-success-700">No connected intelligence signals currently raised.</div>
				</div>
			</div>
		</section>
		<!-- Summary strip -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
			<!-- Client -->
			<div class="bg-white border border-ink-200 p-3.5" style="border-radius: 8px">
				<div class="flex items-center gap-2">
					<svg
						class="w-4 h-4 text-ink-600"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						v-html="getWorkspaceIconPath('building-2')"
					/>
					<div class="text-[10px] uppercase tracking-wider text-ink-500 font-medium">
						Client
					</div>
				</div>
				<div class="text-sm text-ink-900 font-medium mt-1.5 truncate">
					{{ project.client || "—" }}
				</div>
			</div>

			<!-- Actual vs Planned -->
			<div class="bg-white border border-ink-200 p-3.5" style="border-radius: 8px">
				<div class="flex items-center gap-2">
					<svg
						class="w-4 h-4 text-ink-600"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						v-html="getWorkspaceIconPath('wallet')"
					/>
					<div class="text-[10px] uppercase tracking-wider text-ink-500 font-medium">
						Actual vs Planned
					</div>
				</div>
				<div class="flex items-baseline gap-1 mt-1.5 tabular-nums">
					<span class="text-base font-semibold text-ink-900">{{
						fmtCompactINR(actualCost())
					}}</span>
					<span class="text-xs text-ink-400">/ {{ fmtCompactINR(plannedCost()) }}</span>
				</div>
				<div
					class="text-[11px] mt-1 tabular-nums"
					:class="deviationColor(costDeviationPct())"
				>
					<span class="font-medium"
						>{{ costDeviation() > 0 ? "+" : ""
						}}{{ fmtCompactINR(Math.abs(costDeviation())) }}</span
					>
					<span class="ml-0.5"
						>({{ costDeviationPct() > 0 ? "+" : ""
						}}{{ costDeviationPct().toFixed(1) }}%)</span
					>
					<span class="text-ink-400 ml-0.5">{{
						costDeviationPct() > 0 ? "over" : "under"
					}}</span>
				</div>
			</div>

			<!-- Progress + delayed -->
			<div class="bg-white border border-ink-200 p-3.5" style="border-radius: 8px">
				<div class="flex items-center gap-2">
					<svg
						class="w-4 h-4 text-ink-600"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						v-html="getWorkspaceIconPath('chart-line')"
					/>
					<div class="text-[10px] uppercase tracking-wider text-ink-500 font-medium">
						Progress
					</div>
				</div>
				<div class="flex items-center gap-2 mt-1.5">
					<div
						class="flex-1 h-1.5 bg-ink-100 overflow-hidden"
						style="border-radius: 999px"
					>
						<div
							class="h-full"
							:class="progressBarColor(project)"
							:style="`width:${project.progress}%`"
						></div>
					</div>
					<span class="text-sm text-ink-900 font-semibold tabular-nums"
						>{{ project.progress }}%</span
					>
				</div>
				<div v-if="delayedDays > 0" class="text-[11px] text-danger-700 font-medium mt-1">
					Delayed by {{ delayedDays }}d
				</div>
				<div
					v-else-if="project.progress >= 100"
					class="text-[11px] text-success-700 font-medium mt-1"
				>
					Completed
				</div>
				<div v-else class="text-[11px] text-success-700 font-medium mt-1">On track</div>
			</div>

			<!-- Timeline -->
			<div class="bg-white border border-ink-200 p-3.5" style="border-radius: 8px">
				<div class="flex items-center gap-2">
					<svg
						class="w-4 h-4 text-ink-600"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
						v-html="getWorkspaceIconPath('calendar')"
					/>
					<div class="text-[10px] uppercase tracking-wider text-ink-500 font-medium">
						Timeline
					</div>
				</div>
				<div class="text-xs text-ink-900 font-medium mt-1.5 tabular-nums">
					{{ fmtDate(project.startDate) }} → {{ fmtDate(project.endDate) }}
				</div>
				<div v-if="scheduleSummary" class="text-[11px] text-ink-500 mt-1 tabular-nums">
					{{ scheduleSummary.totalDays }}d total · {{ scheduleSummary.remainingDays }}d
					remaining
				</div>
			</div>
		</div>

		<!-- Two-column main / sidebar layout -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
			<!-- Main column (span 2) -->
			<div class="lg:col-span-2 space-y-4">
				<section
					class="bg-white border border-ink-200 overflow-hidden"
					style="border-radius: 10px"
				>
					<header
						class="px-5 py-3 bg-gradient-to-r from-brand-50 to-white border-b border-ink-100 flex items-center gap-2"
					>
						<svg
							class="w-4 h-4 text-ink-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
							v-html="getWorkspaceIconPath('clipboard-list')"
						/>
						<h3 class="text-sm font-semibold text-ink-900">About this project</h3>
					</header>
					<div class="p-5">
						<p class="text-sm text-ink-800 leading-relaxed whitespace-pre-wrap">
							{{ project.description || "No description provided yet." }}
						</p>
					</div>
				</section>

				<section
					class="bg-white border border-ink-200 overflow-hidden"
					style="border-radius: 10px"
				>
					<header
						class="px-5 py-3 bg-gradient-to-r from-info-50 to-white border-b border-ink-100 flex items-center gap-2"
					>
						<svg
							class="w-4 h-4 text-ink-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
							v-html="getWorkspaceIconPath('chart-line')"
						/>
						<h3 class="text-sm font-semibold text-ink-900">Reports</h3>
						<span class="text-[11px] text-ink-500 tabular-nums">{{
							projectReports.length
						}}</span>
					</header>
					<div class="p-4">
						<!-- S270 — the Progress Report (primary) is an action, distinguished by a
										 brand tint rather than a larger control. -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-2">
							<RouterLink
								v-for="rt in visibleReports"
								:key="rt.slug"
								:to="reportLink(rt)"
								class="border p-2.5 flex items-center gap-2.5 transition-colors group"
								:class="
									rt.primary
										? 'bg-brand-50 border-brand-300 hover:bg-brand-100'
										: 'bg-white border-ink-200 hover:border-brand-400 hover:bg-brand-50'
								"
								style="border-radius: 8px"
								:title="rt.desc"
							>
								<span
									class="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 transition-colors"
									:class="
										rt.primary
											? 'bg-brand-600 text-white'
											: 'bg-ink-50 group-hover:bg-brand-50 text-ink-600 group-hover:text-brand-700'
									"
								>
									<svg
										class="w-4 h-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
										v-html="getWorkspaceIconPath(rt.icon)"
									/>
								</span>
								<span
									class="text-sm font-medium truncate transition-colors"
									:class="
										rt.primary
											? 'text-ink-900'
											: 'text-ink-900 group-hover:text-brand-700'
									"
									>{{ rt.label }}</span
								>
								<span
									v-if="rt.primary"
									class="ml-auto text-brand-700 text-sm flex-shrink-0 group-hover:translate-x-0.5 transition-transform"
									>→</span
								>
							</RouterLink>
						</div>
						<div class="border-t border-ink-100 mt-3 pt-2.5">
							<button
								type="button"
								class="text-xs text-brand-700 hover:underline"
								@click="reportsShowMore = !reportsShowMore"
							>
								{{ reportsShowMore ? "Show less ▴" : "Show more ▾" }}
							</button>
						</div>
					</div>
				</section>
			</div>

			<!-- Sidebar (span 1) -->
			<div class="space-y-4">
				<section
					class="bg-white border border-ink-200 overflow-hidden"
					style="border-radius: 10px"
				>
					<header
						class="px-4 py-3 bg-gradient-to-r from-brand-50 to-white border-b border-ink-100 flex items-center gap-2"
					>
						<svg
							class="w-4 h-4 text-ink-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
							v-html="getWorkspaceIconPath('hr')"
						/>
						<h3 class="text-sm font-semibold text-ink-900">Project Manager</h3>
					</header>
					<div class="p-4 flex items-center gap-3">
						<template v-if="project.pm">
							<UserAvatar :user-id="project.pm" size="md" />
							<div class="min-w-0 flex-1">
								<div class="text-sm font-semibold text-ink-900 truncate">
									{{
										pmName || store.teamMember(project.pm)?.name || project.pm
									}}
								</div>
								<div class="text-[11px] text-ink-500 truncate">
									{{ project.pm }}
								</div>
							</div>
						</template>
						<div v-else class="text-sm text-ink-500">No project manager assigned.</div>
					</div>
				</section>

				<section
					class="bg-white border border-ink-200 overflow-hidden"
					style="border-radius: 10px"
				>
					<header
						class="px-4 py-3 bg-gradient-to-r from-ink-50 to-white border-b border-ink-100 flex items-center gap-2"
					>
						<svg
							class="w-4 h-4 text-ink-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.8"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
							v-html="getWorkspaceIconPath('tag')"
						/>
						<h3 class="text-sm font-semibold text-ink-900">Project details</h3>
						<button
							v-if="canEdit('project')"
							type="button"
							class="ml-auto text-[11px] text-brand-700 hover:text-brand-800 font-medium"
							@click="emit('edit')"
						>
							Edit
						</button>
					</header>
					<dl class="divide-y divide-ink-100">
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Status</dt>
							<dd><StatusBadge :status="project.status" /></dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Priority</dt>
							<dd><StatusBadge :status="project.priority" /></dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Category</dt>
							<dd class="text-ink-800">{{ project.type || "—" }}</dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Project Type</dt>
							<dd class="text-ink-800">{{ project.projectType || "—" }}</dd>
						</div>
						<div
							v-if="store.isMultiCompany && project.company"
							class="flex items-center justify-between px-4 py-2.5 text-xs"
						>
							<dt class="text-ink-500 font-medium">Company</dt>
							<dd class="flex items-center gap-1.5 text-ink-800 min-w-0">
								<span
									v-if="store.companyById(project.company)"
									:class="store.companyById(project.company).color"
									class="w-2 h-2 flex-shrink-0"
									style="border-radius: 999px"
								></span>
								<span class="truncate">{{
									store.companyById(project.company)?.shortName ||
									project.company
								}}</span>
							</dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Location</dt>
							<dd class="text-ink-800 truncate ml-2">
								{{ project.location || "—" }}
							</dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Project ID</dt>
							<dd class="text-ink-800 font-mono">{{ project.code }}</dd>
						</div>
						<div class="flex items-center justify-between px-4 py-2.5 text-xs">
							<dt class="text-ink-500 font-medium">Created</dt>
							<dd class="text-ink-700 tabular-nums">
								{{ fmtDate(project.createdAt) }}
							</dd>
						</div>
					</dl>
				</section>
			</div>
		</div>
	</div>
</template>

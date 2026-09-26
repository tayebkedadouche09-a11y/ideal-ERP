<script setup>
/*
 * Legacy report-route dispatcher.
 *
 * Older workspace configuration may still point at /reports/:slug. These
 * slugs resolve to the live in-app report/module that owns the real data.
 * This component never renders fabricated report rows.
 */
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import DeskPage from "@/components/desk/DeskPage.vue";

const route = useRoute();
const router = useRouter();

const DESTINATIONS = {
	"project-status-summary": {
		title: "Project Dashboard",
		to: { path: "/project-dashboard" },
		description: "Live project health, schedule, commitments, decisions and cost position.",
	},
	"task-completion-by-week": {
		title: "Progress Entries",
		to: { path: "/progress-entries" },
		description: "Live task progress entries filed by the project team.",
	},
	"pending-progress-entries": {
		title: "Task Progress Entries",
		to: { path: "/progress-entries" },
		description: "Live progress-entry register with task and date information.",
	},
	"stage-vs-actual": {
		title: "Stage Planning",
		to: { path: "/stage-plannings" },
		description: "Live stage plans, approvals and task progress.",
	},
	"labour-deployed": {
		title: "Attendance Summary",
		to: { path: "/workforce/attendance-summary" },
		description: "Live workforce attendance and deployment summary.",
	},
};

const slug = computed(() => String(route.params.slug || ""));
const destination = computed(() => DESTINATIONS[slug.value] || null);

onMounted(() => {
	if (!destination.value) return;
	router.replace({
		...destination.value.to,
		query: { ...route.query },
	});
});
</script>

<template>
	<DeskPage
		:title="destination?.title || 'Report not found'"
		:subtitle="destination?.description || 'This legacy report route is no longer registered.'"
		:breadcrumbs="[
			{ label: 'BuildSuite Core', to: '/' },
			{ label: 'Reports' },
			{ label: destination?.title || slug || 'Unknown report' },
		]"
	>
		<div class="border border-ink-200 rounded-lg px-5 py-8 text-center bg-white">
			<div v-if="destination" class="text-sm text-ink-600">
				Opening the live report…
			</div>
			<template v-else>
				<div class="text-sm font-medium text-ink-800">No live report is registered for this route.</div>
				<p class="text-xs text-ink-500 mt-1">
					Use the Project Dashboard, Progress Entries, Stage Planning or Workforce reports from their live modules.
				</p>
			</template>
		</div>
	</DeskPage>
</template>

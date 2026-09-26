<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { DeskPage } from "@/components/desk";
import DeskField from "@/components/desk/DeskField.vue";
import DeskInput from "@/components/desk/DeskInput.vue";
import DeskSearchableSelect from "@/components/desk/DeskSearchableSelect.vue";
import { useProjectOptions } from "@/composables/useProjectOptions";
import { frappeRequest } from "frappe-ui-frappe-request";
import { showToast } from "@/utils/appToast";

const { projectOptions } = useProjectOptions();

const project = ref("");
const language = ref("fr");
const transcript = ref("");
const priority = ref("Medium");
const proposal = ref(null);
const busy = ref(false);
const creating = ref(false);
const error = ref("");
const listening = ref(false);

let recognition = null;

const supported = computed(() => {
	if (typeof window === "undefined") return false;
	return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
});

function startListening() {
	error.value = "";
	proposal.value = null;
	const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
	if (!Recognition) {
		error.value = "This browser does not expose Speech Recognition. You can still paste/type a transcript below.";
		return;
	}
	recognition?.stop?.();
	recognition = new Recognition();
	recognition.lang = language.value === "ar" ? "ar-DZ" : language.value === "en" ? "en-US" : "fr-FR";
	recognition.continuous = true;
	recognition.interimResults = true;

	recognition.onstart = () => {
		listening.value = true;
	};
	recognition.onend = () => {
		listening.value = false;
	};
	recognition.onerror = (event) => {
		listening.value = false;
		error.value = event?.error ? "Speech recognition: " + event.error : "Speech recognition failed.";
	};
	recognition.onresult = (event) => {
		const parts = [];
		for (let i = event.resultIndex; i < event.results.length; i++) {
			parts.push(event.results[i][0]?.transcript || "");
		}
		const chunk = parts.join(" ").trim();
		if (chunk) transcript.value = chunk;
	};
	recognition.start();
}

function stopListening() {
	recognition?.stop?.();
	listening.value = false;
}

function clearAll() {
	stopListening();
	transcript.value = "";
	proposal.value = null;
	error.value = "";
}

async function parse() {
	if (!project.value || !transcript.value.trim()) {
		error.value = "Pick a project and provide a transcript.";
		return;
	}
	busy.value = true;
	error.value = "";
	try {
		const result = await frappeRequest({
			url: "buildsuite_core.api.ideal_erp.voice_to_work",
			params: {
				project: project.value,
				transcript: transcript.value,
				language: language.value,
				confirm: 0,
				priority: priority.value,
			},
		});
		proposal.value = result?.proposal || null;
	} catch (err) {
		error.value = err?.message || "Could not interpret the transcript.";
	} finally {
		busy.value = false;
	}
}

async function confirmAndCreate() {
	if (!project.value || !transcript.value.trim()) return;
	creating.value = true;
	error.value = "";
	try {
		const result = await frappeRequest({
			url: "buildsuite_core.api.ideal_erp.voice_to_work",
			params: {
				project: project.value,
				transcript: transcript.value,
				language: language.value,
				confirm: 1,
				priority: priority.value,
			},
		});
		if (result?.created) {
			showToast(result.name + " created.");
			proposal.value = result.proposal;
		} else {
			showToast(result?.proposal?.next_step || "No document was created.", "warning");
			proposal.value = result?.proposal || proposal.value;
		}
	} catch (err) {
		error.value = err?.message || "Could not create the work item.";
	} finally {
		creating.value = false;
	}
}

onBeforeUnmount(stopListening);
</script>

<template>
	<DeskPage
		title="Voice to Work"
		subtitle="Speak or paste a site note, review the detected action, then confirm before anything is created."
		:breadcrumbs="[{ label: 'Site Execution', to: '/site-execution' }, { label: 'Voice to Work' }]"
	>
		<DeskField label="Project" required>
			<DeskSearchableSelect v-model="project" :options="projectOptions" placeholder="Pick a project…" search-placeholder="Search projects…" />
		</DeskField>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
			<DeskField label="Language">
				<select v-model="language" class="w-full text-sm border border-ink-200 rounded-md px-3 py-2 bg-white">
					<option value="fr">Français</option>
					<option value="ar">العربية</option>
					<option value="en">English</option>
				</select>
			</DeskField>
			<DeskField label="Priority">
				<select v-model="priority" class="w-full text-sm border border-ink-200 rounded-md px-3 py-2 bg-white">
					<option>Low</option>
					<option>Medium</option>
					<option>High</option>
				</select>
			</DeskField>
			<DeskField label="Recognition">
				<div class="flex items-center gap-2">
					<button
						type="button"
						class="text-xs px-3 py-2 rounded-md border"
						:class="listening ? 'bg-danger-50 border-danger-200 text-danger-700' : 'bg-brand-50 border-brand-200 text-brand-700'"
						@click="listening ? stopListening() : startListening()"
					>
						{{ listening ? "Stop" : "Start mic" }}
					</button>
					<span class="text-[11px] text-ink-500">{{ supported ? "Browser STT available" : "Type/paste transcript" }}</span>
				</div>
			</DeskField>
		</div>

		<DeskField label="Transcript" class="mt-5">
			<DeskInput v-model="transcript" placeholder="Ex: Il y a un retard sur le sol, vérifier demain…" />
		</DeskField>

		<div class="flex flex-wrap gap-2 mt-4">
			<button type="button" class="desk-save-btn text-xs" :disabled="busy" @click="parse">
				{{ busy ? "Reading…" : "Interpret" }}
			</button>
			<button
				v-if="proposal"
				type="button"
				class="text-xs px-3 py-1.5 rounded-md border border-brand-300 bg-brand-50 text-brand-700"
				:disabled="creating || proposal.action_type === 'photo' || proposal.action_type === 'purchase'"
				@click="confirmAndCreate"
			>
				{{ creating ? "Creating…" : "Confirm & create work item" }}
			</button>
			<button type="button" class="text-xs text-ink-600 hover:text-ink-900" @click="clearAll">Clear</button>
		</div>

		<div v-if="error" class="mt-4 px-3 py-2 rounded-md bg-danger-50 border border-danger-200 text-xs text-danger-700">
			{{ error }}
		</div>

		<div v-if="proposal" class="mt-5 border border-ink-200 rounded-lg bg-white p-4">
			<div class="text-[10px] uppercase tracking-wider text-ink-500">Proposed action</div>
			<div class="flex items-center gap-3 mt-2">
				<span class="text-sm font-semibold text-ink-900 capitalize">{{ proposal.action_type }}</span>
				<span class="text-xs text-ink-500">confidence {{ Math.round((proposal.confidence || 0) * 100) }}%</span>
			</div>
			<p class="text-sm text-ink-700 mt-2">{{ proposal.text }}</p>
			<p v-if="proposal.next_step" class="text-xs text-warning-700 mt-2">{{ proposal.next_step }}</p>
		</div>
	</DeskPage>
</template>

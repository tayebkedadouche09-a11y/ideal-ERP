# IDEAIL ERP — Capability Ports

The merge is now one runtime. The following capabilities are deliberately added
around the canonical BuildSuite/ERPNext models rather than copied as second
applications.

## From Ideal-tayeb1

### Client progress billing
Ports the IPC/progress-billing idea into the same project contract and invoice
flow. It must terminate in ERPNext Sales Invoice documents.

### Retention release
Adds a release workflow against the canonical project/client billing records.
No second receivable or accounting engine is introduced.

### Material planning
Adds forecast/requirement views over ERPNext stock and BuildSuite project
consumption. It does not create another inventory ledger.

## From Ideal-tayeb2

### AI estimation
AI drafts BOQ/rate/assumption candidates. Human confirmation is required before
a canonical BOQ or quote is mutated.

### Semantic cost matching
IDEAIL now contains an offline baseline matcher. Exact/token matching is the
fallback; an embedding provider can later replace or augment it without a
second catalog.

### Advanced schedule / 4D
Future adapter targets the canonical Task/Schedule records. The existing
schedule engine remains the source of truth.

### EVM / 5D
EVM and cost-model calculations consume canonical project baseline/actuals and
write analytical snapshots only. Accounting remains ERPNext.

### Risk / change intelligence
Risk and change analysis reference existing project, task, cost and change
records. They do not create parallel project masters.

### Voice / evidence
Voice is a capture channel. It produces a draft structured action which follows
the normal validate/approve/post workflow.

### Documents / CDE
Document intelligence enriches project files and metadata; it does not replace
ERPNext/Frappe file storage.

### CAD / BIM / takeoff
These are adapters connected to Project, BOQ, Cost Code and Task. The digital
construction layer never becomes a second ERP.

## IDEAIL-native

### Company Intelligence
A deterministic, evidence-first rule layer is already implemented. It can be
extended with historical similarity, LLM explanation and forecasting later.

### Resin / epoxy technical estimator
A pure calculation engine is already implemented for area, thickness, solids,
density, waste, primer, labour and equipment. The estimator returns a cost
draft; the project/quote transaction remains canonical.

### Algeria / DZD
The localization layer remains part of the unified application, not a country
fork.

## Non-duplication rule

For every new feature ask:

1. Which canonical document already represents this fact?
2. Can this capability attach to that document instead of creating another
   master?
3. Does the output need an ERPNext posting, an analytical snapshot, or only a
   draft?
4. Where is the evidence stored?

If a feature would create a second ledger, stock engine, BOQ master or project
master, it is rejected and re-designed as an adapter.

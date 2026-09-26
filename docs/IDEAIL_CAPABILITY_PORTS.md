# IDEAIL ERP — Unified Capability Spine

IDEAIL ERP is one Frappe/ERPNext runtime. The three source repositories were
merged by capability, not by stacking applications beside each other.

## Canonical ownership

ERPNext remains the system of record for accounting, stock, parties, invoices,
payments and posting.

BuildSuite Core remains the system of record for Project, Task, BOQ, Cost Codes,
construction execution, procurement, subcontract, workforce, equipment and
schedule records.

IDEAIL adds intelligence and industry workflows around those canonical records.

## Connected flow

The application now exposes one connected project spine:

Project -> BOQ / estimate -> technical takeoff -> material requirement ->
stock + consumption + open procurement -> Task schedule -> actual cost ->
EVM / 5D -> progress billing / IPC -> ERPNext Sales Invoice -> retention ->
change intelligence -> risk -> Company Intelligence -> forecasting / anomalies /
lessons learned.

Field evidence is another input channel on the same spine:

browser voice transcript / mobile photo / site diary -> draft evidence -> human confirmation ->
Project / Task / document evidence -> intelligence. Voice-to-Work can create a confirmed Project ToDo;
purchasing and photo actions remain review-first.

No step creates a second Project, BOQ, Stock Ledger or Accounting Ledger.

## Source contributions

### Ideal-tayeb1

Implemented into the canonical runtime:

- Client progress billing / IPC
- Retention release with over-release protection
- Material forecast connected to stock, project consumption and open purchase orders

### Ideal-tayeb2

Implemented as connected capability contracts and deterministic adapters:

- AI-style estimation draft with canonical cost matching and mandatory confirmation
- Advanced schedule analysis / critical path
- EVM / 5D analytical snapshots
- Risk and change intelligence
- Voice evidence classification
- Project document/CDE metadata normalization
- CAD/BIM/takeoff normalization into BOQ-review candidates
- Site diary, photo evidence, approvals and site-inventory variance helpers
- Forecasting, anomaly detection and lessons learned

Actual external LLM, server-side speech-to-text, CAD/BIM parser or embedding provider can be
plugged in behind the same interfaces. Browser speech recognition is supported for Voice-to-Work
when the browser exposes it. Those providers are not allowed to become a second system of record.

## Industry layer

IDEAIL-native technical estimation supports:

- Resin / epoxy
- Industrial flooring
- Technical coatings
- Waterproofing and decorative-concrete commercial calculations

The estimator creates technical/cost drafts. Confirmation posts through the canonical project, BOQ and ERPNext commercial flow.
The current resin estimator can create a native ERPNext Quotation draft with server-authoritative margin calculation.

## Localization

The same application supports FR / AR / EN, Arabic RTL and DZD-ready commercial
formatting. Tax and accounting rules remain configurable in ERPNext rather than
hard-coded inside the industry calculators.

## Non-duplication contract

For every future capability:

1. Attach to the canonical document that already owns the fact.
2. Use ERPNext posting when money or stock must be posted.
3. Use analytical snapshots for EVM/risk/forecasting.
4. Keep AI/voice/takeoff outputs as drafts until a human confirms them.
5. Store evidence in the shared Frappe document/file layer.

A feature that introduces a second project master, BOQ master, stock engine,
commercial ledger or accounting ledger is rejected and redesigned.

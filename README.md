# IDEAIL ERP

Unified construction + business ERP built as a single Frappe/ERPNext application.

This repository is the consolidation target for three internal source projects:

- `Ideal-tayeb` — BuildSuite Core / ERPNext v16 construction execution engine.
- `Ideal-tayeb1` — older Construction Management Suite / ERPNext v15 feature set.
- `Ideal-tayeb2` — OpenConstructionERP platform with advanced estimating, BIM/CAD, project controls, documents, AI and modular capabilities.

## Consolidation rule

IDEAIL ERP is **not** a three-way copy.

One capability gets one canonical implementation. When the three projects overlap, we keep the implementation that is structurally strongest for the unified product and port only missing behaviour from the other projects.

The selected foundation is the BuildSuite Core architecture on ERPNext v16 because it already models construction reality as operational documents while leaving accounting to ERPNext.

## Unified product layers

1. **ERP Core** — companies, customers, suppliers, items, stock, buying, selling, payments and accounting through ERPNext.
2. **Project Execution** — projects, work packages, tasks, stages, progress, scheduling, site execution, workforce and equipment.
3. **Commercial Construction** — BOQ, rate library, estimation, procurement, subcontracting, measurements, billing, retention and cost control.
4. **Intelligence** — cost/quantity matching, AI-assisted estimating, variance explanations, risk, forecasting, anomaly detection and Company Intelligence.
5. **Digital Construction** — CAD/BIM/takeoff/4D/5D and document/CDE capabilities, added only where they do not duplicate the ERP/project core.
6. **Field & Collaboration** — daily diary, voice capture, approvals, photos, forms, mobile-first workflows and evidence.
7. **Regional & Localization** — Arabic/RTL plus regional tax/compliance packs, with Algeria/DZD treated as a first-class target rather than a hardcoded afterthought.

## Current status

The unified product spine is implemented as additive functionality over the canonical Frappe/ERPNext runtime.

Implemented connected flows include:

- Project 360: project, BOQ, finance, procurement, stock, EVM, schedule, changes, risk and Company Intelligence.
- BOQ → Material Forecast → Material Request → Purchase Order / receipt / consumption.
- IPC → retention calculation → ERPNext Sales Invoice → payment/receivable tracking.
- Retention Release → ERPNext Sales Invoice with native cancellation sync.
- Resin / epoxy technical estimate → margin → native ERPNext Quotation draft.
- Daily Briefing + Smart Priority over live project/approval/supply signals.
- Approval Center over native Frappe workflows and document states.
- Voice-to-Work: browser transcript → explainable proposal → confirmed project ToDo, with purchasing/photo actions kept as review steps.
- Legacy report routes dispatch to live in-app reports instead of rendering fabricated sample data.
- FR / AR / EN, RTL and DZD-ready commercial formatting remain part of the unified layer.

The remaining production gate is live Bench/Frappe/ERPNext runtime validation: migrate, permissions, workflows, submit/cancel behavior, GL/stock posting, and end-to-end document transactions on a real site. No second ERP, ledger, stock engine or project master is introduced.

See [docs/UNIFICATION_MATRIX.md](docs/UNIFICATION_MATRIX.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

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

- Repository initialized as the single consolidation target.
- Unification matrix and architecture decisions committed.
- Next implementation work is staged as additive modules over the canonical construction core; duplicated source systems are not retained as parallel runtimes.

See [docs/UNIFICATION_MATRIX.md](docs/UNIFICATION_MATRIX.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

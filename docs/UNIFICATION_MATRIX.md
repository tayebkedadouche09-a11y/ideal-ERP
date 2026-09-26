# IDEAIL ERP — Three-Source Unification Matrix

## 1. Decision method

The three source projects overlap heavily, but they do not solve the same problem at the same depth.

- Ideal-tayeb / BuildSuite Core is the operational construction engine on ERPNext v16.
- Ideal-tayeb1 / Construction Management Suite contains an older, compact construction ERP feature set, especially IPC/progress billing, retention and material planning.
- Ideal-tayeb2 / OpenConstructionERP is a much broader construction platform: estimating, cost databases, CAD/BIM, 4D/5D, documents, quality/safety, AI and project intelligence.

IDEAIL ERP chooses one canonical implementation for each domain. Other projects contribute only non-duplicated behaviour, workflow ideas or specialized algorithms.

---

## 2. Core ERP and accounting

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Company / multi-company | ERPNext + BuildSuite scoping | ERPNext integration | Platform-level company support | BuildSuite + ERPNext canonical |
| Customers / suppliers | ERPNext | ERPNext | CRM/vendor modules | ERPNext canonical |
| Sales / purchase | ERPNext | ERPNext | Project commerce modules | ERPNext canonical |
| Ledger / GL | ERPNext owns ledger | ERPNext | Finance layer | Never re-implement ledger |
| Payments | ERPNext Payment Entry | ERPNext integration | Finance | ERPNext canonical |
| Stock | ERPNext | Material planning around ERPNext | Site inventory/procurement | ERPNext stock + site layer |

### How it works

Operational construction documents capture field reality. Submitted documents generate or reference ERPNext accounting/stock documents. This prevents a second competing accounting engine.

---

## 3. Project structure and execution

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Project spine | Strong: project → work package → task → stage | ERPNext Project | Project/portfolio hierarchy | BuildSuite canonical |
| Work packages | Native | Limited | Tasks / schedule | BuildSuite canonical |
| Tasks | Native + dependency engine | Basic project tasks | Advanced tasks | BuildSuite canonical; add missing intelligence |
| Progress | Roll-up from task/work package | Site progress | Period deltas, S-curves, geo-tagged entries | BuildSuite roll-up + OpenConstruction analytics |
| Schedule | Gantt, FS/SS/FF, lag, cascade | Basic | 4D + Last Planner | BuildSuite engine + 4D/advanced planning layer |
| Portfolio | Limited | Limited | Native portfolio | Add non-duplicated portfolio layer |
| Stage planning | Native | Basic | Phase/look-ahead ideas | BuildSuite canonical |

### Canonical flow

Project → Stage → Work Package → Task → Progress → Cost/Value → Dashboard

Every lower-level operational record derives project/company context rather than asking users to repeat it.

---

## 4. BOQ and estimating

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Hierarchical BOQ | Strong | Strong | Strong | BuildSuite canonical BOQ engine |
| BOQ revisions | Yes | Yes | Yes | One revision model |
| Assemblies | Yes | Rate analysis | Advanced assemblies | BuildSuite assembly model + richer calculation rules |
| Rate history | Yes | Rate Analysis | Cost database + price index | Unified Rate Master |
| Cost codes | First-class | First-class | Cost model | BuildSuite canonical |
| Resource build-up | Yes | Strong | Very strong | Add resource decomposition to Rate Master |
| Conceptual estimate | No | No | Yes | Add as estimation mode |
| AI estimate builder | No | No | Yes | Add as AI service on top of canonical BOQ/rates |
| Design alternatives | No | No | Yes | Add as scenario/option layer |
| Waste / coverage factors | Partial | Resource costing | Yes | Add calculation factors to estimation engine |
| Post-calculation learning | Limited | Limited | Yes | Add productivity feedback loop |

### Canonical estimating flow

Scope → BOQ → Rate/Assembly → Resource demand → Cost → Markups → Tender/Quote → Baseline

AI never posts financial documents directly. It drafts; a user confirms; then the canonical document workflow executes.

---

## 5. Procurement and materials

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Material Request | Yes | Yes | Yes | ERPNext/BuildSuite canonical |
| Purchase Order | Yes | Yes | Yes | ERPNext canonical |
| Receipt | Yes | ERPNext | Yes | ERPNext canonical |
| Consumption | Yes | Yes | Site inventory | BuildSuite/site layer |
| Material forecast | Limited | Explicit | Resource summary/forecast | Add planning layer from #1 + #2 ideas |
| Supplier catalog | Supplier/rate masters | Basic | Advanced vendor catalogs | Unified supplier/rate catalog |
| Site inventory | Cost-coded consumption | Basic | Dedicated site inventory | Add site inventory view over ERPNext stock |
| Transfers | ERPNext/stock | Site transfers | Procurement/site logistics | ERPNext Stock Entry + site UX |

---

## 6. Subcontracting and billing

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Work orders | Strong | Strong | Contract engine | BuildSuite canonical |
| Schedule of values | Yes | Payment certificates | Contract types | BuildSuite + contract extension |
| Measurement book | Yes | Payment certificates | Variations/site measurements | BuildSuite measurement foundation |
| Subcontract bill | Yes → Purchase Invoice | Payment certificates | Subcontract applications | BuildSuite canonical accounting bridge |
| IPC / client progress billing | Explicitly outside core | Strong | Variations/progress billing concepts | Port as additive commercial module |
| Retention release | Explicitly outside core | Strong | Contract retention | Port retention workflow once |
| Advances | Settlement model | Included in certificates | Contract/finance | BuildSuite settlement principle |
| Variations / change orders | Scope Change Order | Basic | Strong change/claims family | BuildSuite base + advanced change layer |

---

## 7. Workforce and equipment

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Field workers | Native | Attendance | Field Time | BuildSuite canonical identity |
| Crews | Native | Basic | Resource planning | BuildSuite + resource availability |
| Daily muster | Native | Site attendance | Field labour | BuildSuite canonical |
| Overtime | Native | Attendance | Payroll | BuildSuite + payroll integration later |
| Machinery | Native | Equipment | Fleet/telemetry | BuildSuite canonical equipment + telemetry adapter |
| Hired equipment cost | Yes | Basic | Owned/rented/telemetry | Unified equipment costing |

---

## 8. Project finance and controls

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Project P&L | Strong | Project costing | Finance/control dashboards | BuildSuite canonical |
| Budget vs actual | Yes | Strong | EVM/5D | BuildSuite baseline + EVM layer |
| Cost codes | Strong | Strong | Cost model | One canonical cost-code model |
| Cash flow | Finance | Forecasting | CVR/cashflow | Unified project cashflow |
| EVM | Not primary | Not primary | Strong | Add as non-duplicated control module |
| Risk register | Limited | No | Strong | Add risk module |
| Delay analysis | Yes | Limited | Advanced schedule intelligence | BuildSuite delay model + analytics |
| Change intelligence | Limited | No | Strong | Add change intelligence layer |

---

## 9. Site, evidence and collaboration

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Daily site report | Yes | Yes | Strong field diary | BuildSuite/site canonical + richer evidence |
| Photos | Basic support | Basic | Strong diary/reality capture | Unified evidence attachments |
| Voice capture | No | No | Yes | Add voice-to-draft workflow |
| Forms/checklists | Limited | Site reports | Dedicated forms/checklists | Add reusable form engine |
| Phone/verbal records | No | No | Phone log | Optional evidence module |
| Approvals | Workflows | Workflows | File approvals / review authority | One approval engine + document approvals |

---

## 10. Documents and information management

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| Project documents | ERPNext/Frappe files | ERPNext | Dedicated CDE | Add project document spine |
| Versioning | Frappe document/file history | Basic | File version chains | Add explicit file version entity |
| CDE / ISO 19650 concepts | No | No | Yes | Optional advanced document layer |
| OCR search | No | No | Yes | Add document intelligence |
| Correspondence | No | No | Yes | Add communication record layer |
| Transmittals | No | No | Yes | Add only if required by project type |

---

## 11. BIM / CAD / takeoff

| Capability | Ideal-tayeb | Ideal-tayeb1 | Ideal-tayeb2 | IDEAIL decision |
|---|---|---|---|---|
| CAD import | No | No | Yes | Advanced module |
| BIM hub | No | No | Yes | Advanced module |
| DWG takeoff | No | No | Yes | Advanced module |
| Clash detection | No | No | Yes | Advanced module |
| Point cloud | No | No | Yes | Advanced module |
| BOQ ↔ BIM cost match | No | No | Yes | AI/cost intelligence bridge |

These stay additive. They do not replace ERPNext projects, BOQ or accounting.

---

## 12. AI and intelligence

### Selected functions

1. AI Estimate Builder
   - Input: scope text, project type, location and optional history.
   - Output: draft BOQ/rates/assumptions.
   - Human confirmation required.

2. Semantic Cost Match
   - Match a material/work description to the canonical rate catalog.
   - Exact match first, then semantic candidates.
   - Store the selected match as auditable data.

3. Voice Capture
   - Spoken site note → structured draft.
   - User confirms before posting consumption, attendance or progress.

4. Company Intelligence
   - Combine project cost, progress, schedule, procurement and quality signals.
   - Explain variance as evidence-linked findings, not opaque scores.

5. Forecasting
   - Use project baseline + actuals + schedule/progress data.
   - Produce expected cost/time/cashflow views.

6. Anomaly detection
   - Flag unusual material usage, cost spikes, delays, duplicated transactions or suspicious combinations.
   - Never auto-delete or auto-post.

7. Lessons learned
   - After project close, store causes, corrective actions and reusable knowledge.

---

## 13. Quality and safety

Ideal-tayeb2 contains a broad quality/safety family. IDEAIL adopts the data model concepts without copying a second ERP:

- inspections
- NCR
- punch list
- QMS
- incident/observation
- HSE
- commissioning
- compliance documents
- requirements / quality gates

The canonical record remains project-linked and cost/schedule-aware.

---

## 14. Localization

Selected:

- Arabic / RTL as first-class UI concern.
- French and English.
- DZD/DA and Algerian business formatting.
- Extensible regional tax/compliance packs.

The old project's KSA/UAE/Pakistan/India packs are treated as patterns, not as Algeria rules. No foreign tax rule is silently applied to Algerian companies.

---

## 15. Industrial finishing / resin specialization

This is IDEAIL's own differentiator, not copied from the three projects.

The core construction engine remains generic, while an industry layer provides:

- area-based quantity calculation
- thickness / coverage
- resin + hardener + primer systems
- waste factors
- labour productivity
- equipment usage
- site measurements
- technical method statements
- quote from technical calculation
- baseline vs actual material consumption
- real project margin

Canonical flow:

Measurement → Technical Recipe → Material Requirement → Cost → Margin → Quote → Project → Actuals

The same project can still use normal construction BOQs.

---

## 16. What is deliberately NOT duplicated

IDEAIL keeps exactly one canonical implementation of:

- accounting / GL
- customers / suppliers
- stock
- company
- project identity
- BOQ identity
- rate master
- cost code
- task identity
- payment posting
- subcontract accounting bridge

No second ledger, no second stock engine, no second project engine and no parallel BOQ system.

---

## 17. Chosen architecture

Canonical base: Ideal-tayeb / BuildSuite Core on Frappe/ERPNext v16.

Ports from Ideal-tayeb1: client progress billing, retention-release flow, material planning ideas and compact role/workflow ergonomics.

Ports from Ideal-tayeb2: AI estimation, semantic matching, EVM/5D controls, advanced planning, risk/change intelligence, voice/evidence, document/CDE, CAD/BIM/takeoff and modular platform patterns.

IDEAIL-original layer: industrial finishing/resin calculation, Company Intelligence, unified AI assistant, Algerian/DZD localization, and the final cross-module automation model.

The three projects therefore become one product architecture rather than three copied codebases.

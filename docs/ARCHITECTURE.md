# IDEAIL ERP — Unified Architecture

## Runtime

Primary framework: Frappe Framework v16  
ERP foundation: ERPNext v16  
Application identity: IDEAIL ERP  
Canonical construction package: the BuildSuite Core implementation already proven in the Ideal-tayeb source.

The repository is a single product. Source projects are references/lineage, not three parallel applications.

## Layer 0 — ERPNext system of record

ERPNext remains authoritative for:
- Company
- Customer / Supplier
- Item
- Warehouse / Stock
- Sales / Purchase
- Invoice
- Payment Entry
- Journal Entry
- GL

Construction modules generate standard ERPNext documents instead of cloning the ledger.

## Layer 1 — Construction operating model

Canonical entities:

Project  
Stage  
Work Package  
Task  
BOQ  
BOQ Item  
Rate Master  
Cost Code  
Material Request  
Work Order  
Measurement  
Progress  
Field Attendance  
Equipment Usage

Each cost-bearing record carries project and cost-code context.

## Layer 2 — Commercial control

Adds:
- estimation revisions
- tender / quote lifecycle
- client progress billing
- retention
- subcontract measurement/billing
- change orders / variations
- budget vs actual
- EVM
- cashflow

All financial posting terminates in ERPNext.

## Layer 3 — Intelligence

A single intelligence service consumes canonical records:

Project data → feature extraction → rules/LLM/analytics → evidence-linked insight → human action → auditable result

AI services do not create a second data model for the same business object.

## Layer 4 — Digital construction

Optional capability packs:

- CAD
- BIM
- DWG takeoff
- point cloud
- clash
- 4D schedule
- 5D cost model
- CDE
- OCR/document search

They link back to the canonical Project/BOQ/Cost Code/Task records.

## Layer 5 — Field and mobile workflows

Field UX is built around:

Capture → Validate → Approve → Post

Examples:
- voice note → draft progress
- photo → evidence
- material usage → stock/cost movement
- attendance → labour record
- daily report → project evidence

## Layer 6 — IDEAIL Business Intelligence

Cross-module KPI views:

- planned vs actual cost
- committed vs spent
- earned value
- margin
- material variance
- schedule variance
- cashflow
- receivables
- subcontract exposure
- change exposure
- safety/quality trend

## Company Intelligence

Company Intelligence is not a separate ERP.

It is a read-only analytical layer over canonical project history.

Inputs:
- projects
- estimates
- actual costs
- material consumption
- schedule
- procurement
- quality
- change
- customer/payment data

Outputs:
- what changed?
- why?
- what evidence supports it?
- what action is suggested?
- what happened on similar historical projects?

Every generated conclusion should store:
- source record IDs
- computation/model version
- timestamp
- confidence/uncertainty where relevant
- user action

## Module boundaries

### Foundation modules
erp
project_execution
estimation
procurement
subcontract
workforce
equipment
commercial
reporting

### Capability modules
advanced_schedule
risk
change_intelligence
field_capture
documents
quality
hse
ai_estimation
semantic_cost_match
company_intelligence
bim
cad_takeoff
evm_5d

### Industry modules
resin_epoxy
decorative_concrete
waterproofing
industrial_flooring
technical_coatings

Industry modules consume generic estimation/project APIs and must not duplicate the ERP/project master data.

## Versioning rule

Do not call these modules V2/V3 products. They are capability packs in the same IDEAIL ERP.

A capability can be:
- enabled
- disabled
- configured

without creating a second product or database.

## Migration rule

For any port from an upstream project:
1. identify the business capability;
2. choose one canonical implementation;
3. port missing behaviour only;
4. map to ERPNext documents;
5. add tests around the merged behaviour;
6. delete or avoid the duplicate path.

## Security rule

AI and field integrations are never trusted to bypass permissions. Every action resolves permissions against the canonical user/company/project records before mutation.

## Design target

IDEAIL should feel simple to a small contractor but expose deeper construction controls to project managers, quantity surveyors, engineers, accountants and directors when their role requires them.

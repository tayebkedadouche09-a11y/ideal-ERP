# IDEAIL ERP Source Lineage

IDEAIL ERP is one active Frappe/ERPNext runtime.

## Canonical runtime

Ideal-tayeb / BuildSuite Core:
- ERPNext v16 construction execution
- project spine
- BOQ and cost codes
- estimation/rates
- procurement
- subcontract
- workforce
- equipment
- project finance
- reporting

## Selective feature sources

Ideal-tayeb1 contributes behaviour requirements:
- client progress billing / IPC
- retention release
- material planning

Ideal-tayeb2 contributes capability requirements:
- AI estimation
- semantic cost matching
- advanced planning
- EVM/5D
- risk/change intelligence
- voice/evidence
- documents/CDE
- CAD/BIM/takeoff

These sources are not embedded as parallel ERP runtimes.

## Duplicate-elimination rule

One domain = one canonical implementation.

ERPNext owns accounting, stock, parties and payment posting.
BuildSuite owns project execution, BOQ, construction cost coding and
construction operations.
IDEAIL-native capabilities attach to those models instead of replacing them.

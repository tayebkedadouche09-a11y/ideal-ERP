# IDEAIL ERP Source Lineage

The active runtime is one Frappe/ERPNext application.

## Canonical runtime source

Ideal-tayeb / BuildSuite Core
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

## Selective feature references

Ideal-tayeb1 / Construction Management Suite
- client progress billing / IPC
- retention release
- material planning
- compact regional construction workflows

These are ported as behaviour and workflow requirements, not as a second active ERP.

Ideal-tayeb2 / OpenConstructionERP
- AI-assisted estimation
- semantic cost matching
- advanced planning
- EVM / 5D controls
- risk/change intelligence
- voice/evidence capture
- document/CDE concepts
- CAD/BIM/takeoff concepts

These become additive IDEAIL capability packs. The OpenConstructionERP runtime is not embedded beside ERPNext.

## Duplicate-elimination rule

One domain = one canonical data model and implementation.

ERPNext owns:
- ledger
- accounting
- customers
- suppliers
- stock
- payments

BuildSuite owns:
- project execution
- BOQ
- work packages
- task/schedule execution
- construction cost coding
- subcontract operations

IDEAIL capability packs extend those models instead of replacing them.

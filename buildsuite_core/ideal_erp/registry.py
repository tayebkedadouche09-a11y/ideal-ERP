"""Single registry for the connected IDEAIL ERP capability graph."""

CANONICAL_DOMAINS = {
    "erp": "ERPNext",
    "project_execution": "BuildSuite Core",
    "boq": "BuildSuite Core",
    "cost_codes": "BuildSuite Core",
    "procurement": "ERPNext + BuildSuite Core",
    "subcontract": "BuildSuite Core",
    "workforce": "BuildSuite Core",
    "equipment": "BuildSuite Core",
    "accounting": "ERPNext",
    "stock": "ERPNext",
    "commercial_posting": "ERPNext",
    "documents": "Frappe File/Document",
    "project_finance": "ERPNext + BuildSuite Core",
}

CAPABILITIES = {
    "client_progress_billing": {"source": "Ideal-tayeb1", "mode": "native", "dependencies": ["project_execution", "boq", "commercial_posting"]},
    "retention_release": {"source": "Ideal-tayeb1", "mode": "native", "dependencies": ["client_progress_billing", "commercial_posting"]},
    "material_planning": {"source": "Ideal-tayeb1", "mode": "native", "dependencies": ["boq", "stock", "procurement"]},
    "ai_estimation": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["estimation", "semantic_cost_match", "resin_epoxy"]},
    "semantic_cost_match": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["cost_codes"]},
    "advanced_schedule": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution"]},
    "evm_5d": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "boq", "accounting"]},
    "risk": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["evm_5d", "advanced_schedule", "material_planning", "change_intelligence"]},
    "change_intelligence": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "boq", "commercial_posting"]},
    "voice_evidence": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "documents", "approvals"]},
    "documents_cde": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "documents", "approvals"]},
    "cad_bim_takeoff": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["boq", "cost_codes", "project_execution"]},
    "company_intelligence": {"source": "IDEAIL", "mode": "native", "dependencies": ["evm_5d", "advanced_schedule", "material_planning"]},
    "resin_epoxy": {"source": "IDEAIL", "mode": "native", "dependencies": ["estimation", "cost_codes"]},
    "resin_to_quotation": {"source": "IDEAIL", "mode": "native", "dependencies": ["resin_epoxy", "commercial_posting"]},
    "algeria_dzd": {"source": "IDEAIL", "mode": "native", "dependencies": ["accounting", "commercial_posting"]},
    "forecasting": {"source": "IDEAIL", "mode": "native", "dependencies": ["company_intelligence", "evm_5d"]},
    "anomaly_detection": {"source": "IDEAIL", "mode": "native", "dependencies": ["evm_5d", "material_planning"]},
    "lessons_learned": {"source": "IDEAIL", "mode": "native", "dependencies": ["company_intelligence", "documents_cde", "change_intelligence"]},
    "daily_diary": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "voice_evidence", "photos"]},
    "forms": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "documents_cde"]},
    "photos": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["project_execution", "documents"]},
    "approvals": {"source": "IDEAIL", "mode": "native", "dependencies": ["project_execution", "documents"]},
    "site_inventory": {"source": "Ideal-tayeb2", "mode": "native", "dependencies": ["material_planning", "stock"]},
    "project_360": {"source": "IDEAIL", "mode": "native", "dependencies": ["project_execution", "boq", "procurement", "project_finance", "accounting", "stock"]},
    "daily_briefing": {"source": "IDEAIL", "mode": "native", "dependencies": ["company_intelligence", "project_360", "approvals"]},
    "smart_priority_engine": {"source": "IDEAIL", "mode": "native", "dependencies": ["daily_briefing", "risk", "change_intelligence"]},
}


def get_registry() -> dict:
    return {
        "canonical_domains": dict(CANONICAL_DOMAINS),
        "capabilities": {
            name: {
                **meta,
                "dependencies": list(meta.get("dependencies", [])),
            }
            for name, meta in CAPABILITIES.items()
        },
        "integration_policy": {
            "single_project_master": True,
            "single_boq_master": True,
            "single_stock_ledger": True,
            "single_accounting_ledger": True,
            "single_commercial_posting": True,
            "shared_evidence_store": "Frappe File/Document",
            "drafts_require_confirmation": [
                "ai_estimation",
                "voice_evidence",
                "cad_bim_takeoff",
            ],
        },
    }


def validate_dependency_graph() -> list[str]:
    errors: list[str] = []
    names = set(CAPABILITIES) | set(CANONICAL_DOMAINS) | {"estimation"}
    for capability, meta in CAPABILITIES.items():
        for dependency in meta.get("dependencies", []):
            if dependency not in names:
                errors.append(
                    f"{capability} depends on unknown domain/capability {dependency}"
                )
    return errors

"""Single registry for the capabilities selected during the three-source merge."""

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
}

CAPABILITIES = {
    "client_progress_billing": {"source": "Ideal-tayeb1", "mode": "port"},
    "retention_release": {"source": "Ideal-tayeb1", "mode": "port"},
    "material_planning": {"source": "Ideal-tayeb1", "mode": "port"},
    "ai_estimation": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "semantic_cost_match": {"source": "Ideal-tayeb2", "mode": "native"},
    "advanced_schedule": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "evm_5d": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "risk": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "change_intelligence": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "voice_evidence": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "documents_cde": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "cad_bim_takeoff": {"source": "Ideal-tayeb2", "mode": "adapter"},
    "company_intelligence": {"source": "IDEAIL", "mode": "native"},
    "resin_epoxy": {"source": "IDEAIL", "mode": "native"},
    "algeria_dzd": {"source": "IDEAIL", "mode": "native"},
}


def get_registry() -> dict:
    """Return a copy suitable for dashboards/API responses."""
    return {
        "canonical_domains": dict(CANONICAL_DOMAINS),
        "capabilities": {name: dict(meta) for name, meta in CAPABILITIES.items()},
    }

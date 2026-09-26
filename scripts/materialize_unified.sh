#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BUILD_URL="https://github.com/tayebkedadouche09-a11y/Ideal-tayeb.git"
CMS_URL="https://github.com/tayebkedadouche09-a11y/Ideal-tayeb1.git"
OCE_URL="https://github.com/tayebkedadouche09-a11y/Ideal-tayeb2.git"

echo "==> Cloning source projects"
git clone --depth 1 --branch develop "$BUILD_URL" "$WORK/buildsuite"
git clone --depth 1 --branch master "$CMS_URL" "$WORK/cms_v15"
git clone --depth 1 --branch main "$OCE_URL" "$WORK/openconstruction"

echo "==> Materializing canonical BuildSuite source"
# BuildSuite is the only source copied into the active runtime because it is the
# chosen canonical ERPNext v16 construction engine. Other source systems are
# treated as selective feature references so duplicate runtimes are not retained.
rsync -a --delete   --exclude '.git/'   --exclude '.github/'   --exclude 'README.md'   --exclude 'docs/'   "$WORK/buildsuite/" "$ROOT/"

echo "==> Applying IDEAIL product identity"
python3 - <<'PY'
from pathlib import Path

p = Path("buildsuite_core/hooks.py")
s = p.read_text(encoding="utf-8")
s = s.replace('app_title = "BuildSuite Core"', 'app_title = "IDEAIL ERP"')
s = s.replace('app_publisher = "Infraholic Innovations Pvt. Ltd"', 'app_publisher = "IDEAIL"')
s = s.replace('app_email = "app@buildsuite.io"', 'app_email = "support@ideail-erp.local"')
s = s.replace('app_description = "A construction operating system built on Frappe"', 'app_description = "Unified construction and business ERP with AI-assisted project intelligence"')
p.write_text(s, encoding="utf-8")

p = Path("buildsuite_core/modules.txt")
if p.exists():
    p.write_text("IDEAIL ERP\n", encoding="utf-8")
PY

echo "==> Adding the non-duplicated source lineage and port decisions"
mkdir -p docs/source-lineage
cat > docs/source-lineage/IDEAIL_SOURCE_LINEAGE.md <<'EOF'
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
EOF

echo "==> Generating a single source inventory"
python3 - <<'PY'
import json
from pathlib import Path

payload = {
    "product": "IDEAIL ERP",
    "runtime": "Frappe/ERPNext v16",
    "canonical_source": "tayebkedadouche09-a11y/Ideal-tayeb@develop",
    "feature_sources": [
        {
            "source": "tayebkedadouche09-a11y/ideal-tayeb1@master",
            "ports": ["progress billing", "retention", "material planning"]
        },
        {
            "source": "tayebkedadouche09-a11y/Ideal-tayeb2@main",
            "ports": [
                "AI estimation", "semantic cost matching", "advanced scheduling",
                "EVM/5D", "risk", "change intelligence", "voice/evidence",
                "documents/CDE", "CAD/BIM/takeoff"
            ]
        }
    ],
    "rule": "No parallel ERP, project, BOQ, stock or accounting engines."
}
Path("config/ideal_erp_sources.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

echo "==> Unified materialization complete"

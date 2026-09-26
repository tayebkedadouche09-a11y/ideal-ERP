#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BUILD_URL="https://github.com/tayebkedadouche09-a11y/Ideal-tayeb.git"

echo "==> Cloning canonical construction source"
git clone --depth 1 --branch develop "$BUILD_URL" "$WORK/buildsuite"

echo "==> Materializing canonical BuildSuite source"
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude 'README.md' \
  --exclude 'docs/' \
  --exclude 'config/' \
  --exclude 'scripts/' \
  --exclude 'buildsuite_core/ideal_erp/' \
  --exclude 'buildsuite_core/api/ideal_erp.py' \
  --exclude 'frontend/src/data/project360Api.js' \
  --exclude 'frontend/src/views/project-detail/tabs/OverviewTab.vue' \
  --exclude 'frontend/src/views/PlaceholderView.vue' \
  --exclude 'frontend/src/views/BoqDetailView.vue' \
  --exclude 'frontend/src/utils/boqApi.js' \
  --exclude 'frontend/src/views/workspaces/EstimationWorkspace.vue' \
  --exclude 'frontend/src/views/workspaces/ReportStubView.vue' \
  --exclude 'frontend/src/views/ApprovalCenterView.vue' \
  --exclude 'frontend/src/data/approvalCenterApi.js' \
  --exclude 'frontend/src/data/companyIntelligenceApi.js' \
  --exclude 'frontend/src/views/VoiceToWorkView.vue' \
  --exclude 'frontend/src/views/AppHomeView.vue' \
  --exclude 'buildsuite_core/api/home.py' \
  --exclude 'vercel.json' \
  --exclude 'api/' \
  --exclude 'frontend/vite.config.js' \
  --exclude 'package.json' \
  "$WORK/buildsuite/" "$ROOT/"

echo "==> Applying IDEAIL product identity"
python3 - <<'PY'
from pathlib import Path

p = Path("buildsuite_core/hooks.py")
s = p.read_text(encoding="utf-8")
replacements = {
    'app_title = "BuildSuite Core"': 'app_title = "IDEAIL ERP"',
    'app_publisher = "Infraholic Innovations Pvt. Ltd"': 'app_publisher = "IDEAIL"',
    'app_email = "app@buildsuite.io"': 'app_email = "support@ideail-erp.local"',
    'app_description = "A construction operating system built on Frappe"':
        'app_description = "Unified construction and business ERP with AI-assisted project intelligence"',
}
for old, new in replacements.items():
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8")

modules = Path("buildsuite_core/modules.txt")
if modules.exists():
    modules.write_text("IDEAIL ERP\n", encoding="utf-8")
PY

echo "==> Recreating IDEAIL metadata directories"
mkdir -p config docs/source-lineage scripts

cat > docs/source-lineage/IDEAIL_SOURCE_LINEAGE.md <<'EOF'
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
EOF

cat > config/ideal_erp_sources.json <<'EOF'
{
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
        "AI estimation",
        "semantic cost matching",
        "advanced scheduling",
        "EVM/5D",
        "risk",
        "change intelligence",
        "voice/evidence",
        "documents/CDE",
        "CAD/BIM/takeoff"
      ]
    }
  ],
  "rule": "No parallel ERP, project, BOQ, stock or accounting engines."
}
EOF

echo "==> Unified IDEAIL materialization complete"

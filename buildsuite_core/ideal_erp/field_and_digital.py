"""Field evidence and digital construction normalization helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from buildsuite_core.ideal_erp.intelligence.semantic_cost_match import match_cost


VOICE_PATTERNS = {
    "fr": {
        "delay": ("retard", "en retard", "délai"),
        "purchase": ("acheter", "commande", "commander", "matériel"),
        "inspection": ("inspection", "contrôle", "vérifier"),
        "photo": ("photo", "preuve", "image"),
    },
    "en": {
        "delay": ("delay", "late", "schedule"),
        "purchase": ("buy", "purchase", "order", "material"),
        "inspection": ("inspect", "inspection", "check"),
        "photo": ("photo", "evidence", "image"),
    },
    "ar": {
        "delay": ("تأخر", "متأخر", "آجال"),
        "purchase": ("شراء", "اطلب", "طلب", "مواد"),
        "inspection": ("تفتيش", "فحص", "مراقبة"),
        "photo": ("صورة", "دليل", "تصوير"),
    },
}


@dataclass(frozen=True, slots=True)
class VoiceAction:
    project: str
    action_type: str
    text: str
    confidence: float
    requires_approval: bool = True


def parse_voice_capture(project: str, transcript: str, language: str = "auto") -> VoiceAction:
    text = " ".join(str(transcript).split())
    selected = language.lower()
    languages = [selected] if selected in VOICE_PATTERNS else ["fr", "en", "ar"]
    scores: dict[str, int] = {}
    for lang in languages:
        for action_type, keywords in VOICE_PATTERNS[lang].items():
            scores[action_type] = scores.get(action_type, 0) + sum(
                1 for keyword in keywords if keyword.lower() in text.lower()
            )

    action_type, hits = max(scores.items(), key=lambda pair: pair[1], default=("note", 0))
    confidence = min(0.99, 0.55 + 0.12 * hits) if hits else 0.35
    return VoiceAction(
        project=project,
        action_type=action_type,
        text=text,
        confidence=round(confidence, 2),
    )


def normalize_site_diary(
    *,
    project: str,
    entry_date: str,
    narrative: str,
    weather: str | None = None,
    workers: int = 0,
    photos: Iterable[str] = (),
    issues: Iterable[str] = (),
    measurements: Iterable[dict[str, Any]] = (),
    actions: Iterable[str] = (),
) -> dict[str, Any]:
    if workers < 0:
        raise ValueError("workers cannot be negative")
    return {
        "project": project,
        "entry_date": entry_date,
        "narrative": " ".join(str(narrative).split()),
        "weather": weather,
        "workers": workers,
        "photos": list(photos),
        "issues": list(issues),
        "measurements": [dict(x) for x in measurements],
        "actions": list(actions),
        "status": "Draft",
        "requires_approval": bool(issues or actions),
    }


def approval_gate(
    *,
    status: str,
    action: str,
    required_role: str,
    approved_by: str | None = None,
) -> dict[str, Any]:
    allowed = {"Draft", "Pending Approval", "Approved", "Rejected"}
    if status not in allowed:
        raise ValueError(f"Invalid approval status: {status}")
    action = action.strip().lower()
    if action == "submit":
        return {"status": "Pending Approval", "requires_approval": True, "required_role": required_role}
    if action == "approve":
        if not approved_by:
            raise ValueError("approved_by is required to approve")
        return {"status": "Approved", "requires_approval": False, "required_role": required_role, "approved_by": approved_by}
    if action == "reject":
        return {"status": "Rejected", "requires_approval": False, "required_role": required_role}
    if action == "revise":
        return {"status": "Draft", "requires_approval": False, "required_role": required_role}
    raise ValueError(f"Unsupported approval action: {action}")


def inventory_variance(planned_qty: float, actual_qty: float) -> dict[str, float]:
    planned = float(planned_qty)
    actual = float(actual_qty)
    delta = actual - planned
    percent = 0.0 if planned == 0 else delta / planned * 100.0
    return {
        "planned_qty": planned,
        "actual_qty": actual,
        "variance_qty": round(delta, 4),
        "variance_pct": round(percent, 4),
    }


def photo_evidence(
    *,
    project: str,
    file_ref: str,
    caption: str = "",
    captured_at: str | None = None,
    source: str = "mobile",
    task: str | None = None,
) -> dict[str, Any]:
    if not file_ref:
        raise ValueError("file_ref is required")
    return {
        "project": project,
        "file_ref": file_ref,
        "caption": caption.strip(),
        "captured_at": captured_at,
        "source": source,
        "task": task,
        "status": "Captured",
        "requires_review": True,
    }


def normalize_document(
    *,
    document_id: str,
    project: str,
    title: str,
    version: str = "1.0",
    status: str = "Draft",
    required: bool = False,
    approvals: Iterable[str] = (),
) -> dict[str, Any]:
    allowed = {"Draft", "In Review", "Approved", "Rejected", "Superseded"}
    if status not in allowed:
        raise ValueError(f"Invalid document status: {status}")
    approval_list = list(approvals)
    return {
        "document_id": document_id,
        "project": project,
        "title": title,
        "version": version,
        "status": status,
        "required": required,
        "approvals": approval_list,
        "ready_for_use": status == "Approved" and (not required or bool(approval_list)),
    }


def normalize_takeoff(
    rows: Iterable[dict[str, Any]],
    cost_catalog: Iterable[dict[str, Any]],
    source_type: str = "takeoff",
) -> list[dict[str, Any]]:
    catalog = list(cost_catalog)
    normalized: list[dict[str, Any]] = []
    for row in rows:
        description = str(row.get("description") or row.get("name") or "")
        matches = match_cost(description, catalog, 1)
        best = matches[0] if matches else None
        normalized.append(
            {
                "description": description,
                "quantity": float(row.get("quantity", row.get("qty", 0))),
                "uom": row.get("uom"),
                "item_code": best.item_code if best else None,
                "match_score": best.score if best else 0.0,
                "source": source_type,
                "needs_review": best is None or best.score < 0.4,
            }
        )
    return normalized


def normalize_cad_bim_takeoff(
    *,
    project: str,
    source: str,
    rows: Iterable[dict[str, Any]],
    cost_catalog: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    items = normalize_takeoff(rows, cost_catalog, source_type=source)
    return {
        "project": project,
        "source": source,
        "items": items,
        "ready_for_boq_review": all(not item["needs_review"] for item in items),
        "requires_human_confirmation": True,
    }


def detect_field_forms(text: str) -> dict[str, bool]:
    lowered = text.lower()
    return {
        "has_photo_reference": bool(re.search(r"(photo|image|صورة)", lowered)),
        "has_measurement": bool(re.search(r"(\d+(?:[.,]\d+)?)\s*(m2|m²|m|mm|cm|م2|م²|سم|مم)", lowered)),
        "has_issue": any(word in lowered for word in ("retard", "delay", "problème", "problem", "تأخر", "مشكل")),
    }

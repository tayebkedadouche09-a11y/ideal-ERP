"""Algeria/FR/AR/EN localization helpers.

The ERP remains configurable: tax rates and posting accounts are never
hard-coded into the accounting engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Localization:
    language: str = "fr"
    currency: str = "DZD"
    rtl: bool = False
    decimals: int = 2


def resolve_localization(language: str = "fr", currency: str = "DZD") -> Localization:
    language = (language or "fr").lower()
    if language not in {"fr", "ar", "en"}:
        language = "fr"
    return Localization(
        language=language,
        currency=currency or "DZD",
        rtl=language == "ar",
    )


def format_amount(value: float, localization: Localization | None = None) -> str:
    loc = localization or Localization()
    number = f"{float(value):,.{loc.decimals}f}"
    if loc.language == "fr":
        number = number.replace(",", " ").replace(".", ",")
    return f"{number} {loc.currency}"


def commercial_total(
    *,
    net_amount: float,
    tax_rate_percent: float = 0.0,
    discount_percent: float = 0.0,
) -> dict[str, float]:
    """Commercial calculation; posting/tax templates remain ERPNext-owned."""
    discounted = net_amount * (1 - discount_percent / 100.0)
    tax = discounted * tax_rate_percent / 100.0
    return {
        "net": round(discounted, 2),
        "tax": round(tax, 2),
        "gross": round(discounted + tax, 2),
    }

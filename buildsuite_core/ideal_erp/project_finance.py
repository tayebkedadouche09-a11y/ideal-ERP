"""Pure project-finance helpers used by the live ERPNext snapshot."""

from __future__ import annotations

from typing import Any


def calculate_project_finance(
    *,
    contract_value: float,
    invoiced_net: float,
    outstanding_gross: float,
    actual_cost: float,
    open_commitment: float = 0.0,
) -> dict[str, Any]:
    contract = max(0.0, float(contract_value))
    invoiced = max(0.0, float(invoiced_net))
    outstanding = max(0.0, float(outstanding_gross))
    cost = max(0.0, float(actual_cost))
    commitment = max(0.0, float(open_commitment))

    earned = min(contract, invoiced) if contract else invoiced
    unbilled = max(0.0, contract - invoiced)
    gross_profit = invoiced - cost
    margin_pct = gross_profit / invoiced * 100.0 if invoiced else 0.0
    projected_cost_position = cost + commitment
    projected_profit_position = invoiced - projected_cost_position

    return {
        "earned_commercial_value": round(earned, 2),
        "unbilled_contract_value": round(unbilled, 2),
        "invoiced_net": round(invoiced, 2),
        "outstanding": round(outstanding, 2),
        "estimated_cash_collected": round(max(0.0, invoiced - outstanding), 2),
        "actual_cost": round(cost, 2),
        "gross_profit_on_invoiced": round(gross_profit, 2),
        "margin_percent_on_invoiced": round(margin_pct, 4),
        "open_commitment": round(commitment, 2),
        "projected_cost_position": round(projected_cost_position, 2),
        "projected_profit_position": round(projected_profit_position, 2),
    }

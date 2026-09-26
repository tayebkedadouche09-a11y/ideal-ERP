from buildsuite_core.ideal_erp.project_finance import calculate_project_finance


def test_project_finance_reconciles_contract_invoice_cash_cost_and_commitment():
    result = calculate_project_finance(
        contract_value=1_000_000,
        invoiced_net=600_000,
        outstanding_gross=150_000,
        actual_cost=420_000,
        open_commitment=100_000,
        invoiced_gross=720_000,
    )
    assert result["earned_commercial_value"] == 600_000
    assert result["unbilled_contract_value"] == 400_000
    assert result["estimated_cash_collected"] == 570_000
    assert result["actual_cost"] == 420_000
    assert result["gross_profit_on_invoiced"] == 180_000
    assert result["margin_percent_on_invoiced"] == 30
    assert result["projected_cost_position"] == 520_000
    assert result["projected_profit_position"] == 80_000

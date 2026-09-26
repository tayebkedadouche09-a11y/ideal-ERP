from buildsuite_core.ideal_erp.briefing import build_daily_briefing, prioritize_actions


def test_priority_orders_danger_before_info():
    alerts = [
        {"key": "info", "title": "Info", "tone": "info", "value": 99},
        {"key": "danger", "title": "Danger", "tone": "danger", "value": 1},
    ]
    ranked = prioritize_actions(alerts)
    assert ranked[0]["key"] == "danger"
    assert ranked[0]["priority_rank"] == 1


def test_daily_briefing_reuses_existing_signals():
    result = build_daily_briefing(
        role="pm",
        greeting_sub="Attention",
        alerts=[{"key": "x", "title": "Overdue", "tone": "danger", "value": 2}],
        cta={"title": "Dashboard", "to": "/project-dashboard"},
        active_projects=4,
        at_risk_projects=1,
    )
    assert result["priority"][0]["key"] == "x"
    assert result["primary_action"]["to"] == "/project-dashboard"
    assert any("risk" in line for line in result["summary"])

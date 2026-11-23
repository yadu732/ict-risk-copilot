from datetime import date

from ict_risk_copilot.analytics import risk_metrics


def test_metrics_are_computed_from_tickets(tickets):
    m = risk_metrics(tickets, date(2026, 11, 23))
    assert m["total_tickets"] == 12
    assert m["active_tickets"] == 9
    assert m["overdue_active_tickets"] == 4
    assert m["overdue_ticket_ids"] == ["ICT-001", "ICT-002", "ICT-006", "ICT-007"]
    assert sum(m["by_severity"].values()) == 12


def test_overdue_is_date_dependent(tickets):
    m = risk_metrics(tickets, date(2026, 11, 1))
    assert m["overdue_active_tickets"] == 0

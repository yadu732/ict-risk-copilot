"""Calculated metrics, never delegated to a language model."""

from __future__ import annotations

from collections import Counter
from datetime import date

from .models import RiskTicket, TicketStatus


ACTIVE = {TicketStatus.open, TicketStatus.in_progress}


def risk_metrics(tickets: list[RiskTicket], as_of: date) -> dict:
    if not tickets:
        raise ValueError("At least one ticket is required")
    active = [t for t in tickets if t.status in ACTIVE]
    overdue = [t for t in active if t.due_date < as_of]
    return {
        "total_tickets": len(tickets),
        "active_tickets": len(active),
        "overdue_active_tickets": len(overdue),
        "overdue_ticket_ids": sorted(t.ticket_id for t in overdue),
        "by_severity": {s: sum(t.severity.value == s for t in tickets) for s in
                        ("Critical", "High", "Medium", "Low")},
        "by_status": dict(sorted(Counter(t.status.value for t in tickets).items())),
        "as_of": as_of.isoformat(),
    }

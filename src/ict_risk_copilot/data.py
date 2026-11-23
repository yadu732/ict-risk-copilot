"""Safe loading and deterministic filtering of synthetic risk tickets."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import RiskTicket


class InputDataError(ValueError):
    """Raised for invalid ticket collections."""


def load_tickets(path: str | Path) -> list[RiskTicket]:
    file = Path(path)
    try:
        if file.stat().st_size > 2_000_000:
            raise InputDataError("Input file exceeds 2 MB limit")
        payload = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputDataError(f"Cannot load ticket JSON: {exc}") from exc
    return parse_tickets(payload)


def parse_tickets(payload: object) -> list[RiskTicket]:
    if not isinstance(payload, list) or not 1 <= len(payload) <= 100:
        raise InputDataError("Expected a JSON list containing 1-100 tickets")
    try:
        tickets = [RiskTicket.model_validate(item) for item in payload]
    except ValidationError as exc:
        raise InputDataError(str(exc)) from exc
    ids = [ticket.ticket_id for ticket in tickets]
    if len(set(ids)) != len(ids):
        raise InputDataError("Duplicate ticket IDs are not allowed")
    return tickets

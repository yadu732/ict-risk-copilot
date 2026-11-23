import pytest

from ict_risk_copilot.data import InputDataError, parse_tickets


def test_sample_is_valid(tickets):
    assert len(tickets) == 12
    assert len({t.ticket_id for t in tickets}) == 12


def test_reject_duplicate_ids(tickets):
    rows = [tickets[0].model_dump(mode="json")] * 2
    with pytest.raises(InputDataError, match="Duplicate"):
        parse_tickets(rows)


def test_reject_unknown_fields(tickets):
    row = tickets[0].model_dump(mode="json")
    row["secret_key"] = "should_not_be_included"
    with pytest.raises(InputDataError):
        parse_tickets([row])


def test_reject_empty_input():
    with pytest.raises(InputDataError):
        parse_tickets([])


def test_reject_oversized_input(tickets):
    with pytest.raises(InputDataError):
        parse_tickets([tickets[0].model_dump(mode="json")] * 101)

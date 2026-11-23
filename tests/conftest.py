from pathlib import Path

import pytest

from ict_risk_copilot.data import load_tickets


@pytest.fixture
def tickets():
    return load_tickets(Path(__file__).parents[1] / "data" / "synthetic_tickets.json")

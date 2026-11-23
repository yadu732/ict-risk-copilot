import json
from datetime import date

import pytest
import requests

from ict_risk_copilot.engine import DraftError, create_draft
from ict_risk_copilot.models import TicketSummary
from ict_risk_copilot.ollama_client import OllamaError, generate_structured, local_url
from ict_risk_copilot.review import record_review


@pytest.mark.parametrize(
    "url",
    ["https://api.example.com:11434", "http://8.8.8.8:11434", "file:///etc/passwd",
     "http://localhost:11434/path", "http://localhost:11434?token=a",
     "http://user:pass@localhost:11434", "http://localhost"],
)
def test_ollama_refuses_remote_and_invalid_urls(url):
    with pytest.raises(OllamaError):
        local_url(url)


def test_ollama_accepts_localhost_only():
    assert local_url("http://localhost:11434") == "http://localhost:11434"
    assert local_url("http://127.0.0.1:11434") == "http://127.0.0.1:11434"


def test_ollama_client_requests_structured_output(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": json.dumps({
                "executive_summary": "A reviewable synthetic summary with sufficient detail.",
                "key_risks": ["Source risk"],
                "recommended_followups": ["Verify before acting"],
                "evidence_ticket_ids": ["ICT-001"],
            })}}

    def fake_post(url, *, json, timeout):
        assert url == "http://127.0.0.1:11434/api/chat"
        assert "properties" in json["format"]
        assert json["stream"] is False
        assert timeout == 120
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    result = generate_structured(
        model="llama3.2", system_prompt="Rules", user_prompt="Data",
        schema=TicketSummary,
    )
    assert result["evidence_ticket_ids"] == ["ICT-001"]


def test_ollama_invalid_json_fails_closed(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "not-json"}}

    monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse())
    with pytest.raises(OllamaError):
        generate_structured(
            model="llama3.2", system_prompt="x", user_prompt="y", schema=TicketSummary
        )


def test_llm_output_with_unknown_reference_rejected(tickets, monkeypatch):
    from ict_risk_copilot import engine

    def fake_generate(**kwargs):
        return {
            "executive_summary": "A synthetic risk summary referencing fictitious ICT-999.",
            "key_risks": ["Reported risk"],
            "recommended_followups": ["Verify the claim"],
            "evidence_ticket_ids": ["ICT-999"],
        }

    monkeypatch.setattr(engine, "generate_structured", fake_generate)
    with pytest.raises(DraftError):
        create_draft(tickets=tickets, task="summary", as_of=date(2026, 11, 23), mode="ollama")


def test_approval_requires_reviewer_and_notes():
    with pytest.raises(ValueError):
        record_review(state="approved", reviewer="", notes="ok")
    with pytest.raises(ValueError):
        record_review(state="approved", reviewer="AB", notes="")
    record = record_review(
        state="approved", reviewer="AB", notes="Verified against source"
    )
    assert record.state == "approved"

"""Typed risk data and LLM draft contracts."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"


class TicketStatus(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    mitigated = "Mitigated"
    closed = "Closed"


class RiskTicket(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    ticket_id: str = Field(min_length=3, max_length=40, pattern=r"^[A-Z0-9-]+$")
    title: str = Field(min_length=5, max_length=160)
    category: str = Field(min_length=3, max_length=60)
    severity: Severity
    status: TicketStatus
    asset: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=8, max_length=1800)
    business_impact: str = Field(min_length=8, max_length=1200)
    mitigation: str = Field(min_length=8, max_length=1200)
    risk_owner: str = Field(min_length=3, max_length=100)
    due_date: date
    last_updated: date
    control_reference: str = Field(min_length=2, max_length=80)

    @field_validator("title", "description", "business_impact", "mitigation", mode="after")
    @classmethod
    def reject_control_chars(cls, value: str) -> str:
        if any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise ValueError("Control characters are not allowed")
        return value


class TicketSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    executive_summary: str = Field(min_length=12, max_length=2500)
    key_risks: list[str] = Field(min_length=1, max_length=8)
    recommended_followups: list[str] = Field(min_length=1, max_length=8)
    evidence_ticket_ids: list[str] = Field(min_length=1)


class StatusReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    headline: str = Field(min_length=8, max_length=160)
    management_summary: str = Field(min_length=12, max_length=2500)
    priorities: list[str] = Field(min_length=1, max_length=8)
    blockers: list[str] = Field(default_factory=list, max_length=8)
    evidence_ticket_ids: list[str] = Field(min_length=1)


class KnowledgeArticle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=8, max_length=180)
    objective: str = Field(min_length=12, max_length=1000)
    steps: list[str] = Field(min_length=2, max_length=10)
    escalation_and_review: str = Field(min_length=12, max_length=1200)
    evidence_ticket_ids: list[str] = Field(min_length=1)


TaskName = Literal["summary", "report", "knowledge_base"]
DraftSchema = TicketSummary | StatusReport | KnowledgeArticle

SCHEMAS: dict[str, type[BaseModel]] = {
    "summary": TicketSummary,
    "report": StatusReport,
    "knowledge_base": KnowledgeArticle,
}

"""Explicit review gate, separate from model generation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ReviewRecord(BaseModel):
    state: Literal["approved", "rejected"]
    reviewer: str = Field(min_length=2, max_length=100)
    notes: str = Field(min_length=3, max_length=1000)
    reviewed_at_utc: datetime


def record_review(*, state: str, reviewer: str, notes: str) -> ReviewRecord:
    """Called only by a deliberate user action, never by an LLM."""
    return ReviewRecord(
        state=state,
        reviewer=reviewer.strip(),
        notes=notes.strip(),
        reviewed_at_utc=datetime.now(timezone.utc),
    )

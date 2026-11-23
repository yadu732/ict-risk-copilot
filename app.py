"""Streamlit UI for local, human-reviewed ICT risk copilot demonstrations."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from pydantic import ValidationError
import streamlit as st

from ict_risk_copilot.analytics import risk_metrics
from ict_risk_copilot.data import InputDataError, load_tickets, parse_tickets
from ict_risk_copilot.engine import DraftError, create_draft
from ict_risk_copilot.review import record_review

st.set_page_config(page_title="ICT Risk Copilot", page_icon="🛡️", layout="wide")

DATA_FILE = Path(__file__).parent / "data" / "synthetic_tickets.json"


@st.cache_data
def sample_tickets() -> list[dict]:
    return [t.model_dump(mode="json") for t in load_tickets(DATA_FILE)]


st.title("ICT Risk Copilot")
st.caption("Local LLM · Synthetic data · Human-reviewed output · Portfolio demonstration")
st.info(
    "This is a learning project, not a deployed security tool. No real company "
    "tickets, personal data, credentials, or confidential information should be entered. "
    "Generated text may be incorrect and requires explicit human review."
)

with st.sidebar:
    st.header("Generation settings")
    mode = st.radio(
        "Engine", ["Offline demo (no LLM)", "Local Ollama LLM"], index=0,
        help="Offline demo produces deterministic templates. Local Ollama actually runs an LLM.",
    )
    model = st.text_input("Ollama model", value="llama3.2") if mode.startswith("Local") else ""
    server = (
        st.text_input("Local Ollama URL", value="http://127.0.0.1:11434")
        if mode.startswith("Local") else "http://127.0.0.1:11434"
    )
    as_of = st.date_input("Reporting date", value=date(2026, 11, 23))
    st.caption("Model inference stays on the configured localhost Ollama server.")

st.subheader("Synthetic ICT risk ticket dataset")
source = st.radio(
    "Dataset", ["Included synthetic tickets", "Upload synthetic JSON"], horizontal=True
)
try:
    if source == "Upload synthetic JSON":
        upload = st.file_uploader(
            "JSON list of up to 100 synthetic tickets (2 MB max)", type="json"
        )
        if upload is None:
            st.info("Upload a synthetic JSON file or switch to the included example dataset.")
            st.stop()
        if upload.size > 2_000_000:
            st.error("File exceeds 2 MB limit.")
            st.stop()
        tickets = parse_tickets(json.loads(upload.getvalue().decode("utf-8")))
    else:
        tickets = parse_tickets(sample_tickets())
except (InputDataError, ValueError, UnicodeError) as exc:
    st.error(f"Invalid ticket data: {exc}")
    st.stop()

all_ids = [t.ticket_id for t in tickets]
selected_ids = st.multiselect(
    "Tickets to analyze (1-20 per generation)", all_ids, default=all_ids[:12]
)
selected = [t for t in tickets if t.ticket_id in selected_ids]
if not 1 <= len(selected) <= 20:
    st.warning("Select between 1 and 20 tickets to continue.")
    st.stop()

metrics = risk_metrics(selected, as_of)
a, b, c, d = st.columns(4)
a.metric("Selected tickets", metrics["total_tickets"])
b.metric("Active", metrics["active_tickets"])
c.metric("Overdue active", metrics["overdue_active_tickets"])
d.metric("High + Critical", metrics["by_severity"]["High"] + metrics["by_severity"]["Critical"])
with st.expander("View source tickets and deterministic risk metrics", expanded=False):
    st.dataframe(
        [
            {
                "ID": t.ticket_id,
                "Title": t.title,
                "Severity": t.severity.value,
                "Status": t.status.value,
                "Owner": t.risk_owner,
                "Due": str(t.due_date),
            }
            for t in selected
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.json(metrics)

st.subheader("Generate a reviewable draft")
task_labels = {
    "Ticket summary": "summary",
    "Management status report": "report",
    "Knowledge-base article": "knowledge_base",
}
label = st.selectbox("Output", list(task_labels))
task = task_labels[label]
configuration = {
    "ids": sorted(selected_ids), "source": [t.model_dump(mode="json") for t in selected],
    "date": str(as_of), "task": task, "mode": mode, "model": model, "server": server,
}
fingerprint = hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()

if st.button("Generate draft", type="primary"):
    try:
        with st.spinner("Generating and validating draft..."):
            draft, _ = create_draft(
                tickets=selected,
                task=task,
                as_of=as_of,
                mode="ollama" if mode.startswith("Local") else "demo",
                model=model or "llama3.2",
                ollama_url=server,
            )
        st.session_state["result"] = draft.model_dump(mode="json")
        st.session_state["review_fingerprint"] = fingerprint
        st.session_state["draft_text"] = json.dumps(st.session_state["result"], indent=2)
        st.session_state["draft_editor"] = st.session_state["draft_text"]
        st.session_state["review_record"] = None
        st.session_state["approved_text"] = None
        st.success("Draft generated. It is PENDING HUMAN REVIEW.")
    except DraftError as exc:
        st.error(str(exc))

if "result" in st.session_state:
    if st.session_state.get("review_fingerprint") != fingerprint:
        st.warning(
            "Settings or source tickets changed. Generate a new draft "
            "before reviewing or exporting."
        )
        st.stop()
    if mode.startswith("Offline"):
        st.warning(
            "Deterministic preview: This result was NOT generated by an LLM. "
            "Select Local Ollama LLM to use a model."
        )
    else:
        st.caption(f"Local model: {model} · Draft pending review")

    edited_text = st.text_area(
        "Review and edit the structured draft (JSON)",
        height=350,
        key="draft_editor",
    )
    if st.session_state.get("approved_text") != edited_text:
        st.session_state["review_record"] = None
    st.divider()
    st.markdown("**Human review checkpoint**")
    reviewer = st.text_input("Reviewer name or initials", key="reviewer")
    notes = st.text_input("Review notes (required)", key="review_notes")
    left, right = st.columns(2)
    with left:
        if st.button("Approve reviewed draft"):
            try:
                parsed = json.loads(edited_text)
                if not isinstance(parsed, dict):
                    raise ValueError("Draft must be a JSON object")
                record = record_review(state="approved", reviewer=reviewer, notes=notes)
                st.session_state["review_record"] = record.model_dump(mode="json")
                st.session_state["approved_text"] = edited_text
                st.success("Explicit reviewer approval recorded for this draft.")
            except (ValueError, ValidationError) as exc:
                st.error(f"Review not recorded: {exc}")
    with right:
        if st.button("Reject draft"):
            try:
                record = record_review(state="rejected", reviewer=reviewer, notes=notes)
                st.session_state["review_record"] = record.model_dump(mode="json")
                st.session_state["approved_text"] = None
                st.warning("Draft rejected. No approved export is available.")
            except ValidationError as exc:
                st.error(f"Review not recorded: {exc}")

    review = st.session_state.get("review_record")
    if (
        review
        and review.get("state") == "approved"
        and st.session_state.get("approved_text") == edited_text
    ):
        approved_payload = {
            "disclaimer": (
                "Synthetic demonstration. Human-reviewed draft, not an official risk decision."
            ),
            "task": task,
            "engine": "local_ollama" if mode.startswith("Local") else "deterministic_demo_not_llm",
            "as_of": str(as_of),
            "review": review,
            "metrics": metrics,
            "approved_draft": json.loads(edited_text),
        }
        st.download_button(
            "Download approved JSON",
            data=json.dumps(approved_payload, indent=2),
            file_name=f"approved_{task}.json",
            mime="application/json",
        )
    else:
        st.caption("Exports are available only after explicit human approval.")

st.divider()
st.caption("No live Jira connection, no automated remediation, and no production risk scoring.")

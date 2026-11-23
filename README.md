# ICT Risk Copilot 🛡️

**Local LLM assistant for synthetic ICT risk tickets, management reporting, and draft knowledge-base procedures.**

This portfolio project is designed to illustrate capabilities relevant to ICT risk awareness, innovation, reporting, automation and operational support. The app uses **Python, Streamlit, Pydantic and a locally hosted Ollama model**. It can also run in a clearly labeled **deterministic offline demo mode** without an LLM.

> **Important:** All included records are fictional. This is NOT a production security tool, an autonomous risk decision-maker, a real Jira integration, or evidence of compliance. Outputs require human review. Do not input real enterprise risk tickets, company data, passwords or personal data.

## Features

- **Risk ticket summary:** Generates a structured executive summary with key risks, evidence ticket IDs and proposed follow-up questions.
- **Management status report:** Summarizes unresolved and overdue issues, with deterministic Python metrics rather than LLM-calculated counts.
- **Knowledge-base draft:** Produces a procedure outline for ticket triage, remediation follow-up and escalation, explicitly requiring validation against approved organizational processes.
- **Human review gate:** Reviewers must manually inspect or edit outputs, enter reviewer identification and review notes, and click Approve before any approved JSON can be downloaded.
- **Local LLM:** Uses Ollama's `/api/chat` endpoint with a Pydantic JSON schema in `format`. No paid API required.
- **Reproducible offline demo:** Every feature can be explored before installing an LLM. This mode is NOT an LLM and is clearly labeled in the interface.
- **Risk data validation:** 12 realistic-looking but completely fictitious ICT risk tickets, input size limits, Pydantic validation, duplicate ID checks and referenced-ticket verification.
- **Tests and CI:** pytest, Ruff and GitHub Actions.

## Stack

Python 3.10+, Streamlit, Pydantic v2, requests, pytest, Ollama (optional for real LLM generation), `llama3.2` model (example).


Open the local URL displayed by Streamlit (typically `http://localhost:8501`). Choose **Offline demo (no LLM)** first. It runs without Ollama or a model download.


### Enable the real local LLM

1. Install Ollama from [ollama.com/download](https://ollama.com/download).
2. Start Ollama. In another PowerShell terminal, run:

```powershell
ollama pull llama3.2
ollama list
```

3. Keep Ollama running. In the Streamlit sidebar switch to **Local Ollama LLM**.
4. Model: `llama3.2`; URL: `http://127.0.0.1:11434`.
5. Select tickets, choose an output type, click **Generate draft**, inspect the JSON, and approve only after checking its statements.

The model download requires an internet connection once. Local inference can be slow on older machines. Ollama runs models locally; no API key is used. If local inference is impractical, the deterministic offline demo still demonstrates the reporting pipeline, but **must not be described as LLM inference**.

Generate a summary without an LLM:

```powershell
python -m ict_risk_copilot.cli --task summary --mode demo --as-of 2026-11-23 --out outputs/summary_draft.json
```

Generate a management report with a local LLM (Ollama must be running):

```powershell
python -m ict_risk_copilot.cli --task report --mode ollama --model llama3.2 --as-of 2026-11-23 --out outputs/report_draft.json
```

Generate a knowledge-base draft with the local model:

```powershell
python -m ict_risk_copilot.cli --task knowledge_base --mode ollama --model llama3.2 --as-of 2026-11-23 --out outputs/kb_draft.json
```

CLI output is **always marked `pending_human_review`**. Only the Streamlit UI has an explicit reviewed export flow.

## Tests

```powershell
python -m pytest -q
ruff check src tests app.py
```

## Example data and reproducible metrics

The 12 synthetic tickets include privileged access without MFA, overdue access reviews, logging gaps, patch delays, incomplete service-account inventory, backup evidence gaps, an expired exception, and AI governance inventory questions.

With the fixed reporting date **2026-11-23**, the sample should return:

| Metric | Value |
| --- | ---: |
| Total tickets | 12 |
| Active | 9 |
| Overdue active | 4 |
| Overdue ticket IDs | ICT-001, ICT-002, ICT-006, ICT-007 |

The above values are calculated by code, not invented by the model. An issue is overdue only when its status is Open or In Progress and its due date precedes the reporting date.

## File structure

```text
ict-risk-copilot/
├── app.py                           # Streamlit UI and human review gate
├── data/synthetic_tickets.json      # Fictional dataset only
├── src/ict_risk_copilot/
│   ├── analytics.py                 # Deterministic KPI/KRI metrics
│   ├── data.py                      # Validation and loading
│   ├── engine.py                    # Prompts, generation and evidence checks
│   ├── models.py                    # Pydantic ticket/output contracts
│   ├── ollama_client.py             # Restricted local model client
│   ├── review.py                    # Explicit review record
│   └── cli.py                       # Command-line entry point
├── tests/                           # Unit and mocked local-LLM tests
├── docs/architecture.md            # Data flow, trust boundaries and limitations
├── .github/workflows/ci.yml        # Continuous integration
├── pyproject.toml
├── .gitignore
└── LICENSE
```

## Architecture

```text
Synthetic tickets -> validated data -> deterministic risk metrics ---+
                                                                   +--> contextual prompt -> local Ollama -> structured JSON
                                               Offline demo --------+                        |
                                                                                 evidence-ID validation
                                                                                          |
                                                                                human edits & approval
                                                                                          |
                                                                                  approved JSON export
```

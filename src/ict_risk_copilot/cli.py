"""CLI for repeatable demo and local model generation."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .data import load_tickets
from .engine import create_draft


def main() -> None:
    parser = argparse.ArgumentParser(description="Create review-pending ICT risk drafts")
    parser.add_argument("--tickets", default="data/synthetic_tickets.json")
    parser.add_argument(
        "--task", choices=["summary", "report", "knowledge_base"], default="summary"
    )
    parser.add_argument("--mode", choices=["demo", "ollama"], default="demo")
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--out", help="Optional output JSON file (always pending review)")
    args = parser.parse_args()
    tickets = load_tickets(args.tickets)
    draft, metrics = create_draft(
        tickets=tickets[:20], task=args.task, as_of=args.as_of,
        mode=args.mode, model=args.model, ollama_url=args.ollama_url,
    )
    output = {
        "task": args.task,
        "generation_mode": args.mode,
        "review_status": "pending_human_review",
        "metrics": metrics,
        "draft": draft.model_dump(mode="json"),
    }
    content = json.dumps(output, indent=2, ensure_ascii=False)
    if args.out:
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content + "\n", encoding="utf-8")
        print(f"Draft saved: {dest} (PENDING HUMAN REVIEW)")
    else:
        print(content)


if __name__ == "__main__":
    main()

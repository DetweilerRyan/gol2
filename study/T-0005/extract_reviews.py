"""Save the final answer of each answer-key review as reviews/<name>.txt next to this script.

Usage: python3 extract_reviews.py [OUTPUT_DIR]  (default: the reviews/ folder beside this file)
The transcripts live on the sandbox that ran session 440265dc and expire around 2026-10-25.
"""
import json
import pathlib
import sys

SUB = pathlib.Path(
    "/home/agent/.claude/projects/-c-Users-User-Documents-projects-gol2--claude-worktrees-board-rumdl-task/"
    "440265dc-29df-4a06-99dc-0fa759d9950d/subagents"
)
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "reviews"
OUT.mkdir(parents=True, exist_ok=True)
REVIEWS = {
    "T-0001-at-648d64a": "agent-ac328c90f7d3ffee9",
    "T-0004-at-f5f6bff": "agent-a13299bd72cc9497d",
    "set-T-0001-T-0004-at-c44ca0f": "agent-a8e33acdcc1015860",
}
for name, agent in REVIEWS.items():
    last = ""
    for line in (SUB / f"{agent}.jsonl").read_text().splitlines():
        msg = json.loads(line).get("message") or {}
        content = msg.get("content")
        if msg.get("role") == "assistant" and isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            if any(t.strip() for t in texts):
                last = "\n".join(texts)
    (OUT / f"{name}.txt").write_text(last)
    print(name, len(last.splitlines()), "lines")

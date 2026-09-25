"""Save the final answer of each answer-key review to tmp/keys/<name>.md."""
import json
import pathlib

SUB = pathlib.Path(
    "/home/agent/.claude/projects/-c-Users-User-Documents-projects-gol2--claude-worktrees-board-rumdl-task/"
    "440265dc-29df-4a06-99dc-0fa759d9950d/subagents"
)
OUT = pathlib.Path("/home/agent/.claude/jobs/440265dc/tmp/keys")
OUT.mkdir(exist_ok=True)
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
    (OUT / f"{name}.md").write_text(last)
    print(name, len(last.splitlines()), "lines")

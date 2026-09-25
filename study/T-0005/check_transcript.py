"""Backstop check over run transcripts: flag commands that reach, or try to reach, other refs or remotes, reads
outside the run's environment, and network fetches.

Usage: python3 check_transcript.py RUN_OUT_DIR...   (exits 1 if anything is flagged)

The sandbox holds only the snapshot branch and no remote, so a flagged git command can't have reached anything;
it's listed so a person can confirm that. "Outside the run's environment" means an absolute path in a tool input
that isn't under /study, /tmp, /dev/null, or a system directory holding no study content (/usr, /etc, /proc, /opt).
"""
import json
import os
import re
import sys

GIT_REACH = re.compile(
    r"\bgit\b[^|;&]*?(\s--all\b|\s--remotes?\b|\s--branches\b|\s--tags\b|\s--glob\b|\brefs/(remotes|tags)/|"
    r"\borigin\b|\bupstream\b|\s(fetch|pull|clone|push|remote|ls-remote|worktree|stash)\b)"
)
NETWORK = re.compile(r"\b(curl|wget|nc|ssh|scp|rsync)\b|https?://", re.I)
ALLOWED = ("/study", "/tmp", "/dev/null", "/usr", "/etc", "/proc", "/opt/study-tools", "/opt/study-run", "/opt/claude", "/bin")
ABS_PATH = re.compile(r"(?<![\w.~-])(/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._@-]*)*)")

flags = 0
for out in sys.argv[1:]:
    n_calls = 0
    for line in open(os.path.join(out, "transcript.jsonl"), encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant":
            continue
        for c in (d.get("message") or {}).get("content") or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            n_calls += 1
            inp = c.get("input") or {}
            text = inp.get("command") or ""
            paths = [v for k, v in inp.items() if k in ("file_path", "filePath", "path", "notebook_path") and isinstance(v, str)]
            problems = []
            if c["name"] == "Bash":
                if GIT_REACH.search(text):
                    problems.append("git command naming other refs or remotes")
                if NETWORK.search(text):
                    problems.append("network access")
                paths += ABS_PATH.findall(text)
            if c["name"] in ("WebFetch", "WebSearch"):
                problems.append("web tool")
            outside = sorted({p for p in paths if p.startswith("/") and not p.startswith(ALLOWED)})
            if outside:
                problems.append(f"paths outside the environment: {outside}")
            if problems:
                flags += 1
                print(f"{out}: {c['name']}: {'; '.join(problems)}\n    {json.dumps(inp)[:300]}")
    print(f"{out}: {n_calls} tool calls checked")
print(f"flagged: {flags}")
sys.exit(1 if flags else 0)

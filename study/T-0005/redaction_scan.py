"""Scan files for the user's email address, the sandbox name, and token or key patterns.

Usage: python3 redaction_scan.py FILE... ; exits 1 and prints each hit if anything is found.
The user's email comes from `git config user.email` at run time, so this file holds no personal data; extra terms
can be passed in the REDACT_TERMS environment variable, comma-separated.
"""
import os
import re
import subprocess
import sys

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@(gmail|googlemail|outlook|hotmail|yahoo)\.com", re.I),
    "GitHub token": re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    "Anthropic key": re.compile(r"sk-ant-[A-Za-z0-9-]{10,}"),
    "AWS key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
}
user_email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True).stdout.strip()
terms = [t for t in os.environ.get("REDACT_TERMS", "").split(",") if t]
if user_email:
    terms += [user_email, user_email.split("@")[0]]
for term in terms:
    PATTERNS[f"term {len(PATTERNS)}"] = re.compile(re.escape(term), re.I)
sandbox = os.environ.get("SANDBOX_NAME") or os.uname().nodename
if sandbox:
    PATTERNS["sandbox name"] = re.compile(re.escape(sandbox))

hits = 0
for path in sys.argv[1:]:
    for n, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        for label, rx in PATTERNS.items():
            if rx.search(line):
                hits += 1
                print(f"{path}:{n}: {label}")
print(f"scanned {len(sys.argv) - 1} file(s); sandbox name checked: {bool(sandbox)}; hits: {hits}")
sys.exit(1 if hits else 0)

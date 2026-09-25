"""Copy a run's outputs with the user's email address, the sandbox name, and token patterns replaced.

Usage: python3 redact.py SRC_FILE DST_FILE [EXTRA_TERM...]
Uses the same patterns as redaction_scan.py (which must then find nothing in DST_FILE). Extra terms, such as the
run's access token, are passed on the command line by the runner and never stored.
"""
import os
import re
import subprocess
import sys

src, dst, *extra = sys.argv[1:]
PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@(gmail|googlemail|outlook|hotmail|yahoo)\.com", re.I),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"sk-ant-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
]
email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True).stdout.strip()
terms = [t for t in extra if t]
if email:
    terms += [email, email.split("@")[0]]
sandbox = os.environ.get("SANDBOX_NAME") or os.uname().nodename
if sandbox:
    terms.append(sandbox)
PATTERNS += [re.compile(re.escape(t), re.I) for t in terms]

text = open(src, encoding="utf-8", errors="replace").read()
for rx in PATTERNS:
    text = rx.sub("[REDACTED]", text)
open(dst, "w", encoding="utf-8").write(text)

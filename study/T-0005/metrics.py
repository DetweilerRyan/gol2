"""Compute T-0005's per-run measures from a run's committed outputs.

Usage: python3 metrics.py RUN_OUT_DIR [--grades GRADES_JSON] [--agentpatterns DIR] [--json]

RUN_OUT_DIR is a run's out/ folder (result.json, transcript.jsonl, run.txt). --agentpatterns is a checkout of the
pinned commit (default: the runner's template), used to recognize page content in tool results and to find each
page's "When this backfires" section. The effectiveness measures need --grades, the user-confirmed grading of the
run's findings; without it they are null, so grading can be redone later without new runs.

Grades file shape:
  {"key_size": 7, "findings": [{"id": 1, "key_item": 3 or null, "accepted": true|false,
                                 "citations": [{"page": "instructions/x.md", "correct": true|false}]}]}

How the measures are computed:
- Tokens per tool result are measured, not estimated: the growth of the context between two consecutive API calls,
  minus the output tokens of the first, is the size of what was added (tool results), split among that turn's
  tool results by character count.
- A page's content is recognized by its distinctive lines (at least 30 characters, found in at most 3 pages). A
  tool result "opened" a page when it holds at least 5 of its lines or half of them; a "whole-page read" holds at
  least 90% of them; any other opening is a section read. This works for Read, Bash, Grep, and LSP alike.
- A cited page is any agentpatterns page path or agentpatterns.ai URL in the final answer that exists at the pinned
  commit. Its "When this backfires" section counts as read when at least half of that section's distinctive
  lines appeared in the run's tool results.
- Peak context is the largest input (uncached + cache write + cache read) of any API call. The agentpatterns share
  is the measured tokens of tool results holding agentpatterns content that were in context at the peak call,
  divided by the peak context.
"""
import argparse
import collections
import json
import os
import re
import sys

p = argparse.ArgumentParser()
p.add_argument("out")
p.add_argument("--grades")
p.add_argument("--agentpatterns", default=os.path.expanduser("~/.local/share/gol2-study/T-0005/agentpatterns-86da49a"))
p.add_argument("--json", action="store_true")
a = p.parse_args()
AP = a.agentpatterns.rstrip("/")
AP_TOOLS = ("Read", "Grep", "Glob", "Bash", "LSP")

# ---- agentpatterns index: distinctive line -> pages
pages, sections = {}, {}
for root, dirs, files in os.walk(AP):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for f in files:
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(root, f), AP)
            pages[rel] = open(os.path.join(root, f), encoding="utf-8", errors="replace").read().splitlines()


def distinctive(line):
    s = line.strip()
    return s if len(s) >= 30 else None


line_pages = collections.defaultdict(set)
for rel, lines in pages.items():
    for ln in lines:
        s = distinctive(ln)
        if s:
            line_pages[s].add(rel)
line_pages = {s: ps for s, ps in line_pages.items() if len(ps) <= 3}
page_lines = collections.defaultdict(set)
for s, ps in line_pages.items():
    for rel in ps:
        page_lines[rel].add(s)


def backfire_lines(rel):
    """Distinctive lines of the page's "When this backfires" section (heading to the next heading of same or higher level)."""
    lines, out, level = pages[rel], set(), None
    for ln in lines:
        m = re.match(r"^(#+)\s+(.*)", ln)
        if m:
            if level is not None and len(m.group(1)) <= level:
                break
            if level is None and m.group(2).strip().lower().startswith("when this backfires"):
                level = len(m.group(1))
            continue
        if level is not None:
            s = distinctive(ln)
            if s and s in line_pages:
                out.add(s)
    return out


# ---- transcript: API calls and tool results in order
calls, results, order = {}, {}, []  # message id -> usage; tool_use_id -> info
tool_uses = {}
for line in open(os.path.join(a.out, "transcript.jsonl"), encoding="utf-8", errors="replace"):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    msg = d.get("message") or {}
    if d.get("type") == "assistant" and msg.get("id"):
        mid = msg["id"]
        if mid not in calls:
            order.append(("call", mid))
        calls[mid] = msg.get("usage") or {}
        for c in msg.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                tool_uses[c["id"]] = (c["name"], c.get("input") or {})
    elif d.get("type") == "user" and isinstance(msg.get("content"), list):
        for c in msg["content"]:
            if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") not in results:
                body = c.get("content")
                text = body if isinstance(body, str) else "\n".join(x.get("text", "") for x in body or [] if isinstance(x, dict))
                results[c["tool_use_id"]] = {"text": text}
                order.append(("result", c["tool_use_id"]))


def ctx(u):
    return (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)


# Measured tokens per tool result: context growth between calls, minus the earlier call's output.
call_ids = [x for k, x in order if k == "call"]
pending, prev = [], None
for kind, x in order:
    if kind == "result":
        pending.append(x)
    else:
        if prev is not None and pending:
            added = max(0, ctx(calls[x]) - ctx(calls[prev]) - (calls[prev].get("output_tokens") or 0))
            chars = sum(len(results[t]["text"]) for t in pending) or 1
            for t in pending:
                results[t]["tokens"] = added * len(results[t]["text"]) / chars
                results[t]["before_call"] = x
        pending, prev = [], x
for t in pending:  # results after the last call never entered a measured context
    results[t].setdefault("tokens", len(results[t]["text"]) / 4)

# Page content per tool result.
for t, r in results.items():
    name, inp = tool_uses.get(t, ("?", {}))
    r["tool"], r["input"] = name, inp
    seen = collections.Counter()
    for ln in r["text"].splitlines():
        s = distinctive(re.sub(r"^\s*\d+[\t→:-]", "", ln))  # strip Read/grep line-number prefixes
        if s and s in line_pages:
            for rel in line_pages[s]:
                seen[rel] += 1
    r["pages"] = seen
    r["ap"] = name in AP_TOOLS and ("agentpatterns" in json.dumps(inp) or bool(seen))

opened, whole = collections.Counter(), set()
lines_read = collections.defaultdict(set)
for r in results.values():
    for rel, n in r["pages"].items():
        total = len(page_lines[rel]) or 1
        if n >= 5 or n >= total / 2:
            opened[rel] += 1
            if n >= 0.9 * total:
                whole.add(rel)
    for ln in r["text"].splitlines():
        s = distinctive(re.sub(r"^\s*\d+[\t→:-]", "", ln))
        if s and s in line_pages:
            for rel in line_pages[s]:
                lines_read[rel].add(s)

# Cited pages: page paths or agentpatterns.ai URLs in the final answer that exist at the pinned commit.
result = json.load(open(os.path.join(a.out, "result.json"))) or {}
answer = result.get("result") or ""
cited = set()
for m in re.finditer(r"agentpatterns\.ai/([\w./-]+?)/?(?=[\s)\]>`'\",]|$)", answer):
    for cand in (m.group(1) + ".md", m.group(1) + "/index.md"):
        if cand in pages:
            cited.add(cand)
for m in re.finditer(r"[\w./-]*[\w-]+\.md", answer):
    s = re.sub(r"^(\.\./|/study/)?agentpatterns/", "", m.group(0)).lstrip("./")
    if s in pages:
        cited.add(s)

backfire = {}
for rel in sorted(cited):
    bl = backfire_lines(rel)
    backfire[rel] = None if not bl else len(bl & lines_read[rel]) >= len(bl) / 2

# Context at the peak call.
peak_id = max(call_ids, key=lambda i: ctx(calls[i])) if call_ids else None
peak = ctx(calls[peak_id]) if peak_id else 0
peak_pos = call_ids.index(peak_id) if peak_id else -1
ap_at_peak = sum(
    r.get("tokens", 0) for r in results.values()
    if r["ap"] and r.get("before_call") in call_ids[: peak_pos + 1]
)

tool_tokens = collections.Counter()
for r in results.values():
    if r["ap"]:
        tool_tokens[r["tool"]] += r.get("tokens", 0)
not_cited_tokens = 0.0
for r in results.values():
    tot = sum(r["pages"].values()) or 1
    for rel, n in r["pages"].items():
        if rel in opened and rel not in cited:
            not_cited_tokens += r.get("tokens", 0) * n / tot

usage = result.get("usage") or {}
m = {
    "run": open(os.path.join(a.out, "run.txt")).read().strip(),
    "efficiency": {
        "cost_usd": result.get("total_cost_usd"),
        "tokens": {
            "input": usage.get("input_tokens"),
            "output": usage.get("output_tokens"),
            "cache_write": usage.get("cache_creation_input_tokens"),
            "cache_read": usage.get("cache_read_input_tokens"),
        },
        "turns": result.get("num_turns"),
        "api_calls": len(call_ids),
        "agentpatterns_tool_tokens": {k: round(tool_tokens[k]) for k in AP_TOOLS},
        "agentpatterns_tool_tokens_total": round(sum(tool_tokens.values())),
        "pages_opened": len(opened),
        "pages_cited": len(cited),
        "whole_page_reads": len(whole),
        "section_only_pages": len(set(opened) - whole),
        "lsp_calls": sum(1 for n, _ in tool_uses.values() if n == "LSP"),
        "tool_calls": dict(collections.Counter(n for n, _ in tool_uses.values())),
    },
    "context": {
        "peak_context_tokens": peak,
        "agentpatterns_tokens_at_peak": round(ap_at_peak),
        "agentpatterns_share_at_peak": round(ap_at_peak / peak, 3) if peak else None,
        "tokens_opened_not_cited": round(not_cited_tokens),
        "cited_pages": sorted(cited),
        "backfire_read": backfire,
        "backfire_read_share": (
            round(sum(1 for v in backfire.values() if v) / len([v for v in backfire.values() if v is not None]), 3)
            if any(v is not None for v in backfire.values()) else None
        ),
    },
    "effectiveness": None,
}

if a.grades:
    g = json.load(open(a.grades))
    fs = g["findings"]
    acc = [f for f in fs if f.get("accepted")]
    matched = {f["key_item"] for f in fs if f.get("key_item") is not None}
    cites = [c for f in fs for c in f.get("citations", [])]
    m["effectiveness"] = {
        "accepted_findings": len(acc),
        "accepted_in_key": sum(1 for f in acc if f.get("key_item") is not None),
        "accepted_off_key": sum(1 for f in acc if f.get("key_item") is None),
        "key_recall": round(len(matched) / g["key_size"], 3),
        "rejected_findings": sum(1 for f in fs if f.get("accepted") is False),
        "incorrect_citations": sum(1 for c in cites if c.get("correct") is False),
    }

if a.json:
    json.dump(m, sys.stdout, indent=2)
    print()
else:
    for section in ("efficiency", "context", "effectiveness"):
        print(f"[{section}]")
        for k, v in (m[section] or {}).items():
            print(f"  {k}: {v}")

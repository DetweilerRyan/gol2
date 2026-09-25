---
id: T-0010
title: Extract, confirm, and commit the benefit study's answer keys before their transcripts expire
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "The Handoff names the transcript file holding each of the three coach reviews used as answer keys: T-0001 at `648d64a`, T-0004 at `f5f6bff`, and the set T-0001 to T-0004 at `c44ca0f`"
  - "Each review's findings are listed with the user's decision on each (accepted, rejected, or changed by a later decision), taken from the same session's main transcript"
  - "The user confirmed each key's final list of accepted findings, and the evidence records where"
  - "The keys and the list of findings behind them are committed, redacted, on branch `prototype/T-0005-lsp-benefit` (created here if it doesn't exist; pushed, kept, never merged), after a scan for the user's email address, token and key patterns, and the sandbox name finds nothing; the scan's command and output are in the evidence"
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence: []
---

## Context

The benefit study (T-0005, T-0008) scores the coach's reviews against answer keys built from three coach reviews
made on 2026-09-25. Those reviews exist only in session transcripts under
`~/.claude/projects/-c-Users-User-Documents-projects-gol2--claude-worktrees-board-rumdl-task/440265dc-29df-4a06-99dc-0fa759d9950d/subagents/`.
Claude Code deletes transcripts after `cleanupPeriodDays` (30 days by default, so around 2026-10-25), and removing
the sandbox deletes them too. Do this task first, well before then. Epic: T-0009.

The same folder holds later coach runs too (reviews of other versions and of the whole set), so identify each of
the three by its prompt and the commit it reviewed. The user's decisions are in the session's main transcript
(`440265dc-29df-4a06-99dc-0fa759d9950d.jsonl` in the parent folder): for these three reviews the user said to apply
all findings, and some were shaped by the user's answers to follow-up questions. A fourth review, of T-0005 at
`ff794b4`, isn't used: that version of T-0005 describes the study itself, which would contaminate it (the user's
decision, 2026-09-25).

The transcripts contain injected context such as the user's email address and sandbox details, so only redacted
extracts are committed.

## Handoff

Not started.

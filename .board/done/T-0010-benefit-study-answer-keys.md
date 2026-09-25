---
id: T-0010
title: Extract, confirm, and commit the benefit study's answer keys before their transcripts expire
depends_on: []
claimed_by: claude-session-440265dc
verified_by: coach
acceptance:
  - "The Handoff names the transcript file holding each of the three coach reviews used as answer keys: T-0001 at `648d64a`, T-0004 at `f5f6bff`, and the set T-0001 to T-0004 at `c44ca0f`"
  - "Each review's findings are listed with the user's decision on each (accepted, rejected, or changed by a later decision), taken from the same session's main transcript"
  - "The user confirmed each key's final list of accepted findings, and the evidence records where"
  - "The keys and the list of findings behind them are committed, redacted, on branch `prototype/T-0005-lsp-benefit` (created here if it doesn't exist; pushed, kept, never merged), after a scan for the user's email address, token and key patterns, and the sandbox name finds nothing; the scan's command and output are in the evidence"
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence:
  - criterion: "The Handoff names the transcript file holding each of the three coach reviews used as answer keys: T-0001 at `648d64a`, T-0004 at `f5f6bff`, and the set T-0001 to T-0004 at `c44ca0f`"
    command: "Listed each subagent transcript in the session's subagents/ folder with its .meta.json description, first prompt line, and start time, then matched each review to the task version it reviewed; the mapping is in `study/T-0005/extract_reviews.py` (REVIEWS) at commit bc19162 (first committed in 3c311fc)"
    result: 'T-0001 at 648d64a: agent-ac328c90f7d3ffee9.jsonl ("Coach reviews T-0001 via agentpatterns", 14:39Z); T-0004 at f5f6bff: agent-a13299bd72cc9497d.jsonl (15:31Z); set at c44ca0f: agent-a8e33acdcc1015860.jsonl ("Coach reviews all board tasks", 15:45Z). agent-afbfbe9df6fa67168 was a T-0001 review the user stopped, with no output, so it''s excluded. Named in the Handoff.'
  - criterion: "Each review's findings are listed with the user's decision on each (accepted, rejected, or changed by a later decision), taken from the same session's main transcript"
    command: "git show bc19162:study/T-0005/answer-keys.md"
    result: "Three tables, one per review, listing 7, 9, and 10 findings by the coach's numbering with the user's decision on each: all 26 accepted (the user said to apply all after answering each review's questions). Later changes noted: Key 1 #7 and Key 3 #5 (approval became the user merging the PR), Key 2 #9 (Rust became TypeScript/Node), Key 3 #9 (CLAUDE.md pointer deferred). The round labels on Key 1 #7 and Key 3 #5 were corrected from round 3 to round 2 in bc19162."
  - criterion: "The user confirmed each key's final list of accepted findings, and the evidence records where"
    command: "The user's answers to three questions in session 440265dc-29df-4a06-99dc-0fa759d9950d on 2026-09-25, one per key, recorded in the session's main transcript"
    result: 'The user chose "Confirm as drafted" for Key 1 (7 findings, the "Outside this review" note not counted), Key 2 (9 findings, finding 9 counted once), and Key 3 (10 findings, including the two later changed), at 2026-09-25T18:00:26Z, 18:01:03Z, and 18:01:24Z respectively in the main transcript. Recorded in answer-keys.md.'
  - criterion: "The keys and the list of findings behind them are committed, redacted, on branch `prototype/T-0005-lsp-benefit` (created here if it doesn't exist; pushed, kept, never merged), after a scan for the user's email address, token and key patterns, and the sandbox name finds nothing; the scan's command and output are in the evidence"
    command: "python3 study/T-0005/redaction_scan.py study/T-0005/answer-keys.md study/T-0005/reviews/T-0001-at-648d64a.txt study/T-0005/reviews/T-0004-at-f5f6bff.txt study/T-0005/reviews/set-T-0001-T-0004-at-c44ca0f.txt study/T-0005/redaction_scan.py study/T-0005/extract_reviews.py (on prototype/T-0005-lsp-benefit before commit 3c311fc was pushed)"
    result: "scanned 6 file(s); sandbox name checked: True; hits: 0. The same scanner on a test file with the user's email address and the sandbox name reported 4 hits and exited 1, so it detects them. Branch prototype/T-0005-lsp-benefit created from main, committed as 3c311fc, and pushed to origin. After the label and script fixes, the same scan again gave hits: 0, and the branch was pushed at bc19162, two commits on top of main and not merged."
  - criterion: "`npm run check` exits 0 on the branch that carries this task file"
    command: "npm run check (pre-commit hook on branch t-0010-answer-keys)"
    result: "exit 0: formatting clean, markdownlint 0 issues, Board OK: 10 task(s), typecheck passed, vitest found no test files (exit 0)"
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

**Done.** The three answer keys are committed on `prototype/T-0005-lsp-benefit` (first at `3c311fc`; current,
after the verification fixes, at `bc19162`), under
`study/T-0005/`: `answer-keys.md` (the keys, the user's decisions, and the user's confirmation), `reviews/` (each
review's full final output as plain text), `extract_reviews.py` (pulls those outputs from the transcripts), and
`redaction_scan.py` (the scan T-0005 and T-0008 can reuse before pushing).

**Transcripts used** (in the `subagents/` folder named in Context):

- T-0001 at `648d64a`: `agent-ac328c90f7d3ffee9.jsonl`, 7 findings.
- T-0004 at `f5f6bff`: `agent-a13299bd72cc9497d.jsonl`, 9 findings.
- The set T-0001 to T-0004 at `c44ca0f`: `agent-a8e33acdcc1015860.jsonl`, 10 findings.

**Found.** Every finding in the three reviews was accepted, so each key is the review's full list (26 findings in
all). Four were later changed by other decisions; they stay in the keys, marked. The reviews' texts contained no
email address, token, or sandbox name. The first version of the scanner had the user's email username hard-coded as
a pattern, which the scan itself caught; it now reads the address from `git config user.email` at run time, so the
committed script holds no personal data.

**Needs attention.** The transcripts still expire around 2026-10-25, but nothing downstream needs them now. The
keys match findings by the coach's numbering; T-0005 still has to fix how a new review's finding counts as matching
a key finding.

**Unresolved.** None.

**Verification.** The coach verified all five criteria independently on 2026-09-25: it compared the task text each
review read in its transcript with the three commits byte for byte, reran the extraction and the redaction scan
(0 hits, and 6 hits on a planted test file), matched every decision and confirmation to the user's messages, and
ran `npm run check` (exit 0). Its verdict: ready for `done/`. It found three minor issues, fixed in `bc19162` on
the prototype branch and in this file: two round labels (round 3 → round 2), missing confirmation timestamps, and
`extract_reviews.py` not reproducing `reviews/*.txt` (it now does, byte for byte). The coach can't write board
lanes, so on the user's explicit instruction the implementing session recorded `verified_by: coach` and moved the
task to `done/`. Note for separation of duties: the coach ran as a subagent of the implementing session
(claude-session-440265dc), so the verifier is a different agent but not a different session.

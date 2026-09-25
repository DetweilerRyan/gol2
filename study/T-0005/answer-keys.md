# Benefit study answer keys

Source session: `440265dc-29df-4a06-99dc-0fa759d9950d` (2026-09-25). Each key lists the findings of one coach review,
by the coach's own numbering, with the user's decision taken from the same session's main transcript. A finding is
in the key if the user accepted it at the time of the review; later changes are noted but don't remove a finding.

**Confirmed by the user** on 2026-09-25 in that session, one key at a time, choosing "Confirm as drafted" for each:
Key 1 (7 findings, the "Outside this review" note not counted), Key 2 (9 findings, finding 9 counted once), and
Key 3 (10 findings, including the two later changed). The reviews' full text, redacted, is in `reviews/`; they
were extracted with `extract_reviews.py` and scanned with `redaction_scan.py`.

## Key 1: T-0001 at `648d64a`

Transcript: `subagents/agent-ac328c90f7d3ffee9.jsonl` ("Coach reviews T-0001 via agentpatterns"). The user's
decision: "go ahead and follow all of coach's recommendations".

| #   | Finding                                                                                                                                                                          | Decision | Later change                                                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------- |
| 1   | The task grew mid-spec (7 → 13 criteria); split the lint swap from the LSP plugin (and the docs)                                                                                 | Accepted | Split further later (T-0002, T-0003, T-0004 to T-0008)           |
| 2   | Worktrees have no `node_modules/`, so the pinned-binary and worktree-session criteria can't both pass as written                                                                 | Accepted |                                                                  |
| 3   | A criterion locks in the marketplace plugin setup the Context calls unverified; state the outcome, not the mechanism (skills-dir route exists)                                   | Accepted |                                                                  |
| 4   | No criterion checks the main reason for rumdl: LSP diagnostics matching the gate's; autofix-off has no check                                                                     | Accepted | Diagnostics check moved to T-0001                                |
| 5   | Three criteria don't fit the evidence rule: the worktree-session check has no command, "record in Handoff" can't fail, the docs criterion is a judgment and belongs to the coach | Accepted |                                                                  |
| 6   | The planted-error criterion needs a command that creates its own temporary file so the verifier can rerun it                                                                     | Accepted |                                                                  |
| 7   | Security: have the user review the executable-config (`.claude/settings.json`) change rather than an agent                                                                       | Accepted | Later changed: the user merges the PR (full-set review, round 3) |

Not counted: the "Outside this review" note (no lane for "specified, awaiting approval"), which is about the board,
not the task; it was left for the retro.

## Key 2: T-0004 at `f5f6bff`

Transcript: `subagents/agent-a13299bd72cc9497d.jsonl` ("Coach reviews T-0004 via agentpatterns"). The user's
decisions: questions 7 to 9 answered one at a time, then "go ahead and apply all of them".

| #   | Finding                                                                                                                                                     | Decision                                               | Later change                                                     |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------- |
| 1   | The prototype on the unmerged task branch means the board never records the result; use a separate kept `prototype/` branch                                 | Accepted                                               |                                                                  |
| 2   | No early exit if file watching can't work on the mount; make the relay criteria conditional ("no way of detecting changes works", not just inotify)         | Accepted                                               |                                                                  |
| 3   | Deliberately broken test links make the Stop hook block the agent repeatedly; use valid links                                                               | Accepted                                               |                                                                  |
| 4   | The host-side step needs the user and a default if the user isn't available                                                                                 | Accepted                                               |                                                                  |
| 5   | The waiting headless session has no turn cap; bound it and signal only after each change command succeeds                                                   | Accepted                                               |                                                                  |
| 6   | The test criterion is ambiguous (one session or one per condition) and puts too much raw output in the task file; store logs as files, summarize in a table | Accepted                                               |                                                                  |
| 7   | Should the spike test only `workspace/didChangeWatchedFiles`, or any relay approach?                                                                        | Accepted: any relay approach                           |                                                                  |
| 8   | No check that the watcher doesn't break the Write/Edit path; add Write and Edit routes                                                                      | Accepted                                               |                                                                  |
| 9   | Two lower-priority risks: expected-answer bias (keep raw output as the guard) and the prototype becoming production code (reimplement)                      | Accepted: keep the guard; reimplement, preferring Rust | Rust later changed to TypeScript/Node (full-set review, round 1) |

## Key 3: the set T-0001 to T-0004 at `c44ca0f`

Transcript: `subagents/agent-a8e33acdcc1015860.jsonl` ("Coach reviews all board tasks"). The user's decisions: six
answered one at a time, then "go ahead and apply all of them".

| #   | Finding                                                                                                                              | Decision                                             | Later change                                                                      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | The set checks whether the LSP can work, never whether it's worth it; add a benefit comparison                                       | Accepted: a new benefit-study spike on agentpatterns |                                                                                   |
| 2   | T-0004's "go" has no stated rule and doesn't match T-0002; decide whether host edits must be fresh                                   | Accepted: go matches T-0002, host edits optional     |                                                                                   |
| 3   | Most of T-0002's criteria can't fail (record-only); decide which operations must work                                                | Accepted: all four must work                         |                                                                                   |
| 4   | The relay works around a Claude Code gap with no removal condition; weigh Rust for a stopgap                                         | Accepted: Node, with a removal condition in the ADR  |                                                                                   |
| 5   | The user's review covers only the first version of executable config; require a checkable approval on the final commit               | Accepted: final-commit approval                      | Later changed: the user merges the PR (full-set review, round 3)                  |
| 6   | The same research facts are copied into several tasks and will drift; give each one home                                             | Accepted                                             |                                                                                   |
| 7   | T-0002 is too big; split the relay out; say how to record evidence for criteria that didn't apply                                    | Accepted                                             |                                                                                   |
| 8   | The board has no final state for a dropped task                                                                                      | Accepted: new `dropped/` lane (T-0006)               |                                                                                   |
| 9   | Nothing gets agents to use the LSP; add a `CLAUDE.md` pointer when the docs land, with a retro prediction                            | Accepted                                             | Pointer later deferred until a retro shows it's needed (full-set review, round 3) |
| 10  | Some of T-0002's evidence may not be producible from a worktree; name who runs main-checkout sessions; no hand-set `ENABLE_LSP_TOOL` | Accepted                                             |                                                                                   |

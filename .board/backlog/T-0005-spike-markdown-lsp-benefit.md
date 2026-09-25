---
id: T-0005
title: "Spike: does a Markdown LSP make the coach's agentpatterns reviews cheaper and better?"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "A Claude Code session serves rumdl's LSP over the agentpatterns corpus (`/c/Users/User/Documents/projects/agentpatterns`), shown by raw `documentSymbol` and `workspaceSymbol` output for agentpatterns files; if that isn't possible, the Handoff shows why with evidence, and the remaining study criteria are recorded as not applicable"
  - "Before any study run, a workload file on branch `prototype/T-0005-lsp-benefit` (pushed, kept, never merged) fixes the review tasks, the prompt, the two conditions, the number of runs, the quality rubric, and the go rule, and the evidence gives its commit"
  - "The two conditions differ only in whether the coach has the LSP tool and a one-line instruction to use it for Markdown navigation; the model, prompt, tools otherwise, and review tasks are the same, and the evidence shows the configuration of each"
  - "Each review task in the workload is run at least 3 times per condition, and each run's `claude -p --output-format json` output (tokens, turns, cost) and transcript are committed as files on the prototype branch"
  - "For each run the evidence records total input and output tokens, tokens returned by file-reading tools (Read, Grep, Glob, LSP) split by tool, the number of agentpatterns pages opened versus cited, and whether the LSP tool was used at all"
  - "The user rates each pair of review outputs (one per condition, condition hidden) against the rubric, and the evidence records the ratings and how the condition was hidden"
  - "Every agentpatterns page cited in each review is checked to exist and to have been opened in that run, by a command whose output is in the evidence"
  - "The Handoff states whether the hypothesis held, applying the go rule fixed in the workload file, with the numbers, and recommends go or no-go for T-0002"
  - "`npm run check` exits 0 on the task's branch"
evidence: []
---

## Context

The user wants to know whether a Markdown LSP is worth adopting before building it (T-0002). gol2's own docs (11
files, about 520 lines) are too small to show a difference; the agentpatterns corpus the coach reviews against is
large enough. The hypothesis to test: when the coach performs a review using the Markdown LSP to navigate
agentpatterns, it uses fewer tokens, and it's more effective, because irrelevant text stays out of its context.
A no-go is a valid result. This task can run in parallel with T-0004; freshness doesn't matter here because the
corpus doesn't change during the study.

**Go rule (proposed; fix it in the workload file before the first run).** Go if the LSP condition's median total
tokens per review is at least 20% lower and the user rates its output equal or better in at least half of the
pairs. If the LSP condition is cheaper but rated worse, that's no-go. The user may change the threshold when
approving this task; it must not change after runs start.

**Rubric (proposed).** For each review: relevant findings (would the user act on it), correct citations (the cited
page says what the review claims), and noise (findings that don't apply). Rate each pair as LSP better, same, or
baseline better, per dimension.

**Setup notes (unverified; record what worked in the Handoff):**

- **The coach and the LSP tool.** The coach's role file (`.claude/agents/coach.md`) doesn't list the LSP tool, and
  its constraints say not to loosen that file without the user's approval. Don't change it for the study; define
  the two study variants with `claude -p --agents <file>` (or an equivalent), keeping the coach's instructions and
  adding only the LSP tool and the one-line instruction in the LSP condition. `--agent <name>` selects one.
- **Pointing rumdl at agentpatterns.** The LSP server's workspace is normally the session's project folder
  (gol2). Options: the `.lsp.json` `workspaceFolder` field set to the agentpatterns path; running the session
  with agentpatterns as its project folder (it must be a trusted workspace); or `--add-dir`. `--plugin-dir <path>`
  loads a plugin for one session only, which keeps the study's plugin out of the repo. T-0002's Context has the
  plugin layout that loaded in the 2026-09-25 spike, and T-0003's Context has how rumdl's LSP operations behave.
- **Measuring.** `claude -p --output-format json` reports `usage` (input, output, cache tokens), `num_turns`, and
  `total_cost_usd` for the session. Tokens per tool come from the transcript's tool results.
- **Worktree isolation.** An isolated worktree session refuses to start a nested `claude` session that has Bash.
  The coach's tools include Bash; either run the study from a session that isn't worktree-isolated, remove Bash
  from both study variants equally, or have the user run the sessions.
- **Review tasks.** Use reviews the coach actually does: for example, reviewing a fixed snapshot of a board task
  file against agentpatterns, like the reviews of T-0001 to T-0004 on 2026-09-25. Commit the snapshots with the
  workload so every run reviews the same text.

Out of scope: changing the coach's role file or `CLAUDE.md`, and building the production plugin (T-0002).

## Handoff

Not started.

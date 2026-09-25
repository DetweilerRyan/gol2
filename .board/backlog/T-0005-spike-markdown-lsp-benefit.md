---
id: T-0005
title: "Spike: does a Markdown LSP make the coach's agentpatterns reviews cheaper and better?"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "A Claude Code session serves rumdl's LSP over the agentpatterns corpus (`/c/Users/User/Documents/projects/agentpatterns`), shown by raw `documentSymbol` and `workspaceSymbol` output for agentpatterns files; if that isn't possible, the Handoff shows why with evidence, and the remaining study criteria are recorded as not applicable"
  - "A pilot of one run per condition on one review task is run before the workload is fixed, its cost and LSP use are recorded in the Handoff, and it is excluded from the study data"
  - "Before any study run, a workload file on branch `prototype/T-0005-lsp-benefit` (pushed, kept, never merged) fixes the review tasks (at least 3, each a snapshot with a reference answer key), the prompt, the exact LSP instruction text, the two conditions, the number of runs, how runs are paired for rating, the quality rubric, the uptake rule, and the go rule; the evidence gives its commit"
  - "The two conditions differ only in whether the coach has the LSP tool and the one-line LSP instruction; the model, Claude Code version, effort level, prompt, other tools (including Bash), and review tasks are the same, and the evidence shows each configuration"
  - "Each review task is run at least 3 times per condition, alternating conditions run by run, and the working tree is reset to the same commit before each run, shown by `git status` in the evidence"
  - "Each run's `claude -p --output-format json` output and a redacted copy of its transcript (the user's email, secrets, and sandbox identifiers removed) are committed as files on the prototype branch, and the redaction command is in the evidence"
  - "For each run the evidence records cost in USD, tokens by type (input, output, cache write, cache read), turns, tokens returned by each tool that read agentpatterns content (Read, Grep, Glob, Bash, LSP), the number of agentpatterns pages opened by any tool versus cited, whether the coach read whole pages or single sections, and how many LSP calls it made"
  - "The user rates each pair of review outputs against the rubric, with the condition hidden, left/right order randomized, and mentions of LSP, symbols, or line anchors removed before rating; the evidence records the ratings and how this was done"
  - "Every agentpatterns page cited in each review is checked to exist and to have been opened in that run by any tool, by a command whose output is in the evidence"
  - "The Handoff reports each metric per review task and condition as a median with its range, and applies the uptake rule and the go rule fixed in the workload file, recommending go, no-go, or not tested for T-0002, as a screen rather than a ranking"
  - 'The Handoff describes the corpus''s structure (pages, lines per page, headings per page, links between pages) with the command that measured it, and, if the result is no-go, states whether that structure rather than the LSP could explain it, citing per-run data such as how often the coach read whole pages versus single sections; a no-go explained by structure is recorded as "not shown on this corpus", not as "the LSP doesn''t help"'
  - "`npm run check` exits 0 on the task's branch"
evidence: []
---

## Context

The user wants to know whether a Markdown LSP is worth adopting before building it (T-0002). gol2's own docs (11
files, about 520 lines) are too small to show a difference; the agentpatterns corpus the coach reviews against is
large enough, and T-0002 serves agentpatterns too, so a go here is a benefit T-0002 ships. The hypothesis to test:
when the coach performs a review using the Markdown LSP to navigate agentpatterns, it costs less, and it's more
effective, because irrelevant text stays out of its context. A no-go is a valid result. This task can run in
parallel with T-0004; freshness doesn't matter here because the corpus doesn't change during the study. The result
is a screen: a small number of runs can show a clear, consistent difference, not rank close ones.

**Go rule (proposed; fix it in the workload file before the first study run; the user may change the numbers when
approving this task, never after runs start).** Go only if all of these hold:

- Median cost in USD per review and median tokens returned by agentpatterns-reading tools per review are both at
  least 20% lower in the LSP condition, in every review task, and each gap is larger than the spread of the runs
  within each condition.
- On correct citations and on relevant findings, the user rated the baseline better in no more pairs than they
  rated the LSP better.
- The uptake rule holds.

**Uptake rule (proposed).** The LSP condition counts as tested only if the coach made at least one LSP call in at
least two thirds of its runs. Otherwise the result is "not tested", not no-go: agents often skip an optional tool.

**Rubric (proposed).** For each review: relevant findings (would the user act on it; compare with the answer key),
correct citations (the cited page says what the review claims), and noise (findings that don't apply). Rate each
pair as LSP better, same, or baseline better, per dimension. Pair run 1 with run 1, run 2 with run 2, and so on,
within each review task.

**LSP instruction.** Word it as a capability, not as a way to save tokens: for example, "To find headings or
sections in Markdown, use the LSP tool's documentSymbol and workspaceSymbol." An efficiency framing ("save tokens",
"avoid reading whole pages") can change cost and quality by itself, whatever the tool does.

**Review tasks and answer keys.** Snapshots from before each 2026-09-25 coach review, so there's something to find,
with that review's findings as the reference answer key:

- T-0001 at commit `648d64a` (the first review: 7 findings, led by splitting the task).
- T-0004 at `f5f6bff` (9 findings).
- The set T-0001 to T-0004 at `c44ca0f` (10 findings).
- T-0005 at `ff794b4` (10 findings).

The coach's outputs aren't in the repo; take them from the subagent transcripts under
`~/.claude/projects/-c-Users-User-Documents-projects-gol2/` for session `440265dc…`, and commit them (redacted) with
the workload.

**False-negative risk: the corpus's structure.** agentpatterns may not be structured so that an LSP is materially
effective, and the study could then report no-go even if an LSP helps on larger or differently structured docs.
Measured on 2026-09-25: 1,587 pages and 190,065 lines; lines per page median 112 (mean 120, range 24 to 1,825);
headings per page median 10 (8 of them level 2); links to other pages median 9 per page, with 2 pages having none.
A median section is about a dozen lines, but a whole median page is only about 112, so reading an outline plus
one section may save little over reading the page. The coach also often knows a page's path already, which grep
or a direct read finds cheaply. The LSP's edge is more likely in heading search across pages and in long pages.
If the result is no-go, say whether this explains it before recommending anything beyond this corpus.

**Cost measurement.** In Claude Code, most input tokens are the cached prompt re-sent each turn. An LSP that
replaces one whole-page read with several small calls lowers the tokens tools return but adds turns, which can
raise cost. That's why the go rule needs both cost and tool-returned tokens to fall. Alternating conditions keeps
prompt-cache warmth from favoring one side.

**Setup notes (unverified; record what worked in the Handoff):**

- **The coach and the LSP tool.** The coach's role file (`.claude/agents/coach.md`) doesn't list the LSP tool, and
  its constraints say not to loosen that file without the user's approval. Don't change it for the study; define
  the two study variants with `claude -p --agents <file>` (or an equivalent), keeping the coach's instructions and
  adding only the LSP tool and the instruction in the LSP condition. `--agent <name>` selects one.
- **Bash stays in both conditions,** as in the real coach, which reads pages with `cat`, `grep`, and `sed`. An
  isolated worktree session refuses to start a nested `claude` session that has Bash, so run the study from a
  session that isn't worktree-isolated, or have the user run the sessions.
- **Isolation.** The coach has Edit and Write. Reset the working tree to the snapshot commit before every run, so
  one run's edits can't change what the next sees.
- **Pointing rumdl at agentpatterns.** The LSP server's workspace is normally the session's project folder
  (gol2). Options: the `.lsp.json` `workspaceFolder` field set to the agentpatterns path; running the session
  with agentpatterns as its project folder (it must be a trusted workspace); or `--add-dir`. `--plugin-dir <path>`
  loads a plugin for one session only, which keeps the study's plugin out of the repo. T-0002's Context has the
  plugin layout that loaded in the 2026-09-25 spike, and T-0003's Context has how rumdl's LSP operations behave.
- **Measuring.** `claude -p --output-format json` reports `usage` (input, output, cache tokens), `num_turns`, and
  `total_cost_usd` for the session. Tokens per tool come from the transcript's tool results.
- **Pilot.** The pilot's cost times the planned number of runs estimates the study's cost; if that looks larger
  than the decision is worth, stop and ask the user before fixing the workload.

Out of scope: changing the coach's role file or `CLAUDE.md`, and building the production plugin (T-0002).

## Handoff

Not started.

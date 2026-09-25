---
id: T-0005
title: "Spike setup and pilot: Markdown LSP benefit study for the coach's agentpatterns reviews"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "A runner script and a metrics script are committed on branch `prototype/T-0005-lsp-benefit` (pushed, kept, never merged): the runner builds an isolated environment, runs one coach review, and redacts its transcript; the metrics script computes every per-run measure in this file's Context from a run's JSON output and transcript, so grading can be redone without new runs"
  - "Each run the runner builds happens in an environment where the original gol2 checkout, the shared agentpatterns checkout, and `~/.claude/projects/` don't exist (for example a separate home directory or user, or a container), holding only a fresh clone of its snapshot commit (no other branches or tags, no remote, no reflog), a separate checkout of agentpatterns at commit `86da49a` at the `../agentpatterns` path relative to that clone, and a Claude config directory of its own; the runner's output for each run shows `git rev-parse HEAD`, `git for-each-ref`, and `git remote` for the clone, the agentpatterns commit, and a listing of the home directory"
  - "Inside a run the runner built, the coach's LSP tool is listed and `documentSymbol` and `workspaceSymbol` calls on agentpatterns files return results, shown by the raw output; if that can't be made to work, the Handoff shows why with evidence, the remaining criteria are recorded as not applicable, and T-0008 moves to `dropped/`"
  - "A diff of the two conditions' agent definitions, and of the tool lists each pilot run started with, shows they differ only in the LSP tool and the one-line LSP instruction; the diff is in the evidence"
  - "A check over every run's transcript finds no command reaching other refs or remotes and no read outside the run's environment; its output is in the evidence"
  - "Before anything is pushed, a scan of the files to be committed for the user's email address, token and key patterns, and the sandbox name finds nothing, and its command and output are in the evidence; credentials a run needs are set up before its session starts"
  - "Each answer key contains only findings the user accepted from the review it comes from, and the user confirmed each key; the keys are committed (redacted) on the prototype branch"
  - "A pilot of at least two runs per condition on one review task records in the Handoff: cost and its spread per condition, accepted findings and key recall of the baseline, LSP uptake, peak context and the agentpatterns share of it per condition, and an estimate of the user's rating time for the study; pilot runs are excluded from the study data"
  - "A grader agent's answer-key matches and citation judgments, made on redacted, condition-hidden pilot outputs, agree with the user's on a sample the user graded, measured by balanced accuracy or Cohen's kappa with at least 5 true matches in the sample, and meet the calibration rule in the workload file; the evidence records the sample and the result"
  - "A workload file on the prototype branch fixes the review tasks (at least 3 snapshots with their answer keys), the agentpatterns commit, the prompt, the exact LSP instruction text, the two conditions, the number of runs, how runs are paired for rating, the rubric, how findings are matched to the key, the calibration rule, the uptake rule, the effectiveness gate, the efficiency guardrail, and the smallest differences in accepted findings and in cost the study can detect, derived from the pilot; the evidence gives its commit"
  - "The Handoff states whether any pilot stop condition in this file's Context was hit, and if so the user decided whether to proceed before T-0008 leaves `backlog/`; it records the user's decision"
  - "The Handoff notes how the study coach differs from the real one (for example, no user-level settings or plugins in its config directory)"
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence: []
---

## Context

The user wants to know whether a Markdown LSP is worth adopting before building it (T-0002). This task builds the
study's isolated setup, confirms the LSP works inside it, runs a pilot, calibrates the grader, and fixes the
workload; T-0008 runs the study. The pilot's Handoff is the user's decision point before the expensive part. This
file is the home for the study's design; T-0008 points here. It can run in parallel with T-0004. Epic: T-0009.

gol2's own docs (11 files, about 520 lines) are too small to show a difference; the agentpatterns corpus the coach
reviews against is large enough, and T-0002 serves agentpatterns too, so a go is a benefit T-0002 ships. A no-go
is a valid result. The result is a screen: a small number of runs can show a clear, consistent difference, not rank
close ones.

**The hypothesis.** When the coach performs a review using the Markdown LSP to navigate agentpatterns, it's more
effective, because irrelevant text stays out of its context, and it also uses fewer tokens. The user decided
(2026-09-25) that **effectiveness is the gate and efficiency is a guardrail**: the LSP is adopted only if reviews
get better, and only as long as they don't get costlier. Lower cost is reported but doesn't earn a go by itself.

**Main effectiveness score: accepted findings per run.** The findings the user accepts from a run, whether in the
answer key or not, with off-key findings rated on their merits before the user sees the key (the user's decision,
2026-09-25). Key recall is secondary. Recall alone mostly measures how closely a run repeats the baseline reviews
the keys came from, which penalizes an LSP coach that finds different good problems.

**Counting runs.** The main result counts every LSP-condition run as assigned, whether or not it called the LSP,
because that's what adopting it looks like. Runs that did call it are a secondary result (the user's decision).

**Effectiveness gate (proposed; fix it in the workload file before the first study run; the user may change the
numbers when approving this task, never after runs start).** Go requires all of these:

- The median number of accepted findings per run is higher in the LSP condition in every review task, by at least
  one finding in at least half of them, and each gap is larger than the spread of the runs within each condition.
- In the user's blind pair ratings of relevant findings, the LSP is rated better in more pairs than the baseline.
- The LSP condition is not worse on incorrect citations, rejected findings (noise), or the share of cited pages
  whose "When this backfires" section was read.

**Efficiency guardrail (proposed, fixed the same way).** Outcomes: held, breached, or not measurable. A breach,
which is a no-go even if the gate passes, needs both: in some review task, the LSP condition's median cost in USD or
median tokens returned by agentpatterns-reading tools is more than 10% higher than the baseline's, and that gap is
larger than the spread of the runs within each condition. It's not measurable when the pilot shows the smallest
detectable cost difference at the planned number of runs is above 10%; run-to-run cost for the same setup varies by
about ×1.34, so at 3 runs "held" can be close to the default.

**Uptake rule (proposed).** The LSP condition counts as tested only if the coach made at least one LSP call in at
least two thirds of its runs. Otherwise the result is "not tested", not no-go: agents often skip an optional tool.

**Pilot stop conditions.** Stop and ask the user before fixing the workload if any of these hold: LSP uptake in the
pilot is below the uptake rule; the baseline already finds so much that the gate's gain is out of reach; the
agentpatterns share of context isn't lower in the LSP condition; or the estimated cost in dollars or the user's
rating time looks larger than the decision is worth.

**Per-run measures (computed by the metrics script):**

- Effectiveness: accepted findings (in the key and off-key), key recall (key findings matched divided by key
  size), rejected findings, and citations that don't say what the review claims.
- Context: peak context tokens, the agentpatterns share of it, tokens from agentpatterns pages opened but not cited,
  and whether each cited page's "When this backfires" section was read.
- Efficiency: cost in USD, tokens by type (input, output, cache write, cache read), turns, tokens returned by each
  tool that read agentpatterns content (Read, Grep, Glob, Bash, LSP), pages opened versus cited, whole-page versus
  section reads, and the number of LSP calls.

**What the study can detect.** The keys have 7 to 10 findings, and a review may add a few accepted off-key ones, so
one finding is a large step. Cost varies a lot from run to run with the number of turns. The pilot estimates both;
write the smallest detectable differences into the workload file, and if the gate or guardrail can't be met or
tripped at that sample size, raise the runs or ask the user.

**The grader.** The implementing agent is the same model family as the coach and can see which condition each run
used, so it doesn't grade blind by default. A grader agent works from the redacted, condition-hidden outputs, after
its judgments agree with the user's on a sample the user grades (the user's decision). Use balanced accuracy or
Cohen's kappa, not raw agreement: most findings are clear non-matches, so a grader that always says "no match" gets
high raw agreement (across 21 judges, raw agreement overstated chance-corrected agreement by 33 to 41 points).

**Answer keys.** Built only from the findings the user accepted from each 2026-09-25 coach review, and confirmed by
the user. The keys come from reviews made without the LSP, and the user acted on them, so their findings will look
familiar; that's why off-key findings are rated before the user sees the key. The reviews cited agentpatterns at
`86da49a` ("Release v1.8.67", 2026-09-24), which is why the study pins that commit. Review tasks, snapshots from
before each review so there's something to find:

- T-0001 at commit `648d64a` (the first review: 7 findings, led by splitting the task).
- T-0004 at `f5f6bff` (9 findings).
- The set T-0001 to T-0004 at `c44ca0f` (10 findings).
- T-0005 at `ff794b4` (10 findings).

The coach's outputs aren't in the repo. They're in the subagent transcripts under
`~/.claude/projects/-c-Users-User-Documents-projects-gol2--claude-worktrees-board-rumdl-task/440265dc-29df-4a06-99dc-0fa759d9950d/subagents/`.
The user's accept or reject decisions for each finding are in that session's main transcript alongside them.

**Isolation.** Resetting a working tree doesn't hide the answers: from any snapshot, `git log --all` reaches the
later commits that applied each review, the prototype branch holds the keys, earlier transcripts sit under
`~/.claude/projects/` (a folder the coach's role file tells it to read), and memory is shared between runs.
Catching reads afterwards and discarding runs would skew the sample if one condition explores more, so the user
decided (2026-09-25) to hide these paths entirely: each run's environment contains only what it needs. The coach's
role file points to `../agentpatterns`, so place the pinned agentpatterns checkout there relative to the clone;
don't check out the pinned commit in the shared `../agentpatterns`, which other agents use. The transcript check
stays as a backstop. The mechanism for a separate config directory (for example `CLAUDE_CONFIG_DIR`) and whether it
needs its own login are unverified; check them first, and set up any credentials before the session starts so
they never enter a transcript.

**Workspace trust.** Each run's clone is a new folder. `claude -p` doesn't grant workspace trust, and a project
plugin was skipped in an untrusted folder (T-0002's Context), and in `-p` mode the LSP tool may also need a
permission setting. That's why the LSP must be shown working inside a runner-built run before any pilot run
counts.

**The mechanism.** The claim is that irrelevant text in context lowers quality, so the context measures matter.
Tokens from pages opened but not cited is only a proxy: opening a page and deciding not to cite it is legitimate
review work, and the measure falls automatically with section reads. Describe its relation to the scores within
each task and condition, not pooled. The coach measured the 2026-09-25 reviews: peak context about 35K to 157K
tokens, with agentpatterns reads about 55 to 90% of tool-result text (approximate). That's inside the range where
research sees quality start to degrade, though newer models degrade later, so the effect may be small. If the
irrelevant share is small in both conditions, a quality null is "not measurable".

**Section reads can hurt quality.** The coach's role file says to read a page's "When this backfires" section
before citing it. An LSP-guided coach reading a single section may skip it, and pruning context too hard can
under-inform the model, which is why the gate checks backfire-section reads in both conditions.

**Rubric (proposed).** For each review: relevant findings (would the user act on it), correct citations (the cited
page says what the review claims), and noise (findings that don't apply). Rate each pair as LSP better, same, or
baseline better, per dimension. Pair run 1 with run 1, run 2 with run 2, and so on, within each review task.

**LSP instruction.** Word it as a capability, not as a way to save tokens: for example, "To find headings or
sections in Markdown, use the LSP tool's documentSymbol and workspaceSymbol." An efficiency framing ("save tokens",
"avoid reading whole pages") can lower quality by itself, whatever the tool does.

**False-negative risk: the corpus's structure.** agentpatterns may not be structured so that an LSP is materially
effective. Measured on 2026-09-25: 1,587 pages and 190,065 lines; lines per page median 112 (mean 120, range 24 to
1,825); headings per page median 10 (8 of them level 2); links to other pages median 9 per page, with 2 pages
having none. A median section is about a dozen lines, but a whole median page is only about 112, so reading an
outline plus one section may keep little text out of context. The coach also often knows a page's path already,
which grep or a direct read finds cheaply. The LSP's edge is more likely in heading search across pages and in long
pages.

**Cost measurement.** In Claude Code, most input tokens are the cached prompt re-sent each turn. An LSP that
replaces one whole-page read with several small calls lowers the tokens tools return but adds turns, which can
raise cost; that's why the guardrail checks both cost and tool-returned tokens. Alternating conditions keeps
prompt-cache warmth from favoring one side.

**Setup notes (unverified; record what worked in the Handoff):**

- **The coach and the LSP tool.** The coach's role file (`.claude/agents/coach.md`) doesn't list the LSP tool, and
  its constraints say not to loosen that file without the user's approval. Don't change it for the study; define
  the two study variants with `claude -p --agents <file>` (or an equivalent), keeping the coach's instructions and
  adding only the LSP tool and the instruction in the LSP condition. `--agent <name>` selects one.
- **Bash stays in both conditions,** as in the real coach, which reads pages with `cat`, `grep`, and `sed`. An
  isolated worktree session refuses to start a nested `claude` session that has Bash, so run the runner from a
  session that isn't worktree-isolated, or have the user run it.
- **Pointing rumdl at agentpatterns.** Options: the `.lsp.json` `workspaceFolder` field set to the pinned
  agentpatterns checkout, running the session with it as the project folder, or `--add-dir`. `--plugin-dir <path>`
  loads a plugin for one session only, which keeps the study's plugin out of the repo. T-0002's Context has the
  plugin layout that loaded in the 2026-09-25 spike, and T-0003's Context has how rumdl's LSP operations behave.
- **Measuring.** `claude -p --output-format json` reports `usage` (input, output, cache tokens), `num_turns`, and
  `total_cost_usd` for the session. Tokens per tool, peak context, and which sections were read come from the
  transcript.

Out of scope: the study runs themselves (T-0008), changing the coach's role file or `CLAUDE.md`, and building the
production plugin (T-0002).

## Handoff

Not started.

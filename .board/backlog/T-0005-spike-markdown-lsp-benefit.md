---
id: T-0005
title: "Spike: does a Markdown LSP make the coach's agentpatterns reviews better, without making them costlier?"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "A Claude Code session serves rumdl's LSP over the agentpatterns corpus (`/c/Users/User/Documents/projects/agentpatterns`), shown by raw `documentSymbol` and `workspaceSymbol` output for agentpatterns files; if that isn't possible, the Handoff shows why with evidence, and the remaining study criteria are recorded as not applicable"
  - "A runner script and a metrics script are committed on branch `prototype/T-0005-lsp-benefit` (pushed, kept, never merged): the runner sets up an isolated run, runs one coach review, and redacts its transcript; the metrics script computes every per-run measure below from the run's JSON output and transcript, so grading can be redone without new runs"
  - "Every run (pilot and study) happens in a fresh clone holding only its snapshot commit, with no other branches or tags, no remote, and no reflog, and with a Claude config directory of its own, so no earlier transcripts or memory are visible; the runner's output for each run shows `git rev-parse HEAD`, `git for-each-ref`, and `git remote`"
  - "A check over every run's transcript finds no command reaching other refs or remotes and no read under `~/.claude` or the original gol2 checkout; its output is in the evidence, and any run it flags is discarded and rerun"
  - "A pilot of at least two runs per condition on one review task is run before the workload is fixed; the Handoff records its cost and cost spread, the baseline's answer-key recall, LSP use, peak context, and an estimate of the user's rating time, and the pilot is excluded from the study data"
  - "Each answer key contains only findings the user accepted from the review it comes from, and the user confirmed each key before the first study run; the keys are committed (redacted) on the prototype branch"
  - "Before any study run, a workload file on the prototype branch fixes the review tasks (at least 3 snapshots with their answer keys), the agentpatterns commit, the prompt, the exact LSP instruction text, the two conditions, the number of runs, how runs are paired for rating, the quality rubric, how findings are matched to the key, the grader's calibration rule, the uptake rule, the effectiveness gate, the efficiency guardrail, and the smallest recall and cost differences the study can detect, derived from the pilot; the evidence gives its commit"
  - "The two conditions differ only in whether the coach has the LSP tool and the one-line LSP instruction; the model, Claude Code version, effort level, prompt, other tools (including Bash), review tasks, and agentpatterns commit are the same, and the evidence shows each configuration"
  - "Each review task is run at least 3 times per condition, alternating conditions run by run, and each run's agentpatterns commit is recorded and matches the workload file"
  - "Each run's `claude -p --output-format json` output and its redacted transcript (the user's email, secrets, and sandbox identifiers removed) are committed as files on the prototype branch"
  - 'The metrics script records, per run, the effectiveness scores (answer-key recall, off-key findings the user accepted and rejected, and citations that don''t say what the review claims), the context measures (peak context tokens, agentpatterns share of it, tokens from agentpatterns pages opened but not cited, and whether each cited page''s "When this backfires" section was read), and the efficiency measures (cost in USD, tokens by type, turns, tokens returned by each tool that read agentpatterns content including Bash and LSP, pages opened versus cited, whole-page versus section reads, and LSP calls)'
  - "The answer-key matching and citation checks are graded from the same redacted, condition-hidden outputs the user rates, by a grader whose judgments agreed with the user's on a sample the user graded first, per the calibration rule; the evidence records the sample and the agreement"
  - "The user rates each finding not in the answer key on its own merits before seeing the key, and then rates each pair of review outputs against the rubric, with the condition hidden, left/right order randomized, and mentions of LSP, symbols, or line anchors removed; the evidence records the ratings and how this was done"
  - "Every agentpatterns page cited in each review is checked to exist and to have been opened in that run by any tool, by a command whose output is in the evidence"
  - "The Handoff gives a separate verdict on each hypothesis (effectiveness: better, not better, or not measurable; efficiency guardrail: held or breached), reports every metric per review task and condition as a median with its range, and describes, within each task and condition, how tokens from pages opened but not cited relate to the effectiveness scores"
  - "The Handoff applies the uptake rule, the effectiveness gate, and the efficiency guardrail fixed in the workload file, and recommends go, no-go, or not tested for T-0002, as a screen rather than a ranking"
  - 'The Handoff describes the corpus''s structure (pages, lines per page, headings per page, links between pages) with the command that measured it, and, if effectiveness wasn''t shown to be better, states whether that structure, the context measures, or the study''s detection limits rather than the LSP could explain it; such a result is recorded as "not measurable" or "not shown on this corpus", not as "the LSP doesn''t help"'
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence: []
---

## Context

The user wants to know whether a Markdown LSP is worth adopting before building it (T-0002). gol2's own docs (11
files, about 520 lines) are too small to show a difference; the agentpatterns corpus the coach reviews against is
large enough, and T-0002 serves agentpatterns too, so a go here is a benefit T-0002 ships. A no-go is a valid
result. This task can run in parallel with T-0004. The result is a screen: a small number of runs can show a clear,
consistent difference, not rank close ones.

**The hypothesis.** When the coach performs a review using the Markdown LSP to navigate agentpatterns, it's more
effective, because irrelevant text stays out of its context, and it also uses fewer tokens. The user decided
(2026-09-25) that **effectiveness is the gate and efficiency is a guardrail**: the LSP is adopted only if reviews
get better, and only as long as they don't get costlier. Lower cost is reported but doesn't earn a go by itself.

**Effectiveness gate (proposed; fix it in the workload file before the first study run; the user may change the
numbers when approving this task, never after runs start).** Go requires all of these:

- Median answer-key recall is higher in the LSP condition in every review task, by at least 10 percentage points
  in at least half of them, and each gap is larger than the spread of the runs within each condition.
- In the user's blind pair ratings of relevant findings, the LSP is rated better in more pairs than the baseline.
- The LSP condition is not worse on incorrect citations, rejected findings (noise), or the share of cited pages
  whose "When this backfires" section was read.

**Efficiency guardrail (proposed, fixed the same way).** A breach, which is a no-go even if the gate passes, needs
both: in some review task, the LSP condition's median cost in USD or median tokens returned by agentpatterns-reading
tools is more than 10% higher than the baseline's, and that gap is larger than the spread of the runs within each
condition (the user's decision, 2026-09-25, matching how the gate treats noise).

**Uptake rule (proposed).** The LSP condition counts as tested only if the coach made at least one LSP call in at
least two thirds of its runs. Otherwise the result is "not tested", not no-go: agents often skip an optional tool.

**What the study can detect.** The keys have 7 to 10 accepted findings at most, so one finding moves recall by 10 to
14 points, and the gate effectively needs about two more findings in every task. Cost varies a lot from run to run
with the number of turns. The pilot estimates the cost spread and the baseline's recall; write the smallest
detectable recall and cost differences into the workload file before the study runs, and if the gate or guardrail
can't be met or tripped at that sample size, raise the runs or ask the user before starting.

**Measuring effectiveness.** The per-run scores against the answer keys (recall, noise, incorrect citations) are the
primary measure; the ordinal pair ratings back them up, since "same" is likely to be common across 9 to 12 pairs.
Fix how a review's finding matches a key finding in the workload file (for example, the same defect in the same
criterion).

**The grader.** The implementing agent is the same model family as the coach and can see which condition each run
used, so it doesn't grade blind by default. An agent grades from the redacted, condition-hidden outputs, after its
matching and citation judgments agree with the user's on a sample the user grades first (the user's decision,
2026-09-25). Fix the agreement rule (for example, the same match decision on at least 90% of findings in the sample)
in the workload file.

**Answer keys.** Built only from the findings the user accepted from each 2026-09-25 coach review, and confirmed by
the user before runs start. The keys come from reviews made without the LSP, and the user acted on them, so their
findings will look familiar; a valid finding that only an LSP run surfaces could look like noise. So the user rates
findings not in the key on their own merits before seeing the key, and those are reported separately from recall.
Review tasks, snapshots from before each review so there's something to find:

- T-0001 at commit `648d64a` (the first review: 7 findings, led by splitting the task).
- T-0004 at `f5f6bff` (9 findings).
- The set T-0001 to T-0004 at `c44ca0f` (10 findings).
- T-0005 at `ff794b4` (10 findings).

The coach's outputs aren't in the repo. They're in the subagent transcripts under
`~/.claude/projects/-c-Users-User-Documents-projects-gol2--claude-worktrees-board-rumdl-task/440265dc-29df-4a06-99dc-0fa759d9950d/subagents/`.
The user's accept or reject decisions for each finding are in that session's main transcript alongside them.

**Isolation.** Resetting a working tree doesn't hide the answers: from any snapshot, `git log --all` reaches the
later commits that applied each review (for example, `c44ca0f`'s diff is the key for the T-0004 snapshot), the
prototype branch holds the keys, earlier transcripts sit under `~/.claude/projects/` (a folder the coach's role file
tells it to read), and memory is shared between runs. So each run gets a fresh clone with only its snapshot commit
and a Claude config directory of its own, and a transcript check discards any run that reached other history or
`~/.claude`. Fresh clones also keep the study from resetting the shared main checkout, which other agents use. The
mechanism for a separate config directory (for example the `CLAUDE_CONFIG_DIR` environment variable) and whether it
needs its own login are unverified; check both in the pilot.

**Pinned corpus.** `../agentpatterns` is a clone of a site that releases often (HEAD was `86da49a`, "Release
v1.8.67", on 2026-09-24). A pull mid-study would change what pages say and which citations count as correct, so the
workload file fixes the commit and each run records it.

**The mechanism.** The claim is that irrelevant text in context lowers quality, so measure context too: peak
context, the agentpatterns share of it, and tokens from pages opened but not cited. That last measure is only a
proxy: opening a page and deciding not to cite it is legitimate review work, and the measure falls automatically
with section reads. So describe its relation to the scores within each task and condition, not pooled, and don't
treat it as proof. The coach measured the 2026-09-25 reviews that serve as answer keys: peak context about 35K to
157K tokens, with agentpatterns reads about 55 to 90% of tool-result text (approximate, from character counts).
That's inside the range where research sees quality start to degrade, though newer models degrade later, so the
effect may be small. If the irrelevant share is small in both conditions, a quality null is "not measurable".

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
effective, and the study could then show no benefit even if an LSP helps on larger or differently structured docs.
Measured on 2026-09-25: 1,587 pages and 190,065 lines; lines per page median 112 (mean 120, range 24 to 1,825);
headings per page median 10 (8 of them level 2); links to other pages median 9 per page, with 2 pages having none.
A median section is about a dozen lines, but a whole median page is only about 112, so reading an outline plus
one section may keep little text out of context compared with reading the page. The coach also often knows a
page's path already, which grep or a direct read finds cheaply. The LSP's edge is more likely in heading search
across pages and in long pages.

**Cost measurement.** In Claude Code, most input tokens are the cached prompt re-sent each turn. An LSP that
replaces one whole-page read with several small calls lowers the tokens tools return but adds turns, which can
raise cost; that's why the guardrail checks both cost and tool-returned tokens. Alternating conditions keeps
prompt-cache warmth from favoring one side.

**Budget.** The study costs dollars and the user's time: 12 or more pairs on 3 dimensions, plus the off-key
findings and the calibration sample. If the pilot's estimate of either looks larger than the decision is worth,
stop and ask the user before fixing the workload.

**Setup notes (unverified; record what worked in the Handoff):**

- **The coach and the LSP tool.** The coach's role file (`.claude/agents/coach.md`) doesn't list the LSP tool, and
  its constraints say not to loosen that file without the user's approval. Don't change it for the study; define
  the two study variants with `claude -p --agents <file>` (or an equivalent), keeping the coach's instructions and
  adding only the LSP tool and the instruction in the LSP condition. `--agent <name>` selects one.
- **Bash stays in both conditions,** as in the real coach, which reads pages with `cat`, `grep`, and `sed`. An
  isolated worktree session refuses to start a nested `claude` session that has Bash, so run the study from a
  session that isn't worktree-isolated, or have the user run the runner.
- **Pointing rumdl at agentpatterns.** The LSP server's workspace is normally the session's project folder.
  Options: the `.lsp.json` `workspaceFolder` field set to the pinned agentpatterns checkout; running the session
  with it as the project folder (it must be a trusted workspace); or `--add-dir`. `--plugin-dir <path>` loads a
  plugin for one session only, which keeps the study's plugin out of the repo. T-0002's Context has the plugin
  layout that loaded in the 2026-09-25 spike, and T-0003's Context has how rumdl's LSP operations behave.
- **Measuring.** `claude -p --output-format json` reports `usage` (input, output, cache tokens), `num_turns`, and
  `total_cost_usd` for the session. Tokens per tool, peak context, and which sections were read come from the
  transcript.

Out of scope: changing the coach's role file or `CLAUDE.md`, and building the production plugin (T-0002).

## Handoff

Not started.

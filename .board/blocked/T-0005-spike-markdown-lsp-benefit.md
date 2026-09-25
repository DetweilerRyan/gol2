---
id: T-0005
title: "Spike setup and pilot: Markdown LSP benefit study for the coach's agentpatterns reviews"
depends_on: [T-0006, T-0010]
claimed_by: claude-job-00fe2a0f
verified_by: null
acceptance:
  - "A runner script and a metrics script are committed on branch `prototype/T-0005-lsp-benefit` (pushed, kept, never merged): the runner builds an isolated environment, runs one coach review, and redacts its transcript; the metrics script computes every per-run measure in this file's Context from a run's JSON output and transcript, so grading can be redone without new runs"
  - "Each run the runner builds happens in an environment where the original gol2 checkout, the shared agentpatterns checkout, and `~/.claude/projects/` don't exist (for example a separate home directory or user, or a container), holding only a fresh clone of its snapshot commit (no other branches or tags, no remote, no reflog), a separate checkout of agentpatterns at commit `86da49a` at the `../agentpatterns` path relative to that clone, and a Claude config directory of its own; the runner's output for each run shows `git rev-parse HEAD`, `git for-each-ref`, and `git remote` for the clone, the agentpatterns commit, and a listing of the home directory; the runner refuses to start a run unless these conditions hold"
  - "Inside a run the runner built, the coach's LSP tool is listed and `documentSymbol` and `workspaceSymbol` calls on agentpatterns files return results, a Bash read of an agentpatterns page succeeds, and the hooks that ran are listed for each condition, shown by the raw output; if that can't be made to work, the Handoff shows why with evidence, the remaining criteria are recorded as not applicable, and, with the user's agreement, T-0008 moves to `dropped/`"
  - "A diff of the two conditions' agent definitions, and of the tool lists each pilot run started with, shows they differ only in the LSP tool and the one-line LSP instruction; the diff is in the evidence"
  - "A check over every run's transcript finds no command reaching other refs or remotes and no read outside the run's environment; its output is in the evidence"
  - "Before anything is pushed, a scan of the files to be committed for the user's email address, token and key patterns, and the sandbox name finds nothing, and its command and output are in the evidence; credentials a run needs are set up before its session starts"
  - "The study uses the answer keys T-0010 committed and the user confirmed, unchanged; the evidence gives their commit"
  - "A pilot of at least three runs per condition on one review task records in the Handoff: cost and its spread per condition, accepted findings and key recall of the baseline, LSP uptake, peak context and the agentpatterns share of it per condition, and an estimate of the user's rating time for the study; pilot runs are excluded from the study data"
  - "A workload file on the prototype branch fixes the review tasks (at least 3 snapshots with their answer keys), the agentpatterns commit, the prompt, the exact LSP instruction text, the two conditions, the number of runs, how runs are paired for rating, the rubric, how findings are matched to the key, the uptake rule, the effectiveness gate, the efficiency guardrail, and the smallest differences in accepted findings and in cost the study can detect, derived from the pilot; the evidence gives its commit"
  - "The Handoff states whether any pilot stop condition in this file's Context was hit, and if so the user decided whether to proceed before T-0008 leaves `backlog/`; it records the user's decision"
  - "The Handoff notes how the study coach differs from the real one, including user-level settings and plugins, the project's and the coach's hooks and the `node_modules/` they need, and the sandbox's parent `CLAUDE.md`"
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence: []
---

## Context

The user wants to know whether a Markdown LSP is worth adopting before building it (T-0002). This task builds the
study's isolated setup, confirms the LSP works inside it, runs a pilot, and fixes the
workload; T-0008 runs the study. The pilot's Handoff is the user's decision point before the expensive part. This
file is the home for the study's design; T-0008 points here. T-0004 (the freshness spike) runs only if T-0008 recommends go. Epic: T-0009.

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

**Effectiveness gate (approved by the user as proposed when approving this task, 2026-09-25; fix it in the
workload file before the first study run, and never change it after runs start).** Go requires all of these:

- The median number of accepted findings per run is higher in the LSP condition in every review task, by at least
  one finding in at least half of them, and each gap is larger than the spread of the runs within each condition.
- In the user's blind pair ratings of relevant findings, the LSP is rated better in more pairs than the baseline.
- The LSP condition is not worse on incorrect citations, rejected findings (noise), or the share of cited pages
  whose "When this backfires" section was read.

**Efficiency guardrail (approved as proposed, 2026-09-25; fixed the same way).** Outcomes: held, breached, or not measurable. A breach,
which is a no-go even if the gate passes, needs both: in some review task, the LSP condition's median cost in USD or
median tokens returned by agentpatterns-reading tools is more than 10% higher than the baseline's, and that gap is
larger than the spread of the runs within each condition. It's not measurable when the pilot shows the smallest
detectable cost difference at the planned number of runs is above 10%; run-to-run cost for the same setup varies by
about ×1.34, so at 3 runs "held" can be close to the default.

**Uptake rule (approved as proposed, 2026-09-25).** The LSP condition counts as tested only if the coach made at least one LSP call in at
least two thirds of its runs. Otherwise the result is "not tested", not no-go: agents often skip an optional tool.

**Pilot stop conditions.** Stop and ask the user before fixing the workload if any of these hold: LSP uptake in the
pilot is below the uptake rule; the baseline already finds so much that the gate's gain is out of reach; the
agentpatterns share of context isn't lower in the LSP condition; or the projected cost of the pilot and study
together is over $50, or the user's total grading and rating time over 3 hours (the user's limits, 2026-09-25).

**Per-run measures (computed by the metrics script):**

- Effectiveness: accepted findings (in the key and off-key), key recall (key findings matched divided by key
  size), rejected findings, and citations that don't say what the review claims.
- Context: peak context tokens, the agentpatterns share of it, tokens from agentpatterns pages opened but not cited,
  and whether each cited page's "When this backfires" section was read.
- Efficiency: cost in USD, tokens by type (input, output, cache write, cache read), turns, tokens returned by each
  tool that read agentpatterns content (Read, Grep, Glob, Bash, LSP), pages opened versus cited, whole-page versus
  section reads, and the number of LSP calls.

**What the study can detect.** The keys have 7 to 10 findings, and a review may add a few accepted off-key ones, so
one finding is a large step. Cost varies a lot from run to run with the number of turns. The pilot estimates both, from at least three runs per condition (a spread across two runs bounds nothing, and three
gives only a rough estimate, so label the derived limits as rough);
write the smallest detectable differences into the workload file, and if the gate or guardrail can't be met or
tripped at that sample size, raise the runs or ask the user.

**The grader.** A grader agent proposes answer-key matches and citation checks from the redacted,
condition-hidden outputs, and the user confirms every proposed match (at most one per key item per run), so a false
match can't reach the score unseen (the user's decision, 2026-09-25). A missed match is harmless, since the user
rates every off-key finding anyway. This replaces a separate calibration step; the confirmation time counts toward
the user's 3-hour limit.

**Answer keys.** Extracted, confirmed by the user, and committed by T-0010, from the findings the user accepted in
each 2026-09-25 coach review. The keys come from reviews made without the LSP, and the user acted on them, so their findings will look
familiar; that's why off-key findings are rated before the user sees the key. The reviews cited agentpatterns at
`86da49a` ("Release v1.8.67", 2026-09-24), which is why the study pins that commit. Review tasks, snapshots from
before each review so there's something to find:

- T-0001 at commit `648d64a` (the first review: 7 findings, led by splitting the task).
- T-0004 at `f5f6bff` (9 findings).
- The set T-0001 to T-0004 at `c44ca0f` (10 findings).

All three are about rumdl and the LSP, so the LSP condition may use the tool more because the topic invites it;
the Handoff notes this. A fourth review, of T-0005 at `ff794b4`, is excluded because that version describes the
study itself (the user's decision). When outputs are prepared for blind rating, remove only traces of tool use (LSP
calls, symbol listings, line-anchor citations), not mentions of the LSP as the topic under review.

Where the reviews came from and how the keys were built: T-0010's Context.

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

**Rubric (approved as proposed, 2026-09-25).** For each review: relevant findings (would the user act on it), correct citations (the cited
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
- **Hooks.** The coach's role file sets PreToolUse hooks that run `$CLAUDE_PROJECT_DIR/node_modules/.bin/tsx` and
  fail closed, and the project's `.claude/settings.json` hooks need the same `tsx`; plain `claude -p` loads them. A
  fresh clone has no `node_modules/`, so every Bash call could be blocked in both conditions. Either install
  `node_modules/` in each run's environment, or leave the hooks out of both conditions and say so in the Handoff.
  The runs also won't load the sandbox's parent `CLAUDE.md`, which the real coach loads.
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

**Blocked on the user's decision: the graded pilot hits stop conditions** (grading records and scores:
`study/T-0005/grading/pilot/` at `e7ad475`).

The skeptic panel agreed on 8 issues (real: I1 split the task, I2 worktrees lack `node_modules/`, I3 session
criteria name no command, I4 CLAUDE.md doesn't point to the new doc; not real: I11, I14, I16, I18). The user
settled the other 11: real I10 (question whether the LSP part is needed now) and I17 (protect the existing hooks),
not real the rest, overruling the panel's majority on I5 and I6. Six issues are verified. In stage 2 the user
confirmed every proposed key match except I10 (key 7 to no match); the verified issues cover key items 1, 2, and 5.

| Measure, median (range)                  | Baseline         | LSP, refined wording |
| ---------------------------------------- | ---------------- | -------------------- |
| Verified issues per run (main score)     | 5 (3-5)          | 3 (3-4)              |
| Unverified issues raised                 | 4 (2-5)          | 4 (2-6)              |
| Key recall (of 7)                        | 0.43 (0.29-0.43) | 0.43 (0.43-0.57)     |
| Issues the user would act on (old score) | 6 (6-10)         | 8 (5-9)              |

Stop conditions: **hit**: the gate's gain is out of reach on this task (6 verified issues exist and the baseline
median is 5, so the LSP condition would need all 6 in every run); **hit (projected)**: the user's time was about 47
minutes for one task's 6 runs (25 rating, 22 settling and matching), so 3 tasks plus pair ratings would pass the
3-hour limit. Not hit: uptake (3 of 3), the agentpatterns share (lower), cost (about $0.8 a run; $9.52 so far). The
pilot's direction also runs against the hypothesis: fewer verified issues with the LSP, the same key recall, the
same cost, and more than twice the turns. Three runs per condition give only a rough estimate.

Options for the user: (a) stop: record the result as "not shown" (pilot: no gain in verified issues or key recall,
and the gate is out of reach on this task) and move T-0008 to `dropped/`; (b) run the study anyway, with the
workload changed to fit the time limit (for example fewer tasks or no pair ratings) and the gate adjusted to the
ceiling; (c) something else the user names.

**Pilot grading (session 00fe2a0f, 2026-09-25).** Grading covers the 3 baseline runs and the 3 refined-LSP runs,
labelled R1 to R6 in shuffled order. Blind agents split each answer into findings and removed traces of tool use
(52 findings). Residual risk: LSP runs reported their own session's rumdl diagnostics and `workspaceSymbol`
results; those were reworded neutrally, but a few claims remain that a reviewer without the LSP would rarely make.
The user found 52 findings too many to judge ("they blend together"), so a blind agent grouped them into 19
distinct issues, a second agent checked the grouping (2 statements revised, 2 more non-findings excluded), and
the user rated each issue once; 6 findings propose no action and are excluded. Scoring counts distinct issues per
run, so a run can't score twice by repeating itself; how well a finding is argued is left to the pair ratings.
The user accepted 17 of 19 issues in 25 minutes and said: "i would act on almost all of the findings but that's
because i am not very familiar with the subject matter and the findings are generally persenting in ways that
sound confidant." Accepted issues per run: baseline 6, 6, 10; LSP 9, 8, 5 — nearly the same as issues raised, so
user acceptance measures how many plausible issues a review raises, not whether they're right.

**The user's third decision (same session): "option 1"** of three offered: replace user acceptance as the main
effectiveness score with evidence-checked issues. Three condition-blind skeptic agents (repo facts,
consequences, rules and reference) each try to refute every issue against the snapshot, the pinned agentpatterns,
and the pinned rumdl binary, without gol2's later history; an issue is verified when at least 2 of 3 find it
real, and the user settles every issue the panel doesn't agree on unanimously. The main score becomes verified
issues per run; key recall stays secondary.

**The user's second decision (session 00fe2a0f, 2026-09-25)**, answering options (a) and (b) below: "let's
refine the instructions to include telling coach to prefer reading sections via lsp and not through bash". The LSP
tool returns headings and start lines, not section text, so the refined wording has the coach locate sections with
the LSP and read them with the Read tool's offset and limit instead of Bash: "Before reading an agentpatterns page,
use the LSP tool's documentSymbol to see its sections, and workspaceSymbol to find headings across pages. Then read
only the sections you need with the Read tool's offset and limit, not through Bash (cat, sed, grep)." The LSP arm was
rerun with it (`57f4210`, runs `pilot3-T-0001-lsp-1` to `-3`, back to back). Median (range), against the same
baseline runs:

| Measure                             | Baseline          | LSP, refined wording |
| ----------------------------------- | ----------------- | -------------------- |
| Cost, USD                           | 0.78 (0.56-0.80)  | 0.80 (0.68-0.81)     |
| Turns                               | 13 (12-16)        | 33 (22-40)           |
| LSP calls                           | 0                 | 12 (4-14)            |
| Ranged Reads / Bash reads of pages  | 0 / most reads    | 10 (7-16) / 3 (2-5)  |
| Peak context, tokens                | 57K (43K-69K)     | 56K (53K-57K)        |
| agentpatterns share at peak         | 0.57 (0.55-0.72)  | 0.52 (0.50-0.53)     |
| agentpatterns tool tokens           | 32K (24K-49K)     | 28K (28K-30K)        |
| Pages opened / cited                | 16 / 10           | 9 / 9                |
| Opened-not-cited tokens             | 5.6K (5.4K-16.5K) | 0.6K (0-1.2K)        |
| Cited pages whose backfire was read | 0.78 (0.67-1.00)  | 1.00 (1.00-1.00)     |

Uptake 3 of 3. The agentpatterns share at peak is now below every baseline run, so that stop condition no longer
holds; the gap (0.05) is small next to the baseline's spread (0.55 to 0.72). Cost is about the same, with more than
twice the turns. The transcript check flagged only `git worktree list` (2). Spend $2.29; total so far $9.52.
Stop conditions not yet known: whether the gate's gain is within reach, and the user's rating time; both need the
pilot graded. Next step: grade the baseline and refined-LSP pilot runs against Key 1.

**The user's decision (session 00fe2a0f, 2026-09-25): option 2**, answering the options at the end with "2": test a
stronger instruction and rerun the pilot's LSP arm. New wording (now `lsp_instruction` in `tasks.json`; the first
wording is kept in `lsp_instruction_history`): "Before reading an agentpatterns page, use the LSP tool's
documentSymbol to see its sections, and workspaceSymbol to find headings across pages."

**Rerun of the LSP arm** (`c5f32ec`, runs `pilot2-T-0001-lsp-1` to `-3`, run back to back, not alternated with
baseline runs). Median (range), against the same baseline runs as the table below:

| Measure                             | Baseline          | LSP, new wording |
| ----------------------------------- | ----------------- | ---------------- |
| Cost, USD                           | 0.78 (0.56-0.80)  | 0.73 (0.70-1.24) |
| Turns                               | 13 (12-16)        | 24 (18-39)       |
| LSP calls                           | 0                 | 11 (1-18)        |
| Peak context, tokens                | 57K (43K-69K)     | 55K (53K-83K)    |
| agentpatterns share at peak         | 0.57 (0.55-0.72)  | 0.57 (0.55-0.57) |
| agentpatterns tool tokens           | 32K (24K-49K)     | 32K (29K-47K)    |
| Pages opened / cited                | 16 / 10           | 13 / 11          |
| Opened-not-cited tokens             | 5.6K (5.4K-16.5K) | 1.5K (0-6.4K)    |
| Cited pages whose backfire was read | 0.78 (0.67-1.00)  | 1.00 (0.64-1.00) |

Uptake 3 of 3 (calls: `documentSymbol` 10, 16, 1; `workspaceSymbol` 1, 2, 0), so the uptake rule is met. The
transcript check flagged only `git worktree list` (2). Rerun spend $2.67; total so far $7.23.

**Stop conditions after the rerun.** Still hit: the agentpatterns share of context isn't lower in the LSP condition
(0.57 in both). The coach reads fewer pages it doesn't cite, but uses the outline to pick sections it then reads
through Bash, so total agentpatterns text is about the same, with more turns. Not hit: uptake, projected cost.
Unknown until the pilot is graded: whether the gate's gain is within reach, and the rating time.

**Needs the user again.** Options: (a) proceed: grade the pilot (a grader agent proposes matches against Key 1,
you confirm, about 20 to 30 minutes for 6 runs), then fix the workload with the new wording, accepting that the
context mechanism wasn't shown in the pilot (the gate is effectiveness, which the pilot hasn't measured yet);
(b) stop: record "not shown" (the LSP didn't reduce the agentpatterns text in context) and drop T-0008.

**Was blocked on the user's decision: the pilot hit a stop condition.** The LSP condition made no LSP call in any of
its 3 pilot runs, below the uptake rule (at least two thirds). The workload file is not written, and T-0008 stays in
`backlog/`. Options are listed at the end.

Everything below is on `prototype/T-0005-lsp-benefit` (`45e9ccc` runner and setup runs, `dd1f423` pilot), under
`study/T-0005/`.

**Done.**

- `runner.sh` builds each run in a bubblewrap sandbox holding only `/study/gol2` (a fresh clone of the snapshot:
  one branch `main`, no tags, no remote, no reflog), `/study/agentpatterns` (a depth-1 checkout of `86da49a`, so
  `../agentpatterns` resolves), and `/study/home` with its own `CLAUDE_CONFIG_DIR`. `/c` (both host checkouts) and
  `/home` (so `~/.claude/projects/`) aren't mounted. `preflight.sh` runs inside the sandbox, prints `git rev-parse
HEAD`, `git for-each-ref`, `git remote`, the agentpatterns commit, and a home listing, and the runner refuses the
  run unless all 14 checks pass (shown working: a quoting bug failed one check and the run was refused).
- Credentials: the runner copies only the host's OAuth access token into the run's config directory before the
  session starts (no refresh token, so a run can never rotate the host login), refuses to start if the token
  expires within 2 hours, deletes it after the run, and redacts it from every output.
- `make_agents.mjs` builds both conditions from the snapshot's own `coach.md` (identical at all three snapshots and
  on `main`) and passes them with `--agents`/`--agent coach`. The only differences are the `LSP` tool and the
  instruction "To find headings or sections in Markdown, use the LSP tool's documentSymbol and workspaceSymbol.",
  placed after "Read a page, including its "When this backfires" section, before citing it." Session tool lists:
  baseline `Read, Edit, Write, Bash`; LSP `Read, Edit, Write, Bash, LSP` plus the `rumdl-lsp` plugin, loaded with
  `--plugin-dir` (no workspace-trust setup needed). `.lsp.json`'s `workspaceFolder` set to `/study/agentpatterns`
  makes `workspaceSymbol` search the corpus.
- Setup runs `runs/setup-lsp-1` and `runs/setup-baseline-1`: inside a runner-built run, `documentSymbol` and
  `workspaceSymbol` on agentpatterns returned results, a Bash `sed` of a page worked, and `--include-hook-events`
  shows the hooks that ran in both conditions: `UserPromptSubmit` (project), `PreToolUse:Bash` (the coach's push
  guard), and `Stop` (project).
- `metrics.py` computes the per-run measures from `out/`; effectiveness comes from a grades file (not yet
  exercised with real grades). Tokens per tool result are measured from context growth between API calls. Pages
  are recognized by content, so Bash, Read, and LSP reads count alike.
- `check_transcript.py` over the 6 pilot runs: 6 flags, all harmless: four `git worktree list` (the sandbox has
  one worktree) and two regex false positives (`/d` and `/backfires/` inside `sed` patterns).
- Redaction: every run's outputs were scanned before commit (0 hits; 69 files in the last commit).

**Pilot** (T-0001 review at `648d64a`, 3 runs per condition, alternating, Opus 5.5 at medium effort, Claude Code
2.1.282, 2026-09-25). Median (range):

| Measure                             | Baseline          | LSP condition      |
| ----------------------------------- | ----------------- | ------------------ |
| Cost, USD                           | 0.78 (0.56-0.80)  | 0.77 (0.57-0.93)   |
| Turns                               | 13 (12-16)        | 13 (11-16)         |
| LSP calls                           | 0                 | 0 (0-0)            |
| Peak context, tokens                | 57K (43K-69K)     | 69K (49K-77K)      |
| agentpatterns share at peak         | 0.57 (0.55-0.72)  | 0.67 (0.62-0.69)   |
| agentpatterns tool tokens           | 32K (24K-49K)     | 47K (30K-52K)      |
| Pages opened / cited                | 16 / 10           | 13 / 9             |
| Opened-not-cited tokens             | 5.6K (5.4K-16.5K) | 11.4K (9.4K-12.0K) |
| Cited pages whose backfire was read | 0.78 (0.67-1.00)  | 0.82 (0.75-0.86)   |

Every run succeeded in about 2 minutes. Pilot spend $4.40 (plus $0.16 of setup runs).

**Stop conditions.** Hit: LSP uptake 0 of 3, and (as a consequence) the agentpatterns share of context isn't lower
in the LSP condition. Not hit: projected cost (18 study runs at about $0.8 to $1.2 each, about $15 to $22, plus
$4.56 so far, is well under $50). Not yet known: the baseline's accepted findings and key recall, and the user's
rating time. The pilot runs aren't graded; grading needs the user, so it waits for the decision below. Rough
estimate of rating time: about 9 findings per run, 18 study runs, so about 160 findings to rate or confirm, around 1.5
to 2.5 hours, near the 3-hour limit.

**Found.**

- The coach navigates agentpatterns with `grep -n '^## '` and `sed -n` ranges through Bash, which already gets an
  outline and single sections; whole-page reads were 0 to 8 per run. That is the job the LSP instruction offers,
  so the coach has little reason to switch.
- In one LSP run the coach grepped the clone's `coach.md` for "LSP" and found nothing (the variant lives in
  `--agents`, not the file); a real adoption would change the file too.
- `workspaceSymbol` for a common heading returns everything: "When this backfires" matched 1,242 headings (132 KB),
  which Claude Code saved to a file instead of the context.
- All three review tasks are about rumdl and the LSP, so the topic may invite the tool; in the pilot it didn't.

**How the study coach differs from the real one.** It runs as the session's main agent (`--agent coach`), not as a
subagent of a main session; the prompt is the original reviews' prompt with paths changed to `/study/...` and the
branch sentence dropped. It has no user-level settings, memory, or plugins (only the built-in `agents-md` and
`telemetry`), and no parent `CLAUDE.md` (the sandbox's `../CLAUDE.md`). The project's and the coach's hooks run,
with the host's `node_modules/` mounted read-only. `Grep` and `Glob`, listed in the role file, aren't offered by this
Claude Code build in either condition; the original reviews used only Bash and Read. Permission mode is
`bypassPermissions` inside the sandbox.

**Needs the user: how to proceed** (the Context says to stop and ask before fixing the workload):

1. Record "not tested" and stop: T-0008 moves to `dropped/` with this pilot as the reason, recorded as "not shown",
   not "doesn't help".
2. Test a stronger instruction: for example, name the case where it applies ("Before reading an agentpatterns page,
   use documentSymbol to see its sections") and rerun the pilot's LSP arm (about $2.50). This changes what is
   tested: a directive, not an optional capability.
3. Rerun the pilot on another review task (T-0004 or the set) to check whether uptake depends on the task.

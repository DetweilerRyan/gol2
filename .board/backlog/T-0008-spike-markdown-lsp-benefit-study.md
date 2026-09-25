---
id: T-0008
title: "Spike study: does a Markdown LSP make the coach's agentpatterns reviews better, without making them costlier?"
depends_on: [T-0005]
claimed_by: null
verified_by: null
acceptance:
  - "Each review task in T-0005's workload file is run the fixed number of times per condition, alternating conditions run by run, every run built by T-0005's runner script in its isolated environment, with each run's agentpatterns commit matching the workload file"
  - "The transcript check finds no command reaching other refs or remotes and no read outside the run's environment in any run; any run it flags is discarded and rerun, and the evidence records the number discarded per condition"
  - "Each run's `claude -p --output-format json` output and its redacted transcript are committed on `prototype/T-0005-lsp-benefit` after the redaction scan finds nothing; the scan's command and output are in the evidence"
  - "T-0005's metrics script produces every per-run measure listed in T-0005's Context for every run, committed as a file on the prototype branch"
  - "The calibrated grader from T-0005 does the answer-key matching and citation checks from redacted, condition-hidden outputs"
  - "The user rates each finding not in the answer key on its own merits before seeing the key, and then rates each pair of review outputs against the rubric, with the condition hidden, left/right order randomized, and traces of tool use (LSP calls, symbol listings, line-anchor citations) removed without removing the topic under review; the evidence records the ratings and how this was done"
  - "Every agentpatterns page cited in each review is checked to exist and to have been opened in that run by any tool, by a command whose output is in the evidence"
  - "The Handoff gives a separate verdict on each hypothesis (effectiveness: better, not better, or not measurable; efficiency guardrail: held, breached, or not measurable), reports every measure per review task and condition as a median with its range, counting LSP-condition runs as assigned, with runs that used the LSP as a secondary result, and describes within each task and condition how tokens from pages opened but not cited relate to the effectiveness scores"
  - "The Handoff applies the uptake rule, the effectiveness gate, and the efficiency guardrail fixed in the workload file, and recommends go, no-go, or not tested for T-0002, as a screen rather than a ranking"
  - 'The Handoff describes the corpus''s structure (pages, lines per page, headings per page, links between pages) with the command that measured it, and, if effectiveness wasn''t shown to be better, states whether that structure, the context measures, or the study''s detection limits rather than the LSP could explain it; such a result is recorded as "not measurable" or "not shown on this corpus", not as "the LSP doesn''t help"'
  - 'If the recommendation is not tested, or effectiveness is not measurable, the user chose among rerunning with changes (as a new task), accepting a lighter bar, and dropping, and the Handoff records the choice; if the user hasn''t chosen, the default is to drop, recorded as "not shown", not "doesn''t help"'
  - "`npm run check` exits 0 on the branch that carries this task file"
evidence: []
---

## Context

Runs the benefit study that T-0005 set up and piloted. The design (hypothesis, gate, guardrail, uptake rule,
measures, rubric, answer keys, isolation) is in T-0005's Context, and the fixed rules are in the workload file on
`prototype/T-0005-lsp-benefit`; follow the workload file, and don't change any rule after the first run. This task
leaves `backlog/` only after the user has reviewed T-0005's pilot Handoff and decided to proceed. Its go
recommendation, together with T-0004's, decides T-0002. If the user decides not to proceed, or T-0005 shows the LSP
can't work in the study's setup, move this task to `dropped/` (T-0006) with the user's agreement. Epic: T-0009.

The user's time is part of the cost: rating the off-key findings and the pairs. T-0005's Handoff has the estimate.

Out of scope: changing the setup, scripts, or rules (reopen T-0005's work instead), and building the production
plugin (T-0002).

## Handoff

Not started.

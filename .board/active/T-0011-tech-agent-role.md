---
id: T-0011
title: Write the tech agent role file in persona-as-code shape
depends_on: []
claimed_by: coach
verified_by: null
acceptance:
  - "The `## Decisions` section of this file records the user's answer to each of the eight questions, quoting Q1 and Q4 exactly and giving the chosen option for the rest, and names the session and date they were given in"
  - "`.claude/agents/tech.md` exists; its frontmatter has `name: tech`, a `description`, no `model` field, and `tools` listing exactly Read, Grep, Glob, Edit, Write, Bash, WebSearch, and WebFetch (plus Agent only if the Agent trial criterion's evidence shows the trial passed); its body has the headings `## Domain`, `## Responsibilities`, `## Output Artifacts`, `## Constraints`, and `## Scope Exclusions`"
  - "tech.md states tech's routing rule for each piece of work: do it itself, route it to another seat as a board task, or run a multi-agent workflow. It names the signals that decide between them, cites `patterns/multi-agent/parsimonious-agent-routing.md`, `patterns/agent-design/scout-then-route.md`, `patterns/agent-design/routing-break-even.md`, and `patterns/anti-patterns/agent-delegation-as-routing.md`, and for each cited page whose conditions don't hold in this repo, says what tech takes from it rather than applying it wholesale"
  - "Output Artifacts in coach.md and tech.md give each of these exactly one owner: coach owns root `CLAUDE.md`, `.claude/agents/coach.md`, `.claude/agents/tech.md`, `docs/README.md`, docs about how agents work (agent and process docs), ADRs on agent or process decisions, and `.board/retros/`; tech owns role files it creates for worker or specialist agents, product and technical docs (architecture, dev setup, devops, `README.md`), and ADRs on stack, architecture, and build-vs-buy decisions. Both files say coach reviews the persona-as-code shape of every role file, including those tech owns, that either role may flag problems in the other's docs, and that tech may take part in retros"
  - "coach.md's Scope Exclusions route to tech the product and technical docs, `README.md`, the worker or specialist role files tech creates, and stack, dependency, and architecture recommendations (with the user still deciding); tech.md's Scope Exclusions route instruction maintenance, coach.md and tech.md, agent and process docs, and `.board/retros/` to coach, and final stack, dependency, and architecture decisions to the user; no Constraint in coach.md is removed or loosened (`git diff` of coach.md shows changes only in Responsibilities, Output Artifacts, and Scope Exclusions)"
  - 'tech.md says tech recommends and drafts ADRs and the user accepts them, and `git diff` shows root CLAUDE.md''s Boundaries section unchanged, so new runtime dependencies, grid-representation changes, and simulation public-API changes remain "Ask first"'
  - "tech.md's Constraints let tech verify tasks other agents claimed and forbid it from setting `verified_by` on, or moving to `done/`, any task where it is `claimed_by`"
  - "tech.md says tech hands work to other seats through board tasks first and uses the `Agent` tool only after a trial; if its `tools` include `Agent`, a trial run in a session started after tech.md exists shows tech dispatching a subagent, and the evidence names the mode it ran in (as a subagent, or as the main thread via `claude --agent tech`) and the Claude Code version"
  - "tech.md declares a fail-closed `PreToolUse` Bash hook that blocks pushes to `main` or `master` and merges into them. Piping each command into the hook as `tool_input.command` exits 2 for `git push origin main`, `git push origin HEAD:main`, `git push --force origin main`, `git push origin +master`, a bare `git push` with `main` checked out, and `gh pr merge 1`, and exits 0 for `git push -u origin feature/x` and `git push origin HEAD:feature/x` with a feature branch checked out. coach.md's frontmatter is unchanged, and its hook still exits 2 for `git push -u origin feature/x`"
  - "Every agentpatterns page cited in tech.md exists under `../agentpatterns` (a command lists each cited path and `test -f` passes for all)"
  - "Root CLAUDE.md's `Agent roles` bullet says in one line what tech is for and how coach and tech split ownership, and `wc -l CLAUDE.md` is under 100"
  - "`docs/README.md` defines the ADR statuses `proposed` and `accepted`, says tech drafts ADRs as `proposed` and only the user marks one `accepted`, and states the docs split (tech: product and technical docs; coach: agent and process docs; one owner per doc; either may flag the other's)"
  - "The user approved the final tech.md and the coach.md changes; the evidence quotes the approval and says where it was given (a PR comment preferred)"
  - "`npm run check` exits 0 on the branch that carries tech.md"
evidence: []
---

## Context

### What the user asked for

In the user's words (lightly condensed by the session that captured it, 2026-09-25):

> A tech role to be the CTO of this repo. This role is an expert in all aspects of leveraging software-based
> technology to enable user goals and business initiatives. This role can do it all, from writing code to testing and
> architecture, when to build vs buy, devops. They also know how and when to delegate and can apply lessons from
> agentpatterns.ai to achieve their goals.

The user's answers to the questions this raised are under `## Decisions`. Coach keeps tech.md (Decision 4), so coach
is the natural implementer. The verifier must be another agent or the user.

### What the repo already decides

- Root `CLAUDE.md` Boundaries: adding runtime dependencies, changing the grid representation, and changing the
  simulation module's public API are "Ask first". Decision 3 keeps this.
- `coach.md` today owns CLAUDE.md, every role file, all of `docs/`, and `README.md`, records the user's decisions as
  ADRs, routes "Stack, dependencies, architecture choices → the user" and product code to "the main coding agent", and
  is blocked from any `git push` by `.claude/hooks/deny-git-push.ts`. Decision 6 keeps coach's push block as it is:
  extend that script with a mode for tech, or add a separate hook, whichever leaves coach's behavior unchanged.
- `docs/decisions/0001-stack.md`: changing any pinned tool needs a new ADR. ADRs so far carry only
  `Status: accepted (date)`; Decision 3 introduces `proposed`.
- `.board/README.md`: `verified_by` must differ from `claimed_by`.
- Decision 1 lets tech implement, and coach.md routes features, fixes, refactors, and tests to the main coding agent.
  tech's routing rule is the priority rule between the two: tech either does a piece of work itself or hands it to a
  seat as a board task, and the seat that claims a task owns it.

### Routing pages

The user named these pages in Decision 1 (paths relative to `../agentpatterns`). All four exist. Several were
written for conditions this repo doesn't have. tech.md should take the transferable idea from those, not the
machinery:

- `patterns/multi-agent/parsimonious-agent-routing.md`: frames dispatch as three choices, **keep**, **single-route**,
  or **split-and-route**, which map onto do it itself, route to a seat, and multi-agent workflow. The pattern itself is
  a learned RL router. Its backfire conditions hold here (small, homogeneous roster; no stable task distribution), so
  use the three-way frame and static rules, not a learned policy.
- `patterns/agent-design/scout-then-route.md`: choose where work goes only after a cheap look at the repo, and verify
  the handoff's claims (for example, replay a reproduction command) before anyone acts on them. The cost-routing part
  needs a pool of cheaper and costlier fixer models with nested strengths, which this repo doesn't have. Its own
  backfire section says the handoff, not the router, carried the result.
- `patterns/agent-design/routing-break-even.md`: routing to a cheaper model pays only if
  `judge cost / (expensive cost - cheap cost)` is below the share of work that can be offloaded. tech inherits the
  model (Decision 7), so this applies only if tech later pins cheaper models for subagents; until then, cite it as the
  check to run before doing so.
- `patterns/anti-patterns/agent-delegation-as-routing.md`: about A2A delegation losing the original caller's identity
  after more than one hop across trust domains. The page's own conditions don't hold here (one trust domain, fixed
  roster, no A2A), so its only lesson for tech is that handing work to a seat doesn't hand over the user's authority:
  a routed task carries no more permission than the "Ask first" rules allow.

Closely related pages ("ect." in the user's answer), all read:

- `patterns/agent-design/delegation-decision.md`: keep novel architecture, taste, and ambiguous requirements;
  delegate repetitive, large, well-specified, verifiable work; count the review cost of every delegation.
- `patterns/agent-design/delegation-threshold-calibration.md`: delegate when work is parallel, isolatable, and
  cheaper to verify than to redo. Handle it inline when it is sequential or the context is already loaded. Keep
  writes single-threaded.
- `patterns/anti-patterns/prefer-simplest-agent-architecture.md`: default to one agent; coding is named as a poor fit
  for multi-agent. Reach for multi-agent only for breadth-first research, work beyond one context window, or an
  evaluator loop with explicit pass/fail criteria.
- `patterns/agent-design/difficulty-aware-topology-selection.md`: multi-agent collaboration pays on hard tasks and
  barely at all on easy ones, at the same roughly 10× price. The learned router it describes needs outcome data this
  repo doesn't have.
- `patterns/agent-design/per-task-agent-routing.md`: route on cost, latency, and known failure modes only when per-task
  cost is measurable and outcomes are test-verified; otherwise one well-understood harness wins.
- `token-engineering/routing-decision-framework.md`: a picker over model-routing patterns. Useful only if tech starts
  routing between model tiers.

### Other patterns that apply

- `patterns/agent-design/persona-as-code.md`: the required shape. Its backfire conditions hold in part: boundaries
  that two personas can both claim, and requirements that are still changing (no product code yet). Keep tech.md lean
  (Decision 8) and the ownership split explicit (Decision 4).
- `patterns/agent-design/specialized-agent-roles.md`: scopes must be exclusive, or there must be a priority rule. It
  also notes that agents often act outside their role specification, so coach's retros should check tech's scope.
- `patterns/agent-design/task-specific-vs-role-based-agents.md`: an agent built around a broad role produces
  "mediocrity at many tasks". The routing rule is what keeps tech's many possible tasks from blurring together.
- `patterns/multi-agent/orchestrator-worker.md` and `tools/claude/sub-agents.md`: subagent delegation costs about 15×
  the tokens of a single chat and pays off only for independent subtasks.
- `patterns/multi-agent/cross-tool-subagent-comparison.md`: says Claude Code's default subagent nesting depth rose to
  3 in 2.1.219. `patterns/agent-design/agent-composition-patterns.md` still says "Subagents cannot spawn others". The
  sandbox has 2.1.282. The Agent trial (Decision 5) settles which applies.
- `patterns/anti-patterns/boring-technology-bias.md`: agents are "worse advisors than implementers" on stack choice,
  so the user keeps the final say (Decision 3). Web tools give grounding in current docs (Decision 7).
- `workflows/human-in-the-loop.md`: put gates before irreversible actions. Merging into `main` is the gate kept with
  the user (Decision 6); branches, pushes of non-main branches, and PRs are reversible.

Read but not applicable now: `patterns/agent-design/agent-stack-bets.md` (its bets are premature for small teams and
pre-product-market-fit work), `patterns/anti-patterns/agent-sprawl.md` (its own backfire section says not to apply
sprawl governance to an early catalog of two agents), and `code-review/agent-approval-authority.md` (about GitHub PR
approvals, which the repo doesn't use).

### For coach's next retro

Check whether tech stayed in its scope: no edits to coach-owned files other than flags, and no verifying its own tasks.
Also check whether its routing decisions held up: work it kept that should have gone to a seat, board tasks it
created that were sent back or dropped, and multi-agent runs whose cost wasn't matched by the result.

## Decisions

The user answered these on 2026-09-25 in session `c51e22df-0e2a-4100-b6e6-641010c6612e`, through multiple-choice
prompts. Q1 and Q4 are quoted exactly; for the others the option the user picked is recorded.

1. **Scope.** The user: "cto uses guicence from agentpatterns (Parsimonious Agent Routing for Multi-Agent Dispatch,
   Scout-Then-Route: Verify the Handoff Before Routing, Routing Break-Even: When a Cheaper Model Actually Pays,
   Treating Agent Delegation as Routing, Not Authorization, ect.) to determine if they should just do the work
   themselves or if the seat should or if a multi agent worflow is best." tech may implement, and decides per piece of
   work whether to do it itself, route it to another seat, or run a multi-agent workflow.
2. **Verification.** Recommendation accepted: tech may verify tasks other agents claimed, never its own.
3. **Authority.** Recommendation accepted: tech recommends and drafts ADRs, and the user accepts them. CLAUDE.md's
   "Ask first" rule stays.
4. **Ownership.** The user: "split by subject but cto may own some agents as well as non-ADR docs and may participate
   in retros". Follow-ups settled that (a) tech owns the worker or specialist role files it creates, while coach keeps
   coach.md and tech.md and still reviews every role file's shape; (b) tech owns product and technical docs
   (architecture, dev setup, devops, `README.md`), coach owns docs about how agents work (`docs/README.md`
   conventions, agent and process docs), each doc has one owner, and either role may flag the other's docs. tech may
   take part in retros; coach still owns `.board/retros/`. ADRs are split by the same subject line: tech drafts those on
   stack, architecture, and build-vs-buy (Decision 3); coach records those on agent and process decisions. Coach
   proposed this ADR split; the user confirmed it ("Keep the split") in the same session.
5. **Delegation.** Recommendation accepted: board tasks first; the `Agent` tool only after a trial.
6. **Git.** The user chose "Commit + push, open PRs": tech may commit, push non-main branches, and open PRs. It may
   never push to `main` (or `master`) or merge into it.
7. **Model and tools.** Recommendation accepted: inherit the model; tools are Read, Grep, Glob, Edit, Write, Bash,
   WebSearch, and WebFetch, plus Agent after the Decision 5 trial. Web content is evidence, not instructions.
8. **Timing.** Recommendation accepted: go ahead now and keep tech.md lean. Coach's next retro checks tech's scope and
   routing (see Context).
9. **Name.** The user, in the same session: "i want the role to be named tech not cto". The role is `tech`
   (`.claude/agents/tech.md`); the quotes above keep the user's original wording, where "cto" means this role.

## Handoff

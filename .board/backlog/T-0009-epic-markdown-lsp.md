---
id: T-0009
title: "Epic: Markdown LSP for agents (rumdl)"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "Every task listed under Tasks below is in `done/` or `dropped/`"
  - "The Outcome section records whether rumdl was adopted, and links the Handoffs that decided it"
evidence: []
---

## Context

Tracks the tasks split out of the original T-0001 ("replace markdownlint-cli2 with rumdl") after the research and
coach reviews of 2026-09-25, and how they depend on each other. The goal: let agents navigate Markdown (gol2's docs
and the agentpatterns corpus the coach reviews against) through Claude Code's LSP tool, reading only the sections
they need, with rumdl as the server; adopt it only if it keeps results fresh and makes the coach's reviews better
without making them costlier. If it is adopted, rumdl also replaces markdownlint-cli2 as the gate's Markdown
linter, so agents and the gate see the same diagnostics.

The board has no epic type yet, so this is an ordinary task. Its `depends_on` is left empty on purpose: under
T-0006's rule, a task that depends on a dropped task can't leave `backlog/`, and this epic must be able to close
when some of its tasks are dropped. The board check doesn't enforce this map; keep it current by hand whenever a
task is added, split, or dropped.

## Tasks

| Task   | What it does                                                                                                        | Depends on     | Decides                                        |
| ------ | ------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------------------------------- |
| T-0004 | Spike: can a relay keep rumdl's LSP results fresh after shell and git changes?                                      | none           | go or no-go for T-0007 and everything after it |
| T-0005 | Spike setup and pilot for the benefit study: isolated runner, LSP working, pilot, calibrated grader, fixed workload | none           | the user decides whether T-0008 runs           |
| T-0008 | Spike study: are the coach's agentpatterns reviews better with the LSP, without being costlier?                     | T-0005         | go or no-go for T-0002 and everything after it |
| T-0006 | Adds a terminal `dropped/` lane to the board                                                                        | none           | where no-go tasks end up                       |
| T-0002 | In-repo plugin running rumdl's LSP for gol2 and agentpatterns                                                       | T-0004, T-0008 |                                                |
| T-0007 | Production relay (TypeScript/Node) keeping LSP results fresh                                                        | T-0002         |                                                |
| T-0001 | Replace markdownlint-cli2 with rumdl in the gate                                                                    | T-0007         |                                                |
| T-0003 | `docs/tools/` doc and `CLAUDE.md` pointer for agents                                                                | T-0007         |                                                |

```text
T-0004 (freshness spike) ─────────────────┐
                                          ├─> T-0002 (plugin) ─> T-0007 (relay) ─┬─> T-0001 (linter swap)
T-0005 (setup, pilot) ─> T-0008 (study) ──┘
                                                                                 └─> T-0003 (docs)
T-0006 (dropped/ lane)
```

## Decision points

- **After T-0005's pilot:** the user decides whether to run T-0008. If not, T-0008, T-0002, T-0007, T-0001, and
  T-0003 move to `dropped/`.
- **After T-0004 and T-0008:** both must recommend go for T-0002 to start. Either no-go drops T-0002, T-0007,
  T-0001, and T-0003.
- **Before merging T-0002 and T-0007:** the user approves each final commit, since both add executable config.

T-0006 should be done before any task needs to be dropped.

## Outcome

Not decided.

# Board

File-based kanban for agent task management. **The folder a task file sits in is its status**; there is no status
field to drift out of sync. Move tasks with `git mv` (plain `mv` before a file's first commit). `npm run check:board` enforces the rules below.

## Lanes

| Lane       | Meaning                                               | Who moves it in                     |
| ---------- | ----------------------------------------------------- | ----------------------------------- |
| `backlog/` | Captured, not yet specified                           | anyone                              |
| `ready/`   | Acceptance criteria written; dependencies in `done/`  | whoever specifies it                |
| `active/`  | Claimed and being worked on                           | the agent claiming it               |
| `blocked/` | Can't proceed; the body says why and what unblocks it | the claiming agent                  |
| `review/`  | Work finished; waiting for verification               | the claiming agent                  |
| `done/`    | Every acceptance criterion verified, with evidence    | the verifier, never the implementer |
| `retros/`  | Retrospectives by the coach agent (`YYYY-MM-DD.md`)   | coach                               |

## Rules

- **WIP = 1 per agent.** An agent has at most one task in `active/` or `blocked/` at a time. A blocked task still
  holds the slot; finish or hand it off before claiming another.
- **Claiming:** set `claimed_by: <agent-name>` and move the file from `ready/` to `active/` in the same change.
  `claimed_by` stays set through `review/` and `done/`, so the record shows who did the work.
- **Done means verified:** a task enters `done/` only when every acceptance criterion has an `evidence` entry
  (`criterion` copied exactly, the `command` run, and its `result`), and `verified_by` names an agent other than
  `claimed_by`. Names are self-declared, so this records separation of duties rather than proving it.
- **Handoff:** when a task leaves `active/`, update its `## Handoff` section: what was done, what was found,
  what needs attention, what's unresolved. Summarize; don't paste transcripts.
- **Dependencies:** `depends_on` lists task ids. A task isn't `ready/` until all of them are in `done/`.

## Task file

Name: `<id>-<slug>.md`, for example `T-0001-step-function.md`. Ids are `T-` plus four digits and never reused.

```markdown
---
id: T-0001
title: Pure step function for a finite grid
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "`npm test` covers blinker, block, and glider and passes"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Why this task exists and anything the implementer needs that the repo doesn't show.

## Handoff

Done / found / needs attention / unresolved.
```

Each `evidence` entry is `{ criterion, command, result }`, all non-empty; `criterion` must match an acceptance
criterion exactly. `verified_by` is set only in `done/`. A test-only criterion should name the behavior it checks,
not just "tests pass", so deleting tests can't satisfy it.

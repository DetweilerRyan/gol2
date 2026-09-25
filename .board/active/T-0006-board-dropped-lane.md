---
id: T-0006
title: Add a terminal dropped/ lane to the board
depends_on: []
claimed_by: claude-job-ef3b791f
verified_by: null
acceptance:
  - "`.board/README.md` lists a `dropped/` lane: a terminal lane for tasks that won't be done, moved in by the user or with the user's agreement, whose body has a `## Dropped` section saying why and linking the task, evidence, or decision that settled it"
  - "`npm run check:board` fails for a task in `dropped/` without a non-empty `## Dropped` section and passes once one is added, shown by a single evidence command that creates the task file, runs the check twice, and deletes the file"
  - "`npm run check:board` fails for a task in `ready/`, `active/`, `blocked/`, or `review/` that depends on a task in `dropped/`, shown by a single evidence command that creates the files, runs the check, and deletes them"
  - "`npm run check:board` does not require `verified_by` or evidence for tasks in `dropped/`, and rejects `verified_by` on them"
  - "`.board/README.md` documents two evidence conventions: for a conditional criterion that didn't apply, `command` is the check that showed it and `result` starts with `not applicable:` and says why; for a criterion met by the user's decision or judgment, `command` says where the decision is recorded (for example a PR comment or conversation) and `result` quotes it"
  - "`npm run check` exits 0"
evidence: []
---

## Context

T-0001, T-0002, T-0003, and T-0007 are dropped if the spikes T-0004 or T-0008 recommend no-go, T-0004 is dropped if
T-0008 doesn't recommend go, and T-0008 is dropped if the user decides not to proceed after T-0005's pilot. The board has no
lane for that: `done/` needs evidence for every criterion, and deleting the task file loses the record of what was
planned and why it stopped. A `dropped/` lane keeps the task and its verdict.

`scripts/check-board.ts` validates lanes, frontmatter, WIP, and dependencies; it rejects unknown top-level entries
in `.board/`, so the new lane must be added to its `LANES` list. A task that depends on a dropped task can't
proceed, so it should stay in `backlog/` or be dropped too. `claimed_by` may or may not be set on a dropped task,
depending on whether work had started.

The evidence conventions come from the rumdl tasks (T-0004, T-0005, T-0008), which have conditional criteria and
criteria met by the user's decisions; the board's `{ criterion, command, result }` format assumes a command.

A separate gap the 2026-09-25 reviews found, not part of this task: the board has no lane for "fully specified,
waiting for the user's approval"; `backlog/` means "captured, not yet specified". That's for the retro on that
session.

Epic: T-0009.

## Handoff

Not started.

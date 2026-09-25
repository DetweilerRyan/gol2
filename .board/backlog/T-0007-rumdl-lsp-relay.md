---
id: T-0007
title: Keep rumdl's LSP results fresh with a relay between Claude Code and rumdl
depends_on: [T-0002]
claimed_by: null
verified_by: null
acceptance:
  - "The plugin from T-0002 starts a relay written in TypeScript/Node instead of starting rumdl directly, and the relay implements the mechanism named in T-0004's Handoff"
  - "The relay adds no new runtime dependency, or the user approved each one it adds, and the evidence says where"
  - "The ADR from T-0002 records that the relay works around Claude Code rejecting rumdl's `workspace/didChangeWatchedFiles` registration, and states the removal condition: once Claude Code accepts that registration, delete the relay and start rumdl directly; it names the check that shows whether Claude Code accepts it"
  - "In a single Claude Code session in a worktree, after each change route T-0004 tested (Write tool, Edit tool, shell edit to a queried file, shell edit to an unqueried file, file created from the shell, `git mv`, `git rm`, `git checkout` of different content, and a switch to a branch whose Markdown differs), `documentSymbol`, `workspaceSymbol`, `goToDefinition`, and `findReferences` reflect the change; the raw LSP tool output is committed to the task's evidence as files, summarized in a route × operation table"
  - "The Handoff records whether changes the user makes on the host are reflected, with the command and output; if they aren't, or the user wasn't available, it lists that as a known limitation for T-0003's doc"
  - "The four T-0002 operation criteria still pass in a main-checkout session and a worktree session with the relay in place; the evidence has the raw output"
  - "The user merged the task's PR after reviewing it; agents opened it but didn't merge it, shown by `gh pr view <number> --json state,mergedAt` and the user's confirmation, recorded after the merge"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Without a relay, rumdl's LSP results go stale after shell and git changes, because Claude Code rejects rumdl's
request to be told about file changes and never re-syncs files it didn't change itself. T-0004 (the spike) holds
the findings, the test harness, and the mechanism to build; this task reimplements that mechanism for production
rather than copying the prototype on `prototype/T-0004-lsp-relay`. If T-0004 recommends no-go, move this task to
`dropped/` (T-0006).

- **Language.** TypeScript/Node, which gol2 already uses, so no new toolchain for a temporary workaround (the
  user's decision on 2026-09-25). How to start Node and find the pinned rumdl from a worktree session: see
  T-0002's Context.
- **Temporary by design.** The relay exists only because of the Claude Code gap. The removal condition goes in the
  ADR, not in feature flags.
- **Who runs the main-checkout sessions.** See T-0002's Context.
- **Merging.** The relay is executable config that runs in every session. Agents act on GitHub as the user's
  account, so a PR review can't show that the user approved; the user reviews and merges the PR, and agents never
  merge it.
- **Host edits.** Host-side changes don't decide go (T-0004's rule); if they stay stale, T-0003's doc says so.

Out of scope: the plugin itself (T-0002), changing rumdl or Claude Code.

Epic: T-0009.

## Handoff

Not started.

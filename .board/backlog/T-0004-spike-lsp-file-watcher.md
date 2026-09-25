---
id: T-0004
title: "Spike: can a relay alongside rumdl keep its LSP results fresh in Claude Code?"
depends_on: [T-0008]
claimed_by: null
verified_by: null
acceptance:
  - "The Handoff states whether inotify events fire on the repo's virtiofs mount for Markdown changes made inside the sandbox, with the command used and its output"
  - "The Handoff states whether inotify events fire on the mount for Markdown changes the user makes on the host, with the command and output; if the user isn't available when the step is reached, the Handoff records host-side changes as untested and the task continues"
  - "If inotify doesn't fire for sandbox changes, the Handoff states whether polling the disk (for example comparing modification times) detects them, with the command and output"
  - "Unless the Handoff shows with evidence that no method detects Markdown changes on the mount, a prototype relay runs between Claude Code and rumdl, and its source is on a separate branch `prototype/T-0004-lsp-relay` that is pushed, kept, and never merged; the evidence gives the branch and commit"
  - "Unless no method detects changes, the relay is tested first sending rumdl only `workspace/didChangeWatchedFiles`, and, if any route stays stale that way, also re-sending the current text of files Claude Code already opened (for example as `textDocument/didChange`); the Handoff reports each mechanism separately"
  - "Unless no method detects changes, one Claude Code session per condition (no relay, then each mechanism tested) runs `documentSymbol`, `workspaceSymbol`, `goToDefinition`, and `findReferences` after each change route: Write tool, Edit tool, shell edit to a queried file, shell edit to an unqueried file, file created from the shell, `git mv`, `git rm`, `git checkout` of different content, and a switch to a branch whose Markdown differs; the raw LSP tool output and relay traffic log of each session are committed as files on the prototype branch"
  - "The evidence gives, for each condition, a table of change route × operation × fresh or stale, pointing to the raw log files by path and commit, and records the Claude Code and rumdl versions used"
  - "The Handoff recommends go only if one mechanism kept every change route above fresh for all four operations in a single session, and no-go otherwise; host-side edits don't decide it but are listed as a known limitation if stale"
  - "The Handoff names the mechanism T-0007 should reimplement if go, and lists what it would cost to maintain (for example dependencies and failure modes)"
  - "`npm run check` exits 0 on the task's branch"
evidence: []
---

## Context

The user wants rumdl only if its LSP plugin works (T-0002), and a test on 2026-09-25 found that its results go
stale. This spike answers one question before any of it lands: can any relay between Claude Code and rumdl keep
rumdl's LSP results fresh? A no-go is a valid result; the go rule is the acceptance criterion above, which matches
T-0007's freshness criterion. It runs only after the benefit study (T-0008) recommends go (the user's decision,
2026-09-25): keeping results fresh only matters if the LSP is worth adopting, so it isn't worth testing first. If
T-0008 doesn't recommend go, move this task to `dropped/` with the user's agreement. This file is the home for the
freshness findings and the test harness; other tasks point here.

**Branches.** The task file, its Handoff, and its evidence move through the lanes on the task's own branch, which
merges to main like any task. The prototype relay and the raw logs go only on `prototype/T-0004-lsp-relay`, which
is pushed and kept for reference but never merged. T-0007 reimplements the chosen mechanism in TypeScript/Node
rather than copying the prototype; the prototype can be in any language.

**Criteria that don't apply.** The board needs an evidence entry for every criterion. When a conditional criterion
doesn't apply (for example, no method detects changes), its entry's `command` is the check that showed that and
its `result` starts with "not applicable:" and says why.

What the 2026-09-25 test found (Claude Code 2.1.282, rumdl 0.2.77, a gitignored worktree):

- **Write and Edit stay fresh.** After each tool use, Claude Code sent rumdl `textDocument/didChange` with the full
  text, then `didSave`, and the next `documentSymbol` and `workspaceSymbol` showed the change.
- **Shell and git changes don't.** After `sed -i` on a queried file, a new file from the shell, a shell edit to a
  not-yet-queried file, and `git mv`, the LSP kept answering from what it had first read. The index kept a
  deleted file.
- **Why.** rumdl has no file watcher of its own in LSP mode. It asks the client to watch `**/*.md` through
  `client/registerCapability` for `workspace/didChangeWatchedFiles`, and Claude Code replies
  `Unhandled method client/registerCapability`. Claude Code sends `didOpen` once per file, on first query, and
  never re-syncs a file it didn't change itself. rumdl caches a file read from disk (`get_document_content` in
  `src/lsp/server.rs`), so that copy goes stale too.
- **What might work.** rumdl's `did_change_watched_files` handler updates the workspace index for Markdown files
  that are created, changed, or deleted; a source comment mentions files "deleted and recreated underneath the
  editor (a branch" switch). Whether it also refreshes a file Claude Code has already opened with `didOpen`
  (stored as editor-owned, `from_disk: false`) is unknown. If it doesn't, a relay can re-send that file's text
  itself, which is why the criteria test a second mechanism before calling no-go.
- **Mount risk.** The repo is on a virtiofs mount (see `CLAUDE.md`). inotify may not report changes made on the
  host, and may behave differently for the sandbox's own writes. Check this first. If inotify fails, try polling
  before concluding that no method detects changes; that conclusion is the only one that skips the relay.
- **Host step.** An agent in the sandbox can't change files on the host, so ask the user to make the host-side
  change while the agent watches. If the user doesn't respond, record host-side changes as untested and continue.

How the 2026-09-25 test was run, to rebuild it:

- **Plugin.** The skills-directory plugin described in T-0002's Context (spike result), with the `.lsp.json`
  `command`/`args` starting the relay instead of rumdl (the test used `python3` and a script path). Workspace trust
  limits where it loads; see T-0002.
- **Relay.** A short Python script that starts `rumdl server`, copies LSP messages between stdin/stdout and rumdl,
  and logs each message's direction, method, and key params (URIs, `didChange` text) to a file. The mechanisms
  under test live in the same relay.
- **Session.** One headless `claude -p` session per condition, with only the `LSP` and `Read` tools, so it can't
  run git itself (an isolated worktree session refuses to start a nested session with Bash). The prompt runs
  baseline queries, then waits by re-reading a signal file until it holds `G1`, `G2`, ..., and queries again. The
  outer session watches the relay log for the previous step's last query, makes that step's change, and writes
  the next signal only after the change command exits 0; in the first run, a `git rm` failed on a staged rename
  after the signal went out, so that step queried too early. Bound each session with `timeout` and
  `--max-budget-usd` (this version of `claude` has no `--max-turns`); the first run needed 18 signal reads for 13
  LSP calls, and this matrix is several times larger. For the Write and Edit routes, the waiting session makes
  the change itself with those tools, so allow them in that session.
- **Test files.** Committed to a temporary branch so git routes have something to act on, then deleted with the
  branch. Keep every link valid: a deliberately broken link fails `npm run check`, which the Stop hook runs, and
  in the first run it blocked the outer session six times. Test link changes by retargeting links to other
  existing files instead.

Out of scope: building the production plugin (T-0002) or relay (T-0007), and changing rumdl or Claude Code.

Epic: T-0009.

## Handoff

Not started.

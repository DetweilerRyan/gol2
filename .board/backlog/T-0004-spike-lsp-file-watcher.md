---
id: T-0004
title: "Spike: can a file watcher alongside rumdl keep its LSP results fresh in Claude Code?"
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "The Handoff states whether inotify events fire on the repo's virtiofs mount for Markdown changes made inside the sandbox and for changes made on the host, with the command used and its output for each"
  - "A prototype watcher runs between Claude Code and rumdl and sends rumdl `workspace/didChangeWatchedFiles` for Markdown files created, changed, or deleted on disk; its source is on the task's branch and is not merged to main"
  - "For each change route (shell edit to a file already queried, shell edit to a file not yet queried, file created from the shell, `git mv`, `git rm`, `git checkout` of different content, and switching to a branch whose Markdown differs), the evidence records raw LSP tool output of `documentSymbol`, `workspaceSymbol`, and `findReferences` after the change, from a single Claude Code session, both without the watcher and with it"
  - "The evidence records the Claude Code and rumdl versions used and the traffic log showing the notifications the watcher sent"
  - "The Handoff recommends go or no-go for T-0002, citing the per-route results, and lists what the watcher would cost to maintain (for example its language, dependencies, and failure modes)"
  - "`npm run check` exits 0 on the task's branch"
evidence: []
---

## Context

The user wants rumdl only if its LSP plugin works (T-0002), and a test on 2026-09-25 found that it goes stale.
This spike answers one question before any of it lands: does a watcher that sends rumdl file-change notifications
fix that? A no-go is a valid result.

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
  (stored as editor-owned, `from_disk: false`) is unknown and is the crux for queries on a single file.
- **Mount risk.** The repo is on a virtiofs mount (see `CLAUDE.md`). inotify may not report changes made on the
  host, and may behave differently for the sandbox's own writes. Check this first; it decides whether a watcher
  can work at all.

How the 2026-09-25 test was run, to rebuild it:

- **Plugin.** `.claude/skills/rumdl-lsp/.claude-plugin/plugin.json` (`name`, `version`, `description`) and
  `.claude/skills/rumdl-lsp/.lsp.json` with an entry whose `command`/`args` start the relay (the test used
  `python3` and a script path), and `extensionToLanguage` `{ ".md": "markdown" }`. It loads only in a trusted
  workspace: this repo's checkout or its worktrees, not a scratch folder.
- **Relay.** A short Python script that starts `rumdl server`, copies LSP messages between stdin/stdout and rumdl,
  and logs each message's direction, method, and key params (URIs, `didChange` text) to a file. A watcher can live
  in the same relay and inject `workspace/didChangeWatchedFiles` notifications to rumdl.
- **Session.** One headless `claude -p` session with only the `LSP` and `Read` tools, so it can't run git itself
  (an isolated worktree session refuses to start a nested session with Bash). The prompt runs baseline queries,
  then waits by re-reading a signal file until it holds `G1`, `G2`, ..., and queries again. The outer session
  watches the relay log for the previous step's last query, makes that step's change with plain shell or git
  commands, then writes the next signal. Make each step's change finish before writing its signal; in the first
  run, a `git rm` failed on a staged rename after the signal went out, so that step queried too early.
- **Test files.** Committed to a temporary branch so git routes have something to act on, then deleted with the
  branch. Deliberately broken links in them fail `npm run check` until cleanup.

Out of scope: building the production plugin (T-0002) and changing rumdl or Claude Code.

## Handoff

Not started.

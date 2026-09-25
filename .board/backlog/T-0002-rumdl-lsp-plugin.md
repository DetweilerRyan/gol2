---
id: T-0002
title: Run rumdl's LSP for agents through an in-repo Claude Code plugin
depends_on: [T-0004]
claimed_by: null
verified_by: null
acceptance:
  - "A new ADR in `docs/decisions/` records adopting rumdl as the Markdown LSP server for agents, loaded through an in-repo Claude Code plugin"
  - "`package.json` pins `rumdl` exactly in devDependencies"
  - "A new Claude Code session started in the main checkout loads a rumdl LSP plugin committed in the repo, with no manual install step, shown by `claude plugin list` or `/plugin` output; the Handoff names the loading mechanism chosen and why"
  - "The running LSP server is the rumdl version pinned in `package.json`, both in a session in the main checkout and in a session in a worktree under `.claude/worktrees/`, shown by the server's version or command line from each session"
  - "An evidence command runs a headless Claude Code session (`claude -p`) in the main checkout and another in a worktree, each calling the LSP tool's `documentSymbol` on `CLAUDE.md`, and records output listing its headings with their start lines"
  - "Raw LSP tool output of `workspaceSymbol` on a Markdown heading query in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `workspaceSymbol` on a Markdown heading query in a worktree session is recorded with the Claude Code version"
  - "Raw LSP tool output of `goToDefinition` on a Markdown link in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `goToDefinition` on a Markdown link in a worktree session is recorded with the Claude Code version"
  - "Raw LSP tool output of `findReferences` from a body line of a linked Markdown file in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `findReferences` from a body line of a linked Markdown file in a worktree session is recorded with the Claude Code version"
  - "In a single Claude Code session, after each change route that T-0004 tested (Write tool, Edit tool, shell edit to a queried file, shell edit to an unqueried file, file created from the shell, `git mv`, `git rm`, `git checkout` of different content, and a branch switch), raw LSP tool output of `documentSymbol`, `workspaceSymbol`, and `findReferences` reflects the change"
  - "The plugin's LSP config does not enable rumdl's autofix-on-save, and editing a Markdown file with a fixable violation in a session leaves the violation in place"
  - "The user has reviewed and approved the diff of the plugin's files and of any `.claude/settings.json` change, and the evidence says where (PR review or comment)"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Lets agents navigate Markdown through Claude Code's LSP tool instead of reading whole files: a file's heading
outline, heading search, link targets, and backlinks. The user wants rumdl in the repo only if the plugin works:
if it can't meet these criteria, don't merge it, and T-0001 (switching the linter to rumdl) doesn't happen either.
It waits on T-0004, a spike on keeping LSP results fresh; if T-0004 recommends no-go, this task is dropped. T-0003
documents usage once this task's evidence shows which operations work. Research was done in a session on
2026-09-25.

- **Freshness (2026-09-25 test, details in T-0004).** Changes made with Claude Code's Write and Edit tools reach
  rumdl immediately. Changes made by shell or git commands never do: Claude Code rejects rumdl's request to watch
  `**/*.md` (`Unhandled method client/registerCapability`) and sends each file only once, so results stay stale
  for the rest of the session. If T-0004 recommends go, reimplement the mechanism it names rather than copying its
  prototype (which stays on the unmerged `prototype/T-0004-lsp-relay` branch), preferably in Rust. A Rust
  toolchain or any other new dependency needs the user's approval first (`CLAUDE.md`).

- **Spike result (2026-09-25, Claude Code 2.1.282).** A plugin folder `.claude/skills/rumdl-lsp/` holding
  `.claude-plugin/plugin.json` (`name`, `version`, `description`) and an `.lsp.json` with
  `{ "rumdl": { "command": "<absolute path to rumdl>", "args": ["server"], "extensionToLanguage": { ".md": "markdown" } } }`
  loaded as `rumdl-lsp@skills-dir` ("✔ loaded" in `claude plugin list`) with no marketplace or install step. A
  headless `claude -p --allowedTools LSP` session in this repo's worktree `.claude/worktrees/board-rumdl-task`
  got results from all five operations: `documentSymbol` (6 headings of `CLAUDE.md`), `workspaceSymbol` ("Decision"
  found in all 3 ADRs), `goToDefinition` (link to `.board/README.md:1:1`), `findReferences` from a body line
  (`CLAUDE.md:10:32`), and `hover`. It used a downloaded binary, not the npm package, and the main checkout wasn't
  tested.
- **`documentSymbol` shows start lines only.** rumdl sends each heading's full section range, but Claude Code's LSP
  tool prints only the start line ("Checks (String) - Line 13"). A section runs until the next heading at the same
  or a higher level, or the end of the file.
- **Workspace trust.** Project-scope plugins load only in a trusted workspace, and `claude -p` doesn't grant trust:
  in an untrusted scratch folder, `claude plugin list` reported the plugin skipped and the session had no LSP tool.
  Worktrees under the main checkout inherit its trust, so evidence sessions must run in this repo's checkout or its
  worktrees, not a fresh scratch copy.
- **Worktrees have no `node_modules/`.** The bind mount in `/etc/sandbox-persistent.sh` covers only the main
  checkout, and agents work in `.claude/worktrees/`. `npm run check` works there only because npm and Node look
  in parent directories and find the main checkout's `node_modules/`. Check what `${CLAUDE_PROJECT_DIR}` is in a
  worktree session before relying on `${CLAUDE_PROJECT_DIR}/node_modules/...`. One option: have the plugin start a
  small Node script that locates rumdl with `require.resolve("rumdl/bin/rumdl", { paths: [process.env.CLAUDE_PROJECT_DIR] })`,
  which walks up to the main checkout's `node_modules/` the same way. The existing hooks call
  `$CLAUDE_PROJECT_DIR/node_modules/.bin/tsx` and may have the same gap; that's outside this task.
- **Launching rumdl.** rumdl's npm launcher, `node_modules/rumdl/bin/rumdl`, is a Node script that runs the
  platform binary, so starting it with `node` uses the pinned version. The subcommand is `server`, not `serve`.
  Don't rely on symlinks inside the repo; the virtiofs mount drops them (see `CLAUDE.md`).
- **Install.** The npm package `rumdl` ships platform binaries as optional dependencies (`@rumdl/cli-linux-x64` and
  others). Confirm the binary resolves both in the sandbox (`node_modules/` is a bind mount, see `CLAUDE.md`) and
  in CI.
- **Loading mechanisms.** The spike used the skills-directory route (Claude Code 2.1.157+). It isn't discovered
  when Claude Code is launched from a subdirectory. The alternative is a local marketplace registered in
  `.claude/settings.json` under `extraKnownMarketplaces` and `enabledPlugins`, which may still prompt each user to
  install ([plugins shared through a repository](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository)).
  LSP entry fields: [LSP servers](https://code.claude.com/docs/en/plugins/components#lsp-servers).
- **Claude Code LSP tool bug** ([anthropics/claude-code#72316](https://github.com/anthropics/claude-code/issues/72316)).
  Since 2.1.47 the tool can return nothing for `workspaceSymbol`, `goToDefinition`, and `findReferences` when the
  queried file is gitignored, including by a parent directory's repo. The issue was closed as not planned by the
  stale bot on 2026-09-14. The main checkout's `.gitignore` ignores `.claude/worktrees/`, but the spike got
  results from a worktree, so the bug didn't trigger there on 2.1.282. Record what happens; don't work around it.
- **Lint config.** Until T-0001 adds `.rumdl.toml`, the LSP reports rumdl's defaults, including MD013 line-length
  warnings on most docs. Matching the gate's diagnostics is T-0001's job.
- **`findReferences` depends on where the cursor is.** From a heading, rumdl returns only links to that heading's
  anchor. To get every link to a file, query from a body line. Details go in T-0003's doc.
- **Security and churn.** The plugin makes every session run a 0.x npm binary that releases every few days. The
  exact version pin plus the lockfile is the control; treat each rumdl upgrade as its own task. The plugin's files
  and any `.claude/settings.json` change are executable config, so the user reviews that diff rather than an agent
  approving it. `.claude/settings.json` already holds the project's hooks; add to it without disturbing them.

Out of scope: switching the linter (T-0001), working around the Claude Code LSP tool bug beyond recording which
operations work, and the `docs/tools/` doc (T-0003). The freshness relay is in scope only as T-0004 recommends.

## Handoff

Not started.

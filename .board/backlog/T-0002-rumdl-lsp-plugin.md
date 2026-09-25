---
id: T-0002
title: Run rumdl's LSP for agents through an in-repo Claude Code plugin
depends_on: [T-0001]
claimed_by: null
verified_by: null
acceptance:
  - "A new Claude Code session started in the main checkout loads a rumdl LSP plugin committed in the repo, with no manual install step, shown by `claude plugin list` or `/plugin` output; the Handoff names the loading mechanism chosen and why"
  - "The running LSP server is the rumdl version pinned in `package.json`, both in a session in the main checkout and in a session in a worktree under `.claude/worktrees/`, shown by the server's version or command line from each session"
  - "An evidence command runs a headless Claude Code session (`claude -p`) in the main checkout and another in a worktree, each calling the LSP tool's `documentSymbol` on `CLAUDE.md`, and records output listing its headings with section line ranges; if headless sessions can't pass the workspace-trust gate, the user runs the two sessions and the evidence records their output"
  - "Raw LSP tool output of `workspaceSymbol` on a Markdown heading query in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `workspaceSymbol` on a Markdown heading query in a worktree session is recorded with the Claude Code version"
  - "Raw LSP tool output of `goToDefinition` on a Markdown link in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `goToDefinition` on a Markdown link in a worktree session is recorded with the Claude Code version"
  - "Raw LSP tool output of `findReferences` from a body line of a linked Markdown file in a main-checkout session is recorded with the Claude Code version"
  - "Raw LSP tool output of `findReferences` from a body line of a linked Markdown file in a worktree session is recorded with the Claude Code version"
  - "An evidence command creates a Markdown file with known lint errors, collects the LSP server's diagnostics for it, and shows they name the same rule IDs as `npm run lint:md` on that file and include no MD013, then deletes the file"
  - "The plugin's LSP config does not enable rumdl's autofix-on-save, and editing a Markdown file with a fixable violation in a session leaves the violation in place"
  - "The user has reviewed and approved the `.claude/settings.json` diff, and the evidence says where (PR review or comment)"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Lets agents navigate Markdown through Claude Code's LSP tool instead of reading whole files: a file's heading
outline with section line ranges, heading search, link targets, and backlinks. T-0001 makes rumdl the repo's
Markdown linter, so the LSP reads the same `.rumdl.toml` as the gate. T-0003 documents usage once this task's
evidence shows which operations work. Research was done in a session on 2026-09-25.

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
- **Loading mechanisms** (unverified; pick one and record why in the Handoff):
  - Since Claude Code 2.1.157, a folder `.claude/skills/<name>/` containing `.claude-plugin/plugin.json` loads
    automatically as `<name>@skills-dir` and can bundle an LSP server, with no marketplace. It isn't discovered
    when Claude Code is launched from a subdirectory. Source: agentpatterns.ai
    `tools/claude/local-plugin-scaffolding.md`.
  - A local marketplace directory with `.claude-plugin/marketplace.json`, registered in `.claude/settings.json`
    under `extraKnownMarketplaces` and switched on in `enabledPlugins`. It may still prompt each user to install.
    Docs: [plugins shared through a repository](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository).
  - Either way the LSP entry has `command`, `args`, and `extensionToLanguage` (`{ ".md": "markdown" }`), plus
    optional `initializationOptions`, `settings`, `env`, `workspaceFolder`, `startupTimeout`, and `restartOnCrash`
    ([LSP servers](https://code.claude.com/docs/en/plugins/components#lsp-servers)). `command` must be on `PATH`;
    `args` can use `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.
  - Project-scope LSP servers start only after the user trusts the workspace. Check loading with
    `claude plugin list` or `/plugin`, and `claude --debug` for server start errors.
- **Claude Code LSP tool bug** ([anthropics/claude-code#72316](https://github.com/anthropics/claude-code/issues/72316)).
  `workspaceSymbol`, `goToDefinition`, and `findReferences` return nothing while `hover` and `documentSymbol` work.
  A maintainer traced it: since 2.1.47 the tool drops results located in gitignored files, but wrongly drops all of
  them when the queried file is gitignored, including by a `.gitignore` in a parent directory's repo. The fix was
  promised, but the issue was closed as not planned by the stale bot on 2026-09-14; Claude Code here is 2.1.282.
  The main checkout's `.gitignore` ignores `.claude/worktrees/`. From inside a worktree, `git check-ignore` says
  its files aren't ignored, so worktree sessions may be fine; the evidence criteria above settle it. Record what
  happens; don't work around it.
- **`findReferences` depends on where the cursor is.** From a heading, rumdl returns only links to that heading's
  anchor. To get every link to a file, query from a body line. Details go in T-0003's doc.
- **Security.** The plugin makes every session run a 0.x npm binary. The exact version pin plus the lockfile is
  the control; treat each rumdl upgrade as its own task. `.claude/settings.json` is executable config, so the user
  reviews that diff rather than an agent approving it. It already holds the project's hooks; add to it without
  disturbing them.

Out of scope: working around the Claude Code LSP tool bug beyond recording which operations work, and the
`docs/tools/` doc (T-0003).

## Handoff

Not started.

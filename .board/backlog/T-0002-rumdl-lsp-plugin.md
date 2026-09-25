---
id: T-0002
title: Run rumdl's LSP for agents through an in-repo Claude Code plugin
depends_on: [T-0004, T-0008]
claimed_by: null
verified_by: null
acceptance:
  - "A new ADR in `docs/decisions/` records adopting rumdl as the Markdown LSP server for agents, serving both gol2's Markdown and the agentpatterns corpus, loaded through an in-repo Claude Code plugin, and cites the go recommendations of T-0004 and T-0008"
  - "In a worktree session, the LSP tool returns correct results on agentpatterns files for each of `documentSymbol` (a page's headings with their start lines), `workspaceSymbol` (a heading that exists in agentpatterns), `goToDefinition` (a relative link in an agentpatterns page), and `findReferences` (from a body line of an agentpatterns page that others link to); the evidence has the raw output and Claude Code version"
  - "`package.json` pins `rumdl` exactly in devDependencies"
  - "A new Claude Code session started in the main checkout loads a rumdl LSP plugin committed in the repo, with no manual install step and no hand-set environment variable such as `ENABLE_LSP_TOOL`, shown by `claude plugin list` or `/plugin` output; the Handoff names the loading mechanism chosen and why"
  - "The running LSP server is the rumdl version pinned in `package.json`, both in a session in the main checkout and in a session in a worktree under `.claude/worktrees/`, shown by the server's version or command line from each session"
  - "In a main-checkout session and in a worktree session, the LSP tool's `documentSymbol` on `CLAUDE.md` returns each of its headings with the line it starts on, matching the file; the evidence has the raw output and Claude Code version"
  - 'In a main-checkout session and in a worktree session, the LSP tool''s `workspaceSymbol` for "Decision" returns the "Decision" heading of every ADR in `docs/decisions/`; the evidence has the raw output and Claude Code version'
  - "In a main-checkout session and in a worktree session, the LSP tool's `goToDefinition` on a relative link in `CLAUDE.md` returns the linked file; the evidence has the raw output and Claude Code version"
  - "In a main-checkout session and in a worktree session, the LSP tool's `findReferences` from a body line of `.board/README.md` returns the link to it in `CLAUDE.md`; the evidence has the raw output and Claude Code version"
  - "The plugin's LSP config does not enable rumdl's autofix-on-save, and editing a Markdown file with a fixable violation in a session leaves the violation in place"
  - "The user merged the task's PR after reviewing it; agents opened it but didn't merge it, shown by `gh pr view <number> --json state,mergedAt` and the user's confirmation, recorded after the merge"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Lets agents navigate Markdown, in gol2 and in the agentpatterns corpus the coach reviews against, through Claude
Code's LSP tool instead of reading whole files: a file's heading outline, heading search, link targets, and
backlinks. The user wants rumdl in the repo only if the plugin works.
This task waits on two spikes, run in order: T-0008 (is it worth it, set up and piloted by T-0005), then T-0004
(can results be kept fresh), which runs only after T-0008 recommends go. If either
recommends no-go, move this task to `dropped/` (T-0006). Freshness itself is T-0007, which adds a relay on top of
this plugin. This file is the home for the plugin-setup facts; other tasks point here. Research was done in a
session on 2026-09-25.

- **Spike result (2026-09-25, Claude Code 2.1.282).** A plugin folder `.claude/skills/rumdl-lsp/` holding
  `.claude-plugin/plugin.json` (`name`, `version`, `description`) and an `.lsp.json` with
  `{ "rumdl": { "command": "<absolute path to rumdl>", "args": ["server"], "extensionToLanguage": { ".md": "markdown" } } }`
  loaded as `rumdl-lsp@skills-dir` ("✔ loaded" in `claude plugin list`) with no marketplace or install step. A
  headless `claude -p --allowedTools LSP` session in this repo's worktree `.claude/worktrees/board-rumdl-task`
  got results from `documentSymbol`, `workspaceSymbol`, `goToDefinition`, `findReferences`, and `hover`, with no
  environment variable set by hand. It used a downloaded binary, not the npm package, and the main checkout wasn't
  tested. (A May 2026 agentpatterns page, `tools/claude/feature-flags.md`, says the LSP tool needs
  `ENABLE_LSP_TOOL`; the spike contradicts that for 2.1.282.)
- **Serving agentpatterns too.** The coach reviews against the agentpatterns corpus, cloned at `../agentpatterns`
  relative to the repo (`/c/Users/User/Documents/projects/agentpatterns` here), and T-0008 measures the benefit
  there, so the plugin serves it as well as gol2's Markdown. Options: a second LSP workspace folder, the
  `.lsp.json` `workspaceFolder` field, or a second server entry; whichever is chosen, don't hard-code this
  machine's absolute path. A path relative to the project folder doesn't work from a worktree: from
  `.claude/worktrees/<name>/`, `../agentpatterns` points at `.claude/worktrees/agentpatterns`, which doesn't exist.
  Resolve it from the main checkout instead, the way `node_modules/` is found (see below). The coach's role file
  has the same flaw in its reference line; that's for the coach, not this task. The corpus has 1,587 pages, so check
  that indexing it doesn't slow session start noticeably and record the time in the Handoff. rumdl will also
  publish lint diagnostics for agentpatterns files it opens; that's expected, since agentpatterns isn't linted
  by gol2's gate.
- **Who runs the main-checkout sessions.** Agents work in worktrees, and an isolated worktree session refuses
  commands it can't prove stay in its worktree, so it can't run sessions in the main checkout. The user runs
  them, or a session started in the main checkout (not worktree-isolated) does; the evidence records their
  output.
- **Workspace trust.** Project-scope plugins load only in a trusted workspace, and `claude -p` doesn't grant trust:
  in an untrusted scratch folder, `claude plugin list` reported the plugin skipped and the session had no LSP tool.
  Worktrees under the main checkout inherit its trust, so evidence sessions must run in this repo's checkout or its
  worktrees, not a fresh scratch copy.
- **Worktrees have no `node_modules/`.** The bind mount in `/etc/sandbox-persistent.sh` covers only the main
  checkout, and agents work in `.claude/worktrees/`. `npm run check` works there only because npm and Node look
  in parent directories and find the main checkout's `node_modules/`. Check what `${CLAUDE_PROJECT_DIR}` is in a
  worktree session before relying on `${CLAUDE_PROJECT_DIR}/node_modules/...`. One option: start a small Node
  script that locates rumdl with `require.resolve("rumdl/bin/rumdl", { paths: [process.env.CLAUDE_PROJECT_DIR] })`,
  which walks up to the main checkout's `node_modules/` the same way; T-0007's relay can reuse it. The existing
  hooks call `$CLAUDE_PROJECT_DIR/node_modules/.bin/tsx` and may have the same gap; that's outside this task.
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
  results from a worktree, so the bug didn't trigger there on 2.1.282. If it triggers, the criteria above fail;
  don't work around it.
- **How the operations behave** (start lines only in `documentSymbol`, `findReferences` depending on the cursor):
  see T-0003's Context.
- **Freshness.** Results go stale after shell and git changes; see T-0004. This task doesn't fix that; T-0007 does.
- **Lint config.** Until T-0001 adds `.rumdl.toml`, the LSP reports rumdl's defaults, including MD013 line-length
  warnings on most docs. Matching the gate's diagnostics is T-0001's job.
- **Security and churn.** The plugin makes every session run a 0.x npm binary that releases every few days. The
  exact version pin plus the lockfile is the control; treat each rumdl upgrade as its own task. The plugin's files
  and any `.claude/settings.json` change are executable config, so the user reviews and merges the PR rather than
  an agent: agents act on GitHub as the user's account, so a PR review can't show who approved, and agents never
  merge. `.claude/settings.json` already holds the project's hooks; add to it without disturbing them.

Out of scope: freshness after shell and git changes (T-0007), switching the linter (T-0001), working around the
Claude Code LSP tool bug, and the `docs/tools/` doc (T-0003).

Epic: T-0009.

## Handoff

Not started.

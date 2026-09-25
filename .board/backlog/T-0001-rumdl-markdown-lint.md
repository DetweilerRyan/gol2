---
id: T-0001
title: Replace markdownlint-cli2 with rumdl for Markdown linting and set up its LSP for agents
depends_on: []
claimed_by: null
verified_by: null
acceptance:
  - "A new ADR in `docs/decisions/` records replacing markdownlint-cli2 and markdownlint-rule-relative-links with rumdl for Markdown linting, keeps oxfmt as the Markdown formatter, and ADR 0001 links to it as superseding its Markdown line"
  - "`package.json` pins `rumdl` exactly in devDependencies, no longer lists `markdownlint-cli2` or `markdownlint-rule-relative-links`, and `lint:md` runs rumdl"
  - "`.markdownlint-cli2.jsonc` is removed and `.rumdl.toml` disables MD013 and pins MD003 to atx, MD004 to dash, MD049 to underscore, and MD050 to asterisk"
  - "A temporary Markdown file containing a link to a missing file, a missing same-file anchor, and a missing cross-file anchor makes `npm run lint:md` exit non-zero and report all three"
  - "A Markdown file with a lint error in a gitignored path such as `.claude/worktrees/` does not fail `npm run lint:md`"
  - "`rumdl fmt` is not wired into any script, hook, or CI step"
  - "A Claude Code plugin committed in the repo runs rumdl as an LSP server for `.md` files, and `.claude/settings.json` enables it for the project, so a new session needs no manual plugin install"
  - "The plugin starts the rumdl version pinned in `package.json` from the project's `node_modules/`, not a global install"
  - "In a new Claude Code session in the main checkout and in one in a worktree under `.claude/worktrees/`, the LSP tool's `documentSymbol` on a doc returns its headings with section line ranges"
  - "The task's Handoff records, for the Claude Code version tested, whether `workspaceSymbol`, `goToDefinition`, and `findReferences` return results on Markdown files in the main checkout and in a worktree"
  - "A doc in `docs/tools/` explains how agents use rumdl's LSP to navigate Markdown: list a file's headings with their section line ranges and read only the section needed, search headings across files, follow links, and find backlinks from a body line rather than a heading. It marks any operation the Handoff found not working, with the Claude Code version"
  - "`docs/README.md` lists `tools/` and says what it holds"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Why rumdl: one tool can lint Markdown in the gate and act as an LSP server that agents use to navigate `docs/`
(heading outlines with section line ranges, heading search, go-to-definition, backlinks). Keeping markdownlint for
the gate and rumdl for the LSP would mean two configs, and agents would see diagnostics that differ from what
`npm run check` enforces. Research was done in a session on 2026-09-25; the findings the implementer needs:

- **Parity.** rumdl 0.2.77 implements all 53 markdownlint rules. With MD013 off, both tools report 0 issues on the
  repo's Markdown. On planted errors both caught a missing file (rumdl MD057), a missing same-file anchor (MD051),
  and a missing cross-file anchor (MD051), so the `relative-links` custom rule is no longer needed.
- **Config.** `rumdl import .markdownlint-cli2.jsonc` fails ("trailing comma at line 6 column 3"), and the file is
  in the cli2 wrapper format anyway, so write `.rumdl.toml` by hand. A minimal version that matched markdownlint:
  `[global]` with `disable = ["MD013"]` and `exclude = ["node_modules", "dist"]`. rumdl respects `.gitignore` by
  default (`respect_gitignore = true`).
- **Pinned styles.** MD003 and MD004 default to "consistent", and rumdl picks the most common style in a file where
  markdownlint picks the first one it sees. Pin them (and MD049/MD050) to what oxfmt writes, so the linter never
  demands a style the formatter will undo.
- **Formatting stays with oxfmt.** oxfmt reprints Markdown in a fixed style without changing how it renders.
  `rumdl fmt` only applies lint fixes, and on a test file it removed a hard line break and merged three separate
  lists into one. The two tools rewrite each other's output, so only one of them may format.
- **Install.** The npm package `rumdl` ships platform binaries as optional dependencies (`@rumdl/cli-linux-x64` and
  others). Confirm the binary resolves both in the sandbox (`node_modules/` is a bind mount, see `CLAUDE.md`) and
  in CI.
- **Churn.** rumdl is 0.x and releases every few days. Pin the exact version and upgrade deliberately.
- **Time.** On the 7 current files, rumdl takes ~0.07 s and markdownlint-cli2 ~0.6 s, so speed isn't a factor.

- **LSP behavior for the `docs/tools/` doc** (rumdl 0.2.77, tested over raw LSP against this repo):
  - `textDocument/documentSymbol` returns the heading tree. Each heading's range spans its whole section and ends on
    the section's last line, so an agent can read just that line range instead of the whole file.
  - `workspace/symbol` searches headings across all Markdown files (query "Decision" found the heading in each ADR).
  - `textDocument/definition` on a link target resolves to the linked file, or to the heading for `file.md#anchor`.
  - `textDocument/references` depends on the cursor (`handle_references` in rumdl's `src/lsp/navigation.rs`). On a
    heading, it returns links to that heading's anchor only. On a link target, it returns links to the same
    target. On any other line, it returns every link to the current file. On the link text `[...]`, it
    returns nothing. So to find what links to a file, ask from a body line, not the `#` title on line 1.
- **Claude Code LSP tool bug** ([anthropics/claude-code#72316](https://github.com/anthropics/claude-code/issues/72316)).
  `workspaceSymbol`, `goToDefinition`, and `findReferences` return nothing while `hover` and `documentSymbol` work.
  A maintainer traced it: since 2.1.47 the tool drops results located in gitignored files, but wrongly drops all of
  them when the queried file is gitignored, including by a `.gitignore` in a parent directory's repo. The fix was
  promised, but the issue was closed as not planned by the stale bot on 2026-09-14; Claude Code here is 2.1.282.
  The main checkout's `.gitignore` ignores `.claude/worktrees/`, where agents work. From inside a worktree,
  `git check-ignore` says its files aren't ignored, so worktree sessions may be fine, but that's untested.
- **Plugin setup** (from the Claude Code docs, via a research subagent; verify while implementing):
  - The plugin is a directory with `.claude-plugin/plugin.json` and an `.lsp.json` whose entry has `command`,
    `args`, and `extensionToLanguage` (`{ ".md": "markdown" }`). Optional fields include `initializationOptions`,
    `settings`, `env`, `workspaceFolder`, `startupTimeout`, and `restartOnCrash`.
  - To ship it with the repo: a local marketplace directory with `.claude-plugin/marketplace.json` listing the
    plugin by relative `source`, registered in `.claude/settings.json` under `extraKnownMarketplaces` (a
    `directory` source) and switched on in `enabledPlugins` as `<plugin>@<marketplace>`. Docs:
    [plugins shared through a repository](https://code.claude.com/docs/en/plugins/loading#plugins-shared-through-a-repository),
    [LSP servers](https://code.claude.com/docs/en/plugins/components#lsp-servers).
  - `command` must be on `PATH`, but `args` can use `${CLAUDE_PROJECT_DIR}`. rumdl's npm launcher,
    `node_modules/rumdl/bin/rumdl`, is a Node script that runs the platform binary, so `command: "node"` with
    `args: ["${CLAUDE_PROJECT_DIR}/node_modules/rumdl/bin/rumdl", "server"]` uses the pinned version. The
    subcommand is `server`, not `serve`.
  - Don't rely on symlinks inside the repo; the virtiofs mount drops them (see `CLAUDE.md`).
  - Check loading with `claude plugin list` or `/plugin`, and `claude --debug` for server start errors.
  - `.claude/settings.json` already holds the project's hooks; add to it without disturbing them.
- **Ownership.** The coach maintains `docs/`, so the coach writes or reviews the `docs/tools/` doc. Per
  `docs/README.md`, the doc should cover only what agents can't learn by reading the repo.

Out of scope: rumdl's autofix-on-save (leave it off), and working around the Claude Code LSP tool bug beyond
recording which operations work.

## Handoff

Not started.

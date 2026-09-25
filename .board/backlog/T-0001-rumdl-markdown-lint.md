---
id: T-0001
title: Replace markdownlint-cli2 with rumdl for Markdown linting
depends_on: [T-0007]
claimed_by: null
verified_by: null
acceptance:
  - "A new ADR in `docs/decisions/` records replacing markdownlint-cli2 and markdownlint-rule-relative-links with rumdl for Markdown linting, keeps oxfmt as the Markdown formatter, and ADR 0001 links to it as superseding its Markdown line"
  - "`package.json` no longer lists `markdownlint-cli2` or `markdownlint-rule-relative-links`, and `lint:md` runs the rumdl pinned by T-0002"
  - "`.markdownlint-cli2.jsonc` is removed and `.rumdl.toml` disables MD013 and pins MD003 to atx, MD004 to dash, MD049 to underscore, and MD050 to asterisk"
  - "A single evidence command creates a Markdown file containing a link to a missing file, a missing same-file anchor, and a missing cross-file anchor, runs `npm run lint:md`, which exits non-zero and reports all three, and then deletes the file"
  - "A single evidence command creates a Markdown file with a lint error in a gitignored path such as `.claude/worktrees/`, runs `npm run lint:md`, which exits 0, and then deletes the file"
  - "An evidence command creates a Markdown file with known lint errors, collects the LSP server's diagnostics for it, and shows they name the same rule IDs as `npm run lint:md` on that file and include no MD013, then deletes the file"
  - "`rumdl fmt` is not wired into any script, hook, or CI step"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Why: T-0002 adds rumdl as the LSP server agents use to navigate `docs/`. Keeping markdownlint for the gate and
rumdl for the LSP would mean two configs, and agents would see diagnostics that differ from what `npm run check`
enforces. This task runs only after the plugin (T-0002) and its freshness relay (T-0007) are done; if either
spike (T-0004, T-0005) recommends no-go, rumdl isn't adopted and this task moves to `dropped/` (T-0006). Research was done in a session on 2026-09-25; the findings the implementer needs:

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
- **LSP diagnostics.** The LSP server started by T-0002's plugin reads the same `.rumdl.toml`, so once it exists,
  agents' diagnostics should match the gate. Before it exists, the LSP reports rumdl's defaults, including MD013.
- **Time.** On the 7 current files, rumdl takes ~0.07 s and markdownlint-cli2 ~0.6 s, so speed isn't a factor.

## Handoff

Not started.

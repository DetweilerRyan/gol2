---
id: T-0003
title: Document how agents navigate Markdown with rumdl's LSP
depends_on: [T-0007]
claimed_by: null
verified_by: null
acceptance:
  - "A doc in `docs/tools/` presents as usable only the LSP operations whose T-0002 and T-0007 evidence shows correct results, with the Claude Code version they were verified on"
  - "The doc says how to read a single section: `documentSymbol` gives each heading's start line, the section runs until the next heading at the same or a higher level (or the end of the file), and the agent reads only those lines"
  - "The doc says `findReferences` from a heading returns only links to that heading's anchor, and from a body line returns every link to the file"
  - "The doc lists each known limitation recorded in T-0007's Handoff (for example, changes made on the host), or says there are none"
  - "The doc contains no copy of `.rumdl.toml` settings or the plugin's config; it links to those files instead"
  - "`docs/README.md` lists `tools/` and says what it holds"
  - "`CLAUDE.md` has a one-line pointer telling agents to navigate Markdown with the LSP tool, linking to the doc, and stays under its ~100-line limit"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Intended for the coach, which maintains `docs/` and `CLAUDE.md`. Per `docs/README.md`, the doc covers only what
agents can't learn by reading the repo: how the operations behave, which ones work in Claude Code, and their
limits, not how rumdl is configured. Write it from the evidence and Handoffs of T-0002 and T-0007. If the spikes
recommend no-go, move this task to `dropped/` (T-0006).

The `CLAUDE.md` pointer is there because agents often skip an installed tool unless their always-loaded
instructions name it. The coach's prediction to check at the next retro: at least one session among the next five
that navigates Markdown uses the LSP tool on `.md` files.

This file is the home for how rumdl's LSP operations behave; other tasks point here. From testing rumdl 0.2.77 over
raw LSP and through Claude Code 2.1.282 on 2026-09-25:

- `textDocument/documentSymbol` returns the heading tree. rumdl sends each heading's whole section range, but Claude
  Code's LSP tool prints only the start line ("Checks (String) - Line 13"). The section's end is the line before
  the next heading at the same or a higher level, or the end of the file.
- `workspace/symbol` searches headings across all Markdown files (query "Decision" found the heading in each ADR).
- `textDocument/definition` on a link target resolves to the linked file, or to the heading for `file.md#anchor`.
- `textDocument/references` depends on the cursor (`handle_references` in rumdl's `src/lsp/navigation.rs`). On a
  heading, it returns links to that heading's anchor only. On a link target, it returns links to the same target.
  On any other line, it returns every link to the current file. On the link text `[...]`, it returns nothing. So
  to find what links to a file, ask from a body line, not the `#` title on line 1.
- Claude Code's LSP tool has a known bug that can empty some results for gitignored files; see T-0002. The doc
  states what the evidence showed, not the bug's history.

Epic: T-0009.

## Handoff

Not started.

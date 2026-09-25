---
id: T-0003
title: Document how agents navigate Markdown with rumdl's LSP
depends_on: [T-0002]
claimed_by: null
verified_by: null
acceptance:
  - "A doc in `docs/tools/` presents as usable only the LSP operations that have a T-0002 evidence entry showing results, and marks each operation T-0002 found returning nothing as not working, with the Claude Code version and checkout (main or worktree)"
  - "The doc says how to read a single section: `documentSymbol` gives each heading's start line, the section runs until the next heading at the same or a higher level (or the end of the file), and the agent reads only those lines"
  - "The doc says `findReferences` from a heading returns only links to that heading's anchor, and from a body line returns every link to the file"
  - "The doc contains no copy of `.rumdl.toml` settings or the plugin's config; it links to those files instead"
  - "`docs/README.md` lists `tools/` and says what it holds"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Intended for the coach, which maintains `docs/`. Per `docs/README.md`, the doc covers only what agents can't learn
by reading the repo: how the operations behave and which ones work in Claude Code, not how rumdl is configured.
Write it from T-0002's evidence and Handoff; the notes below come from testing rumdl 0.2.77 over raw LSP against
this repo on 2026-09-25, before the plugin existed.

- `textDocument/documentSymbol` returns the heading tree. rumdl sends each heading's whole section range, but Claude
  Code's LSP tool prints only the start line ("Checks (String) - Line 13", tested on 2.1.282). The section's end is
  the line before the next heading at the same or a higher level, or the end of the file.
- `workspace/symbol` searches headings across all Markdown files (query "Decision" found the heading in each ADR).
- `textDocument/definition` on a link target resolves to the linked file, or to the heading for `file.md#anchor`.
- `textDocument/references` depends on the cursor (`handle_references` in rumdl's `src/lsp/navigation.rs`). On a
  heading, it returns links to that heading's anchor only. On a link target, it returns links to the same target.
  On any other line, it returns every link to the current file. On the link text `[...]`, it returns nothing. So
  to find what links to a file, ask from a body line, not the `#` title on line 1.
- Claude Code's LSP tool has a known bug that can empty `workspaceSymbol`, `goToDefinition`, and `findReferences`
  results for gitignored files (see T-0002). The doc should state what T-0002's evidence showed, not the bug's
  history.

## Handoff

Not started.

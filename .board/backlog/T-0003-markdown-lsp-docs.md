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
  - "Only if T-0008 recommended go: with the user's approval, recorded in the evidence, `.claude/agents/coach.md` lists the LSP tool and contains the exact LSP instruction text fixed in T-0005's workload file, so the coach runs the configuration that was tested"
  - "`npm run check` exits 0"
evidence: []
---

## Context

Intended for the coach, which maintains `docs/` and its own role file. Per `docs/README.md`, the doc covers only what
agents can't learn by reading the repo: how the operations behave, which ones work in Claude Code, and their
limits, not how rumdl is configured. Write it from the evidence and Handoffs of T-0002 and T-0007. If the spikes
recommend no-go, move this task to `dropped/` (T-0006).

The coach's role file reuses the instruction wording the study tested, not new wording, because agents often skip
an installed tool unless their instructions name it. There's no `CLAUDE.md` pointer yet: the study tests the
instruction only for the coach reviewing agentpatterns, and a `CLAUDE.md` line would reach every agent, including
ones working on gol2's own docs, where no benefit was measured. Add one only after a retro sees another agent skip
the tool (the user's decision, 2026-09-25). The coach's prediction to check at the next retro, matching the study's
uptake rule: in at least two thirds of the next coach reviews against agentpatterns (at least three), the coach
makes an LSP call.

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

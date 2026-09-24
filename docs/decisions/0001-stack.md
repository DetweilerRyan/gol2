# 0001: TypeScript, Vite, Vitest, oxc

Status: accepted (2026-09-24)

## Decision

TypeScript in strict mode, rendered to an HTML canvas. Vite for the dev server and build, Vitest for tests,
oxlint and oxfmt for linting and formatting, markdownlint-cli2 for Markdown.

## Consequences

Tool versions are pinned exactly in `package.json`. Changing any of these tools needs a new ADR.

Tooling scripts (`scripts/`) and Claude Code hooks (`.claude/hooks/`) are TypeScript too, run with `tsx` and
type-checked by `tsconfig.node.json`. `tsx` is needed because the sandbox's Node build lacks native type stripping.

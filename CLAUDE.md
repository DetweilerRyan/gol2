# gol2 — Agent Instructions

Conway's Game of Life in TypeScript, rendered to an HTML canvas. Expected to grow large, with many agents working
in parallel. Keep this file a map (under ~100 lines); detail lives in the files it points to.

## Where things are

- Decisions and their reasons: [`docs/decisions/`](docs/decisions/). Read the relevant ADR before changing
  architecture; propose a new ADR instead of silently deviating.
- Task management: [`.board/`](.board/README.md). Work from a task file when one exists.
- Agent roles: `.claude/agents/`. `tech` builds or routes technical work, owns product docs; `coach` owns agent docs.

## Checks

`npm run check` is the gate. It runs as the git pre-commit hook, in CI, and when the main agent or a subagent
stops after changing files (Stop/SubagentStop hooks). Run it before reporting done; if it fails, say so rather than
claiming success.

## Before starting any task

Run `git status`. Other agents share this working tree; don't build on someone else's uncommitted work without asking.

## Boundaries

- Always: add or update a test when changing simulation rules.
- Ask first: adding runtime dependencies; changing the grid representation or the simulation module's public API.
- Never: bypass the gate with `--no-verify` or by disabling hooks.

## Sandbox gotchas

- The repo's virtiofs mount silently drops symlinks, so `node_modules/` is a bind mount of
  `~/.local/share/gol2/node_modules`, recreated by `/etc/sandbox-persistent.sh`. Don't delete or replace the
  directory; if `node_modules/.bin` is empty, check `mountpoint node_modules`.
- Git hooks live in `.githooks/`; a fresh clone needs `git config core.hooksPath .githooks`.

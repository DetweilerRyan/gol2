# gol2 — Agent Instructions

Conway's Game of Life in TypeScript, rendered to an HTML canvas. Expected to grow large, with many agents working
in parallel. Keep this file a map (under ~100 lines); detail lives in the files it points to.

## Where things are

- Decisions and their reasons: [`docs/decisions/`](docs/decisions/). Read the relevant ADR before changing
  architecture; propose a new ADR instead of silently deviating.
- Task management: [`.board/`](.board/README.md). Work from a task file when one exists.
- Agent roles: `.claude/agents/`. The `coach` agent maintains this file, agent roles, and `docs/`.

## Checks

`npm run check` is the gate. It runs as the git pre-commit hook, in CI, and when the main agent or a subagent
stops after changing files (Stop/SubagentStop hooks). Run it before reporting done; if it fails, say so rather than
claiming success.

## Before starting any task

Run `git status`. Other agents share this working tree; don't build on someone else's uncommitted work without asking.

## Boundaries

- Always: add or update a test when changing simulation rules.
- Ask first: adding runtime dependencies; changing the grid representation or the simulation module's public API;
  moving a task into `.board/ready/` (draft tasks in `backlog/`; the user approves each one before it's ready).
- Never: bypass the gate with `--no-verify` or by disabling hooks.

## Working with the user

- Record practices, preferences, and decisions in the repo (this file, `docs/`, `.board/`), never in auto-memory.
  If the right file is outside your scope, say so, and the coach's next retro picks it up.
- Coach task reviews: ask the coach to review the task file(s) and add no checklist of your own; its role file
  defines the review. Then put each item that needs the user's decision to them one at a time, with the options
  and the coach's recommendation, and apply the remaining fixes only once the user agrees.

## Environment gotchas

- The repo's virtiofs mount silently drops symlinks, so `node_modules/` is a bind mount of
  `~/.local/share/gol2/node_modules`, recreated by `/etc/sandbox-persistent.sh`. Don't delete or replace the
  directory; if `node_modules/.bin` is empty, check `mountpoint node_modules`.
- Git hooks live in `.githooks/`; a fresh clone needs `git config core.hooksPath .githooks`.
- Agents act on GitHub as the user's account (`gh api user`), so the user is the author of every PR an agent opens
  and can't approve it, and an agent's review would look like the user's. Record the user's approval as their merge
  or their own message, never as a PR review.
- In a worktree session, Claude Code refuses Bash commands it can't prove stay in the worktree: compound commands
  that contain "git" anywhere (even `.github`, `.gitignore`, `github_pat_`), `git -C`, `source`, `HOME=…`, or
  commands built at runtime (`$(…)`, loops over variables). Run one plain command per call; put scripts and commit
  messages in files.

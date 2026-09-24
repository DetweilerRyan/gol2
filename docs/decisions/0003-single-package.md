# 0003: Single package for now

Status: accepted (2026-09-24)

## Context

The repo is expected to grow large, but the module boundaries aren't known yet.

## Decision

One npm package with code under `src/`. Split into npm workspaces (`packages/*`) once a module boundary is
stable and has its own conventions, tests, or consumers.

## Consequences

When the split happens, each package gets its own `CLAUDE.md` only if its conventions differ from the root.

# 0002: Pure simulation, separate rendering

Status: accepted (2026-09-24)

## Decision

Simulation logic (grid, rules, step) is pure and deterministic: no DOM or canvas access, and `step` returns a new
grid instead of mutating one. Rendering and input handling live in a separate module that depends on the
simulation, never the reverse.

## Consequences

The simulation can be tested in Node without a browser. Performance work that needs mutation must keep the
public API pure (for example, double-buffering behind the API).

// PreToolUse hook for Edit/Write/NotebookEdit (coach only): coach may write almost anywhere; this
// blocks only the few places where a direct write breaks the repo or sandbox.
// Fails closed: any error blocks the call. Mirrors the Constraints in .claude/agents/coach.md.
import { resolve } from "node:path";
import { block, readInput } from "./lib";

const DENIED = [
  /(?:^|\/)\.git(?:\/|$)/, // git internals; use git commands instead
  /(?:^|\/)node_modules(?:\/|$)/, // bind mount, see CLAUDE.md "Sandbox gotchas"
];

try {
  const input = await readInput();
  const target = input.tool_input?.file_path ?? input.tool_input?.notebook_path;
  if (!target) block("Coach write guard: no file path in tool input; blocking to be safe.");

  const root = process.env.CLAUDE_PROJECT_DIR ?? input.cwd ?? process.cwd();
  const path = resolve(input.cwd ?? root, target).replaceAll("\\", "/");

  if (DENIED.some((pattern) => pattern.test(path))) {
    block(`Blocked: coach doesn't write inside .git/ or node_modules/ (${path}).`);
  }
} catch (error) {
  block(`Coach write guard error, blocking to be safe: ${(error as Error).message}`);
}

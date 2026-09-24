// PreToolUse hook for Edit/Write/NotebookEdit (coach only): allow writes only inside coach's scope.
// Fails closed: any error blocks the call. Mirrors the Output Artifacts in .claude/agents/coach.md.
import { isAbsolute, relative, resolve } from "node:path";
import { block, readInput } from "./lib";

const ALLOWED = [
  /^(?:.+\/)?CLAUDE\.md$/, // root and subdirectory instruction files
  /^\.claude\/agents\/[^/]+\.md$/,
  /^docs\//,
  /^README\.md$/,
  /^\.board\/retros\/[^/]+\.md$/,
];

try {
  const input = await readInput();
  const target = input.tool_input?.file_path ?? input.tool_input?.notebook_path;
  if (!target) block("Coach write guard: no file path in tool input; blocking to be safe.");

  const root = process.env.CLAUDE_PROJECT_DIR ?? input.cwd ?? process.cwd();
  const path = relative(root, resolve(input.cwd ?? root, target)).replaceAll("\\", "/");

  if (path.startsWith("..") || isAbsolute(path) || !ALLOWED.some((pattern) => pattern.test(path))) {
    block(
      `Blocked: ${path} is outside coach's write scope (CLAUDE.md files, .claude/agents/, docs/, ` +
        "README.md, .board/retros/). Propose the change to the user instead.",
    );
  }
} catch (error) {
  block(`Coach write guard error, blocking to be safe: ${(error as Error).message}`);
}

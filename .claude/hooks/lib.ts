// Shared helpers for Claude Code hooks. See https://code.claude.com/docs/en/hooks for the input shape.
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";
import { text } from "node:stream/consumers";

export interface HookInput {
  session_id?: string;
  cwd?: string;
  hook_event_name?: string;
  agent_id?: string;
  agent_type?: string;
  stop_hook_active?: boolean;
  tool_name?: string;
  tool_input?: { command?: string; file_path?: string; notebook_path?: string };
}

export async function readInput(): Promise<HookInput> {
  const parsed: unknown = JSON.parse(await text(process.stdin));
  if (typeof parsed !== "object" || parsed === null)
    throw new Error("hook input is not a JSON object");
  return parsed as HookInput;
}

/** Block the tool call or stop, with a reason Claude sees. */
export function block(reason: string): never {
  console.error(reason);
  process.exit(2);
}

const git = (args: string[], env: NodeJS.ProcessEnv = process.env) =>
  execFileSync("git", args, { encoding: "utf8", env, stdio: ["ignore", "pipe", "pipe"] }).trim();

/** Per-worktree directory for hook state, inside .git so it's never committed or linted. */
export function stateDir(): string {
  const dir = git(["rev-parse", "--git-path", "claude-hooks"]);
  mkdirSync(dir, { recursive: true });
  return dir;
}

/**
 * Tree hash of the whole working tree (tracked and untracked, minus ignored files), built in a
 * throwaway index so the real index is untouched. Equal hashes mean no file content changed.
 */
export function treeFingerprint(key: string): string {
  const index = join(stateDir(), `index-${key}`);
  try {
    const env = { ...process.env, GIT_INDEX_FILE: index };
    git(["add", "--all"], env);
    return git(["write-tree"], env);
  } finally {
    rmSync(index, { force: true });
  }
}

/** Key for per-turn state: the subagent's id inside a subagent, else the session. */
export const stateKey = (input: HookInput): string =>
  (input.agent_id ?? input.session_id ?? "unknown").replace(/[^\w.-]/g, "_");

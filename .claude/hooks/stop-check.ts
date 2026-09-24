// Stop / SubagentStop hook: if files changed during this turn (or this subagent's run), run
// `npm run check` before the agent may finish. Exit 2 blocks the stop and feeds the failure back.
import { execSync } from "node:child_process";
import { readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { block, readInput, stateDir, stateKey, treeFingerprint } from "./lib";

const HEAD_LINES = 40;
const TAIL_LINES = 15;

interface ExecError {
  stdout?: string;
}

/** First and last lines of long output: the first failure is near the top, the summary at the end. */
function excerpt(output: string): string {
  const lines = output.trim().split("\n");
  if (lines.length <= HEAD_LINES + TAIL_LINES) return lines.join("\n");
  const omitted = lines.length - HEAD_LINES - TAIL_LINES;
  return [
    ...lines.slice(0, HEAD_LINES),
    `... ${omitted} lines omitted; rerun \`npm run check\` for the full output ...`,
    ...lines.slice(-TAIL_LINES),
  ].join("\n");
}

const input = await readInput();
const key = stateKey(input);
const snapshot = join(stateDir(), `${key}.tree`);

// Already blocked once: let the agent stop and report, instead of looping.
if (input.stop_hook_active) process.exit(0);

let baseline: string | undefined;
try {
  baseline = readFileSync(snapshot, "utf8");
} catch {
  // No snapshot (hook added mid-session, or snapshot failed): run the gate to be safe.
}
if (input.agent_id) rmSync(snapshot, { force: true });

let unchanged = false;
try {
  unchanged = baseline !== undefined && treeFingerprint(key) === baseline;
} catch {
  // Can't fingerprint: run the gate.
}
if (unchanged) process.exit(0);

try {
  execSync("npm run -s check 2>&1", {
    encoding: "utf8",
    stdio: "pipe",
    maxBuffer: 64 * 1024 * 1024,
    env: { ...process.env, NO_COLOR: "1", FORCE_COLOR: "0" },
  });
} catch (error) {
  block(
    "npm run check failed. Fix it, or report the failure to the user; don't claim done.\n\n" +
      excerpt((error as ExecError).stdout ?? String(error)),
  );
}

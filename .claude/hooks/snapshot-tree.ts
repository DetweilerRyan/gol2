// UserPromptSubmit / SubagentStart hook: record a fingerprint of the working tree at the start of a turn
// (or of a subagent's run), so stop-check.ts can skip the gate when nothing changed.
// Never blocks: exit 2 here would reject the user's prompt.
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { readInput, stateDir, stateKey, treeFingerprint } from "./lib";

try {
  const key = stateKey(await readInput());
  writeFileSync(join(stateDir(), `${key}.tree`), treeFingerprint(key));
} catch (error) {
  // Without a snapshot, stop-check runs the gate anyway.
  console.error(`snapshot-tree: ${(error as Error).message}`);
}

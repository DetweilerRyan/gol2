// PreToolUse hook for Bash (coach only): block `git push`. Fails closed: any error blocks the call.
import { block, gitCommand, readInput } from "./lib";

const GIT_PUSH = gitCommand("push");

try {
  const command = (await readInput()).tool_input?.command ?? "";
  if (GIT_PUSH.test(command)) block("Blocked: coach may not run git push.");
} catch (error) {
  block(`Push guard error, blocking to be safe: ${(error as Error).message}`);
}

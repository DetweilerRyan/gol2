// PreToolUse hook for Bash (coach only): block `git push`. Fails closed: any error blocks the call.
import { block, readInput } from "./lib";

// `git` as a command (start of a subcommand, optionally after env assignments or wrappers like sudo),
// followed by its global options, then the `push` subcommand. Won't match `git commit -m "push"`,
// `git stash push`, or `echo git push`; can't see through variable substitution like `$G push`.
const GIT_PUSH =
  /(?:^|[;&|(`\n]|\$\()\s*(?:(?:sudo|env|command|exec|nohup|time|xargs)\s+|\w+=\S*\s+)*(?:\S*\/)?git(?:\s+(?:-[cC]\s+\S+|--\S+|-\S+))*\s+push\b/;

try {
  const command = (await readInput()).tool_input?.command ?? "";
  if (GIT_PUSH.test(command)) block("Blocked: coach may not run git push.");
} catch (error) {
  block(`Push guard error, blocking to be safe: ${(error as Error).message}`);
}

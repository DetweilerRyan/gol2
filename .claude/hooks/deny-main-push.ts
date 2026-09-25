// PreToolUse hook for Bash (tech only): block pushes to main/master and merges into them; allow other pushes.
// Fails closed: an error, or a push whose destination it can't resolve (variables, detached HEAD, --all,
// remote.*.push config), blocks the call. It resolves branches in the hook's cwd, so it can't see a `cd` or
// `git checkout` earlier in the same command.
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { block, gitCommand, readInput, shellCommand } from "./lib";

const PROTECTED = new Set(["main", "master"]);
const PUSH = gitCommand("push", "g");
const MERGE = gitCommand("merge(?!-)", "g"); // not `git merge-base`
// `gh pr merge` merges on GitHub; `gh repo sync` updates a remote default branch; `gh api` can call the merge
// endpoints or write refs directly.
const GH = shellCommand(String.raw`gh\s+(pr\s+merge|repo\s+sync|api)\b`, "g");
const GH_API_RISKY = /\/merges?\b|refs\/heads\/(?:main|master)\b/;
// Push options that take a separate value.
const VALUE_OPTIONS = new Set(["-o", "--push-option", "--repo", "--receive-pack", "--exec"]);
const ALL_BRANCHES = new Set(["--all", "--mirror", "--branches"]);

const unquote = (token: string) => token.replace(/^(['"])(.*)\1$/, "$2");

/** The rest of this simple command: up to the next separator, split into words. */
function argsAfter(command: string, end: number): string[] {
  const segment = command.slice(end).split(/[;&|\n)`]/)[0] ?? "";
  return segment.trim().split(/\s+/).filter(Boolean).map(unquote);
}

/** Directory git will run in: the hook's cwd plus any `-C dir` global options in the matched prefix. */
function gitDir(prefix: string, cwd: string): string {
  if (/--git-dir|--work-tree/.test(prefix))
    block("Blocked: can't resolve the branch with --git-dir/--work-tree.");
  let dir = cwd;
  for (const m of prefix.matchAll(/\s-C\s+(\S+)/g)) dir = resolve(dir, unquote(m[1] ?? ""));
  return dir;
}

function git(dir: string, args: string[]): string | undefined {
  try {
    return execFileSync("git", ["-C", dir, ...args], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return undefined;
  }
}

function currentBranch(dir: string): string {
  const branch = git(dir, ["symbolic-ref", "--short", "-q", "HEAD"]);
  if (!branch)
    block(
      "Blocked: can't tell which branch is checked out (detached HEAD?), so can't rule out main.",
    );
  return branch;
}

const branchName = (ref: string) => ref.replace(/^refs\/heads\//, "");

function checkPush(args: string[], dir: string): void {
  if (args.some((a) => /[$`*?]/.test(a)))
    block("Blocked: push arguments use substitution or globs; spell them out.");
  const positional: string[] = [];
  for (let i = 0; i < args.length; i++) {
    const arg = args[i] ?? "";
    if (arg === "--") {
      positional.push(...args.slice(i + 1));
      break;
    }
    if (ALL_BRANCHES.has(arg)) block(`Blocked: \`git push ${arg}\` can push main.`);
    if (VALUE_OPTIONS.has(arg)) i++;
    else if (!arg.startsWith("-")) positional.push(arg);
  }
  const refspecs = positional.slice(1);

  if (refspecs.length === 0) {
    // Bare push: destination comes from config. Block if anything could map it to main.
    if (git(dir, ["config", "--get-regexp", String.raw`^remote\..*\.push$`]))
      block(
        "Blocked: remote.*.push is configured, so a push without a refspec may reach main; name the branch.",
      );
    const branch = currentBranch(dir);
    const upstream = git(dir, ["config", `branch.${branch}.merge`]);
    for (const target of [branch, upstream && branchName(upstream)])
      if (target && PROTECTED.has(target))
        block(`Blocked: this push would update ${target}. Open a PR instead.`);
    return;
  }

  for (const spec of refspecs) {
    const plain = spec.replace(/^\+/, "");
    let dst = plain.includes(":") ? plain.slice(plain.indexOf(":") + 1) : plain;
    if (dst === "HEAD" || dst === "@") dst = currentBranch(dir);
    if (PROTECTED.has(branchName(dst)))
      block(`Blocked: tech may not push to ${branchName(dst)}. Open a PR instead.`);
  }
}

try {
  const input = await readInput();
  const command = input.tool_input?.command ?? "";
  const cwd = input.cwd ?? process.cwd();

  for (const m of command.matchAll(PUSH))
    checkPush(argsAfter(command, m.index + m[0].length), gitDir(m[0], cwd));

  for (const m of command.matchAll(MERGE)) {
    const branch = currentBranch(gitDir(m[0], cwd));
    if (PROTECTED.has(branch)) block(`Blocked: tech may not merge into ${branch}.`);
  }

  for (const m of command.matchAll(GH)) {
    const kind = m[1] ?? "";
    if (!kind.startsWith("api"))
      block(`Blocked: tech may not run \`gh ${kind}\`; merging into main is the user's call.`);
    if (GH_API_RISKY.test(argsAfter(command, m.index + m[0].length).join(" ")))
      block("Blocked: this gh api call can merge or move main/master.");
  }
} catch (error) {
  block(`Main-branch guard error, blocking to be safe: ${(error as Error).message}`);
}

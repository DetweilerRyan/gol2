// Validates .board/ task files against the rules in .board/README.md. Exits 1 on any violation.
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";

const BOARD = ".board";
const LANES = ["backlog", "ready", "active", "blocked", "review", "done"] as const;
const OTHER_ENTRIES = new Set(["README.md", "retros"]);
const FILE_NAME = /^(T-\d{4})-[a-z0-9-]+\.md$/;

type Lane = (typeof LANES)[number];

interface Task {
  id: string;
  lane: Lane;
  path: string;
  claimedBy: string | null;
  dependsOn: string[];
}

const errors: string[] = [];
const tasks = new Map<string, Task>();

const isNonEmptyString = (value: unknown): value is string =>
  typeof value === "string" && value.trim().length > 0;
const asList = (value: unknown): unknown[] | undefined =>
  Array.isArray(value) ? value : undefined;
const optionalName = (value: unknown): string | null | "invalid" =>
  value === null || value === undefined ? null : isNonEmptyString(value) ? value : "invalid";

// Anything unexpected at the top level is probably a misspelled lane whose tasks would go unchecked.
for (const entry of existsSync(BOARD) ? readdirSync(BOARD) : []) {
  if (
    !(LANES as readonly string[]).includes(entry) &&
    !OTHER_ENTRIES.has(entry) &&
    entry !== ".gitkeep"
  ) {
    errors.push(`${BOARD}/${entry}: unknown entry; lanes are ${LANES.join(", ")}`);
  }
}

for (const lane of LANES) {
  const dir = join(BOARD, lane);
  if (!existsSync(dir)) continue;

  for (const name of readdirSync(dir)) {
    if (name === ".gitkeep") continue;
    const path = join(dir, name);
    const fail = (message: string) => errors.push(`${path}: ${message}`);

    if (statSync(path).isDirectory()) {
      fail("lanes hold task files only, not directories");
      continue;
    }
    const fileId = FILE_NAME.exec(name)?.[1];
    if (!fileId) {
      fail("file name must be <T-0000>-<slug>.md");
      continue;
    }

    const source = readFileSync(path, "utf8").replaceAll("\r\n", "\n");
    const frontmatter = /^---\n([\s\S]*?)\n---(?:\n|$)/.exec(source)?.[1];
    if (frontmatter === undefined) {
      fail("missing YAML frontmatter");
      continue;
    }

    let data: Record<string, unknown>;
    try {
      const parsed: unknown = parse(frontmatter);
      if (typeof parsed !== "object" || parsed === null)
        throw new Error("frontmatter is not a mapping");
      data = parsed as Record<string, unknown>;
    } catch (error) {
      fail(`invalid YAML: ${(error as Error).message}`);
      continue;
    }

    if (data.id !== fileId) fail(`id "${String(data.id)}" must match the file name (${fileId})`);
    const duplicate = tasks.get(fileId);
    if (duplicate) fail(`duplicate id ${fileId} (also ${duplicate.path})`);
    if (!isNonEmptyString(data.title)) fail("title is required");

    const dependsOn = asList(data.depends_on);
    if (!dependsOn) fail("depends_on must be a list");

    const acceptance = asList(data.acceptance);
    if (!acceptance) fail("acceptance must be a list");
    else if (!acceptance.every(isNonEmptyString))
      fail("acceptance criteria must be non-empty strings");
    else if (lane !== "backlog" && acceptance.length === 0) {
      fail("acceptance criteria are required outside backlog/");
    }

    const claimedBy = optionalName(data.claimed_by);
    const verifiedBy = optionalName(data.verified_by);
    if (claimedBy === "invalid") fail("claimed_by must be an agent name or null");
    if (verifiedBy === "invalid") fail("verified_by must be an agent name or null");

    const claimedLanes: Lane[] = ["active", "blocked", "review", "done"];
    if (claimedLanes.includes(lane) && !claimedBy) fail(`${lane}/ tasks need claimed_by`);
    if ((lane === "backlog" || lane === "ready") && claimedBy)
      fail(`${lane}/ tasks must not be claimed`);

    const evidence = asList(data.evidence);
    if (!evidence) fail("evidence must be a list");
    else {
      evidence.forEach((item, i) => {
        const entry = (typeof item === "object" && item !== null ? item : {}) as Record<
          string,
          unknown
        >;
        const missing = ["criterion", "command", "result"].filter(
          (field) => !isNonEmptyString(entry[field]),
        );
        if (missing.length > 0) fail(`evidence[${i}] needs non-empty ${missing.join(", ")}`);
        else if (acceptance && !acceptance.includes(entry.criterion)) {
          fail(`evidence[${i}].criterion doesn't match any acceptance criterion`);
        }
      });
    }

    if (lane === "done") {
      const covered = new Set(
        (evidence ?? []).map((item) => (item as Record<string, unknown> | null)?.criterion),
      );
      const unverified = (acceptance ?? []).filter((criterion) => !covered.has(criterion));
      if (unverified.length > 0) fail(`done/ needs evidence for: ${unverified.join("; ")}`);
      if (!verifiedBy) fail("done/ tasks need verified_by");
      else if (verifiedBy === claimedBy) fail("verified_by must differ from claimed_by");
    } else if (verifiedBy) {
      fail("only done/ tasks have verified_by");
    }

    tasks.set(fileId, {
      id: fileId,
      lane,
      path,
      claimedBy: claimedBy === "invalid" ? null : claimedBy,
      dependsOn: (dependsOn ?? []).map(String),
    });
  }
}

// WIP = 1 per agent across active/ and blocked/.
const wip = new Map<string, string[]>();
for (const task of tasks.values()) {
  if ((task.lane !== "active" && task.lane !== "blocked") || !task.claimedBy) continue;
  wip.set(task.claimedBy, [...(wip.get(task.claimedBy) ?? []), task.id]);
}
for (const [agent, ids] of wip) {
  if (ids.length > 1) {
    errors.push(`${agent} holds ${ids.length} tasks (${ids.join(", ")}); WIP limit is 1`);
  }
}

// Dependencies must exist, be done before a task leaves backlog/, and not form a cycle.
for (const task of tasks.values()) {
  for (const dep of task.dependsOn) {
    const target = tasks.get(dep);
    if (!target) errors.push(`${task.path}: depends_on ${dep}, which doesn't exist`);
    else if (task.lane !== "backlog" && task.lane !== "done" && target.lane !== "done") {
      errors.push(`${task.path}: depends_on ${dep}, which is in ${target.lane}/, not done/`);
    }
  }
}

const visiting = new Set<string>();
const visited = new Set<string>();
const reportedCycles = new Set<string>();
function visit(id: string, trail: string[]): void {
  if (visited.has(id)) return;
  if (visiting.has(id)) {
    const cycle = [...trail.slice(trail.indexOf(id)), id];
    const signature = [...new Set(cycle)].sort().join(",");
    if (!reportedCycles.has(signature)) {
      reportedCycles.add(signature);
      errors.push(`dependency cycle: ${cycle.join(" -> ")}`);
    }
    return;
  }
  visiting.add(id);
  for (const dep of tasks.get(id)?.dependsOn ?? []) if (tasks.has(dep)) visit(dep, [...trail, id]);
  visiting.delete(id);
  visited.add(id);
}
for (const id of tasks.keys()) visit(id, []);

if (errors.length > 0) {
  console.error(`Board check failed:\n${errors.map((e) => `  - ${e}`).join("\n")}`);
  process.exit(1);
}
console.log(`Board OK: ${tasks.size} task(s).`);

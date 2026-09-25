// Build the two study variants of the coach as a `claude --agents` JSON object.
// Usage: LSP_INSTRUCTION=<text> node make_agents.mjs <coach.md> <baseline|lsp> > agents.json
// Both variants keep the role file's description, tools, hooks, and body. The lsp variant adds only the LSP tool
// and the one-line instruction in LSP_INSTRUCTION (tasks.json's lsp_instruction), placed right after the Reference section's "read before citing" sentence.
import { readFileSync } from "node:fs";
import { parse } from "yaml";

const LSP_INSTRUCTION = process.env.LSP_INSTRUCTION;
// The sentence wraps in the role file, so match any whitespace between its words.
const ANCHOR =
  /Read a page,\s+including\s+its\s+"When\s+this\s+backfires"\s+section,\s+before\s+citing\s+it\./;

const [file, condition] = process.argv.slice(2);
if (!file || !["baseline", "lsp"].includes(condition)) {
  console.error("usage: node make_agents.mjs <coach.md> <baseline|lsp>");
  process.exit(1);
}
const match = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(readFileSync(file, "utf8"));
if (!match) throw new Error(`${file} has no frontmatter`);
const front = parse(match[1]);
let body = match[2].trim();
let tools = front.tools.split(",").map((t) => t.trim());

if (condition === "lsp") {
  if (!LSP_INSTRUCTION) throw new Error("LSP_INSTRUCTION is not set");
  if (!ANCHOR.test(body)) throw new Error("anchor sentence not found in the role file");
  body = body.replace(ANCHOR, (sentence) => `${sentence} ${LSP_INSTRUCTION}`);
  tools = [...tools, "LSP"];
}

const agent = { description: front.description, prompt: body, tools };
if (front.hooks) agent.hooks = front.hooks;
if (front.model) agent.model = front.model;
process.stdout.write(`${JSON.stringify({ [front.name]: agent }, null, 2)}\n`);

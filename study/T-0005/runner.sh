#!/bin/bash
# Run one coach review for T-0005's benefit study in an isolated environment.
#
# Usage: runner.sh <task: T-0001|T-0004|set> <condition: baseline|lsp> <run-id>
#
# Each run gets a bubblewrap sandbox holding only: a fresh clone of the task's snapshot commit (one branch, no tags,
# no remote, no reflog) at /study/gol2, a checkout of agentpatterns at the pinned commit at /study/agentpatterns
# (so the coach's `../agentpatterns` resolves), and a home directory with a Claude config directory of its own.
# The host's gol2 and agentpatterns checkouts and its home directory (including ~/.claude/projects/) aren't mounted.
# preflight.sh prints the isolation evidence inside the sandbox; the run is refused unless every check passes.
#
# Run it from a session that isn't worktree-isolated (a worktree-isolated session refuses to start a nested
# `claude` session that has Bash). Everything it writes goes under $STUDY_BASE, outside the repo:
#   runs/<run-id>/out/      committable: preflight.txt, stream.jsonl, result.json, transcript.jsonl (all redacted)
#   runs/<run-id>/private/  never committed: raw transcript and stream, stderr
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
GOL2=${GOL2_REPO:-/c/Users/User/Documents/projects/gol2}
AP=${AGENTPATTERNS_REPO:-/c/Users/User/Documents/projects/agentpatterns}
BASE=${STUDY_BASE:-$HOME/.local/share/gol2-study/T-0005}
NODE_MODULES=${GOL2_NODE_MODULES:-$HOME/.local/share/gol2/node_modules}
TOOLS=$BASE/tools
MAX_USD=${MAX_USD:-10}
TIMEOUT=${RUN_TIMEOUT:-45m}

task=${1:?task} condition=${2:?condition} run_id=${3:?run id}
[[ $condition == baseline || $condition == lsp ]] || { echo "condition must be baseline or lsp" >&2; exit 1; }
cfg() { python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {}, {"d": d}))' "$HERE/tasks.json" "$1"; }
cfg "d['tasks']['$task']" >/dev/null || { echo "unknown task $task" >&2; exit 1; }
snapshot=$(git -C "$GOL2" rev-parse "$(cfg "d['tasks']['$task']['snapshot']")^{commit}")
ap_commit=$(cfg "d['agentpatterns_commit']")
prompt=${PROMPT_OVERRIDE:-$(cfg "d['tasks']['$task']['prompt']")}  # PROMPT_OVERRIDE: setup runs only, never pilot or study runs
model=$(cfg "d['model']") effort=$(cfg "d['effort']")

RUN=$BASE/runs/$run_id
[ -e "$RUN" ] && { echo "refusing: $RUN already exists" >&2; exit 1; }

# Host-side checks: pinned tool versions, and an access token that outlives the run.
claude_bin=$(readlink -f "$(command -v claude)")
[ "$("$claude_bin" --version | cut -d' ' -f1)" = "$(cfg "d['claude_code_version']")" ] || { echo "refusing: Claude Code version differs from tasks.json" >&2; exit 1; }
[ "$(sha256sum "$TOOLS/rumdl" | cut -d' ' -f1)" = "$(cfg "d['rumdl_sha256']")" ] || { echo "refusing: rumdl binary differs from tasks.json" >&2; exit 1; }
python3 - "$HOME/.claude/.credentials.json" <<'EOF' || { echo "refusing: access token expires within 2 hours; refresh the host login first" >&2; exit 1; }
import json, sys, time
sys.exit(0 if json.load(open(sys.argv[1]))["claudeAiOauth"]["expiresAt"] / 1000 - time.time() > 7200 else 1)
EOF

mkdir -p "$RUN/study/home/.claude" "$RUN/out" "$RUN/private" "$RUN/opt"
echo "task=$task condition=$condition snapshot=$snapshot agentpatterns=$ap_commit prompt_override=${PROMPT_OVERRIDE:+yes}" > "$RUN/out/run.txt"

# Pinned agentpatterns template, built once and copied per run: only the pinned commit, no remote, no other refs.
tmpl=$BASE/agentpatterns-${ap_commit:0:7}
if [ ! -d "$tmpl/.git" ]; then
  git init -q "$tmpl"
  git -C "$tmpl" fetch -q --depth 1 --no-tags "$AP" "$ap_commit"
  git -C "$tmpl" checkout -q -b main FETCH_HEAD
  rm -f "$tmpl/.git/FETCH_HEAD" "$tmpl/.git/shallow.lock"
  git -C "$tmpl" reflog expire --expire=now --all
fi
cp -a "$tmpl" "$RUN/study/agentpatterns"

# gol2 snapshot clone: the snapshot commit and its ancestors on one branch, nothing else.
git init -q -b main "$RUN/study/gol2"
git -C "$RUN/study/gol2" fetch -q --no-tags "$GOL2" "$snapshot"
git -C "$RUN/study/gol2" reset -q --hard FETCH_HEAD
rm -f "$RUN/study/gol2/.git/FETCH_HEAD" "$RUN/study/gol2/.git/ORIG_HEAD"
git -C "$RUN/study/gol2" config core.hooksPath .githooks
git -C "$RUN/study/gol2" reflog expire --expire=now --all
git -C "$RUN/study/gol2" gc -q --prune=now
mkdir -p "$RUN/study/gol2/node_modules"

# Agent definitions from the snapshot's own coach role file.
node "$HERE/make_agents.mjs" "$RUN/study/gol2/.claude/agents/coach.md" "$condition" > "$RUN/opt/agents.json"
cp "$HERE/preflight.sh" "$RUN/opt/preflight.sh"

# Credentials: the access token only, so a run can never rotate the host's login.
python3 - "$HOME/.claude/.credentials.json" "$RUN/study/home/.claude/.credentials.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))["claudeAiOauth"]
keep = {k: d[k] for k in ("accessToken", "expiresAt", "scopes", "subscriptionType", "rateLimitTier") if k in d}
keep["refreshToken"] = None
open(sys.argv[2], "w").write(json.dumps({"claudeAiOauth": keep}))
EOF
chmod 600 "$RUN/study/home/.claude/.credentials.json"
token=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["claudeAiOauth"]["accessToken"])' "$RUN/study/home/.claude/.credentials.json")

SB=(bwrap --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/sbin /sbin
  --ro-bind /etc /etc --ro-bind /dev/null /etc/sandbox-persistent.sh --ro-bind /dev/null /etc/profile.d/sandbox-persistent.sh
  --proc /proc --dev /dev --tmpfs /tmp
  --bind "$RUN/study" /study --ro-bind "$NODE_MODULES" /study/gol2/node_modules
  --ro-bind "$TOOLS" /opt/study-tools --ro-bind "$RUN/opt" /opt/study-run --ro-bind "$claude_bin" /opt/claude/claude
  --unshare-pid --unshare-ipc --unshare-uts --hostname study --die-with-parent --clearenv
  --setenv HOME /study/home --setenv CLAUDE_CONFIG_DIR /study/home/.claude --setenv USER study
  --setenv PATH /opt/claude:/usr/local/bin:/usr/bin:/bin --setenv TERM dumb --setenv LANG C.UTF-8
  --setenv HTTPS_PROXY "$HTTPS_PROXY" --setenv HTTP_PROXY "$HTTP_PROXY"
  --setenv https_proxy "$HTTPS_PROXY" --setenv http_proxy "$HTTP_PROXY"
  --setenv NO_PROXY "$NO_PROXY" --setenv no_proxy "$NO_PROXY" --setenv NODE_USE_ENV_PROXY 1
  --setenv NODE_EXTRA_CA_CERTS /etc/ssl/certs/ca-certificates.crt --setenv SSL_CERT_FILE /etc/ssl/certs/ca-certificates.crt
  --chdir /study/gol2)

if ! "${SB[@]}" /bin/bash /opt/study-run/preflight.sh "$snapshot" "$ap_commit" > "$RUN/private/preflight.txt" 2>&1; then
  cat "$RUN/private/preflight.txt"
  echo "refusing: preflight failed; see $RUN/private/preflight.txt" >&2
  exit 1
fi

args=(-p "$prompt" --agents /opt/study-run/agents.json --agent coach --model "$model" --effort "$effort"
  --permission-mode bypassPermissions --output-format stream-json --verbose --include-hook-events
  --max-budget-usd "$MAX_USD")
[ "$condition" = lsp ] && args+=(--plugin-dir /opt/study-tools/rumdl-lsp)
printf '%q ' claude "${args[@]}" > "$RUN/out/command.txt"; echo >> "$RUN/out/command.txt"

date -u +%FT%TZ > "$RUN/out/started.txt"
set +e
timeout "$TIMEOUT" "${SB[@]}" claude "${args[@]}" > "$RUN/private/stream.jsonl" 2> "$RUN/private/stderr.txt"
status=$?
set -e
date -u +%FT%TZ > "$RUN/out/finished.txt"
echo "$status" > "$RUN/out/exit-status.txt"

# Collect the session transcript, then remove the credentials from the run's directory.
find "$RUN/study/home/.claude/projects" -name '*.jsonl' -print0 2>/dev/null | xargs -0 -r cat > "$RUN/private/transcript.jsonl"
rm -f "$RUN/study/home/.claude/.credentials.json"

for f in preflight.txt stream.jsonl transcript.jsonl; do
  python3 "$HERE/redact.py" "$RUN/private/$f" "$RUN/out/$f" "$token"
done
python3 - "$RUN/out/stream.jsonl" "$RUN/out/result.json" <<'EOF'
import json, sys
result = None
for line in open(sys.argv[1]):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "result":
        result = d
json.dump(result, open(sys.argv[2], "w"), indent=2)
EOF
python3 "$HERE/redaction_scan.py" "$RUN"/out/* > "$RUN/out/redaction-scan.txt" || true
cat "$RUN/out/redaction-scan.txt"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])) or {}; print("exit", sys.argv[2], "| cost", d.get("total_cost_usd"), "| turns", d.get("num_turns"), "|", d.get("subtype"))' "$RUN/out/result.json" "$status"

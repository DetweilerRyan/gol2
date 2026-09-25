#!/bin/bash
# T-0005 pilot: 3 runs per condition on one review task, alternating conditions, run one at a time.
# Stops before starting a run once the pilot's spend passes PILOT_MAX_USD.
# Usage: pilot.sh [task]   (default T-0001)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
BASE=${STUDY_BASE:-$HOME/.local/share/gol2-study/T-0005}
task=${1:-T-0001}
limit=${PILOT_MAX_USD:-30}
spent() {
  python3 - "$BASE/runs" <<'EOF'
import glob, json, sys
total = 0.0
for f in glob.glob(f"{sys.argv[1]}/pilot-*/out/result.json"):
    total += (json.load(open(f)) or {}).get("total_cost_usd") or 0
print(f"{total:.2f}")
EOF
}
for i in 1 2 3; do
  for condition in baseline lsp; do
    s=$(spent)
    if python3 -c "import sys; sys.exit(0 if float('$s') >= $limit else 1)"; then
      echo "stopping: pilot spend \$$s reached the \$$limit limit"; exit 0
    fi
    id=pilot-$task-$condition-$i
    echo "== $(date -u +%T) $id (pilot spend so far \$$s)"
    MAX_USD=${MAX_USD:-8} bash "$HERE/runner.sh" "$task" "$condition" "$id" 2>&1 | tail -2
  done
done
echo "pilot done: spend \$$(spent)"

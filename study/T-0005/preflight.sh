#!/bin/bash
# Runs inside a run's sandbox before the coach session starts. Prints the isolation evidence and exits nonzero if
# any condition in T-0005's isolation criterion doesn't hold, so the runner refuses to start the run.
# Usage (inside the sandbox): preflight.sh <full snapshot sha> <full agentpatterns sha>
set -u
snap=$1 ap=$2 fail=0
check() { if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }

echo "== gol2 clone (/study/gol2)"
echo "\$ git rev-parse HEAD"; git -C /study/gol2 rev-parse HEAD
echo "\$ git for-each-ref"; git -C /study/gol2 for-each-ref
echo "\$ git remote"; git -C /study/gol2 remote
echo "\$ git reflog --all | wc -l"; git -C /study/gol2 reflog --all | wc -l
echo "\$ git stash list | wc -l"; git -C /study/gol2 stash list | wc -l
echo "== agentpatterns (/study/agentpatterns)"
echo "\$ git rev-parse HEAD"; git -C /study/agentpatterns rev-parse HEAD
echo "\$ git for-each-ref"; git -C /study/agentpatterns for-each-ref
echo "\$ git remote"; git -C /study/agentpatterns remote
echo "\$ realpath /study/gol2/../agentpatterns"; realpath /study/gol2/../agentpatterns
echo "== home ($HOME)"
echo "\$ find \$HOME -maxdepth 3"; find "$HOME" -maxdepth 3 | sort
echo "== filesystem roots"
echo "\$ ls /"; ls /
echo "\$ ls /study"; ls /study
echo "== environment"
echo "CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR"
echo "== checks"
check "clone HEAD is the snapshot" '[ "$(git -C /study/gol2 rev-parse HEAD)" = "$snap" ]'
check "clone has exactly one ref, refs/heads/main" '[ "$(git -C /study/gol2 for-each-ref --format="%(refname)")" = refs/heads/main ]'
check "clone has no remote" '[ -z "$(git -C /study/gol2 remote)" ]'
check "clone has no reflog entries" '[ "$(git -C /study/gol2 reflog --all | wc -l)" -eq 0 ]'
check "clone has no stash" '[ "$(git -C /study/gol2 stash list | wc -l)" -eq 0 ]'
check "clone working tree is clean" '[ -z "$(git -C /study/gol2 status --porcelain --ignored=no)" ]'
check "agentpatterns HEAD is the pinned commit" '[ "$(git -C /study/agentpatterns rev-parse HEAD)" = "$ap" ]'
check "agentpatterns has no remote" '[ -z "$(git -C /study/agentpatterns remote)" ]'
check "../agentpatterns resolves to the pinned checkout" '[ "$(realpath /study/gol2/../agentpatterns)" = /study/agentpatterns ]'
check "original gol2 and agentpatterns checkouts are absent" '[ ! -e /c ]'
check "the host home directory is absent" '[ ! -e /home ]'
check "config dir belongs to the run" '[ "$CLAUDE_CONFIG_DIR" = /study/home/.claude ]'
check "no earlier transcripts in the run's config dir" '[ ! -e /study/home/.claude/projects ] || [ -z "$(ls -A /study/home/.claude/projects)" ]'
check "no memory in the run's config dir" '[ -z "$(find /study/home -name MEMORY.md -o -name "*.memory*" 2>/dev/null)" ]'
exit $fail

#!/usr/bin/env bash
# Builds and starts the dev container on the current Docker daemon (e.g. inside a Docker sandbox).
set -euo pipefail
cd "$(dirname "$0")/.."
exec npx -y @devcontainers/cli@0 up --workspace-folder . "$@"

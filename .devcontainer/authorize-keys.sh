#!/usr/bin/env bash
# Installs the SSH public keys from .devcontainer/authorized_keys (gitignored, one key per line) for the node user.
set -euo pipefail
keys="$(dirname "$0")/authorized_keys"
if [ ! -s "$keys" ]; then
  echo "No $keys; add your host's public key there to SSH in." >&2
  exit 0
fi
install -d -m 700 ~/.ssh
install -m 600 "$keys" ~/.ssh/authorized_keys

#!/usr/bin/env bash
# Run hackmd.py inside a throwaway python:3.12-slim container.
# HACKMD_API_TOKEN is auto-loaded from .env if present, or read from the shell env.
# Usage: ./hackmd.sh list
#        ./hackmd.sh get <noteId>
#        ./hackmd.sh create note.md --title "Hello"
#        ./hackmd.sh update <noteId> note.md
#        ./hackmd.sh delete <noteId>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-load HACKMD_API_TOKEN from .env when not already exported.
if [[ -z "${HACKMD_API_TOKEN:-}" && -f "${SCRIPT_DIR}/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/.env"
    set +a
fi

if [[ -z "${HACKMD_API_TOKEN:-}" ]]; then
    echo "HACKMD_API_TOKEN env var is required (set in .env or export it)" >&2
    exit 1
fi

# -i so stdin can be piped in (`echo '# md' | ./hackmd.sh create -`)
# --network host is unnecessary; bridge is fine for outbound HTTPS
exec docker run --rm -i \
    -e HACKMD_API_TOKEN \
    -v "${SCRIPT_DIR}:/app" \
    -w /app \
    python:3.12-slim \
    python hackmd.py "$@"

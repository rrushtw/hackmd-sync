#!/usr/bin/env bash
# Run hackmd.py inside a throwaway python:3.12-slim container.
# Usage: HACKMD_API_TOKEN=xxx ./hackmd.sh list
#        HACKMD_API_TOKEN=xxx ./hackmd.sh get <noteId>
#        HACKMD_API_TOKEN=xxx ./hackmd.sh create note.md --title "Hello"
#        HACKMD_API_TOKEN=xxx ./hackmd.sh update <noteId> note.md
#        HACKMD_API_TOKEN=xxx ./hackmd.sh delete <noteId>
set -euo pipefail

if [[ -z "${HACKMD_API_TOKEN:-}" ]]; then
    echo "HACKMD_API_TOKEN env var is required" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -i so stdin can be piped in (`echo '# md' | ./hackmd.sh create -`)
# --network host is unnecessary; bridge is fine for outbound HTTPS
exec docker run --rm -i \
    -e HACKMD_API_TOKEN \
    -v "${SCRIPT_DIR}:/app" \
    -w /app \
    python:3.12-slim \
    python hackmd.py "$@"

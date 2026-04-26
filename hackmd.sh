#!/usr/bin/env bash
# Run hackmd.py via a self-contained Docker image (hackmd-sync:local) that
# bakes the script in. The image is auto-built on first run and rebuilt
# whenever hackmd.py is newer than the existing image.
#
# HACKMD_API_TOKEN is auto-loaded from .env if present, or read from the
# shell env.
#
# File arguments resolve against $PWD (the current working directory), which
# is mounted at /workdir inside the container. So `./hackmd.sh create note.md`
# reads $PWD/note.md regardless of which directory you ran from.
#
# Usage: ./hackmd.sh list
#        ./hackmd.sh get <noteId>
#        ./hackmd.sh create note.md --title "Hello" --tag draft
#        ./hackmd.sh update <noteId> note.md --tag final
#        ./hackmd.sh delete <noteId>
#
# Requires GNU coreutils (`stat -c`, `date -d`).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="hackmd-sync:local"

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

# Build the image if it is missing or stale (hackmd.py newer than image).
needs_build=0
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    needs_build=1
else
    script_mtime=$(stat -c %Y "$SCRIPT_DIR/hackmd.py")
    image_iso=$(docker image inspect --format '{{.Created}}' "$IMAGE")
    image_mtime=$(date -d "$image_iso" +%s)
    if [[ $script_mtime -gt $image_mtime ]]; then
        needs_build=1
    fi
fi

if [[ $needs_build -eq 1 ]]; then
    echo "Building $IMAGE..." >&2
    docker build -t "$IMAGE" "$SCRIPT_DIR" >&2
fi

# -i so stdin can be piped in (`echo '# md' | ./hackmd.sh create -`).
# -v $PWD:/workdir mounts the current directory so file arguments work.
exec docker run --rm -i \
    -e HACKMD_API_TOKEN \
    -v "$PWD:/workdir" \
    -w /workdir \
    "$IMAGE" "$@"

# hackmd-sync

A tiny Python CLI to pull / push / create / update / delete HackMD notes through the official API. Stdlib only — no runtime dependencies.

## Setup

1. Get an API token: HackMD → Settings → API → **Create API token**.
2. Copy `.env.example` to `.env` and fill in your token:
    ```bash
    cp .env.example .env
    # edit .env: HACKMD_API_TOKEN=...
    ```

## Run

### Inside VS Code Dev Container (recommended)

Open the folder in VS Code → "Reopen in Container". The `.env` is loaded automatically.

```bash
python hackmd.py list
python hackmd.py get <noteId> > note.md
python hackmd.py update <noteId> note.md
python hackmd.py create note.md --title "Demo"
python hackmd.py delete <noteId>
```

### One-shot from host (no devcontainer)

`hackmd.sh` runs the script via a self-contained Docker image (`hackmd-sync:local`) built from `Dockerfile`. The image is auto-built on first use and rebuilt whenever `hackmd.py` changes (mtime comparison). It auto-loads `HACKMD_API_TOKEN` from `.env` (or from your shell environment):

```bash
./hackmd.sh list
./hackmd.sh get <noteId> > note.md
echo "# inline md" | ./hackmd.sh create - --title "From stdin"
```

File arguments resolve against your **current working directory** (mounted at `/workdir` inside the container). So `./hackmd.sh create note.md` reads `$PWD/note.md` regardless of which directory you run from.

## Subcommands

| Command | Description |
| :--- | :--- |
| `list` | List notes in your own workspace (id + title). Does **not** include notes shared with you — see [Notes shared with you](#notes-shared-with-you). |
| `get <noteId> [--meta]` | Print markdown to stdout (`--meta` for full JSON) |
| `create <file> [--title T] [--tag T ...] [--read-perm P] [--write-perm P]` | Create a note (`-` reads stdin). `--tag` is repeatable. |
| `update <noteId> <file> [--tag T ...] [--clear-tags]` | Replace note content (`-` reads stdin). `--tag` replaces existing tags; `--clear-tags` empties them; pass neither to leave tags unchanged. |
| `delete <noteId>` | Delete a note (owner only — see [Notes shared with you](#notes-shared-with-you)) |

## Notes shared with you

The HackMD API's `GET /v1/notes` only returns notes in **your own workspace** (notes you created / own). Notes that someone else owns and has shared with you — even with edit permission — **do not appear in `list`**. This is a HackMD API limitation, not a `hackmd-sync` bug.

To work with a shared note you must already know its `noteId` (the segment after `https://hackmd.io/` in the share link). Once you have it:

| Operation | Works on shared note? | Why |
| :--- | :--- | :--- |
| `get <noteId>` | ✅ if you have read permission | API checks per-note permission, not ownership |
| `update <noteId>` | ✅ if you have write permission | Only `content` (and optional `tags`) are sent — no permission fields |
| `delete <noteId>` | ❌ owner-only | The API returns HTTP 403 for non-owners |

Practical workflow for syncing shared notes: keep a small manifest (e.g. `.hackmd-notes.json` mapping local path → noteId) in the project that uses them, and loop `./hackmd.sh get <id> > <path>` over it.

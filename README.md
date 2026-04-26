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
| `list` | List all your notes (id + title) |
| `get <noteId> [--meta]` | Print markdown to stdout (`--meta` for full JSON) |
| `create <file> [--title T] [--tag T ...] [--read-perm P] [--write-perm P]` | Create a note (`-` reads stdin). `--tag` is repeatable. |
| `update <noteId> <file> [--tag T ...] [--clear-tags]` | Replace note content (`-` reads stdin). `--tag` replaces existing tags; `--clear-tags` empties them; pass neither to leave tags unchanged. |
| `delete <noteId>` | Delete a note |

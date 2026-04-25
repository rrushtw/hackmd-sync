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

`hackmd.sh` runs the script in a throwaway `python:3.12-slim` container:

```bash
export HACKMD_API_TOKEN=your_token
./hackmd.sh list
./hackmd.sh get <noteId> > note.md
echo "# inline md" | ./hackmd.sh create - --title "From stdin"
```

## Subcommands

| Command | Description |
| :--- | :--- |
| `list` | List all your notes (id + title) |
| `get <noteId> [--meta]` | Print markdown to stdout (`--meta` for full JSON) |
| `create <file> [--title T] [--read-perm P] [--write-perm P]` | Create a note (`-` reads stdin) |
| `update <noteId> <file>` | Replace note content (`-` reads stdin) |
| `delete <noteId>` | Delete a note |

# hackmd-sync — guide for Claude

A small Python CLI for CRUD on HackMD notes via the official API. Designed so Claude can drive it on the user's behalf.

## When to use this tool

When the user asks Claude to **pull / read / fetch / list / create / update / delete** a HackMD note, run `./hackmd.sh <subcommand>` from the repo root. `HACKMD_API_TOKEN` is auto-loaded from `.env`.

See `README.md` for the full subcommand reference.

## Conventions

- **Prefer id over title**: if the user gives a note id, use it directly with `./hackmd.sh get <id>`. Only when they give just a title, run `./hackmd.sh list` first to resolve the id, then `get <id>`.
- **Save before edit**: when the user wants to edit a note, write the fetched markdown to a local file first (`./hackmd.sh get <id> > note.md`), so changes can be diffed before being pushed back with `update`.
- **Confirm destructive ops**: always check with the user before `delete`, or before an `update` that overwrites a note Claude has not just fetched.
- **No allowlist**: each `./hackmd.sh` call will trigger a permission prompt; this is intentional. Do not add the script to `.claude/settings.json`.

## Ownership scope (shared / non-owned notes)

`./hackmd.sh list` calls `GET /v1/notes`, which only returns notes in the user's **own workspace** (notes they own). Notes that someone else owns and shared with them — even with edit permission — **do not appear** in `list`. This is a HackMD API limitation; do not assume a missing note from `list` means the note doesn't exist.

Per-note operations on a known `noteId` work the same regardless of ownership, because the API gates them on per-note permission rather than ownership:

- `get <noteId>` works if the user has read permission.
- `update <noteId>` works if the user has write permission. The CLI sends only `content` (and `tags` when explicitly requested) — it never sends `readPermission` / `writePermission`, so it won't trip the "only owner can change permissions" rule.
- `delete <noteId>` is owner-only and will fail with HTTP 403 on a shared note. The CLI surfaces a hint in stderr when this happens.

When the user references a note by URL or share link, extract the `noteId` from the path segment after `https://hackmd.io/` and use `get` / `update` directly — do not first `list` to "find" it.

## Execution environment

- **No host `python3` for project code**: do not run `python3 hackmd.py ...` (or import the project) on the host. Use `./hackmd.sh ...` — it runs the script via the self-contained `hackmd-sync:local` image (auto-built from `Dockerfile` on first run and whenever `hackmd.py` changes).
- **File arguments resolve against `$PWD`**: `./hackmd.sh` mounts the current working directory at `/workdir` inside the container. So `./hackmd.sh create note.md` reads `$PWD/note.md`. Files outside `$PWD` (e.g. `/tmp/foo.md`) are NOT visible — pipe via stdin (`cat /tmp/foo.md | ./hackmd.sh create -`) or `cd` to the file's directory first.
- **Ad-hoc Python scripts**: when writing a one-off Python script (test scaffolding, external-system simulation, browser automation, etc.), run it via `docker run --rm ...` with an image appropriate for the task — Claude picks the image based on what the script needs (`python:3.12-slim` for stdlib, `mcr.microsoft.com/playwright/python` for browser automation, etc.). Never `pip install` packages on the host.
- **Stdlib-only JSON parsing on host is OK** — e.g. `./hackmd.sh get <id> --meta | python3 -c "import sys, json; ..."` for inspecting output. It is an output filter, not project execution, and installs no packages.
- **Anything else that needs host `python3`**: stop and ask the user for temporary permission, with a brief justification of why the container path will not work.

## Tags

- **Set tags with `--tag` (repeatable)** on `create` or `update`: `./hackmd.sh create note.md --title T --tag work --tag draft`.
- **`update` preserves tags by default** — an `update` with no `--tag` will not touch existing tags. To wipe them, pass `--clear-tags`.
- **Do NOT use YAML front-matter** (e.g. `tags: foo, bar` at the top of the markdown) to set tags. HackMD's editor parses front-matter on Ctrl+S, but the API does not — so tags set that way only appear after a human opens and saves the note in the UI.

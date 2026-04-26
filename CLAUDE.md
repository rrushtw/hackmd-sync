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

## Tags

- **Set tags with `--tag` (repeatable)** on `create` or `update`: `./hackmd.sh create note.md --title T --tag work --tag draft`.
- **`update` preserves tags by default** — an `update` with no `--tag` will not touch existing tags. To wipe them, pass `--clear-tags`.
- **Do NOT use YAML front-matter** (e.g. `tags: foo, bar` at the top of the markdown) to set tags. HackMD's editor parses front-matter on Ctrl+S, but the API does not — so tags set that way only appear after a human opens and saves the note in the UI.

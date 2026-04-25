#!/usr/bin/env python3
"""HackMD API client — list / get / create / update / delete notes.

Uses Python stdlib only (no pip install needed). Auth via HACKMD_TOKEN env var.
Get a token at: HackMD → Settings → API → Create API token.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.hackmd.io/v1"


def request(method, path, token, payload=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"HTTP {e.code} {e.reason}: {e.read().decode('utf-8', 'replace')}\n")
        sys.exit(1)


def cmd_list(args, token):
    notes = request("GET", "/notes", token)
    for n in notes:
        print(f"{n['id']}\t{n.get('title', '(untitled)')}")


def cmd_get(args, token):
    note = request("GET", f"/notes/{args.note_id}", token)
    if args.meta:
        print(json.dumps(note, indent=2, ensure_ascii=False))
    else:
        sys.stdout.write(note["content"])


def cmd_create(args, token):
    content = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    payload = {
        "title": args.title,
        "content": content,
        "readPermission": args.read_perm,
        "writePermission": args.write_perm,
    }
    note = request("POST", "/notes", token, payload)
    print(f"Created: {note['id']}\t{note.get('publishLink', '')}")


def cmd_update(args, token):
    content = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    request("PATCH", f"/notes/{args.note_id}", token, {"content": content})
    print(f"Updated: {args.note_id}")


def cmd_delete(args, token):
    request("DELETE", f"/notes/{args.note_id}", token)
    print(f"Deleted: {args.note_id}")


def main():
    parser = argparse.ArgumentParser(description="HackMD API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List your notes").set_defaults(func=cmd_list)

    p_get = sub.add_parser("get", help="Print a note's markdown to stdout")
    p_get.add_argument("note_id")
    p_get.add_argument("--meta", action="store_true", help="Print full JSON instead of content")
    p_get.set_defaults(func=cmd_get)

    p_create = sub.add_parser("create", help="Create a note from a file ('-' for stdin)")
    p_create.add_argument("file")
    p_create.add_argument("--title", default="Untitled")
    p_create.add_argument("--read-perm", default="owner", choices=["owner", "signed_in", "guest"])
    p_create.add_argument("--write-perm", default="owner", choices=["owner", "signed_in", "guest"])
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update", help="Replace a note's content from a file ('-' for stdin)")
    p_update.add_argument("note_id")
    p_update.add_argument("file")
    p_update.set_defaults(func=cmd_update)

    p_del = sub.add_parser("delete", help="Delete a note")
    p_del.add_argument("note_id")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()

    token = os.environ.get("HACKMD_API_TOKEN")
    if not token:
        sys.exit("HACKMD_API_TOKEN env var is required")
    args.func(args, token)


if __name__ == "__main__":
    main()

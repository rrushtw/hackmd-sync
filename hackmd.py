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


class HackMDHTTPError(Exception):
    def __init__(self, code, reason, body):
        self.code = code
        self.reason = reason
        self.body = body
        super().__init__(f"HTTP {code} {reason}: {body}")


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
        body = e.read().decode("utf-8", "replace")
        raise HackMDHTTPError(e.code, e.reason, body)


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
    if args.tag:
        payload["tags"] = args.tag
    note = request("POST", "/notes", token, payload)
    print(f"Created: {note['id']}\t{note.get('publishLink', '')}")


def cmd_update(args, token):
    content = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    payload = {"content": content}
    if args.clear_tags:
        payload["tags"] = []
    elif args.tag:
        payload["tags"] = args.tag
    try:
        request("PATCH", f"/notes/{args.note_id}", token, payload)
    except HackMDHTTPError as patch_err:
        if patch_err.code != 403:
            raise
        # HackMD's API has been observed to return 403 even when the PATCH
        # actually persisted server-side. Re-fetch and compare what we sent;
        # if everything matches, treat as success.
        try:
            note = request("GET", f"/notes/{args.note_id}", token)
        except HackMDHTTPError:
            raise patch_err
        mismatched = []
        if note.get("content") != payload["content"]:
            mismatched.append("content")
        if "tags" in payload and (note.get("tags") or []) != payload["tags"]:
            mismatched.append("tags")
        if mismatched:
            sys.stderr.write(
                f"PATCH returned 403 and these fields did not persist: "
                f"{', '.join(mismatched)}\n"
            )
            raise patch_err
        sys.stderr.write(
            "Warning: PATCH returned HTTP 403, but a follow-up GET shows all "
            "sent fields persisted. Treating as success (HackMD's API "
            "occasionally reports 403 on a PATCH that actually succeeded).\n"
        )
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
    p_create.add_argument("--tag", action="append", default=[],
                          help="Tag to attach (repeatable). e.g. --tag work --tag draft")
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update", help="Replace a note's content from a file ('-' for stdin)")
    p_update.add_argument("note_id")
    p_update.add_argument("file")
    update_tags = p_update.add_mutually_exclusive_group()
    update_tags.add_argument("--tag", action="append", default=[],
                             help="Replace tags (repeatable). Omit to leave existing tags unchanged.")
    update_tags.add_argument("--clear-tags", action="store_true",
                             help="Remove all tags from the note.")
    p_update.set_defaults(func=cmd_update)

    p_del = sub.add_parser("delete", help="Delete a note")
    p_del.add_argument("note_id")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()

    token = os.environ.get("HACKMD_API_TOKEN")
    if not token:
        sys.exit("HACKMD_API_TOKEN env var is required")
    try:
        args.func(args, token)
    except HackMDHTTPError as e:
        sys.stderr.write(f"{e}\n")
        if e.code == 403:
            sys.stderr.write(
                "Hint: 403 usually means you are not the owner of this note. "
                "Only the owner can delete a note or change its permissions; "
                "shared collaborators can only get/update content.\n"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()

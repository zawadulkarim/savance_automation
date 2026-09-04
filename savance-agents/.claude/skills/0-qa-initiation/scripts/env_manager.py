#!/usr/bin/env python
"""Check and merge QA credentials in a .env file without clobbering it.

Two modes:

  check   Report which canonical keys are present (masked) and which are
          missing. Exit 0 if all present, 1 if any are missing.

  merge   Merge new key=value pairs into the file. Existing lines, comments,
          blank lines and ordering are preserved; a key that already exists is
          updated in place, a new key is appended under a dated header. The
          existing file is backed up first.

Values are read as JSON on stdin, never from argv, so secrets stay out of the
shell history and the process list:

    echo '{"TEST_SERVER_URL":"https://..."}' | python env_manager.py merge --file .env

Canonical keys and the aliases already-in-the-wild that count as satisfying
them are declared in SCHEMA below. Alias matching is case-insensitive, which
is what lets a pre-existing lowercase `asana_token` satisfy
ASANA_ACCESS_TOKEN instead of being duplicated.
"""

import argparse
import datetime
import io
import json
import os
import re
import sys

# canonical key -> (aliases that also satisfy it, is_secret, prompt label)
SCHEMA = [
    ("TEST_SERVER_URL",
     ["TEST_URL", "SERVER_URL", "BASE_URL"],
     False,
     "Test server URL (e.g. https://test.savanceworkplace.com/)"),
    ("TEST_USERNAME",
     ["TEST_USER", "USERNAME", "QA_USERNAME"],
     False,
     "Test account username"),
    ("TEST_PASSWORD",
     ["TEST_PASS", "PASSWORD", "QA_PASSWORD"],
     True,
     "Test account password"),
    ("ASANA_ACCESS_TOKEN",
     ["asana_token", "ASANA_TOKEN", "ASANA_PAT"],
     True,
     "Asana personal access token"),
]

LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")


def parse(path):
    """Return (lines, {UPPER_KEY: (line_index, raw_key, value)})."""
    if not os.path.exists(path):
        return [], {}
    with io.open(path, encoding="utf-8-sig") as fh:
        lines = fh.read().splitlines()
    found = {}
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            raw = raw[1:-1]
        found[key.upper()] = (i, key, raw)
    return lines, found


def mask(value, secret):
    if not value:
        return "(empty)"
    if not secret:
        return value
    if len(value) <= 6:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def resolve(found, canonical, aliases):
    """Find canonical or any alias. Returns (raw_key, value) or None."""
    for name in [canonical] + aliases:
        hit = found.get(name.upper())
        if hit and hit[2]:
            return hit[1], hit[2]
    return None


def do_check(path):
    lines, found = parse(path)
    exists = os.path.exists(path)
    report = {
        "file": os.path.abspath(path),
        "exists": exists,
        "present": [],
        "missing": [],
    }
    for canonical, aliases, secret, label in SCHEMA:
        hit = resolve(found, canonical, aliases)
        if hit:
            raw_key, value = hit
            report["present"].append({
                "key": canonical,
                "stored_as": raw_key,
                "masked": mask(value, secret),
            })
        else:
            report["missing"].append({"key": canonical, "prompt": label})
    print(json.dumps(report, indent=2))
    return 0 if not report["missing"] else 1


def do_merge(path, pairs):
    lines, found = parse(path)
    existed = os.path.exists(path)
    backup = None
    if existed and lines:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = "%s.bak.%s" % (path, stamp)
        with io.open(backup, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")

    secrets = {c: s for c, _a, s, _l in SCHEMA}
    aliases_of = {c: a for c, a, _s, _l in SCHEMA}
    updated, added = [], []

    for key, value in pairs.items():
        value = "" if value is None else str(value)
        # Update the alias already in the file rather than adding a duplicate.
        target = None
        for name in [key] + aliases_of.get(key, []):
            if name.upper() in found:
                target = found[name.upper()]
                break
        if target:
            idx, raw_key, old = target
            if old == value:
                continue
            lines[idx] = "%s=%s" % (raw_key, value)
            found[raw_key.upper()] = (idx, raw_key, value)
            updated.append(raw_key)
        else:
            if not added:
                # One blank-line separator and one header for the whole block.
                if lines and lines[-1].strip():
                    lines.append("")
                lines.append("# --- QA initiation (%s) ---"
                             % datetime.date.today().isoformat())
            lines.append("%s=%s" % (key, value))
            found[key.upper()] = (len(lines) - 1, key, value)
            added.append(key)

    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(json.dumps({
        "file": os.path.abspath(path),
        "created": not existed,
        "backup": os.path.abspath(backup) if backup else None,
        "updated": updated,
        "added": added,
        "values": {k: mask(str(v), secrets.get(k, True))
                   for k, v in pairs.items()},
    }, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["check", "merge"])
    ap.add_argument("--file", default=".env")
    args = ap.parse_args()

    if args.mode == "check":
        return do_check(args.file)

    raw = sys.stdin.read().strip()
    if not raw:
        sys.stderr.write("merge: expected a JSON object on stdin\n")
        return 2
    pairs = json.loads(raw)
    if not isinstance(pairs, dict) or not pairs:
        sys.stderr.write("merge: stdin must be a non-empty JSON object\n")
        return 2
    return do_merge(args.file, pairs)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Flip one draft entry to published: `draft: true` -> `draft: false`.

    python3 tools/publish_draft.py our-lady-of-sorrows
    python3 tools/publish_draft.py --check our-lady-of-sorrows   # dry run

This is the one write step behind the "Publish this entry" button on a draft
preview page. The button can't do it itself — /travel/ is a static site on
GitHub Pages with no backend — so it opens a pre-filled GitHub issue and
.github/workflows/publish-draft.yml runs this, then build_travel.py, then
commits. Keeping the edit in a script (rather than a sed line in the YAML)
means the risky part is runnable and checkable locally, which is also how it
gets tested before it is ever trusted from a phone.

It does exactly one thing and it does not rebuild. Run build_travel.py after,
which is what the workflow does — same two commands either way, so there is no
"the robot does something different from me" divergence to debug later.

Exit codes are meaningful, because a workflow reads them:
    0  flipped
    2  found it, but it is not a draft (already published) — nothing to do
    3  no such entry
    4  the front matter is malformed
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "source", "travel")

SLUG_RE = re.compile(r"^[a-z0-9-]+$")
FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9-]+)\.html$")
TRUEISH = ("1", "true", "yes")          # must match build_travel.load_posts


def find_entry(slug):
    """The source file for a slug, or None. Slug is the filename minus its date,
    which is exactly how build_travel.py derives it — so what you type into the
    button is what the builder already calls this post."""
    if not os.path.isdir(SRC_DIR):
        return None
    for fn in sorted(os.listdir(SRC_DIR)):
        m = FILE_RE.match(fn)
        if m and m.group(2) == slug:
            return os.path.join(SRC_DIR, fn)
    return None


def split_front_matter(text, where):
    """(front_matter_lines, rest) split on the first bare `---`.

    Splitting first — rather than running a regex over the whole file — is what
    keeps a `draft: true` written inside a post's PROSE (quoting this very
    workflow, say) from being rewritten as if it were the real setting.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "---":
            return lines[:i], lines[i:]
    raise ValueError(f"{where}: no `---` line ending the front matter")


def publish(slug, dry_run=False):
    if not SLUG_RE.match(slug or ""):
        print(f"refusing a slug that isn't [a-z0-9-]: {slug!r}", file=sys.stderr)
        return 4

    path = find_entry(slug)
    if not path:
        print(f"no entry in source/travel/ with slug {slug!r}", file=sys.stderr)
        return 3

    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    try:
        front, rest = split_front_matter(text, rel)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 4

    hits = [i for i, l in enumerate(front) if l.split(":", 1)[0].strip() == "draft"]
    if not hits:
        print(f"{rel}: no `draft:` line — already published", file=sys.stderr)
        return 2
    if len(hits) > 1:
        print(f"{rel}: {len(hits)} `draft:` lines — fix by hand", file=sys.stderr)
        return 4

    i = hits[0]
    value = front[i].split(":", 1)[1].strip().lower()
    if value not in TRUEISH:
        print(f"{rel}: draft is already {value!r} — already published", file=sys.stderr)
        return 2

    if dry_run:
        print(f"would publish {rel}  ({front[i].strip()} -> draft: false)")
        return 0

    front[i] = "draft: false"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(front + rest))

    print(f"published {rel}")
    print(f"  {slug}.html — now run: python3 build_travel.py")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Publish one draft /travel/ entry.")
    ap.add_argument("slug", help="e.g. our-lady-of-sorrows")
    ap.add_argument("--check", action="store_true",
                    help="say what would happen, change nothing")
    args = ap.parse_args()
    sys.exit(publish(args.slug, dry_run=args.check))


if __name__ == "__main__":
    main()

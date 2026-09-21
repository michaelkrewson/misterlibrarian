#!/usr/bin/env python3
"""Archive the Notebook's live rundown box into a real, dated entry, then
reset the box so a fresh rundown can start.

    python3 tools/archive_rundown.py
    python3 tools/archive_rundown.py --keep              # archive, don't reset
    python3 tools/archive_rundown.py --title "..." --section technology

The front page's rundown box (see build_notebook.py's _rundown_box) lives in
source/notebook/_rundown.json — a hand-maintained scratchpad, not a normal
YYYY-MM-DD-slug.html entry, because it needs to sit pinned under the hero and
get edited in place as items turn into links. But a scratchpad that just gets
overwritten loses every past rundown. This script is the other half: it turns
today's box into a permanent, tagged entry (using the ordinary entry pipeline
build_notebook.py already has — no new mechanism, just the existing one), so
every past rundown collects on tag-rundown.html for free, via the same
tag-page archive every other Notebook tag already builds.

Run `python3 build_notebook.py` after, same as adding any entry by hand.

STANDARD LIBRARY ONLY, matching the builders.
"""
import argparse
import datetime as dt
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source", "notebook")
RUNDOWN_FILE = os.path.join(SRC, "_rundown.json")
SECTIONS = ("technology", "world", "culture", "notes")


def esc(s):
    return html.escape(str(s), quote=True)


def pretty_date(d):
    try:
        return d.strftime("%B %-d, %Y")
    except ValueError:
        return d.strftime("%B %d, %Y")


def render_body(data):
    """The archived entry's body: the same content _rundown_box() renders on
    the front page, as ordinary entry markup (h2 per category, not h3 — an
    entry has no page-title h1 competing with it the way the front-page box
    sits under one)."""
    parts = []
    if data.get("note"):
        parts.append("<p>%s</p>" % esc(data["note"]))
    for sec in data.get("sections", []):
        items = sec.get("items", [])
        if not items:
            continue
        parts.append("<h2>%s</h2>" % esc(sec.get("label", "")))
        lis = []
        for it in items:
            text = esc(it.get("text", ""))
            href = it.get("href", "").strip()
            if href:
                lis.append('  <li><a href="%s">%s</a></li>' % (esc(href), text))
            else:
                lis.append("  <li>%s</li>" % text)
        parts.append("<ul>\n%s\n</ul>" % "\n".join(lis))
    return "\n\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", default=None,
                     help='Default: "The Rundown — <the box\'s own date, spelled out>"')
    ap.add_argument("--section", default="world", choices=SECTIONS,
                     help="Notebook section (default: world — this is a news roundup)")
    ap.add_argument("--slug", default=None,
                     help="Filename slug (default: the-rundown-<date>, unique per day — "
                          "see the 2026-09-21 fix note below for why a fixed slug is wrong)")
    ap.add_argument("--tags", default="rundown",
                     help='Comma-separated tags (default: "rundown" — '
                          "this is what makes tag-rundown.html the archive)")
    ap.add_argument("--summary", default=None,
                     help="Default: an auto-generated one-liner naming the day's "
                          "categories — the box's own `note` is instructional "
                          "boilerplate, not a description of that day's content, "
                          "so it is deliberately NOT used here")
    ap.add_argument("--keep", action="store_true",
                     help="Archive without resetting _rundown.json afterward")
    args = ap.parse_args()

    if not os.path.exists(RUNDOWN_FILE):
        sys.exit("no source/notebook/_rundown.json to archive")
    with open(RUNDOWN_FILE, encoding="utf-8") as fh:
        data = json.load(fh)

    date_str = (data.get("date") or "").strip()
    if not date_str:
        sys.exit("_rundown.json has no `date` to archive under")
    try:
        y, m, d = (int(p) for p in date_str.split("-"))
        date_obj = dt.date(y, m, d)
    except ValueError:
        sys.exit("_rundown.json `date` (%r) is not YYYY-MM-DD" % date_str)

    sections = [s for s in data.get("sections", []) if s.get("items")]
    if not sections:
        sys.exit("_rundown.json has no items to archive — nothing to do")

    title = args.title or "The Rundown — %s" % pretty_date(date_obj)
    n_items = sum(len(s["items"]) for s in sections)
    labels = ", ".join(s.get("label", "") for s in sections)
    summary = args.summary or (
        "%d stor%s across %s, tracked on %s."
        % (n_items, "y" if n_items == 1 else "ies", labels, pretty_date(date_obj)))

    # 2026-09-21 fix: the default slug used to be the fixed word "the-rundown"
    # for every day. build_notebook.py's load_entries() strips only the
    # YYYY-MM-DD- filename prefix and uses the REMAINING slug as the output
    # URL (notebook/<slug>.html) — the same rule every other entry relies on
    # to get a unique permalink. A fixed slug meant every archived day built
    # to the identical notebook/the-rundown.html, silently overwriting the
    # previous day's — a full rebuild kept whichever date sorted first in
    # os.listdir(), so four of the first five archived rundowns (09-17
    # through 09-20) were invisible on the live site despite existing as
    # real, correctly-tagged source files. Discovered when Michael pointed
    # out the newly-published articles weren't showing as linked on "the
    # rundown posts" and only one of the two he meant (the front-page box)
    # turned out to still be reachable. Each day's slug is now unique by
    # construction.
    slug = args.slug or ("the-rundown-%s" % date_str)
    fn = "%s-%s.html" % (date_str, slug)
    out_path = os.path.join(SRC, fn)
    if os.path.exists(out_path):
        sys.exit("source/notebook/%s already exists — pick a different --slug" % fn)

    front = ("title: %s\n"
              "date: %s\n"
              "section: %s\n"
              "tags: %s\n"
              "summary: %s\n"
              "---\n\n" % (title, date_str, args.section, args.tags, summary))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(front + render_body(data))
    print("archived -> source/notebook/%s" % fn)

    if not args.keep:
        fresh = {"date": dt.date.today().isoformat(), "title": "Today's rundown",
                 "note": data.get("note", ""), "sections": []}
        with open(RUNDOWN_FILE, "w", encoding="utf-8") as fh:
            json.dump(fresh, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("reset source/notebook/_rundown.json for the next cycle")
    else:
        print("--keep: left source/notebook/_rundown.json as-is")

    print("next: python3 build_notebook.py")


if __name__ == "__main__":
    main()

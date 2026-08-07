#!/usr/bin/env python3
"""Publication machinery shared by build_travel.py and build_finance.py.

This domain now has two publications that both publish dated entries — The
Librarian Abroad at /travel/ and The Librarian's Ledger at /finance/. Everything
in here is the part of "being a blog" that has nothing to do with which blog it
is: parsing front matter, deriving a meta description, building an RSS feed,
measuring an image so the browser can reserve space for it.

WHY A SHARED MODULE RATHER THAN A SECOND COPY
The alternative was copying ~300 lines out of build_travel.py into
build_finance.py. Front-matter parsing and feed generation existing twice is
precisely the kind of duplication that drifts silently: someone fixes a
canonical-URL bug in one feed and not the other, and nobody notices for months
because both sites still build. One copy, two callers.

WHAT IS DELIBERATELY *NOT* HERE
Anything a publication should be free to disagree about: page chrome, nav,
colours, the rating scale, card layout, the drafts workflow. Those live in each
builder. This module holds only the things that would be a bug if they differed.

Every function takes its configuration as an argument. Nothing reads a global
from a caller — that is what keeps two publications from quietly sharing a
setting neither of them declared.

STANDARD LIBRARY ONLY, like both builders that import it.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import os
import re
import xml.sax.saxutils as sax

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ------------------------------------------------------------- front matter ---

def parse_front_matter(text, where, known_keys, required_keys):
    """Split `key: value` front matter from the HTML body.

    Fails LOUDLY on an unknown or missing key — a post that silently loses its
    summary or date would quietly ship a broken card and a broken feed entry.

    `known_keys` / `required_keys` are passed in because the two publications
    genuinely differ: a Ledger entry has no `stars:` and a travel review has no
    `chart:`. Sharing the parser must not mean sharing the vocabulary.
    """
    if "\n---" not in text:
        raise ValueError(f"{where}: no `---` line ending the front matter")
    head, _, body = text.partition("\n---")
    meta = {}
    for i, line in enumerate(head.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{where}:{i}: front-matter line is not `key: value` -> {line!r}")
        k, _, v = line.partition(":")
        k = k.strip().lower()
        if k not in known_keys:
            raise ValueError(
                f"{where}:{i}: unknown front-matter key {k!r}. "
                f"Known keys: {', '.join(sorted(known_keys))}")
        meta[k] = v.strip()
    missing = set(required_keys) - set(meta)
    if missing:
        raise ValueError(f"{where}: missing required front matter: {', '.join(sorted(missing))}")
    return meta, body.lstrip("\n")


def plain_text(body_html):
    """Strip tags out of a post body for search indexing. Not a sanitizer —
    the input is our own post source, never reader-supplied — just enough to
    turn markup into words a search box can match against."""
    text = html.unescape(_TAG_RE.sub(" ", body_html))
    return _WS_RE.sub(" ", text).strip()


def meta_desc(explicit, summary, lo, hi):
    """The search-result description: an explicit override, else whole sentences
    off the front of the summary that fit inside `hi` characters.

    Whole sentences matter. A description cut mid-word is one a search engine
    truncates for you, in a place you did not choose.
    """
    if explicit:
        return explicit
    summary = " ".join((summary or "").split())
    if len(summary) <= hi:
        return summary
    out = ""
    for sentence in re.findall(r'[^.!?]*[.!?]', summary):
        if len(out) + len(sentence) > hi:
            break
        out += sentence
    out = out.strip()
    if len(out) >= lo:
        return out
    # One very long opening sentence: fall back to a word-boundary cut. Still
    # better than a mid-word truncation chosen by the search engine.
    cut = summary[:hi - 1].rsplit(" ", 1)[0].rstrip(",;:—- ")
    return cut + "…"


# ------------------------------------------------------------------ helpers ---

def tag_slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def pretty_date(d):
    # %-d is a GNU/BSD extension; fall back to the zero-padded form elsewhere.
    try:
        return d.strftime("%B %-d, %Y")
    except ValueError:
        return d.strftime("%B %d, %Y")


def rfc822(d):
    """RFC-822 date for RSS.

    Noon rather than midnight so a reader in a behind-UTC timezone never renders
    an entry as the previous day. The day and month names are written out rather
    than taken from strftime("%a"/"%b"), which are locale-dependent — a build run
    on a machine set to another language would otherwise emit a feed no reader
    could parse. Byte-identical to strftime's output under an English locale.
    """
    return (f"{_DAYS[d.weekday()]}, {d.day:02d} {_MONTHS[d.month - 1]} {d.year} "
            f"12:00:00 +0000")


def asset_ver(out_dir, rel):
    """Short content hash of a static asset, appended to its URL so a CSS edit is
    never masked by a stale browser cache."""
    try:
        with open(os.path.join(out_dir, rel), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:10]
    except OSError:
        return "0"


_DIMS_CACHE = {}


def img_dims(img_dir, filename):
    """(width, height) of an image, or None.

    Emitting these is a Core Web Vitals fix, not decoration: without them the
    browser reserves no space for a photo until it has loaded, so every image
    shoves the text below it down the page as it arrives, and cumulative layout
    shift is a ranking signal.

    Fails OPEN — if Pillow is missing or the file is unreadable the build still
    produces a correct page, just without the hint. Cached because an index
    re-renders every hero. Keyed by directory as well as name so two
    publications cannot collide on a shared filename.
    """
    key = (img_dir, filename)
    if key in _DIMS_CACHE:
        return _DIMS_CACHE[key]
    dims = None
    try:
        from PIL import Image
        with Image.open(os.path.join(img_dir, filename)) as im:
            dims = im.size
    except Exception:
        dims = None
    _DIMS_CACHE[key] = dims
    return dims


def dim_attrs(img_dir, filename):
    d = img_dims(img_dir, filename)
    return f' width="{d[0]}" height="{d[1]}"' if d else ""


# --------------------------------------------------------------------- feed ---

def build_feed(posts, *, site_name, site_url, base, blurb, limit=30,
               describe=None):
    """RSS 2.0 — a publication's front door for readers who follow it directly.

    Deliberately summary-only (no full post body): the point is to bring readers
    to the page, and a summary feed can't leak half-formatted HTML into someone's
    reader.

    `describe(p)` lets a publication decide what goes in <description> — the
    travel blog appends the place, the Ledger has no place to append.
    """
    describe = describe or (lambda p: p["summary"])
    items = []
    for p in posts[:limit]:
        link = f"{site_url}{base}/{p['file']}"
        cats = "".join(f"    <category>{sax.escape(t)}</category>\n" for t in p["tags"])
        items.append(f"""  <item>
    <title>{sax.escape(p['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{rfc822(p['date'])}</pubDate>
    <description>{sax.escape(describe(p))}</description>
{cats}  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{sax.escape(site_name)}</title>
  <link>{site_url}{base}/</link>
  <atom:link href="{site_url}{base}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{sax.escape(blurb)}</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


# ---------------------------------------------------------------- redirects ---

def redirect_stub(to_url, *, title, note=""):
    """A standing-in page for a URL that has moved.

    GitHub Pages serves static files and cannot issue a 301, so this is the only
    redirect available: an instant meta refresh, plus a canonical pointing at the
    new address, plus a visible link for anyone whose browser ignores both.
    Search engines treat an immediate meta refresh much like a permanent
    redirect — weaker than a real 301, but it passes the signal and it keeps an
    old link from dead-ending.
    """
    t = html.escape(title, quote=True)
    u = html.escape(to_url, quote=True)
    extra = f"<p>{html.escape(note)}</p>" if note else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Moved — {t}</title>
<link rel="canonical" href="{u}"/>
<meta http-equiv="refresh" content="0; url={u}"/>
<meta name="robots" content="noindex,follow"/>
<style>
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:#060b14;color:#e8eef7;font:17px/1.6 Georgia,serif;padding:24px;text-align:center}}
a{{color:#5eb3d6}}
</style>
</head>
<body>
<div>
  <p>This entry has moved.</p>
  {extra}
  <p><a href="{u}">{t} →</a></p>
</div>
</body>
</html>
"""

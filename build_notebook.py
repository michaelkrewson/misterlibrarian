#!/usr/bin/env python3
"""Build /notebook/ — The Librarian's Notebook, a commonplace book.

    python3 build_notebook.py          # build the publication (that's the whole CLI)

STANDARD LIBRARY ONLY, deliberately — the same property build_travel.py,
build_finance.py and build_health.py have. Nothing here touches the network; an
entry is a file on disk and the build is a pure function of the source directory.

FIVE PUBLICATIONS, ONE DOMAIN
─────────────────────────────
mistertranslation.com serves five separate things behind the hand-written hub at
the bare root (index.html): the Bible project (/bible.html, build.py), The Librarian
Abroad (/travel/, build_travel.py), The Librarian's Ledger (/finance/,
build_finance.py), The Librarian's Regimen (/health/, build_health.py), and this
(/notebook/). Added 2026-09-11 (Michael's call) as the one ORDINARY blog on the
domain — the place where the person, not the subject, is the through-line.

WHY A FIFTH PUBLICATION, AND WHY ONLY ONE
The four others are special-purpose by design: scripture, money, the road, the
body — each with its own reader, its own front-matter shape, its own trust
posture. What they leave out is everything else Michael writes every so often:
a technology piece with no Bitcoin in it, a geopolitics or news explainer, the
rare piece on the arts. By 2026-09-11 three such pieces had already landed in
the Ledger under a soft `notes` tag (the Propst cubicle essay, the AI-token
pricing piece, the BIS/IMF/World Bank explainer), which is the tell that the
catch-all existed and was in the wrong publication. Two new verticals (one for
science & technology, one for everything else) were considered and rejected: at
"every so often" and "rarely" they would each look dead within months, and a
low-cadence blog whose last entry is four months old loses the reader on
arrival. One publication at the combined cadence is a living blog.

The editorial line this leaves the Ledger with is sharper for it: if the spine
of a piece is a price, a balance sheet, or an institution that moves money, it's
the Ledger; otherwise it's here.

SECTIONS ARE FIRST-CLASS, TAGS ARE FREE — AND THE SECTIONS ARE THE SPLIT SEAM
Every entry carries one `section:` from SECTIONS below (the build refuses any
other value), plus the same free `tags:` the other blogs use. A section is a
nav link and its own page (technology.html, world.html, culture.html,
notes.html) with the same tile grid, tag chips and search as the front page,
filtered. Four fixed sections give the front page a stable shape while there
are only a handful of entries — a chip cloud over six posts is not navigation —
and, the real reason, they are the seam along which this publication splits
LATER if one section outgrows the others: lift it out into its own masthead with
one redirect stub per entry, and nothing else moves. Decide that from the entry
counts, not now.

WHAT THIS IS A COPY OF, AND WHAT IT DELIBERATELY ISN'T
──────────────────────────────────────────────────────
The WRITING half of build_health.py (itself the writing half of
build_finance.py), near-verbatim: front matter via blogkit, the tile/list front
page with its tag filter bar and header search, entry pages with "Keep reading"
recirculation, per-tag pages held out of the sitemap until they carry
TAG_INDEX_MIN entries, RSS, sitemap, the X comment layer, the FormSubmit ask
page. What it does NOT have: the Regimen's Spanish edition (no twins by default
here — a twin doubles the cost of a post and the point of this publication is
low friction; if a specific entry ever earns one, port the mechanism from
build_health.py then), the Regimen's medical-disclaimer apparatus (this is a
notebook of opinions and explainers, and says so once in the small print), any
of the Ledger's standing boards, and — Michael's call, 2026-09-11 — ANY draft
mechanism at all: there is no `draft:` key, no --drafts flag, no preview page.
Every file in source/notebook/ builds and ships. "I can always go back and have
you reword something."

This builder writes ONLY inside notebook/ and never globs or deletes anywhere
else — the same discipline that lets the other four coexist safely. The one
deletion it performs (`_prune_stale_tag_pages`) is scoped hard to
notebook/tag-*.html. If a shared mechanism needs fixing, fix it in blogkit.py;
if a page-chrome idea proves out here, port it by hand (the builders do not
import each other — see CLAUDE.md).

RENAMING
────────
Edit SITE_NAME / TAGLINE / BLURB below. The hub card on the root index.html and
the sibling links in the other three blog builders carry the name too.
"""
from __future__ import annotations

import collections
import datetime as dt
import html
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone

import blogkit

SITE_NAME = "The Librarian's Notebook"
TAGLINE = "A commonplace book — science and technology, the world, arts and culture, and whatever else didn't fit"
BLURB = ("A commonplace book kept by Mr. Librarian: notes on science and technology, on the "
         "world and its news, on the arts, and on whatever else didn't belong in the Ledger, "
         "the Regimen or the road. Explainers over hot takes; the working shown; one reader's "
         "opinions, labelled as such.")

# The front page's OWN search description — BLURB is the feed's and the About
# page's, and at ~290 characters it would be cut mid-sentence in a search
# result (the Regimen and the Ledger both ship their blurb there; this one
# doesn't). Kept under META_DESC_MAX like every entry's.
FRONT_DESC = ("A commonplace book kept by Mr. Librarian: science and technology, the world "
              "and its news, the arts, and whatever else didn't fit. Working shown.")

BASE_URL = "https://mistertranslation.com/notebook/"
SITE_URL = "https://mistertranslation.com"
BASE = "/notebook"

# Cookie-less, no-consent-banner analytics, same account as the other four so
# there's one dashboard for the whole domain. Set to None to disable entirely.
GOATCOUNTER_CODE = "mistertranslation"

# The Notebook's front-matter vocabulary: the Regimen's, plus `section`, minus
# `draft` (no draft mechanism exists here — see the module docstring).
KNOWN_KEYS = {"title", "date", "section", "tags", "summary", "meta_desc",
              "hero", "hero_alt", "hero_credit"}
REQUIRED_KEYS = {"title", "date", "section", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70

# The sections, in nav order. key → (nav/heading name, output file, the short
# UPPERCASE label that leads a tile's date line, the one-line lede on the
# section's own page). The key is what an entry's `section:` line carries; the
# build refuses any value not listed here. To add a section, add a row — the
# nav, the section pages, the sitemap and the tile labels all read this table.
SECTIONS = {
    "technology": ("Science & Technology", "technology.html", "TECHNOLOGY",
                   "Machines, software, the sciences, and the people who make them — "
                   "the technology writing that has no Bitcoin in it."),
    "world":      ("The World", "world.html", "WORLD",
                   "Geopolitics, institutions and the news — explained rather than "
                   "shouted, with the working shown."),
    "culture":    ("Arts & Culture", "culture.html", "CULTURE",
                   "Books, music, film, buildings, and the occasional argument about "
                   "why one of them is good."),
    "notes":      ("Notes", "notes.html", "NOTES",
                   "Everything else — the entries that fit none of the other three "
                   "sections and needed writing anyway."),
}

# A tag page listing a single entry is a near-duplicate of that entry — nothing
# for a searcher to land on that the entry itself doesn't already answer. The
# pages are still BUILT and still work; they are just held back from the
# sitemap until enough entries share the tag to make the page its own answer.
# Section pages are NOT subject to this: they are navigation, and an empty
# section page saying "nothing here yet" is the honest state, not a dupe.
TAG_INDEX_MIN = 2

# The front-page tag filter bar: a tag earns a visible chip by RECURRING; the
# rest fold behind a "+N more" disclosure (see build_finance.py for the measured
# reasoning — a young blog's one-off tags outnumber its entries).
TAG_BAR_MIN_COUNT = 2
TAG_BAR_MAX_CHIPS = 18

# How many tiles show on the front page before older ones fold behind
# "Show more". No standing pages compete for these slots here.
FRONT_TILE_LIMIT = 6

# The sibling publications — every blog links to every other in its footer.
# The Bible project is reached via the root hub, same as from the other three.
SIBLINGS = (
    ("The Librarian's Ledger", "https://mistertranslation.com/finance/",
     "What the world's money is actually in"),
    ("The Librarian Abroad", "https://mistertranslation.com/travel/",
     "Notes from the road and the table"),
    ("The Librarian's Regimen", "https://mistertranslation.com/health/",
     "Health, nutrition and medicine — one question at a time, from the studies"),
    ("Eight Miles West", "https://mistertranslation.com/west/",
     "A family history — four centuries in America, one document at a time"),
)

# The same FormSubmit endpoint the other blogs post to, so every publication
# lands in one inbox; `_subject` is what tells them apart. Safe to reuse: a shared
# inbox is not a shared page, and the hash is already committed in this same
# public repo. A form rather than comments, for the reasons set out at length in
# build_travel.py.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"


ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "notebook")
ENTRY_SRC = os.path.join(ROOT, "source", "notebook")

# Periwinkle ink. Chosen against the four colours it has to sit beside in a
# shared nav/footer/hub: the Ledger's Bitcoin amber (#f7931a), the travel blog's
# terracotta (#e8865c) and the Bible project's gold (#e8c968) are all warm, and
# the Regimen's mint (#3fd2a8) is the one cool green — so the fifth publication
# reads as its own thing only if it's cool AND blue. Ink-coloured, for a
# notebook. Bright enough (~9:1 on the #060b14 ground) to carry a link colour.
ACCENT = "#8fa3ff"
ACCENT_RGB = "143,163,255"


# ────────────────────────────────────────────────────────────────── entries ──

def esc(s):
    return html.escape(str(s), quote=True)


def load_entries():
    """Read source/notebook/*.html into entry dicts, newest first.

    Shares blogkit's front-matter parser with the other blogs but not their
    vocabulary — see KNOWN_KEYS above. There is no draft state: every file that
    parses is a live entry.
    """
    if not os.path.isdir(ENTRY_SRC):
        return []
    entries = []
    for fn in sorted(os.listdir(ENTRY_SRC)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue
        with open(os.path.join(ENTRY_SRC, fn), encoding="utf-8") as fh:
            meta, body = blogkit.parse_front_matter(
                fh.read(), "source/notebook/" + fn, KNOWN_KEYS, REQUIRED_KEYS)

        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+?)\.html$", fn)
        if not m:
            raise ValueError("source/notebook/%s: name must be YYYY-MM-DD-slug.html" % fn)
        date = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        slug = m.group(4)
        if meta["date"].strip() != date.isoformat():
            raise ValueError(
                "source/notebook/%s: `date: %s` disagrees with the filename (%s). "
                "This is what stops an entry filing itself under the wrong year."
                % (fn, meta["date"], date.isoformat()))

        section = meta["section"].strip().lower()
        if section not in SECTIONS:
            raise ValueError(
                "source/notebook/%s: `section: %s` is not one of %s"
                % (fn, meta["section"], ", ".join(SECTIONS)))

        entries.append({
            "slug": slug,
            "file": slug + ".html",
            "date": date,
            "section": section,
            "title": meta["title"],
            "summary": meta["summary"],
            "meta_desc": meta.get("meta_desc", "").strip(),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "hero": meta.get("hero", "").strip(),
            "hero_alt": meta.get("hero_alt", "").strip(),
            "hero_credit": meta.get("hero_credit", "").strip(),
            "body": body,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def _entry_desc(e):
    return blogkit.meta_desc(e["meta_desc"], e["summary"], META_DESC_MIN, META_DESC_MAX)


def _tag_file(tag):
    return "tag-%s.html" % blogkit.tag_slug(tag)


def _tag_chips(e):
    if not e["tags"]:
        return ""
    chips = "".join('<a class="tg" href="%s">%s</a>' % (_tag_file(t), esc(t))
                    for t in e["tags"])
    return '<div class="tags">%s</div>' % chips


def _section_name(key):
    return SECTIONS[key][0]


def _section_file(key):
    return SECTIONS[key][1]


def _section_label(key):
    return SECTIONS[key][2]


def _date_label(e):
    """The uppercase date line a tile or entry carries, led by the section:
    "TECHNOLOGY · SEPTEMBER 11, 2026". The section leads because on a
    mixed-subject front page it is the first thing a reader wants to know
    about a tile, before the date."""
    return "%s · %s" % (_section_label(e["section"]), blogkit.pretty_date(e["date"]).upper())


def tag_index(entries):
    """{tag: [entries]} — every tag that appears on an entry, newest first."""
    out = {}
    for e in entries:
        for t in e["tags"]:
            out.setdefault(t, []).append(e)
    return out


# ──────────────────────────────────────────────────────────────────── chrome ──

def _nav(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    # Writing (everything), one link per section, About. Six links — wider
    # than the Regimen's two because the sections ARE the point of this
    # publication's navigation; narrower than the Ledger's seven boards.
    # "Ask" is reached from the footer and the per-entry prompt, as elsewhere.
    links = ['<a href="index.html"%s>Writing</a>' % cls("home")]
    for key, (name, fn, _, _) in SECTIONS.items():
        links.append('<a href="%s"%s>%s</a>' % (fn, cls(key), esc(name)))
    links.append('<a href="about.html"%s>About</a>' % cls("about"))
    return '<nav class="nav">%s</nav>' % "".join(links)


def _chrome(active=""):
    """Header used by every page in the publication — brand, search, nav.

    Same markup as build_health._chrome minus the language link, laid out the
    same way (see the "header" block in CSS): brand left + search right on one
    row, the nav on its own row underneath, left-aligned, at every width — so
    the checkbox + hamburger label this still emits are never displayed here.
    The search box is a REAL form (GET, name="q") so it works with JS off by
    navigating to the front page with ?q=…; the front page's own script filters
    live and reads a handed-over ?q=.
    """
    hamburger = ('<svg viewBox="0 0 20 14" width="20" height="14" aria-hidden="true" '
                 'focusable="false"><rect width="20" height="2" rx="1"/>'
                 '<rect y="6" width="20" height="2" rx="1"/>'
                 '<rect y="12" width="20" height="2" rx="1"/></svg>')
    search = ('<form class="headersearch" action="index.html" method="get" role="search">'
              '<input type="search" name="q" id="headerSearch" placeholder="Search entries…" '
              'aria-label="Search past entries"/></form>')
    return ('<header class="hsm">'
            '<a class="brand" href="index.html">%s'
            '<span class="wm">The Librarian\'s <span class="em">Notebook</span></span></a>'
            '%s'
            '<div class="hgroup">'
            '<input type="checkbox" class="navcb" id="navcb"/>'
            '<label class="navtoggle" for="navcb" aria-label="Menu">%s</label>'
            '%s</div></header>'
            % (MARK_SVG.replace("__ACCENT__", ACCENT), search, hamburger, _nav(active)))


def _legal():
    """The small print, deliberately smaller and dimmer than everything else in
    the footer. No personal name anywhere on this site: the byline throughout is
    "Mr. Librarian," and this paragraph keeps that posture rather than becoming
    the one place a real name would naturally go.

    A general-purpose line rather than the Ledger's financial one or the
    Regimen's medical one: this publication ranges over everything, so it
    disclaims everything once, plainly, and says whose opinions these are."""
    year = datetime.now(timezone.utc).year
    return ('<p class="legal">© %d %s. Everything on this site is one reader\'s opinion '
            'and general information, published for interest only. Nothing here is '
            'professional advice of any kind — not financial, legal, medical, technical '
            'or otherwise — and no reply from Mr. Librarian is either. Facts are drawn '
            'from public sources in good faith, are linked where they can be, and may be '
            'misread, superseded or simply wrong; check the originals before relying on '
            'anything here. Opinions are the author\'s own and are not those of any '
            'employer, company or organization. No person, company, product or '
            'organization named on this site has endorsed it or is affiliated with it; '
            'nothing here is sponsored.</p>' % (year, esc(SITE_NAME)))


def _foot(hits_path=None):
    """`hits_path` (e.g. "/notebook/about.html") gets its own live-fetched view
    count appended (per-path GoatCounter counter via `_hits_widget`). `None`
    (the index page, which shows its own "N visits" line in-body) or a
    zero-hit path renders nothing — fail-silent, like every other call site."""
    hits = _hits_widget(hits_path, " views") if hits_path else ""
    hits_bit = " · %s" % hits if hits else ""
    sibs = " · ".join('<a href="%s">%s</a>' % (url, esc(name)) for name, url, _ in SIBLINGS)
    return ('<footer>%s · <a href="about.html">About</a> · '
            '<a href="tags.html">All tags</a> · <a href="ask.html">Ask a question</a> · '
            '<a href="feed.xml">RSS</a> · %s · '
            'one reader\'s opinions, nothing here is advice%s%s</footer>'
            % (esc(SITE_NAME), sibs, hits_bit, _legal()))


def _shell_hits_path(url):
    """Best-effort "/notebook/<file>.html" for `_foot`'s view-count widget,
    derived from the same absolute `url` every `_shell` caller already passes.
    Returns None for a url with no filename (the index page's bare BASE_URL)."""
    name = url.rstrip("/").rsplit("/", 1)[-1]
    return "%s/%s" % (BASE, name) if "." in name else None


FRONT_HERO_IMG = "leonardo-codex-flight-17v.jpg"
FRONT_HERO_ALT = ("A page of Leonardo da Vinci's notebook: lines of his right-to-left mirror "
                  "writing in brown ink, with two small pen sketches of a bird in flight in the "
                  "right margin and a diagram of a wing's rigging below them")
FRONT_HERO_CREDIT = (
    'Folio 17 verso of Leonardo da Vinci\'s <i>Codex on the Flight of Birds</i> (c. 1505, '
    'Biblioteca Reale, Turin): mirror-written notes, two birds, a rigged wing — one page of '
    'the most famous notebook ever kept, in which anatomy, hydraulics, optics, a shopping '
    'list and a flying machine share the same paper. Public domain, via '
    '<a href="https://commons.wikimedia.org/wiki/File:Codice_Volo_17V.jpg" rel="noopener" '
    'target="_blank">Wikimedia Commons</a>.')


def _front_hero():
    """The publication's one page-wide picture, front and center on the index.
    Not an entry hero (see _entry_hero) — the front page's own fixed banner."""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), FRONT_HERO_IMG)
    return ('<div class="fronthero"><figure><img src="img/%s" alt="%s"%s loading="eager"/>'
            '<figcaption>%s</figcaption></figure></div>'
            % (FRONT_HERO_IMG, esc(FRONT_HERO_ALT), dims, FRONT_HERO_CREDIT))


def _entry_hero(e):
    if not e["hero"]:
        return ""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), e["hero"])
    # hero_credit goes in RAW, exactly as FRONT_HERO_CREDIT does — a photo credit
    # has to be able to link its source and its licence.
    cap = "<figcaption>%s</figcaption>" % e["hero_credit"] if e["hero_credit"] else ""
    return ('<figure class="hero"><img src="img/%s" alt="%s"%s loading="eager"/>%s</figure>'
            % (esc(e["hero"]), esc(e["hero_alt"]), dims, cap))


def _comment_box(title, url):
    """The site's whole comment system: X as the comment layer
    (blogkit.x_comment_url / x_search_url) — two buttons, no pitch copy."""
    comment = blogkit.x_comment_url(title, url)
    search = blogkit.x_search_url(url)
    return ('<div class="respond"><div class="respond-actions">'
            '<a class="respond-btn respond-btn-primary" href="%s" target="_blank" '
            'rel="noopener">💬 Comment on X</a>'
            '<a class="respond-btn respond-btn-secondary" href="%s" target="_blank" '
            'rel="noopener">🔍 See what others said</a>'
            '</div></div>'
            % (comment, search))


# ──────────────────────────────────────────── entry-page recirculation ──

def _related_entries(e, pool, limit=4):
    """Entries to offer at the foot of `e`, best first: ranked by shared-tag
    count, then same section, ties broken by recency, topped up with the most
    recent so the block is never short. Section is a weaker signal than a
    shared tag on purpose — on a publication this broad, "also about
    technology" is barely a relation; "also about open source" is one."""
    def tags_of(o):
        return {t.lower() for t in o.get("tags", ())}

    mine = tags_of(e)
    others = [o for o in pool if o["file"] != e["file"]]
    others.sort(key=lambda o: o["date"], reverse=True)
    others.sort(key=lambda o: (len(mine & tags_of(o)), o["section"] == e["section"]),
                reverse=True)
    return others[:limit]


def _related_block(e, pool):
    """"Keep reading" — reuses `_tile`/`_front_item` rather than a private card
    so it can never drift from the front page's typography."""
    picks = _related_entries(e, pool)
    if not picks:
        return ""
    tiles = "\n".join(
        _tile(_front_item(href=o["file"], label=_date_label(o),
                          title=o["title"], desc=_entry_desc(o),
                          date=o["date"], tags=o.get("tags", ())))
        for o in picks)
    return ('  <section class="readnext">\n'
            '    <h2>Keep reading</h2>\n'
            '    <div class="tilegrid">\n%s\n    </div>\n'
            '  </section>' % tiles)


def build_entry_page(e, pool=()):
    """Render one entry."""
    hits_path = "%s/%s" % (BASE, e["file"])
    desc = _entry_desc(e)
    url = BASE_URL + e["file"]
    sec_line = ('<p class="edate"><a class="esec" href="%s">%s</a> · %s</p>'
                % (_section_file(e["section"]), esc(_section_name(e["section"]).upper()),
                   blogkit.pretty_date(e["date"]).upper()))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>%(title)s — %(site)s</title>
<meta name="description" content="%(desc)s"/>
<link rel="canonical" href="%(url)s"/>
<link rel="alternate" type="application/rss+xml" title="%(site)s" href="feed.xml"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="%(site)s"/>
<meta property="og:title" content="%(title)s"/>
<meta property="og:description" content="%(desc)s"/>
<meta property="og:url" content="%(url)s"/>
<meta property="article:section" content="%(section)s"/>
<meta name="twitter:card" content="summary"/>
<style>%(css)s</style>%(goat)s
</head>
<body>
<div class="wrap">
  %(chrome)s
  <article class="entry">
    <h1 class="etitle">%(title)s</h1>
    %(sec_line)s
    %(hero)s
%(body)s
    %(tags)s
  </article>
  %(nudge)s
%(related)s
  <p class="backlink"><a href="index.html">← Back to the Notebook</a></p>
%(foot)s
</div>
</body>
</html>
""" % {
        "title": esc(e["title"]),
        "site": esc(SITE_NAME),
        "desc": esc(desc),
        "url": url,
        "section": esc(_section_name(e["section"])),
        "css": CSS.replace("__ACCENT__", ACCENT).replace("__ACCENT_RGB__", ACCENT_RGB),
        "goat": _goatcounter(),
        "chrome": _chrome(e["section"]),
        "sec_line": sec_line,
        "hero": _entry_hero(e),
        "body": e["body"],
        "tags": _tag_chips(e),
        "nudge": _comment_box(e["title"], url),
        "related": _related_block(e, pool),
        "foot": _foot(hits_path),
    }


def _entry_card(e):
    return ('    <a class="ecard" href="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]), esc(_date_label(e)),
                          esc(e["title"]), esc(e["summary"])))


_WS_RE = re.compile(r"\s+")


def _front_item(*, href, label, title, desc, date, tags=()):
    """One entry in the single shape both `_tile` and `_archive_row` render
    from. `search` is the lowercased haystack the header search box matches."""
    return {"href": href, "label": label, "title": title, "desc": desc,
            "date": date, "tags": list(tags),
            "search": _WS_RE.sub(" ", (title + " " + desc).lower()).strip()}


def _tile(item):
    """A boxed grid tile. `data-search` is what the header search box's
    client-side filter matches; `data-tags` is what the tag chips match."""
    data_tags = " ".join(blogkit.tag_slug(t) for t in item["tags"])
    return ('    <a class="tile" href="%s" data-search="%s" data-tags="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(item["href"]), esc(item["search"]), esc(data_tags),
                          esc(item["label"]), esc(item["title"]), esc(item["desc"])))


def _archive_row(item):
    """The compact LIST view of the same pool the tiles show."""
    data_tags = " ".join(blogkit.tag_slug(t) for t in item["tags"])
    return ('    <li data-search="%s" data-tags="%s"><span class="ec-d">%s</span><a href="%s">%s</a></li>'
            % (esc(item["search"]), esc(data_tags), esc(item["label"]), esc(item["href"]), esc(item["title"])))


def _goatcounter():
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


def _hits_id(path):
    return "hits-" + re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def _hits_widget(path, suffix=""):
    """A small inline view-count chip — GoatCounter's public PER-PATH counter,
    fetched client-side. `path` is the page's own path from the domain root
    (e.g. "/notebook/about.html"). Fails SILENT on any error or a zero-hit path."""
    if not GOATCOUNTER_CODE:
        return ""
    hid = _hits_id(path)
    encoded = urllib.parse.quote(path, safe="")
    return f"""<span class="hits" id="{hid}">\U0001f441 <span id="{hid}-n">—</span>{html.escape(suffix)}</span>
<script>
(function(){{
  fetch("https://{GOATCOUNTER_CODE}.goatcounter.com/counter/{encoded}.json")
    .then(function(r){{ return r.json(); }})
    .then(function(d){{
      var n = document.getElementById("{hid}-n");
      if (n && d && d.count) n.textContent = d.count;
      else {{ var el = document.getElementById("{hid}"); if (el) el.style.display = "none"; }}
    }})
    .catch(function(){{
      var el = document.getElementById("{hid}"); if (el) el.style.display = "none";
    }});
}})();
</script>"""


def _shell(*, title, desc, url, body, active="", noindex=False, og_type="website",
           extra_css="", extra_js=""):
    robots = '<meta name="robots" content="noindex,follow"/>\n' if noindex else ""
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>%(title)s</title>
<meta name="description" content="%(desc)s"/>
%(robots)s<link rel="canonical" href="%(url)s"/>
<link rel="alternate" type="application/rss+xml" title="%(site)s" href="feed.xml"/>
<meta property="og:type" content="%(ogt)s"/>
<meta property="og:site_name" content="%(site)s"/>
<meta property="og:title" content="%(title)s"/>
<meta property="og:description" content="%(desc)s"/>
<meta property="og:url" content="%(url)s"/>
<meta name="twitter:card" content="summary"/>
<style>%(css)s</style>%(goat)s
</head>
<body>
<div class="wrap">
  %(chrome)s
%(body)s
  %(foot)s
</div>
%(js)s</body>
</html>
""" % {"title": esc(title), "desc": esc(desc), "robots": robots, "url": url,
       "site": esc(SITE_NAME), "ogt": og_type,
       "css": (CSS + extra_css).replace("__ACCENT__", ACCENT).replace("__ACCENT_RGB__", ACCENT_RGB),
       "js": ("<script>\n%s\n</script>\n" % extra_js.replace("__ACCENT__", ACCENT)
              if extra_js else ""),
       "chrome": _chrome(active), "body": body,
       "foot": _foot(_shell_hits_path(url)), "goat": _goatcounter()}


# ───────────────────────────────────────────────────────────────────── pages ──

ABOUT_BODY = """  <section class="asklede">
    <h1 class="wtitle">About the Notebook</h1>
    <p class="wsub">A commonplace book — the one place on this site where the subject is
    whatever it happens to be.</p>
  </section>

  <div class="panel">
    <h2>What this is</h2>
    <p>The other four projects on this domain each keep to one subject: the Bible, money, the
    road, the body. This is the fifth, and it is the ordinary one — a blog in the old sense,
    where the through-line is the person writing rather than the thing written about. A piece
    of technology writing with no Bitcoin in it goes here. So does a geopolitics explainer, a
    note on a piece of news that deserved a longer look than the headline gave it, and the
    occasional argument about a book, a building or a record.</p>
    <p>It is sorted into four sections so it has a shape while it is small:
    <a href="technology.html">Science &amp; Technology</a>, <a href="world.html">The World</a>,
    <a href="culture.html">Arts &amp; Culture</a>, and <a href="notes.html">Notes</a> for
    whatever fits none of the other three. Tags run underneath, as on the other blogs.</p>
  </div>

  <div class="panel">
    <h2>How it's written</h2>
    <ul>
      <li><b>Explainers over hot takes.</b> The useful thing about a news story is usually not
      the reaction to it but the piece of the world it turns out to depend on — an institution,
      a mechanism, a number — and that is what an entry here tries to find and set out.</li>
      <li><b>The working shown.</b> Where a claim rests on a figure, the figure is given with its
      source; where it rests on a document, the document is linked. A reader should be able to
      check the entry, not take it on faith.</li>
      <li><b>Opinions labelled as opinions.</b> There are plenty here. They are one reader's,
      they are said to be, and being told one is wrong is the most useful message anyone
      sends.</li>
    </ul>
  </div>

  <div class="panel">
    <h2>What it's not</h2>
    <p>Not advice — not financial, legal, medical, technical or any other kind — and no reply
    from me is either. The money writing lives at <a href="https://mistertranslation.com/finance/">the
    Ledger</a>, the health writing at <a href="https://mistertranslation.com/health/">the
    Regimen</a>, and each of those says at length what it is and isn't. This one ranges over
    everything else, and disclaims it all once, in the small print at the foot of every
    page.</p>
  </div>

  <div class="panel">
    <h2>Why "Notebook"</h2>
    <p>A <i>commonplace book</i> was the personal notebook a reader kept from the Renaissance
    on — a book of passages copied out, thoughts set down, things seen, sorted under headings
    so they could be found again. Everyone who read kept one: Bacon, Milton, Locke (who wrote
    a method for indexing them), Jefferson, Emerson. It was never a book <i>about</i> one thing;
    it was a book about whatever the keeper had been paying attention to, which is exactly
    the job this publication does.</p>
    <p>The page at the top of the front page is the most famous notebook ever kept: a folio
    of Leonardo da Vinci's <i>Codex on the Flight of Birds</i>, in which mirror-written notes
    on how a bird holds its wings share the paper with a diagram of rigging and, elsewhere in
    the same codex, anatomy, hydraulics and lists of things to buy. Science, technology, the
    world, and the arts, on one page, kept by one person. The ambition here is a great deal
    smaller; the shape is the same.</p>
  </div>

  <div class="panel expect">
    <h2>Reaching me</h2>
    <p>Every entry ends with a button that opens a public reply on X, and a search that finds
    what other readers have said about the same page. For anything not tied to one entry —
    a question, a correction, something I should have read — there is
    <a href="ask.html">a form that goes straight to my desk</a>.</p>
  </div>
"""


def build_about():
    """Who is writing, how an entry is worked, what goes here rather than in
    one of the other four publications, and where the name comes from."""
    return _shell(title="About — %s" % SITE_NAME,
                  desc="What The Librarian's Notebook is — a commonplace book of science and "
                       "technology, the world, and the arts — how it's written, and why it "
                       "has that name.",
                  url="%sabout.html" % BASE_URL, active="about", body=ABOUT_BODY)


ASK_BODY = """  <section class="asklede">
    <h1 class="wtitle">Ask Mr. Librarian</h1>
    <p class="wsub">A question about something written here, a correction, or something you
    think I should have read. It goes straight to my desk.</p>
  </section>

  <div class="panel">
    <form action="%(endpoint)s" method="POST" class="askform">
      <input type="hidden" name="_subject" value="The Librarian's Notebook — a question from a reader"/>
      <input type="hidden" name="_template" value="table"/>
      <input type="hidden" name="_next" value="%(next)s"/>
      <!-- Honeypot: a real person never sees this, a bot fills it in. -->
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>

      <label>What is this about? <span class="opt">(optional)</span>
        <input type="text" name="entry" id="entryField"
               placeholder="An entry, or leave blank"/>
      </label>
      <label>Your name <span class="opt">(optional)</span>
        <input type="text" name="name" placeholder="However you'd like to be known — or leave blank"/>
      </label>
      <label>Your email <span class="opt">(optional — only if you'd like a reply)</span>
        <input type="email" name="email" placeholder="you@example.com"/>
      </label>
      <label>Your question <span class="req">(required)</span>
        <textarea name="message" required rows="7"
          placeholder="Where did that number come from? Have you read the other side of this? You've got the date wrong — here's the source."></textarea>
      </label>
      <button class="btn" type="submit">Send it</button>
      <p class="formnote">Sending shows a quick captcha to keep the robots out, then brings
      you back here. Nothing is posted publicly — messages go to my inbox and I read all
      of them.</p>
    </form>
  </div>

  <div class="panel expect" id="expect">
    <h2>What to expect</h2>
    <p><b>Ask me</b> where a figure came from, why I weighted one source over another, to
    point me at something I have missed, or to tell me I have got a fact wrong — those last
    two are the most useful messages anyone sends.</p>
    <p><b>Don't expect advice.</b> Nothing on this site is professional advice of any kind
    and no reply from me will be either. A disagreement about an argument is welcome; a
    request to tell you what to do with your money, your health or your lawyer is one I will
    politely decline.</p>
  </div>

<script>
// Pre-fill "what is this about" when a reader arrives from the foot of an entry.
// Set with .value (never innerHTML) so a crafted URL cannot inject markup.
(function(){
  try {
    var re = new URLSearchParams(location.search).get('re');
    var f = document.getElementById('entryField');
    if (re && f) f.value = re.slice(0, 200);
  } catch (e) {}
})();
</script>
"""


def build_ask():
    """The one place a reader can reach the librarian about the writing.

    Posts to FormSubmit — no backend, no database, no cookie. The `re` query
    parameter carries which entry the reader came from and is filled in
    client-side."""
    body = ASK_BODY % {"endpoint": FORM_ENDPOINT, "next": "%sthanks.html" % BASE_URL}
    return _shell(title="Ask Mr. Librarian — %s" % SITE_NAME,
                  desc="Ask a question about something written on %s, point me at something "
                       "I have missed, or tell me I have a fact wrong." % SITE_NAME,
                  url="%sask.html" % BASE_URL, active="ask", body=body)


def build_thanks():
    body = """  <section class="asklede">
    <h1 class="wtitle">It's on the desk</h1>
  </section>
  <div class="panel">
    <p><b>Your question is in.</b> Thank you — I read everything that arrives, and being
    told I have a fact wrong is the most useful thing anyone sends.</p>
    <p>If you left an email and it wants an answer, you'll get one. Meanwhile there is
    <a href="index.html">the rest of the writing</a>.</p>
  </div>
"""
    # noindex: this page exists only as somewhere to land after submitting.
    return _shell(title="Question received — %s" % SITE_NAME,
                  desc="Your question is on the librarian's desk.",
                  url="%sthanks.html" % BASE_URL, body=body, noindex=True)


FRONT_JS = """
(function(){
  var TILE_FIRST = __TILE_FIRST__, TILE_STEP = 12, LIST_FIRST = 20, LIST_STEP = 40;
  var tilesWrap = document.getElementById('tiles');
  if (!tilesWrap) return;
  var archiveList = document.getElementById('archiveList');
  var viewbar = document.getElementById('viewbar');
  var filterBar = document.getElementById('filters');
  var loadMoreWrap = document.getElementById('loadMoreWrap');
  var loadMoreBtn = document.getElementById('loadMoreBtn');
  var viewCount = document.getElementById('viewCount');
  var searchEmpty = document.getElementById('searchEmpty');
  var activeView = 'cards';
  var revealCount = TILE_FIRST;
  var query = '';
  var activeTag = '';

  function firstFor(v){ return v === 'list' ? LIST_FIRST : TILE_FIRST; }
  function stepFor(v){ return v === 'list' ? LIST_STEP : TILE_STEP; }
  function allOf(v){
    return Array.prototype.slice.call(
      (v === 'list' ? archiveList : tilesWrap).children);
  }
  function matches(el){
    var tags = (el.dataset.tags || '').split(/\\s+/);
    var tagOk = !activeTag || tags.indexOf(activeTag) !== -1;
    var textOk = !query || (el.dataset.search || '').indexOf(query) !== -1;
    return tagOk && textOk;
  }

  // Filter first (search), THEN paginate what's left.
  function render(){
    var all = allOf(activeView);
    var matched = all.filter(matches);
    var total = matched.length;
    var showN = Math.min(revealCount, total);
    var shown = matched.slice(0, showN);
    all.forEach(function(el){
      el.style.display = shown.indexOf(el) !== -1 ? '' : 'none';
    });
    var remaining = total - showN;
    if (loadMoreWrap) loadMoreWrap.hidden = remaining <= 0;
    if (loadMoreBtn) loadMoreBtn.textContent = 'Show ' + Math.min(stepFor(activeView), remaining) + ' more';
    if (viewCount) viewCount.textContent = total ? ('Showing ' + showN + ' of ' + total) : '';
    if (searchEmpty) searchEmpty.hidden = !(query && total === 0);
  }

  function setView(v){
    activeView = v;
    revealCount = firstFor(v);
    tilesWrap.hidden = v !== 'cards';
    if (archiveList) archiveList.hidden = v !== 'list';
    if (viewbar) {
      viewbar.querySelectorAll('.viewbtn').forEach(function(b){
        b.classList.toggle('on', b.dataset.view === v);
      });
    }
    render();
  }

  if (viewbar) {
    viewbar.addEventListener('click', function(e){
      var b = e.target.closest('[data-view]');
      if (!b) return;
      setView(b.dataset.view);
    });
  }
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function(){
      revealCount += stepFor(activeView);
      render();
    });
  }

  // Unfold the long tail of one-off tags — a disclosure, not a filter.
  function openTags(){
    if (!filterBar) return;
    var more = document.getElementById('tagMore');
    filterBar.classList.add('tags-open');
    if (more) {
      more.setAttribute('aria-expanded', 'true');
      more.textContent = '\\u2212 fewer';
    }
  }

  if (filterBar) {
    filterBar.addEventListener('click', function(e){
      var b = e.target.closest('.chip');
      if (!b) return;
      if (b.id === 'tagMore') {
        if (filterBar.classList.contains('tags-open')) {
          filterBar.classList.remove('tags-open');
          b.setAttribute('aria-expanded', 'false');
          b.textContent = '+ ' + b.dataset.count + ' more';
        } else {
          openTags();
        }
        return;
      }
      activeTag = b.dataset.tag;
      filterBar.querySelectorAll('.chip').forEach(function(c){ c.classList.toggle('on', c === b); });
      revealCount = firstFor(activeView);
      render();
    });
  }

  // The header search box — a real form that still works with JS off. With
  // JS on: filters live, keeps ?q= in the URL, and reads a handed-over ?q=.
  var searchInput = document.getElementById('headerSearch');
  if (searchInput) {
    var form = searchInput.closest('form');
    if (form) form.addEventListener('submit', function(e){ e.preventDefault(); });
    searchInput.addEventListener('input', function(){
      query = searchInput.value.toLowerCase().trim();
      revealCount = firstFor(activeView);
      render();
      var url = new URL(location.href);
      if (searchInput.value) url.searchParams.set('q', searchInput.value);
      else url.searchParams.delete('q');
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    });
    var handed = new URLSearchParams(location.search).get('q');
    if (handed) { searchInput.value = handed; query = handed.toLowerCase().trim(); }
  }

  // Arriving from a tag chip lands as index.html?tag=<slug>; honoured only if
  // a chip with that slug exists, so a stale tag shows everything.
  var handedTag = new URLSearchParams(location.search).get('tag');
  if (handedTag && filterBar) {
    var match = filterBar.querySelector('.chip[data-tag="' + handedTag + '"]');
    if (match) {
      if (match.classList.contains('rare')) openTags();
      activeTag = handedTag;
      filterBar.querySelectorAll('.chip').forEach(function(c){ c.classList.toggle('on', c === match); });
    }
  }

  setView('cards');
})();
"""


def _listing(entries, first_entry_html):
    """The tile grid + list view + tag chip bar + pagination over one pool —
    the body every listing page (the front page and each section page) is
    built from, and the JS that drives it. Returns (html, js)."""
    pool = [_front_item(href=e["file"], label=_date_label(e),
                        title=e["title"], desc=e["summary"], date=e["date"],
                        tags=e["tags"]) for e in entries]
    pool.sort(key=lambda it: -it["date"].toordinal())

    tiles = "\n".join(_tile(it) for it in pool)
    rows = "\n".join(_archive_row(it) for it in pool)
    archive_html = '\n    <ul class="archive" id="archiveList" hidden>\n%s\n    </ul>' % rows

    counts = collections.Counter(t for it in pool for t in it["tags"])
    all_tags = sorted(counts, key=str.lower)
    chips = ""
    if all_tags:
        shown = [t for t in all_tags if counts[t] >= TAG_BAR_MIN_COUNT]
        if len(shown) > TAG_BAR_MAX_CHIPS:
            keep = set(sorted(shown, key=lambda t: (-counts[t], t.lower()))
                       [:TAG_BAR_MAX_CHIPS])
            shown = [t for t in all_tags if t in keep]
        shown_set = set(shown)
        rare = [t for t in all_tags if t not in shown_set]

        def _chip(t, is_rare=False):
            n = counts[t]
            cls = "chip"
            if is_rare:
                cls += " rare"
            elif n >= 5:
                cls += " w3"
            elif n >= 3:
                cls += " w2"
            return ('<button class="%s" data-tag="%s" title="%d entr%s">%s</button>'
                    % (cls, blogkit.tag_slug(t), n, "y" if n == 1 else "ies", esc(t)))

        more = ""
        if rare:
            more = ('<button class="chip more" id="tagMore" type="button" '
                    'aria-expanded="false" aria-controls="filters" data-count="%d">'
                    '+ %d more</button>' % (len(rare), len(rare)))
        chips = ('<div class="filters" id="filters">'
                 '<button class="chip on" data-tag="">All</button>'
                 + "".join(_chip(t) for t in shown)
                 + more
                 + "".join(_chip(t, is_rare=True) for t in rare)
                 + "</div>")

    # An empty pool (a brand-new publication, or a section nothing has been
    # filed under yet). Say so in a sentence rather than rendering an empty
    # grid with a view toggle over nothing.
    if not pool:
        viewbar = ""
        loadmore = ""
        empty_note = '    <p class="empty first">%s</p>\n' % first_entry_html
    else:
        empty_note = ""
        viewbar = ('<div class="viewbar" id="viewbar">View: '
                   '<button class="viewbtn on" data-view="cards" type="button">\U0001F5C2 Cards</button>'
                   '<button class="viewbtn" data-view="list" type="button">\U0001F4CB List</button></div>')
        loadmore = ('<div class="loadmorewrap" id="loadMoreWrap" hidden>'
                    '<button class="loadmore" id="loadMoreBtn" type="button">Show more</button>'
                    '<div class="viewcount" id="viewCount"></div></div>')
    body = """  <section class="writing">
%s    %s
    %s
    <p class="empty" id="searchEmpty" hidden>No entries match that search.</p>
    <div class="tilegrid" id="tiles">
%s
    </div>%s
    %s
  </section>""" % (empty_note, chips, viewbar, tiles, archive_html, loadmore)
    js = FRONT_JS.replace("__TILE_FIRST__", str(FRONT_TILE_LIMIT))
    return body, js


def build_front(entries):
    """The publication's front page: what has been written, newest first — as a
    bounded grid of tiles with a list view, a tag filter bar, and the header
    search, all client-side over one pool. Same construction as the Regimen's
    front page, plus the section label leading each tile's date line."""
    listing, js = _listing(entries, (
        'The first entry is being written. <a href="feed.xml">Subscribe to the feed</a> '
        'to catch it, or read <a href="about.html">what this notebook is for</a> meanwhile.'))
    url = BASE_URL
    index_hits = _hits_widget("%s/index.html" % BASE, " visits to this page")
    index_hits_html = ('\n  <p class="pagehits">%s</p>' % index_hits) if index_hits else ""
    intro = '  <p class="tag ftag">%s</p>\n' % esc(TAGLINE)
    return _shell(
        title="%s — %s" % (SITE_NAME, TAGLINE),
        desc=FRONT_DESC, url=url, active="home",
        body="%s%s%s%s\n%s\n" % (_front_hero(), intro, listing, index_hits_html,
                                 _comment_box(SITE_NAME, url)),
        extra_js=js)


def build_section_page(key, entries):
    """One section's own page — the same listing as the front page, filtered
    to the entries filed under `key`, with the section's lede on top instead
    of the hero. Always indexable: it is navigation, and its URL is what a
    section would keep if it ever split out into its own publication."""
    name, fn, _, lede = SECTIONS[key]
    n = len(entries)
    listing, js = _listing(entries, (
        'Nothing has been filed under %s yet. <a href="index.html">All writing</a>, or '
        '<a href="feed.xml">subscribe to the feed</a> to catch the first entry.' % esc(name)))
    head = ('  <section class="asklede seclede">\n'
            '    <h1 class="wtitle">%s</h1>\n'
            '    <p class="wsub">%s</p>\n'
            '    <p class="seccount">%d entr%s · <a href="index.html">All writing</a></p>\n'
            '  </section>\n' % (esc(name), esc(lede), n, "y" if n == 1 else "ies"))
    return _shell(
        title="%s — %s" % (name, SITE_NAME),
        desc=lede, url=BASE_URL + fn, active=key,
        body=head + listing + "\n",
        extra_js=js)


def build_tag_page(tag, entries, indexable):
    slug = blogkit.tag_slug(tag)
    n = len(entries)
    desc = ("%d entr%s on %s from %s."
            % (n, "y" if n == 1 else "ies", tag, SITE_NAME))
    cards = "\n".join(_entry_card(e) for e in entries)
    return _shell(
        title="%s — %s" % (tag, SITE_NAME),
        desc=desc, url="%stag-%s.html" % (BASE_URL, slug),
        noindex=not indexable,
        body="""  <section class="writing">
    <h1 class="wtitle">%s</h1>
    <p class="wsub">%d entr%s tagged <b>%s</b>. <a href="index.html">All writing</a>.</p>
%s
  </section>
""" % (esc(tag), n, "y" if n == 1 else "ies", esc(tag), cards))


def build_tag_list(tags):
    """Every tag, as one browsable page."""
    if not tags:
        return None
    items = "".join(
        '<a class="tg" href="%s">%s <span class="tgn">%d</span></a>'
        % (_tag_file(t), esc(t), len(v))
        for t, v in sorted(tags.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())))
    return _shell(
        title="All tags — %s" % SITE_NAME,
        desc="Every subject written about on %s." % SITE_NAME,
        url="%stags.html" % BASE_URL,
        noindex=True,   # a list of links, nothing to rank for
        body="""  <section class="writing">
    <h1 class="wtitle">All tags</h1>
    <p class="wsub">%d subject%s so far. <a href="index.html">All writing</a>.</p>
    <div class="tags taglist">%s</div>
  </section>
""" % (len(tags), "" if len(tags) == 1 else "s", items))


# ────────────────────────────────────────────────────────────────────── style ──

CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#060b14;color:#e8eef7;
  font:16px/1.65 Georgia,'Iowan Old Style','Palatino Linotype',serif;
  -webkit-font-smoothing:antialiased}
/* Two ambient washes, both `fixed` (see build_finance.py for the reasoning):
   the shared cool wash up top, plus an accent-toned glow centred on the
   viewport so a soft light sits behind whatever cards are on screen. */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(120% 80% at 50% -8%,rgba(94,179,214,.10),transparent 60%),
    radial-gradient(70% 60% at 50% 48%,rgba(__ACCENT_RGB__,.12),transparent 72%)}
.wrap{position:relative;z-index:1;max-width:1060px;margin:0 auto;padding:0 22px 72px}
header{padding:46px 0 8px;text-align:center}
.brand{display:inline-flex;align-items:center;gap:14px;text-decoration:none;color:inherit}
.bmark{width:61px;height:61px;flex:0 0 61px;overflow:visible}
h1{margin:0;font-size:31px;font-weight:400;letter-spacing:.01em}

/* Animated mark: an open notebook page with a pen writing its last line — the
   line draws itself (stroke-dashoffset) while the nib slides along it, then
   the ink fades and the nib returns to the margin for the next line. Same
   construction as the Ledger's lighthouse and the Regimen's mortar: the halo
   (`.bmark-glow`) is a blurred RING drawn behind everything, radius already
   outside the crisp ring's r=21, so the light appears past the icon's edge
   and never inside it. One 4.4s clock for ink and nib so they never drift
   apart. No transform-box override — for an SVG child a plain px transform
   resolves in viewBox units. Respects reduced-motion (the line simply shows
   drawn). */
.bmark-glow{filter:blur(8px);transform-origin:33px 33px;
  animation:bmarkGlow 4.2s ease-in-out infinite}
.bmark-ink{stroke-dasharray:12;stroke-dashoffset:12;
  animation:bmarkInk 4.4s ease-in-out infinite}
.bmark-nib{animation:bmarkNib 4.4s ease-in-out infinite}
@keyframes bmarkGlow{
  0%,100%{opacity:.32;transform:scale(.92)}
  50%{opacity:.7;transform:scale(1.12)}
}
@keyframes bmarkInk{
  0%{stroke-dashoffset:12;opacity:1}
  55%{stroke-dashoffset:0;opacity:1}
  78%{stroke-dashoffset:0;opacity:1}
  90%{stroke-dashoffset:0;opacity:0}
  100%{stroke-dashoffset:12;opacity:0}
}
@keyframes bmarkNib{
  0%{transform:translateX(0)}
  55%{transform:translateX(12px)}
  78%{transform:translateX(12px)}
  100%{transform:translateX(0)}
}
@media (prefers-reduced-motion:reduce){
  .bmark-glow,.bmark-nib{animation:none}
  .bmark-ink{animation:none;stroke-dashoffset:0}
}
h1 .em{color:__ACCENT__;font-style:italic}
.tag{margin:12px 0 0;color:#93a4bd;font-size:15px;font-style:italic}
.lede{margin:30px auto 0;max-width:760px;color:#b9c6d8;font-size:16.5px}
.lede b{color:#e8eef7;font-weight:400}
.hl{color:__ACCENT__}

.panel{margin:44px 0 0;padding:24px 26px;border:1px solid #1b2534;border-radius:12px;
  background:#0a111c}
.panel h2{margin:0 0 12px;font-size:19px;font-weight:400;color:#e8eef7}
/* 760px is this publication's reading measure (see .entry). */
.panel p,.panel ul{max-width:760px}
.panel p{margin:0 0 12px;color:#b9c6d8;font-size:15px}
.panel p:last-child{margin-bottom:0}
.panel code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13.5px;
  color:__ACCENT__;background:#0e1724;padding:1px 6px;border-radius:4px}
.panel ul{margin:0 0 12px;padding-left:20px;color:#b9c6d8;font-size:15px}
.panel li{margin:0 0 8px}
.panel b{color:#e8eef7;font-weight:600}
.asklede + .panel{margin-top:0}
footer{margin:56px 0 0;padding-top:22px;border-top:1px solid #131b27;text-align:center;
  color:#6e7d92;font-size:13.5px;font-family:ui-sans-serif,system-ui,sans-serif}
.legal{margin:14px auto 0;max-width:560px;color:#3f4c5f;font-size:10.5px;line-height:1.6;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.legal a{color:#5a6b80}
.ftag{margin:20px 0 26px;color:#93a4bd;font-size:15px;font-style:italic;text-align:center}
.pagehits{margin:34px 0 0;color:#6e7d92;font-size:12.5px;text-align:center}

/* ── ask form ────────────────────────────────────────────────────────────── */
.asklede{margin:30px 0 22px}
.askform{display:flex;flex-direction:column;gap:17px}
.askform label{display:flex;flex-direction:column;gap:7px;color:#c3d0e0;font-size:15px;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.askform .opt{color:#6e7d92;font-size:13px}
.askform .req{color:__ACCENT__;font-size:13px}
.askform input[type=text],.askform input[type=email],.askform textarea{
  width:100%;box-sizing:border-box;padding:11px 13px;border:1px solid #1e2938;border-radius:9px;
  background:#0d1521;color:#e8eef7;font:15px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif}
.askform input:focus,.askform textarea:focus{outline:none;border-color:__ACCENT__}
.askform textarea{resize:vertical;min-height:130px}
.askform .btn{align-self:flex-start;padding:11px 26px;border:0;border-radius:9px;
  background:__ACCENT__;color:#06131c;font:600 15px ui-sans-serif,system-ui,sans-serif;
  cursor:pointer}
.askform .btn:hover{filter:brightness(1.1)}
.formnote{margin:0;color:#7f8fa6;font-size:13.5px;line-height:1.6}
.expect{margin-top:22px}
.expect h2{margin:0 0 12px;font-size:19px;font-weight:400;color:#e8eef7}
.expect p{margin:0 0 12px;color:#b9c6d8;font-size:15px}
.expect p:last-child{margin:0}
.expect b{color:#e8eef7;font-weight:600}
.respond{max-width:760px;margin:34px auto 0;padding:16px 20px;border:1px solid #1b2534;
  border-radius:11px;background:#0a111c}
.respond p{margin:0;color:#a9b7c9;font-size:15px;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.respond strong{color:#e8eef7}
.respond-actions{display:flex;gap:12px;margin-top:16px;flex-wrap:wrap}
.respond-btn{flex:1 1 180px;text-align:center;padding:12px 20px;border-radius:999px;
  font-weight:700;font-size:14.5px;letter-spacing:.2px;text-decoration:none;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
  transition:transform .12s ease,filter .12s ease}
.respond-btn:hover,.respond-btn:focus{filter:brightness(1.1);transform:translateY(-1px)}
.respond-btn:active{transform:translateY(0)}
.respond-btn-primary{background:__ACCENT__;color:#06131c}
.respond-btn-secondary{background:transparent;border:1px solid __ACCENT__;color:__ACCENT__}
/* Pinned explicitly — a bare pseudo-class selector outranks a single class
   no matter which comes later (the travel site lost a button's text this way,
   2026-09-09). Cheap insurance. */
.respond-btn-primary:hover,.respond-btn-primary:focus{color:#06131c}
.respond-btn-secondary:hover,.respond-btn-secondary:focus{color:__ACCENT__}
@media (prefers-reduced-motion:reduce){
  .respond-btn{transition:none}
  .respond-btn:hover,.respond-btn:focus,.respond-btn:active{transform:none}
}

/* ── front-page hero picture ─────────────────────────────────────────────── */
.fronthero{margin:8px 0 2px}
.fronthero figure{margin:0}
/* object-position sits near the top: on folio 17v the two bird sketches are
   in the upper right (heads at ~5% and ~14% of the page height) and the
   rigged-wing diagram just below them, with the red anatomical wing further
   down and a stain at the very top edge — the band should show the birds
   and the mirror-writing beside them. Measured against the 300px band on a
   1060px-wide render of the page-cropped 1143×1600 image: 5% shows both birds and the
   top of the rigging, and clears the stain. */
.fronthero img{display:block;width:100%;height:300px;object-fit:cover;
  object-position:center 5%;border-radius:14px;border:1px solid #1b2534}
.fronthero figcaption{margin:11px 4px 0;color:#7f8fa6;font-size:13px;font-style:italic;
  line-height:1.55;text-align:center}
.fronthero figcaption a{color:#8b9ab0}
@media (max-width:720px){
  .fronthero img{height:170px;border-radius:10px}
  .fronthero figcaption{font-size:12px}
}

/* ── header: brand left, search right; nav on its own row underneath ────── */
/* Two rows by design (the Regimen's layout, 2026-09-10): row one is the brand
   on the left and the search box pushed to the right edge; row two is the
   nav, left-aligned under the brand. Six links here — Writing, the four
   sections, About — and they read as a table of contents on their own row,
   which is what a sectioned notebook wants. No hamburger at any width —
   `.hgroup` takes the full row (flex-basis:100%) so it can never share a
   line with the search box, and the checkbox/label the shared _chrome()
   markup still emits is simply never displayed. */
header.hsm{display:flex;align-items:center;justify-content:space-between;
  column-gap:18px;row-gap:12px;flex-wrap:wrap;padding:26px 0 12px;
  border-bottom:1px solid #131b27;margin-bottom:4px}
header.hsm .brand{order:1}
.headersearch{order:2;margin:0 0 0 auto}
.hgroup{order:3;flex:1 1 100%;display:flex;align-items:center;gap:22px;flex-wrap:wrap;
  justify-content:flex-start}
.nav{display:flex;align-items:center;gap:22px;flex-wrap:wrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:13.5px;
  letter-spacing:.02em}
.nav a{color:#93a4bd;text-decoration:none;padding:2px 0;border-bottom:1px solid transparent}
.nav a:hover{color:#e8eef7}
.nav a.on{color:__ACCENT__;border-bottom-color:__ACCENT__}
.navcb,label.navtoggle{display:none}
@media (max-width:560px){
  .nav{gap:14px;font-size:13px}
}

.headersearch input[type=search]{
  width:170px;font:14px/1.3 Georgia,'Iowan Old Style','Palatino Linotype',serif;
  color:#e8eef7;background:#0d1521;border:1px solid #1e2938;border-radius:999px;
  padding:8px 15px;-webkit-appearance:none;appearance:none;transition:width .15s ease}
.headersearch input[type=search]::-webkit-search-cancel-button{display:none}
.headersearch input[type=search]::placeholder{color:#5a6b80}
.headersearch input[type=search]:focus{outline:none;width:220px;border-color:__ACCENT__;
  box-shadow:0 0 0 3px rgba(__ACCENT_RGB__,.14)}

/* Below this the brand and a 170px search box no longer share a row
   comfortably: search drops to its own full-width row between the brand and
   the nav, and the nav row stays where it is. */
@media (max-width:520px){
  .headersearch{flex:1 1 100%;margin-left:0}
  .headersearch input[type=search]{width:100%}
  .headersearch input[type=search]:focus{width:100%}
}

/* ── tags ────────────────────────────────────────────────────────────────── */
a.tg{text-decoration:none;transition:border-color .15s,color .15s}
a.tg:hover{border-color:__ACCENT__;color:#e8eef7}
.taglist{gap:9px}
.taglist .tg{font-size:13.5px;padding:6px 13px}
.tgn{color:#5a6b80;margin-left:6px;font-variant-numeric:tabular-nums}

/* ── entries ─────────────────────────────────────────────────────────────── */
header.hsm{padding:30px 0 6px;text-align:left}
header.hsm .brand{gap:11px}
header.hsm .bmark{width:45px;height:45px;flex:0 0 45px}
.wm{font-size:23px;letter-spacing:.01em}
.wm .em{color:__ACCENT__;font-style:italic}
a{color:__ACCENT__}
.entry{max-width:760px;margin:22px auto 0}
.etitle{font-size:33px;font-weight:400;line-height:1.22;margin:0 0 10px;letter-spacing:.01em}
.edate{margin:0 0 26px;color:#5a6b80;font-size:11px;letter-spacing:.12em;
  font-family:ui-sans-serif,system-ui,sans-serif}
/* The section, leading the date line, linked to its own page. */
.esec{color:__ACCENT__;text-decoration:none}
.esec:hover{text-decoration:underline}
.entry p{margin:0 0 20px;color:#c3d0e0;font-size:17px;line-height:1.72}
.entry h2{margin:38px 0 14px;font-size:23px;font-weight:400;color:#e8eef7;
  padding-bottom:7px;border-bottom:1px solid #1b2534}
.entry h3{margin:28px 0 10px;font-size:19px;font-weight:400;color:#e8eef7}
.entry strong{color:#e8eef7;font-weight:700}
.entry em{color:#d6e0ee}
.entry ul,.entry ol{margin:0 0 20px;padding-left:22px;color:#c3d0e0;font-size:17px;
  line-height:1.72}
.entry li{margin:0 0 8px}
.entry figure{margin:26px 0;text-align:center}
.entry figure img{max-width:100%;height:auto;border-radius:10px;display:block;margin:0 auto}
.entry figcaption{margin-top:9px;color:#7f8fa6;font-size:13.5px;font-style:italic;
  line-height:1.55}
.entry blockquote{margin:26px 0;padding:2px 0 2px 20px;border-left:3px solid __ACCENT__;
  color:#d6e0ee;font-size:18.5px;font-style:italic}
.entry blockquote p{color:inherit;font-size:inherit;margin:0}
/* An aside set apart from the argument — a definition, a digression, the
   number behind a sentence. Accent-edged so it reads as part of the entry's
   own voice, not a quotation. */
.entry .aside{margin:32px 0 26px;padding:20px 24px;border-left:3px solid __ACCENT__;
  border-radius:0 10px 10px 0;background:#0a111c}
.entry .aside p{margin:0 0 12px}
.entry .aside p:last-child{margin:0}
.entry .half-note{color:#7f8fa6;font-size:14.5px;font-style:italic}
.entry hr{border:0;border-top:1px solid #1b2534;margin:34px 0}
.entry pre{margin:0 0 20px;padding:14px 16px;overflow-x:auto;border:1px solid #1b2534;
  border-radius:9px;background:#0a111c;color:#c3d0e0;
  font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace}
.entry code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.92em;
  color:#d6e0ee;background:#0e1724;padding:1px 6px;border-radius:4px}
.entry pre code{background:none;padding:0;font-size:inherit;color:inherit}
/* Sources — optional here (an opinion piece may have none), but when an entry
   has them they render the same as on the Regimen: smaller and quieter than
   the prose, real links. */
.entry ol.sources{font-size:14.5px;line-height:1.6;color:#a9b7c9;padding-left:26px}
.entry ol.sources li{margin:0 0 9px}
.entry ol.sources a{word-break:break-word}
.tags{margin:34px 0 0;display:flex;flex-wrap:wrap;gap:7px}
.tg{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12px;color:#8b9ab0;
  border:1px solid #1e2938;border-radius:999px;padding:4px 11px;background:#0a111c}
.backlink{max-width:760px;margin:34px auto 0;font-family:ui-sans-serif,system-ui,sans-serif;
  font-size:14.5px}

/* ── the writing list ────────────────────────────────────────────────────── */
.writing{margin:52px 0 0}
.seclede + .writing{margin-top:0}
.seccount{margin:0;color:#6e7d92;font-size:13.5px;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.wtitle{margin:0 0 6px;font-size:23px;font-weight:400;color:#e8eef7}
.wsub{margin:0 0 20px;color:#93a4bd;font-size:15px;font-style:italic}
.seclede .wsub{margin-bottom:10px}
.ecard{display:block;text-decoration:none;padding:18px 20px;margin:0 0 12px;
  border:1px solid #1b2534;border-radius:11px;background:#0a111c;transition:border-color .15s}
.ecard:hover{border-color:#2f4257}
.ec-d{display:block;color:#6e7d92;font-size:11.5px;letter-spacing:.13em;
  font-family:ui-sans-serif,system-ui,sans-serif;margin-bottom:6px}
.ec-t{display:block;color:#e8eef7;font-size:20px;line-height:1.3;margin-bottom:7px}
.ec-s{display:block;color:#a9b7c9;font-size:15px;line-height:1.6}

/* ── the front-page tile grid ────────────────────────────────────────────── */
.empty{margin:8px 0 22px;color:#7f8fa6;font-size:14.5px;font-style:italic}
.empty.first{text-align:center;margin:4px auto 22px;max-width:640px}
.tilegrid{display:grid;gap:16px}
.tile{display:block;text-decoration:none;padding:20px 22px;
  border:1px solid #1b2534;border-radius:12px;background:#0a111c;
  box-shadow:0 1px 2px rgba(0,0,0,.3);transition:transform .15s,border-color .15s,box-shadow .15s}
.tile:hover{border-color:#2f4257;transform:translateY(-2px);
  box-shadow:0 4px 12px rgba(0,0,0,.35),0 14px 32px rgba(0,0,0,.35)}
@media (min-width:640px){
  .tilegrid{grid-template-columns:1fr 1fr}
}
@media (min-width:980px){
  .tilegrid{grid-template-columns:1fr 1fr 1fr}
}

/* ── entry-page recirculation: "Keep reading" ────────────────────────────── */
.readnext{max-width:760px;margin:52px auto 0;
  border-top:1px solid #1b2534;padding-top:26px}
.readnext h2{font:600 12.5px/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.15em;text-transform:uppercase;color:#6e7d92;margin:0 0 16px}
.readnext .tilegrid{grid-template-columns:1fr}
.readnext .ec-t{font-size:17px}
.readnext .ec-s{font-size:14px}
@media (min-width:640px){
  .readnext .tilegrid{grid-template-columns:1fr 1fr}
}
@media (min-width:980px){
  .readnext .tilegrid{grid-template-columns:1fr 1fr}
}

/* ── the archive list — the LIST view of the same pool the tiles show ───── */
ul.archive{list-style:none;margin:0;padding:0;max-width:none}
.archive li{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;
  padding:9px 0;border-bottom:1px dotted #1b2534;color:inherit;margin:0}
.archive li:last-child{border-bottom:0}
.archive .ec-d{display:inline;flex:none;min-width:17em;margin-bottom:0}
.archive a{color:#e8eef7;text-decoration:none}
.archive a:hover{text-decoration:underline}

/* ── front-page tag filter bar ───────────────────────────────────────────── */
.filters{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;
  gap:8px;margin:0 0 20px}
.chip{font:13px/1 ui-sans-serif,system-ui,-apple-system,sans-serif;padding:7px 13px;
  border-radius:999px;border:1px solid #1b2534;background:transparent;color:#b9c6d8;
  cursor:pointer;transition:all .15s}
.chip:hover{border-color:__ACCENT__;color:__ACCENT__}
.chip.on{background:__ACCENT__;border-color:__ACCENT__;color:#06131c}
.chip.rare{display:none}
.filters.tags-open .chip.rare{display:inline-block}
.chip.more{border-style:dashed;color:#6e7d92;background:transparent}
.chip.more:hover{border-color:__ACCENT__;color:__ACCENT__}
.chip.w2{color:#e8eef7}
.chip.w3{color:#e8eef7;font-weight:600;border-color:#2f4257}
.chip.w2.on,.chip.w3.on{color:#06131c}
@media (max-width:560px){
  .filters{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;
    justify-content:flex-start;padding-bottom:4px;margin:0 0 16px}
  .chip{flex:0 0 auto;white-space:nowrap}
}

/* ── view toggle + "show more" pagination (front page) ──────────────────── */
#tiles[hidden],#archiveList[hidden],#loadMoreWrap[hidden]{display:none!important}
.viewbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;
  gap:8px;margin:22px 0 16px;font:13px/1 ui-sans-serif,system-ui,-apple-system,sans-serif;
  color:#93a4bd}
.viewbtn{font:inherit;padding:7px 13px;border-radius:999px;border:1px solid #1b2534;
  background:transparent;color:#b9c6d8;cursor:pointer;transition:all .15s}
.viewbtn:hover{border-color:__ACCENT__;color:__ACCENT__}
.viewbtn.on{background:__ACCENT__;border-color:__ACCENT__;color:#06131c}
.loadmorewrap{text-align:center;margin:22px 0 0}
.loadmore{font:15px/1 ui-sans-serif,system-ui,-apple-system,sans-serif;
  background:__ACCENT__;color:#06131c;border:0;border-radius:999px;
  padding:13px 28px;cursor:pointer;transition:filter .15s}
.loadmore:hover{filter:brightness(1.1)}
.viewcount{margin:10px 0 0;font:12.5px/1 ui-sans-serif,system-ui,-apple-system,sans-serif;
  color:#6e7d92}

@media (max-width:720px){
  .etitle{font-size:26px}
  .entry p,.entry ul,.entry ol{font-size:16px}
  .ec-t{font-size:18px}
  .wrap{padding:0 15px 56px}
  h1{font-size:25px}
}
"""

# The mark: a notebook page with a pen writing its last line, in the same
# 66×66 frame, ring and halo as the Ledger's lighthouse and the Regimen's
# mortar, so the brands sit at the same visual weight in a shared nav. The
# ink line (`.bmark-ink`) draws itself and the nib (`.bmark-nib`) slides
# along it — see the CSS. No <defs> (no gradient, no clip) so it can be
# inlined on the root hub next to the others without an id collision.
MARK_SVG = """<svg class="bmark" viewBox="0 0 66 66" fill="none" aria-hidden="true">
  <circle class="bmark-glow" cx="33" cy="33" r="24" fill="none" stroke="__ACCENT__" stroke-width="5"/>
  <rect x="21" y="18" width="24" height="30" rx="2.5" fill="#f2f5f9"/>
  <rect x="21" y="18" width="4" height="30" rx="1.5" fill="__ACCENT__" opacity=".85"/>
  <g stroke="#9aa7bd" stroke-width="1.3" stroke-linecap="round">
    <line x1="29" y1="25" x2="41" y2="25"/>
    <line x1="29" y1="30" x2="41" y2="30"/>
    <line x1="29" y1="35" x2="38" y2="35"/>
  </g>
  <line class="bmark-ink" x1="29" y1="41" x2="41" y2="41" stroke="__ACCENT__" stroke-width="1.7" stroke-linecap="round"/>
  <g class="bmark-nib">
    <g transform="translate(29 41) rotate(-50)">
      <polygon points="0,0 3.8,-1.8 3.8,1.8" fill="#d9e0ea"/>
      <rect x="3.8" y="-1.9" width="11" height="3.8" rx="1.6" fill="#f2f5f9"/>
      <rect x="11.2" y="-1.9" width="3.6" height="3.8" rx="1.2" fill="__ACCENT__"/>
    </g>
  </g>
  <circle cx="33" cy="33" r="21" stroke="__ACCENT__" stroke-width="1.4" opacity=".6"/>
</svg>"""


# ──────────────────────────────────────────────────────────────────── build ──

def build_sitemap(entries, tags):
    """A sitemap is the discovery plan — robots.txt advertises this file. Tag
    pages appear only once they carry TAG_INDEX_MIN entries; submitting a page
    we have marked noindex would be asking Google to index something we told it
    not to. Section pages always appear — they are navigation, indexable
    whether or not anything is filed under them yet."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, today), (BASE_URL + "about.html", today), (BASE_URL + "ask.html", today)]
    for key, (_, fn, _, _) in SECTIONS.items():
        dated = [e["date"] for e in entries if e["section"] == key]
        urls.append((BASE_URL + fn, max(dated).isoformat() if dated else today))
    for e in entries:
        urls.append((BASE_URL + e["file"], e["date"].isoformat()))
    for tag, es_ in sorted(tags.items()):
        if len(es_) >= TAG_INDEX_MIN:
            urls.append(("%stag-%s.html" % (BASE_URL, blogkit.tag_slug(tag)),
                         max(x["date"] for x in es_).isoformat()))
    rows = ["  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>" % (loc, mod)
            for loc, mod in urls]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def _prune_stale_tag_pages(tags):
    """Delete tag pages whose tag no longer appears on any entry. Scoped hard to
    notebook/tag-*.html so it can never reach another publication's output."""
    keep = {"tag-%s.html" % blogkit.tag_slug(t) for t in tags}
    for fn in os.listdir(OUT):
        if fn.startswith("tag-") and fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(OUT, fn))
            print("  (removed stale tag page: %s)" % fn)


def check_entries(entries):
    """Refuse to build on the mistakes that are invisible once shipped. A hard
    failure rather than a warning: a warning printed during a build nobody
    reads is not a check. (The section check itself lives in load_entries,
    where an unknown value is caught before it can reach anything.)"""
    problems = []
    seen = {}
    for e in entries:
        d = _entry_desc(e)
        if len(d) > META_DESC_MAX:
            problems.append("%s: description is %d chars (max %d) — it would be "
                            "truncated mid-sentence in search results"
                            % (e["slug"], len(d), META_DESC_MAX))
        if not e["tags"]:
            problems.append("%s: no tags" % e["slug"])
        if e["hero"] and not e["hero_alt"]:
            problems.append("%s: hero image has no hero_alt" % e["slug"])
        if e["hero"] and not os.path.exists(os.path.join(OUT, "img", e["hero"])):
            problems.append("%s: hero image notebook/img/%s does not exist" % (e["slug"], e["hero"]))
        if d in seen:
            problems.append("%s: identical search description to %s" % (e["slug"], seen[d]))
        seen[d] = e["slug"]
    if problems:
        sys.exit("build refused:\n  " + "\n  ".join(problems))


def main():
    entries = load_entries()
    check_entries(entries)
    tags = tag_index(entries)
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(entries))
    for key, (_, fn, _, _) in SECTIONS.items():
        write(fn, build_section_page(key, [e for e in entries if e["section"] == key]))
    write("about.html", build_about())
    write("ask.html", build_ask())
    write("thanks.html", build_thanks())

    for e in entries:
        write(e["file"], build_entry_page(e, entries))
    for tag, es_ in tags.items():
        write("tag-%s.html" % blogkit.tag_slug(tag),
              build_tag_page(tag, es_, len(es_) >= TAG_INDEX_MIN))
    tl = build_tag_list(tags)
    if tl:
        write("tags.html", tl)
    write("feed.xml", blogkit.build_feed(entries, site_name=SITE_NAME, site_url=SITE_URL,
                                         base=BASE, blurb=BLURB))
    write("sitemap.xml", build_sitemap(entries, tags))

    _prune_stale_tag_pages(tags)

    indexable = sum(1 for v in tags.values() if len(v) >= TAG_INDEX_MIN)
    by_section = collections.Counter(e["section"] for e in entries)
    print("built /notebook/ — %d entr%s (%s), %d tag page%s (%d indexable, %d held back "
          "at <%d entries)"
          % (len(entries), "y" if len(entries) == 1 else "ies",
             ", ".join("%s %d" % (k, by_section.get(k, 0)) for k in SECTIONS),
             len(tags), "" if len(tags) == 1 else "s", indexable,
             len(tags) - indexable, TAG_INDEX_MIN))
    for e in entries:
        print("  %s  %-12s %s" % (e["date"], e["section"], e["file"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

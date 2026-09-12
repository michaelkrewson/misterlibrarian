#!/usr/bin/env python3
"""Build /west/ — Eight Miles West, a family history published a chapter at a time.

    python3 build_west.py            # build the book (that's the whole CLI)
    python3 build_west.py --drafts   # LOCAL preview only — also renders `draft: true`
                                     # chapters, unlisted and noindexed. Never commit
                                     # a --drafts build.

STANDARD LIBRARY ONLY, deliberately — the same property every other builder in
this repo has. Nothing here touches the network; a chapter is a file on disk
and the build is a pure function of the source directory.

SIX PUBLICATIONS, ONE DOMAIN
────────────────────────────
mistertranslation.com serves six separate things behind the hand-written hub at
the bare root (index.html): the Bible project (/bible.html, build.py), The
Librarian Abroad (/travel/), The Librarian's Ledger (/finance/), The Librarian's
Regimen (/health/), The Librarian's Notebook (/notebook/), and this (/west/).
Added 2026-09-11 (Michael's call).

WHAT THIS IS
Non-fiction: the Krewson family's four centuries in America — Croesen, Kroesen,
Kroessen, Kreuso, Cruse, Krewson, a dozen spellings of one name — from a cooper
who landed at Breuckelen around 1660, through Staten Island, Bucks County, Ohio,
Iowa and the Pacific, told one documented person at a time. The source is the
family's own record (Warren D. Cruise, *The Croesen Families of America*, Vol. I,
1998; the Manhattan and Brooklyn church books; Pennsylvania wills; Uncle Al's
letters, 2000–2005) and the book says, chapter by chapter, what is documented,
what is inferred, and what is family legend. It is written to be read on the
web first and compiled into a printed book later — every chapter is a finished
thing with its own URL, and the book accretes instead of looming.

WHY A SIXTH PUBLICATION AND NOT AN ENTRY IN THE NOTEBOOK
A book has an ORDER. The Notebook (and the Regimen, the Ledger, the Abroad) are
dated entries, newest first, filtered by tag — the right shape for a blog, the
wrong one for a narrative whose chapter 14 makes no sense without chapter 13.
So this builder has no tags, no tag pages, no search box and no "newest first":
it has PARTS (the five eras below), numbered chapters inside them, a table of
contents that IS the front page, and previous/next links. The publish date
still exists (for the feed and the sitemap) but the reading order comes from
the chapter number in the filename, never from the date.

WHY ITS OWN PUBLICATION AND NOT ITS OWN DOMAIN
Because a new domain starts at zero and this one already has authority and a
Search Console. The readers this book is for search by surname — Croesen,
Kroesen, Krewson, Staats, Nevius, Cregier — and almost nothing exists for those
queries. A chapter here ranks in a month. The same reasoning as every other
publication on the domain.

DRAFTS — the Regimen's posture, kept on purpose
The Notebook has no draft mechanism at all (Michael: "I can always go back and
have you reword something"). This publication keeps `draft: true` = NOT BUILT,
with `--drafts` as a local-only preview, for one reason the Notebook doesn't
have: the later chapters are about living people and a father who left. Those
get read by Michael in his own voice before they get a URL. No drafts PAGE is
published — a draft is invisible until the line is deleted.

SOURCES ARE REQUIRED
Every chapter ends with `<ol class="sources">` and the build refuses one
without it — the Regimen's rule, for the same reason: this is non-fiction, a
reader must be able to check the document behind every claim, and the
book's whole promise is that it says which sentences are documented and which
are family legend.

This builder writes ONLY inside west/ and never globs or deletes anywhere
else — the same discipline that lets the other five coexist safely. If a
shared mechanism needs fixing, fix it in blogkit.py; the builders do not
import each other (see CLAUDE.md).

RENAMING
The working title is "Eight Miles West" — the family's first move was a boat
ride across the Kill from Gowanus to Staten Island, and every generation after
went further the same direction. Edit SITE_NAME / TAGLINE / BLURB below if the
prose decides on a different title; the URL (/west/) stays.
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone

import blogkit

SITE_NAME = "Eight Miles West"
# The one publication on the domain with a real name on it (Michael's call,
# 2026-09-11): this is his own family's book, and the printed edition will carry
# the same name. Everywhere else the domain's byline stays "Mr. Librarian".
AUTHOR = "Michael V. Krewson"
TAGLINE = "A family's four centuries in America — from New Amsterdam to the Pacific, one document at a time"
BLURB = ("The Krewson family's four centuries in America — Croesen, Kroesen, Kroessen, "
         "Kreuso, Cruse, Krewson — from a cooper who landed at Breuckelen around 1660, "
         "through Staten Island, Bucks County, Ohio, Iowa and the Pacific. Non-fiction, "
         "read from the family's own record and the colonial church books, published a "
         "chapter at a time by Michael V. Krewson.")

FRONT_DESC = ("A family's four centuries in America, from New Amsterdam to the Pacific — "
              "the Croesen / Kroesen / Krewson line, read from the documents, one chapter "
              "at a time.")

BASE_URL = "https://mistertranslation.com/west/"
SITE_URL = "https://mistertranslation.com"
BASE = "/west"

GOATCOUNTER_CODE = "mistertranslation"

# Front-matter vocabulary. `part` and the chapter number (from the filename)
# give the reading order; `date` is the PUBLISH date (feed + sitemap) and says
# nothing about order. `dateline` is the in-story place and time a chapter
# opens on ("Manhattan · 5 July 1662") and renders under the title. `people`
# is a comma list of the documented people the chapter is about — rendered as
# an "In the record" line so a surname-searcher landing mid-book sees who this
# is about before the prose starts.
KNOWN_KEYS = {"title", "date", "part", "dateline", "people", "summary", "meta_desc",
              "hero", "hero_alt", "hero_credit", "draft"}
REQUIRED_KEYS = {"title", "date", "part", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70

# The five parts, in reading order. key → (roman numeral, name, span, lede).
# The key is what a chapter's `part:` line carries; the build refuses any
# other value. These are the five eras the family record divides into on its
# own — see the timeline that preceded this build (2026-09-11).
PARTS = {
    "flags":   ("I", "Two Homelands, Two Flags", "1605 – 1709",
                "New Amsterdam, Breuckelen, Staten Island. The colony changes hands "
                "twice around a family that never moves."),
    "will":    ("II", "The X on the Will", "1709 – 1798",
                "Bucks County, Pennsylvania. The surname becomes Krewson in a legal "
                "document. A family buys its freedom by instalment. The Revolution "
                "passes ten miles away."),
    "west":    ("III", "Ohio, Iowa, Oregon", "1788 – 1935",
                "The frontier chain: four generations, one photograph, and a century "
                "the record barely sees."),
    "broke":   ("IV", "The Year the Family Broke Apart", "1935 – 1971",
                "Los Angeles, Tulsa, Dublin, Berlin, the North Atlantic, Vietnam."),
    "keepers": ("V", "The People Who Kept This", "1915 – today",
                "Who wrote it down — and why a four-star general and a machinist's "
                "grandson ended up looking for the same cooper."),
}

SIBLINGS = (
    ("The Librarian's Notebook", "https://mistertranslation.com/notebook/",
     "A commonplace book — science and technology, the world, arts and culture"),
    ("The Librarian's Ledger", "https://mistertranslation.com/finance/",
     "What the world's money is actually in"),
    ("The Librarian Abroad", "https://mistertranslation.com/travel/",
     "Notes from the road and the table"),
    ("The Librarian's Regimen", "https://mistertranslation.com/health/",
     "Health, nutrition and medicine — one question at a time, from the studies"),
)

FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "west")
CHAPTER_SRC = os.path.join(ROOT, "source", "west")

# Delft blue — the one colour the subject owns outright. Distinct from the
# Notebook's periwinkle (#8fa3ff, violet-leaning) and every warm accent on the
# hub.
ACCENT = "#4fa8dc"
ACCENT_RGB = "79,168,220"


def esc(s):
    return html.escape(str(s), quote=True)


# ─────────────────────────────────────────────────────────────────── loading ──

def load_chapters(include_drafts=False):
    """Read source/west/NN-slug.html into chapter dicts, in READING order.

    The filename carries the order: `03-the-tree-thief.html` is chapter 3.
    Numbers must be unique; gaps are allowed (a chapter can be written out of
    order and slotted in), but two files claiming the same number is refused.
    """
    if not os.path.isdir(CHAPTER_SRC):
        return []
    chapters = []
    seen_num = {}
    for fn in sorted(os.listdir(CHAPTER_SRC)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue
        with open(os.path.join(CHAPTER_SRC, fn), encoding="utf-8") as fh:
            meta, body = blogkit.parse_front_matter(
                fh.read(), "source/west/" + fn, KNOWN_KEYS, REQUIRED_KEYS)

        m = re.match(r"(\d{2,3})-(.+?)\.html$", fn)
        if not m:
            raise ValueError("source/west/%s: name must be NN-slug.html (NN = chapter number)" % fn)
        num = int(m.group(1))
        slug = m.group(2)
        if num in seen_num:
            raise ValueError("source/west/%s: chapter number %d is already taken by %s"
                             % (fn, num, seen_num[num]))
        seen_num[num] = fn

        try:
            date = dt.date.fromisoformat(meta["date"].strip())
        except ValueError:
            raise ValueError("source/west/%s: `date: %s` is not YYYY-MM-DD" % (fn, meta["date"]))

        part = meta["part"].strip().lower()
        if part not in PARTS:
            raise ValueError("source/west/%s: `part: %s` is not one of %s"
                             % (fn, meta["part"], ", ".join(PARTS)))

        draft = meta.get("draft", "").strip().lower() in ("true", "yes", "1")
        if draft and not include_drafts:
            continue

        chapters.append({
            "num": num,
            "slug": slug,
            "file": slug + ".html",
            "date": date,
            "part": part,
            "title": meta["title"],
            "dateline": meta.get("dateline", "").strip(),
            "people": [p.strip() for p in meta.get("people", "").split(",") if p.strip()],
            "summary": meta["summary"],
            "meta_desc": meta.get("meta_desc", "").strip(),
            "tags": [],   # blogkit.build_feed reads this key; a book has no tags
            "hero": meta.get("hero", "").strip(),
            "hero_alt": meta.get("hero_alt", "").strip(),
            "hero_credit": meta.get("hero_credit", "").strip(),
            "draft": draft,
            "body": body,
        })
    chapters.sort(key=lambda c: c["num"])
    return chapters


def _desc(c):
    return blogkit.meta_desc(c["meta_desc"], c["summary"], META_DESC_MIN, META_DESC_MAX)


def _part_num(key):
    return PARTS[key][0]


def _part_name(key):
    return PARTS[key][1]


# ──────────────────────────────────────────────────────────────────── chrome ──

def _nav(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    links = ['<a href="index.html"%s>Contents</a>' % cls("home"),
             '<a href="about.html"%s>About the book</a>' % cls("about"),
             '<a href="ask.html"%s>Write in</a>' % cls("ask")]
    return '<nav class="nav">%s</nav>' % "".join(links)


def _chrome(active=""):
    """Header — brand left, nav underneath. No search box: a book is read in
    order, and the contents page is the search."""
    hamburger = ('<svg viewBox="0 0 20 14" width="20" height="14" aria-hidden="true" '
                 'focusable="false"><rect width="20" height="2" rx="1"/>'
                 '<rect y="6" width="20" height="2" rx="1"/>'
                 '<rect y="12" width="20" height="2" rx="1"/></svg>')
    return ('<header class="hsm">'
            '<a class="brand" href="index.html">%s'
            '<span class="wm">Eight Miles <span class="em">West</span></span></a>'
            '<div class="hgroup">'
            '<input type="checkbox" class="navcb" id="navcb"/>'
            '<label class="navtoggle" for="navcb" aria-label="Menu">%s</label>'
            '%s</div></header>'
            % (MARK_SVG.replace("__ACCENT__", ACCENT), hamburger, _nav(active)))


def _legal():
    year = datetime.now(timezone.utc).year
    return ('<p class="legal">© %d %s. A work of family history published for interest. '
            'Every chapter says which of its statements rest on a document, which are '
            'inferred, and which are family legend; documents are cited so they can be '
            'checked, and may be misread, superseded or simply wrong. Living people are '
            'written about with their knowledge. Nothing here is professional advice of '
            'any kind, genealogical or otherwise. Opinions are the author\'s own.</p>'
            % (year, esc(AUTHOR)))


def _foot(hits_path=None):
    hits = _hits_widget(hits_path, " views") if hits_path else ""
    hits_bit = " · %s" % hits if hits else ""
    sibs = " · ".join('<a href="%s">%s</a>' % (url, esc(name)) for name, url, _ in SIBLINGS)
    return ('<footer>%s · <a href="about.html">About the book</a> · '
            '<a href="ask.html">Write in</a> · <a href="feed.xml">RSS</a> · %s%s%s</footer>'
            % (esc(SITE_NAME), sibs, hits_bit, _legal()))


def _shell_hits_path(url):
    name = url.rstrip("/").rsplit("/", 1)[-1]
    return "%s/%s" % (BASE, name) if "." in name else None


def _goatcounter():
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


def _hits_id(path):
    return "hits-" + re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def _hits_widget(path, suffix=""):
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


def _shell(*, title, desc, url, body, active="", noindex=False, og_type="website"):
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
<meta name="author" content="%(author)s"/>
<style>%(css)s</style>%(goat)s
</head>
<body>
<div class="wrap">
  %(chrome)s
%(body)s
  %(foot)s
</div>
</body>
</html>
""" % {"title": esc(title), "desc": esc(desc), "robots": robots, "url": url,
       "site": esc(SITE_NAME), "ogt": og_type, "author": esc(AUTHOR),
       "css": CSS.replace("__ACCENT__", ACCENT).replace("__ACCENT_RGB__", ACCENT_RGB),
       "chrome": _chrome(active), "body": body,
       "foot": _foot(_shell_hits_path(url)), "goat": _goatcounter()}


# ───────────────────────────────────────────────────────────── chapter page ──

def _hero(c):
    if not c["hero"]:
        return ""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), c["hero"])
    cap = "<figcaption>%s</figcaption>" % c["hero_credit"] if c["hero_credit"] else ""
    return ('<figure class="hero"><img src="img/%s" alt="%s"%s loading="eager"/>%s</figure>'
            % (esc(c["hero"]), esc(c["hero_alt"]), dims, cap))


# ─────────────────────────────────────────────────────────────────── plates ──
#
# A PLATE is a picture placed in the chapter it belongs to — never gathered
# into an insert section in the middle of the book (Michael's call, 2026-09-12).
# The author writes the minimum:
#
#     <figure class="plate">
#       <img src="img/name.jpg" alt="what is in the frame"/>
#       <figcaption>What is known about it.
#         <span class="cite">Where it came from.</span></figcaption>
#     </figure>
#
# and the BUILD fills in the rest — real width/height off the file on disk (so
# the page never reflows as pictures load) plus lazy decoding. Dimensions are
# read, not declared, for the same reason the wills are quoted and not
# paraphrased: a number typed by hand is a number that can drift from the
# thing it describes.
#
# `check_chapters` refuses a plate whose file is missing, whose `alt` is empty,
# or which has no caption — the picture equivalent of the rule that refuses a
# chapter with no `<ol class="sources">`.

PLATE_RE = re.compile(r'<figure\b[^>]*\bclass="[^"]*\bplate\b[^"]*"[^>]*>(.*?)</figure>',
                      re.S | re.I)
IMG_SRC_RE = re.compile(r'<img\b([^>]*?)\bsrc="img/([^"]+)"([^>]*?)/?>', re.I)


def plate_images(body):
    """Every img filename referenced by a plate in this body, in reading order.

    Used by the web build for `og:image` and by `build_west_book.py` to know
    which pictures the printed edition and the EPUB have to carry.
    """
    out = []
    for block in PLATE_RE.findall(body or ""):
        for _pre, name, _post in IMG_SRC_RE.findall(block):
            if name not in out:
                out.append(name)
    return out


def _prepare_plates(body):
    """Inject measured width/height + lazy decoding into every plate image."""
    img_dir = os.path.join(OUT, "img")

    def fix_block(m):
        block = m.group(0)

        def fix_img(im):
            pre, name, post = im.group(1), im.group(2), im.group(3)
            attrs = (pre + post)
            add = ""
            if " width=" not in attrs:
                add += blogkit.dim_attrs(img_dir, name)
            if "loading=" not in attrs:
                add += ' loading="lazy" decoding="async"'
            return '<img%ssrc="img/%s"%s%s/>' % (pre, name, post.rstrip(), add)

        return IMG_SRC_RE.sub(fix_img, block)

    return PLATE_RE.sub(fix_block, body or "")


def _comment_box(c, url):
    """X as the comment layer, published chapters only — a draft preview's URL
    is unlisted and must never be pushed to X."""
    if c["draft"]:
        return ""
    comment = blogkit.x_comment_url(c["title"], url)
    search = blogkit.x_search_url(url)
    return ('<div class="respond"><div class="respond-actions">'
            '<a class="respond-btn respond-btn-primary" href="%s" target="_blank" '
            'rel="noopener">💬 Comment on X</a>'
            '<a class="respond-btn respond-btn-secondary" href="%s" target="_blank" '
            'rel="noopener">🔍 See what others said</a>'
            '</div></div>' % (comment, search))


def _prevnext(c, live):
    """Previous / next in READING order among published chapters — a draft
    never appears as anyone's neighbour."""
    order = [o for o in live if not o["draft"]]
    idx = next((i for i, o in enumerate(order) if o["num"] == c["num"]), None)
    prev_ = order[idx - 1] if idx is not None and idx > 0 else None
    next_ = order[idx + 1] if idx is not None and idx + 1 < len(order) else None
    left = ('<a class="pn prev" href="%s"><span class="pnl">← Previous</span>'
            '<span class="pnt">%d · %s</span></a>' % (prev_["file"], prev_["num"], esc(prev_["title"]))
            if prev_ else '<span class="pn"></span>')
    right = ('<a class="pn next" href="%s"><span class="pnl">Next →</span>'
             '<span class="pnt">%d · %s</span></a>' % (next_["file"], next_["num"], esc(next_["title"]))
             if next_ else '<a class="pn next" href="index.html"><span class="pnl">Contents</span>'
                           '<span class="pnt">The next chapter isn\'t written yet</span></a>')
    return '<nav class="prevnext">%s%s</nav>' % (left, right)


def build_chapter_page(c, live):
    hits_path = None if c["draft"] else "%s/%s" % (BASE, c["file"])
    desc = _desc(c)
    url = BASE_URL + c["file"]
    noindex = '<meta name="robots" content="noindex,nofollow"/>\n' if c["draft"] else ""
    dateline = '<p class="dateline">%s</p>' % esc(c["dateline"]) if c["dateline"] else ""
    people = ('<p class="record"><span class="rlabel">In the record</span> %s</p>'
              % " · ".join(esc(p) for p in c["people"])) if c["people"] else ""
    draft_banner = ('<p class="draftbanner">DRAFT — local preview, not published</p>'
                    if c["draft"] else "")
    # The chapter's first plate is its share card. Nothing is rendered twice
    # for this: the picture is in the prose where it belongs and the card just
    # points at the same file. A chapter with no picture keeps the plain
    # `summary` card it has always had.
    plates = plate_images(c["body"])
    og_image = ""
    card = "summary"
    if plates:
        og_image = ('<meta property="og:image" content="%simg/%s"/>\n'
                    % (BASE_URL, plates[0]))
        card = "summary_large_image"
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>%(title)s — %(site)s</title>
<meta name="description" content="%(desc)s"/>
%(noindex)s<link rel="canonical" href="%(url)s"/>
<link rel="alternate" type="application/rss+xml" title="%(site)s" href="feed.xml"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="%(site)s"/>
<meta property="og:title" content="%(title)s"/>
<meta property="og:description" content="%(desc)s"/>
<meta property="og:url" content="%(url)s"/>
%(ogimg)s<meta property="article:section" content="Part %(pnum)s — %(pname)s"/>
<meta name="author" content="%(author)s"/>
<meta name="twitter:card" content="%(card)s"/>
<style>%(css)s</style>%(goat)s
</head>
<body>
<div class="wrap">
  %(chrome)s
  %(draft)s
  <article class="entry chapter">
    <p class="edate"><a class="esec" href="index.html#part-%(pkey)s">Part %(pnum)s · %(pname_u)s</a> · Chapter %(num)d</p>
    <h1 class="etitle">%(title)s</h1>
    %(dateline)s
    %(people)s
    %(hero)s
%(body)s
  </article>
  %(prevnext)s
  %(nudge)s
%(foot)s
</div>
</body>
</html>
""" % {
        "title": esc(c["title"]), "site": esc(SITE_NAME), "desc": esc(desc), "url": url,
        "noindex": noindex, "pkey": c["part"], "pnum": _part_num(c["part"]),
        "pname": esc(_part_name(c["part"])), "pname_u": esc(_part_name(c["part"]).upper()),
        "num": c["num"], "author": esc(AUTHOR),
        "css": CSS.replace("__ACCENT__", ACCENT).replace("__ACCENT_RGB__", ACCENT_RGB),
        "goat": _goatcounter(), "chrome": _chrome(""), "draft": draft_banner,
        "dateline": dateline, "people": people, "hero": _hero(c),
        "body": _prepare_plates(c["body"]),
        "ogimg": og_image, "card": card,
        "prevnext": _prevnext(c, live), "nudge": _comment_box(c, url),
        "foot": _foot(hits_path),
    }


# ─────────────────────────────────────────────────────────────── front page ──

FRONT_HERO_IMG = "castello-plan-1660.jpg"
FRONT_HERO_ALT = ("A hand-drawn colour map of the southern tip of Manhattan in 1660: the fort at "
                  "the bottom, a wall across the top, streets and garden plots between, and "
                  "the East River shore lined with small houses")
FRONT_HERO_CREDIT = (
    'The Castello Plan — New Amsterdam in 1660, drawn by Jacques Cortelyou, the year Garret '
    'Croesen landed across the river at Breuckelen. The fort at the foot of the island, the '
    'wall that became Wall Street across the top, and between them the garden plots and '
    'house lots of about 1,500 people, several of them in this book. Public domain, via '
    '<a href="https://commons.wikimedia.org/wiki/File:Castelloplan.jpg" rel="noopener" '
    'target="_blank">Wikimedia Commons</a>.')


def _front_hero():
    if not os.path.exists(os.path.join(OUT, "img", FRONT_HERO_IMG)):
        return ""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), FRONT_HERO_IMG)
    return ('<div class="fronthero"><figure><img src="img/%s" alt="%s"%s loading="eager"/>'
            '<figcaption>%s</figcaption></figure></div>'
            % (FRONT_HERO_IMG, esc(FRONT_HERO_ALT), dims, FRONT_HERO_CREDIT))


def _toc(chapters):
    """The table of contents — five parts, always all five, each listing its
    published chapters in order. A part with nothing written yet says so
    plainly rather than vanishing: the reader should see the shape of the
    whole book from day one, and where the writing has got to."""
    out = []
    for key, (num, name, span, lede) in PARTS.items():
        mine = [c for c in chapters if c["part"] == key]
        rows = "".join(
            '<li><a href="%s"><span class="cnum">%d</span><span class="ctitle">%s</span>'
            '<span class="cdate">%s</span></a></li>'
            % (c["file"], c["num"], esc(c["title"]), esc(c["dateline"] or ""))
            for c in mine)
        body = ('<ol class="chapters">%s</ol>' % rows if mine
                else '<p class="unwritten">Not yet written.</p>')
        out.append('<section class="part" id="part-%s">'
                   '<p class="pnum">Part %s</p>'
                   '<h2>%s</h2><p class="pspan">%s</p><p class="plede">%s</p>%s</section>'
                   % (key, num, esc(name), esc(span), esc(lede), body))
    return "\n".join(out)


def build_front(chapters):
    n = len(chapters)
    count = ("%d chapter%s published so far" % (n, "" if n == 1 else "s") if n
             else "The first chapter is being written")
    body = """  <p class="tag">%(tagline)s</p>
  <p class="byline">by %(author)s</p>
  %(hero)s
  <div class="lede">
    <p>This is the story of one family becoming American, read from the documents it left
    behind. It begins with a cooper from Winschoten who landed across the river from
    New Amsterdam around 1660 and married a girl born in the colony, and it follows their
    descendants — <b>Croesen, Kroesen, Kroessen, Kreuso, Cruse, Krewson</b>, a dozen spellings
    of one name — across the Kill to Staten Island, into Bucks County, Pennsylvania, on to
    Ohio and Iowa and the Pacific coast, and into the twentieth century's wars. Every chapter
    says which of its sentences rest on a document, which are inferred, and which are family
    legend.</p>
    <p class="count">%(count)s · <a href="about.html">About the book and its sources</a></p>
  </div>
  <blockquote class="epigraph">
    <p>"Seems like the whole Krewson line all the way back to the 1600s had these problems with rifts over disagreements… but no one was talking about what they were."</p>
    <footer>— Alfred G. M. Krewson to his nephew, 20 January 2005</footer>
  </blockquote>
%(toc)s
""" % {"tagline": esc(TAGLINE), "author": esc(AUTHOR), "hero": _front_hero(), "count": count, "toc": _toc(chapters)}
    return _shell(title="%s — %s" % (SITE_NAME, "a family's four centuries in America"),
                  desc=FRONT_DESC, url=BASE_URL, active="home", body=body)


# ──────────────────────────────────────────────────────────────── about page ──

ABOUT_BODY = """  <section class="asklede">
    <h1 class="wtitle">About the book</h1>
    <p class="wsub">What this is, where it comes from, and the rules it keeps.</p>
  </section>

  <div class="panel">
    <h2>What it is</h2>
    <p>A family history, written as narrative non-fiction and published one chapter at a
    time. The family is the one that landed at Breuckelen (Brooklyn) around 1660 as
    <b>Croesen</b> and has been spelled <b>Kroesen, Kroessen, Kreuso, Cruse</b> and
    <b>Krewson</b> since — the author's own. It is written by Michael V. Krewson, a
    tenth-generation descendant of the cooper, and published under his name; the rest of
    this domain is kept as Mr. Librarian, and the two are the same person. The book follows it from the Dutch colony
    through the English takeover, into Pennsylvania, across the frontier to Ohio and Iowa,
    and into the wars and breakages of the twentieth century. It is written to be read
    here first, in order, and compiled into a printed book when it is done.</p>
    <p>The working title is <i>Eight Miles West</i>: the family's first move, in 1677, was
    a boat ride across the Kill from Gowanus to Staten Island, and every generation after
    went further in the same direction.</p>
  </div>

  <div class="panel">
    <h2>Where it comes from</h2>
    <ul>
      <li><b>Warren D. Cruise, <i>The Croesen Families of America</i>, Vol. I</b> (Gateway
      Press, Baltimore, 1998) — the family's own published genealogy of the 1600s, drawn from
      the Manhattan and Brooklyn church books, the New Amsterdam court minutes, the Staten
      Island patents and the Bucks County wills, most of them transcribed in full. Quoted
      throughout, with page numbers; not reproduced. Among its credited contributors is
      <b>General Frederick J. Kroesen</b> (1923–2020), who researched his branch of the family
      for forty years, some of it in the Netherlands while commanding the United States Army
      in Europe.</li>
      <li><b>The colonial record itself</b> — the Reformed Dutch Church baptisms and marriages
      (Collections of the New York Genealogical and Biographical Society), the Court Minutes
      of New Amsterdam, the Esopus journals of Martin Cregier (in <i>Documents Relative to the
      Colonial History of the State of New York</i>), the Labadist travellers' journal of
      1679–80.</li>
      <li><b>Family papers</b> — the letters of Alfred G. M. Krewson, the family's own
      genealogist, written 2000–2005; certificates, wills and photographs in the family's
      keeping; an annotated photograph of ten people, c. 1890.</li>
    </ul>
  </div>

  <div class="panel">
    <h2>The rules it keeps</h2>
    <ul>
      <li><b>Documented, inferred, or legend — every chapter says which.</b> A date from a
      church book is stated as fact. A date worked back from someone's age is stated as an
      inference. The Cherokee (or Blackfoot) great-grandmother is stated as what it is: a
      story the family told, which the family's own genealogist could not resolve.</li>
      <li><b>Sources at the foot of every chapter.</b> The build refuses a chapter without
      them. A reader must be able to check the document behind a claim.</li>
      <li><b>The hard parts stay in.</b> A father who took his mother-in-law's money and left
      four children in Tulsa; a will that priced a family's freedom at eighty pounds; a
      twenty-nine-year quarrel between two brothers over a burned will. The family's own
      genealogist, asked in 2005 why the family had never built up land or wealth like others
      of its vintage, answered that the same rifts reached "all the way back to the 1600s."
      That answer is the book's thesis and it is not softened.</li>
      <li><b>Living people are written about with their knowledge.</b></li>
    </ul>
  </div>

  <div class="panel">
    <h2>If this is your family too</h2>
    <p>If you are a Croesen, Kroesen, Kroessen, Cruse or Krewson — or a Staats, Nevius,
    Cregier, Bergen, Van Artsdalen or Stickler — some of these people are your ancestors as
    well, and you may hold a document, a photograph or a story this book does not have.
    <a href="ask.html">Write in.</a> Corrections are the most useful thing anyone sends.</p>
  </div>
"""


def build_about():
    return _shell(title="About the book — %s" % SITE_NAME,
                  desc="What Eight Miles West is, the documents it is read from, and the rules "
                       "it keeps about what is fact, inference and family legend.",
                  url="%sabout.html" % BASE_URL, active="about", body=ABOUT_BODY)


ASK_BODY = """  <section class="asklede">
    <h1 class="wtitle">Write in</h1>
    <p class="wsub">A correction, a document, a photograph, a story — or a question about
    something in a chapter. It goes straight to my desk.</p>
  </section>

  <div class="panel">
    <form action="%(endpoint)s" method="POST" class="askform">
      <input type="hidden" name="_subject" value="Eight Miles West — a reader wrote in"/>
      <input type="hidden" name="_template" value="table"/>
      <input type="hidden" name="_next" value="%(next)s"/>
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>

      <label>Which chapter, or which person? <span class="opt">(optional)</span>
        <input type="text" name="entry" id="entryField" placeholder="A chapter, a name, or leave blank"/>
      </label>
      <label>Your name <span class="opt">(optional)</span>
        <input type="text" name="name" placeholder="However you'd like to be known — or leave blank"/>
      </label>
      <label>Your email <span class="opt">(optional — only if you'd like a reply)</span>
        <input type="email" name="email" placeholder="you@example.com"/>
      </label>
      <label>Your message <span class="req">(required)</span>
        <textarea name="message" required rows="7"
          placeholder="You have the date wrong — here is the record. My grandmother was his sister. We have a photograph of that house."></textarea>
      </label>
      <button class="btn" type="submit">Send it</button>
      <p class="formnote">Sending shows a quick captcha to keep the robots out, then brings
      you back here. Nothing is posted publicly — messages go to my inbox and I read all
      of them.</p>
    </form>
  </div>

<script>
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
    body = ASK_BODY % {"endpoint": FORM_ENDPOINT, "next": "%sthanks.html" % BASE_URL}
    return _shell(title="Write in — %s" % SITE_NAME,
                  desc="Send a correction, a document, a photograph or a story about the "
                       "Croesen / Kroesen / Krewson family, or ask about a chapter.",
                  url="%sask.html" % BASE_URL, active="ask", body=body)


def build_thanks():
    body = """  <section class="asklede">
    <h1 class="wtitle">It's on the desk</h1>
  </section>
  <div class="panel">
    <p><b>Your message is in.</b> Thank you — I read everything that arrives, and a
    correction or a document is the most useful thing anyone sends.</p>
    <p>If you left an email and it wants an answer, you'll get one. Meanwhile there is
    <a href="index.html">the book</a>.</p>
  </div>
"""
    return _shell(title="Message received — %s" % SITE_NAME,
                  desc="Your message is on the desk.",
                  url="%sthanks.html" % BASE_URL, body=body, noindex=True)


# ──────────────────────────────────────────────────────────── sitemap, checks ──

def build_sitemap(chapters):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, max((c["date"] for c in chapters), default=None) or today),
            (BASE_URL + "about.html", today), (BASE_URL + "ask.html", today)]
    urls[0] = (urls[0][0], urls[0][1] if isinstance(urls[0][1], str) else urls[0][1].isoformat())
    for c in chapters:
        urls.append((BASE_URL + c["file"], c["date"].isoformat()))
    rows = ["  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>" % (loc, mod)
            for loc, mod in urls]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def check_chapters(chapters):
    """Refuse to build on the mistakes that are invisible once shipped."""
    problems = []
    seen = {}
    for c in chapters:
        d = _desc(c)
        if len(d) > META_DESC_MAX:
            problems.append("%s: description is %d chars (max %d)" % (c["slug"], len(d), META_DESC_MAX))
        if '<ol class="sources">' not in c["body"]:
            problems.append("%s: no <ol class=\"sources\"> — every chapter cites its documents"
                            % c["slug"])
        if c["hero"] and not c["hero_alt"]:
            problems.append("%s: hero image has no hero_alt" % c["slug"])
        if c["hero"] and not os.path.exists(os.path.join(OUT, "img", c["hero"])):
            problems.append("%s: hero image west/img/%s does not exist" % (c["slug"], c["hero"]))
        # Plates: the file must exist, the picture must be described for a
        # reader who cannot see it, and it must carry a caption saying what is
        # known about it. Same posture as the sources rule — a picture with no
        # provenance is exactly the kind of thing this book promises not to do.
        for block in PLATE_RE.findall(c["body"]):
            imgs = IMG_SRC_RE.findall(block)
            if not imgs:
                problems.append('%s: a <figure class="plate"> has no '
                                '<img src="img/…"/>' % c["slug"])
            for _pre, name, _post in imgs:
                if not os.path.exists(os.path.join(OUT, "img", name)):
                    problems.append("%s: plate image west/img/%s does not exist"
                                    % (c["slug"], name))
            if not re.search(r'\balt="[^"]+"', block):
                problems.append("%s: plate %s has no alt text"
                                % (c["slug"], imgs[0][1] if imgs else "?"))
            if "<figcaption" not in block:
                problems.append("%s: plate %s has no <figcaption> — every picture "
                                "says what is known about it and where it came from"
                                % (c["slug"], imgs[0][1] if imgs else "?"))
        if d in seen:
            problems.append("%s: identical search description to %s" % (c["slug"], seen[d]))
        seen[d] = c["slug"]
    if problems:
        sys.exit("build refused:\n  " + "\n  ".join(problems))


# ───────────────────────────────────────────────────────────────────── main ──

def main():
    include_drafts = "--drafts" in sys.argv
    chapters = load_chapters(include_drafts=include_drafts)
    check_chapters(chapters)
    live = [c for c in chapters if not c["draft"]]
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(live))
    write("about.html", build_about())
    write("ask.html", build_ask())
    write("thanks.html", build_thanks())
    for c in chapters:
        write(c["file"], build_chapter_page(c, live))
    # The feed lists chapters newest-PUBLISHED first — that is what a feed is
    # for; the reading order lives on the contents page.
    write("feed.xml", blogkit.build_feed(sorted(live, key=lambda c: c["date"], reverse=True),
                                         site_name=SITE_NAME, site_url=SITE_URL,
                                         base=BASE, blurb=BLURB))
    write("sitemap.xml", build_sitemap(live))

    print("built /west/ — %d chapter%s%s" % (
        len(live), "" if len(live) == 1 else "s",
        " (+%d draft%s, LOCAL PREVIEW — do not commit)" % (
            len(chapters) - len(live), "" if len(chapters) - len(live) == 1 else "s")
        if include_drafts and len(chapters) > len(live) else ""))
    for c in chapters:
        print("  %2d  %-8s %s%s" % (c["num"], c["part"], "[DRAFT] " if c["draft"] else "", c["file"]))
    return 0


# ───────────────────────────────────────────────────────────────────── style ──

# The domain's shared look (dark ground, Georgia, the accent) — the same base
# every blog on the domain carries, plus this publication's own rules for the
# contents page and a chapter's dateline / record line / previous-next.
CSS = r"""
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

/* ── the animated mark: a compass whose needle settles west ─────────────── */
.bmark-needle{transform-origin:33px 33px;animation:bmarkNeedle 5.2s ease-in-out infinite}
@keyframes bmarkNeedle{
  0%{transform:rotate(-60deg)}
  45%{transform:rotate(14deg)}
  62%{transform:rotate(-6deg)}
  75%,100%{transform:rotate(0deg)}
}
@media (prefers-reduced-motion:reduce){.bmark-needle{animation:none}}

/* The Castello Plan's fort sits at the lower left of the sheet; the shared
   hero crop (object-position near the top) would cut it off. */
.fronthero img{height:340px;object-position:42% 78%}

.byline{margin:-6px 0 18px;color:#c3d0e0;font-size:15px;letter-spacing:.02em}

/* ── epigraph: Uncle Al's sentence, the book's thesis ─────────────────── */
.epigraph{max-width:640px;margin:48px auto 8px;padding:0;border:0;text-align:center}
.epigraph p{margin:0;color:#e8eef7;font-size:19px;line-height:1.6;font-style:italic}
.epigraph footer{margin:12px 0 0;padding:0;border:0;color:#7f8fa6;font-size:13px;font-style:normal;
  font-family:ui-sans-serif,system-ui,sans-serif;letter-spacing:.04em;text-align:center}

/* ── contents page ──────────────────────────────────────────────────────── */
.count{margin-top:14px;color:#7f8fa6;font-size:14px;font-style:italic}
.count a{color:#8b9ab0}
.part{max-width:760px;margin:44px auto 0;padding-top:26px;border-top:1px solid #1b2534}
.part .pnum{margin:0 0 4px;color:__ACCENT__;font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;font-family:ui-sans-serif,system-ui,sans-serif}
.part h2{margin:0;font-size:27px;font-weight:400;line-height:1.2;color:#e8eef7}
.part .pspan{margin:4px 0 0;color:#5a6b80;font-size:13px;letter-spacing:.06em;
  font-family:ui-sans-serif,system-ui,sans-serif;font-variant-numeric:tabular-nums}
.part .plede{margin:12px 0 0;color:#b9c6d8;font-size:15.5px}
.part .unwritten{margin:16px 0 0;color:#5a6b80;font-size:14px;font-style:italic}
.chapters{list-style:none;margin:18px 0 0;padding:0}
.chapters li{border-top:1px solid #131b27}
.chapters li:first-child{border-top:0}
.chapters a{display:grid;grid-template-columns:2.6rem 1fr auto;gap:12px;align-items:baseline;
  padding:12px 4px;text-decoration:none;color:inherit;border-radius:8px}
.chapters a:hover{background:#0a111c}
.chapters .cnum{color:__ACCENT__;font-variant-numeric:tabular-nums;font-size:15px}
.chapters .ctitle{color:#e8eef7;font-size:17.5px}
.chapters .cdate{color:#5a6b80;font-size:12.5px;letter-spacing:.04em;
  font-family:ui-sans-serif,system-ui,sans-serif;text-align:right}
@media (max-width:560px){.chapters a{grid-template-columns:2.2rem 1fr}.chapters .cdate{grid-column:2;text-align:left}}

/* ── chapter page ───────────────────────────────────────────────────────── */
.dateline{margin:-16px 0 22px;color:#93a4bd;font-size:15px;font-style:italic}
.record{margin:0 0 26px;padding:10px 14px;border:1px solid #1b2534;border-radius:8px;
  background:#0a111c;color:#a9b7c9;font-size:14px;line-height:1.6}
.record .rlabel{color:__ACCENT__;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  font-family:ui-sans-serif,system-ui,sans-serif;margin-right:8px}
.entry .sources{margin:38px 0 0;padding:22px 0 0 22px;border-top:1px solid #1b2534;
  color:#93a4bd;font-size:14px;line-height:1.6}
.entry .sources li{margin:0 0 7px}
.entry .sources a{color:#8b9ab0}
/* The three registers a chapter writes in. `.doc` is a quoted document, set
   apart; `.legend` is a family story stated as a story; `.infer` marks a
   sentence worked back from a date or an age rather than read off a page. */
.entry .doc{margin:26px 0;padding:14px 20px;border-left:3px solid __ACCENT__;background:#0a111c;
  border-radius:0 10px 10px 0;color:#d6e0ee;font-size:15.5px;line-height:1.7}
.entry .doc p{margin:0 0 10px;color:inherit;font-size:inherit}
.entry .doc p:last-child{margin:0}
.entry .doc .cite{display:block;margin-top:8px;color:#7f8fa6;font-size:13px;font-style:italic}
.entry .legend{border-left-color:#e8c968;background:#120f0a}
.entry .infer{color:#a9b7c9;font-style:italic}
/* ── PLATES — a photograph is a document, so it wears a document's clothes ───
   figure.plate is the picture counterpart of `.doc`: the image,
   then a caption saying what is actually known about it, then a `.cite` line
   giving the provenance — the same shape, the same accent rule, the same quiet
   italic citation. `.plate.legend` takes `.doc.legend`'s gold rule for a
   picture whose identification is family tradition rather than record, and
   `<span class="infer">` works inside a caption exactly as it does in the
   prose. A reader who has learned to read the three registers in the text
   reads them in the captions without being told a second time.
   ⚠ `max-width:100%` and nothing else: the pictures are NEVER upscaled, in CSS
   or on disk. Most of this archive is 1920s–60s snapshots surviving only as
   small scans of 250–600px, and a 1961 photograph of a man and a dog on a lawn
   renders as a small inset because that is the size of what exists. Stretching
   it would be the picture equivalent of promoting a legend to a fact. */
.entry .plate{margin:30px auto 30px;padding:0 0 0 20px;border-left:3px solid __ACCENT__;
  text-align:left}
.entry .plate img{display:block;max-width:100%;height:auto;border-radius:8px;
  background:#0a111c}
.entry .plate figcaption{margin:11px 0 0;max-width:620px;color:#93a4bd;font-size:14px;
  font-style:normal;line-height:1.6}
.entry .plate figcaption .cite{display:block;margin-top:6px;color:#7f8fa6;font-size:12.5px;
  font-style:italic}
.entry .plate.legend{border-left-color:#e8c968}
@media (max-width:560px){
  .entry .plate{padding-left:14px}
  .entry .plate figcaption{font-size:13.5px}
}
.draftbanner{margin:18px 0 -8px;text-align:center;color:#e8c968;font-size:12px;letter-spacing:.14em;
  font-family:ui-sans-serif,system-ui,sans-serif}
.prevnext{max-width:760px;margin:40px auto 0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.pn{display:flex;flex-direction:column;gap:4px;padding:14px 16px;border:1px solid #1b2534;
  border-radius:10px;text-decoration:none;color:inherit;background:#0a111c}
.pn:empty{border:0;background:transparent}
.pn.next{text-align:right}
.pn:hover{border-color:__ACCENT__}
.pnl{color:__ACCENT__;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  font-family:ui-sans-serif,system-ui,sans-serif}
.pnt{color:#c3d0e0;font-size:15px}
@media (max-width:560px){.prevnext{grid-template-columns:1fr}.pn.next{text-align:left}}
"""

MARK_SVG = """<svg class="bmark" viewBox="0 0 66 66" fill="none" aria-hidden="true">
  <circle class="bmark-glow" cx="33" cy="33" r="24" fill="none" stroke="__ACCENT__" stroke-width="5"/>
  <circle cx="33" cy="33" r="21" fill="#0a111c" stroke="__ACCENT__" stroke-width="1.4" opacity=".9"/>
  <g stroke="#9aa7bd" stroke-width="1.2" stroke-linecap="round" opacity=".8">
    <line x1="33" y1="14" x2="33" y2="18"/><line x1="33" y1="48" x2="33" y2="52"/>
    <line x1="14" y1="33" x2="18" y2="33"/><line x1="48" y1="33" x2="52" y2="33"/>
  </g>
  <text x="14.5" y="35.8" font-family="ui-sans-serif,system-ui,sans-serif" font-size="6.5" fill="__ACCENT__" text-anchor="middle">W</text>
  <g class="bmark-needle">
    <polygon points="33,33 18,33 33,29.6" fill="__ACCENT__"/>
    <polygon points="33,33 18,33 33,36.4" fill="__ACCENT__" opacity=".55"/>
    <polygon points="33,33 48,33 33,29.6" fill="#d9e0ea" opacity=".9"/>
    <polygon points="33,33 48,33 33,36.4" fill="#d9e0ea" opacity=".5"/>
    <circle cx="33" cy="33" r="2.2" fill="#f2f5f9"/>
  </g>
</svg>"""


if __name__ == "__main__":
    sys.exit(main())

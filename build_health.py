#!/usr/bin/env python3
"""Build /health/ — The Librarian's Regimen, a blog on health, nutrition and medicine.

    python3 build_health.py            # build the publication
    python3 build_health.py --drafts   # LOCAL preview only — also renders `draft: true`
                                       # entries (unlisted, noindexed, banner on top).
                                       # Never commit a --drafts build.

STANDARD LIBRARY ONLY, deliberately — same property build_travel.py and
build_finance.py have. Nothing here touches the network; an entry is a file on
disk and the build is a pure function of the source directory.

FOUR PUBLICATIONS, ONE DOMAIN
─────────────────────────────
mistertranslation.com serves four separate things behind the hand-written hub at
the bare root (index.html): the Bible project (/bible.html, build.py), The Librarian
Abroad (/travel/, build_travel.py), The Librarian's Ledger (/finance/,
build_finance.py), and this (/health/). Added 2026-09-10 (Michael's call) as a
DEDICATED health publication rather than a general "post anything" blog: health
and money are both subjects where a reader's trust is judged per topic, and a
kidney-stone piece sitting between two Bitcoin wallet audits is not the framing
either deserves. The name follows the house pattern — the noun carries the
subject: a *ledger* is where money is recorded; a *regimen* is the whole of how
you live — food, sleep, movement, and what you take when something goes wrong.
The medieval *Regimen sanitatis* handbooks (and Ibn Butlan's *Tacuinum
sanitatis*, the front-page hero) were exactly that genre.

This builder writes ONLY inside health/ and never globs or deletes anywhere else —
the same discipline that lets the other three coexist safely. The one deletion
it performs (`_prune_stale_tag_pages`) is scoped hard to health/tag-*.html.

WHAT THIS IS A COPY OF, AND WHAT IT DELIBERATELY ISN'T
──────────────────────────────────────────────────────
The *writing* half of build_finance.py, near-verbatim: front matter via blogkit,
the tile/list front page with its tag filter bar and header search, entry pages
with "Keep reading" recirculation, per-tag pages held out of the sitemap until
they carry TAG_INDEX_MIN entries, RSS, sitemap, the X comment layer, the
FormSubmit ask page. What it does NOT have is any of the Ledger's standing
boards — there is no live data feed here, and a health blog has no business
pretending a dashboard is writing. If a shared mechanism needs fixing, fix it in
blogkit.py; if a page-chrome idea proves out here, port it by hand (the two
builders do not import each other — see CLAUDE.md).

NO DRAFTS PAGE — SHIPS STRAIGHT LIVE, like the Ledger (Michael's call,
2026-09-10, offered the travel blog's drafts.html and declined). `draft: true`
means the entry does not build at all except under --drafts locally.

THE MEDICAL-ADVICE POSTURE, WHICH IS THE ONE THING THAT MAKES THIS BUILDER
DIFFERENT FROM THE OTHER TWO BLOGS
──────────────────────────────────
Every page's footer says it, `_legal` spells it out, every entry carries a
`.mednote` under its tags, the ask page turns "what should I take?" away, and the
About page explains how an entry is actually worked (primary sources, evidence
hierarchy, a Sources list on every entry, "what the evidence says" kept separate
from "what I'd do"). None of that is boilerplate to trim: this is a publication
about other people's bodies, written by a reader rather than a clinician, and the
reader has to be told that on every page they can land on, not just the About
page they may never open.

RENAMING
────────
Edit SITE_NAME / TAGLINE / BLURB below. The hub card on the root index.html and
the sibling links in build_travel.py / build_finance.py carry the name too.
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

SITE_NAME = "The Librarian's Regimen"
TAGLINE = "Health, nutrition and medicine — one question at a time, from the studies"
BLURB = ("Notes on health, nutrition and medicine, worked through one question at a time "
         "from the primary literature: what the studies actually found, how sure anyone "
         "can honestly be, and what that leaves a reasonable person to do. Written by a "
         "reader, not a clinician — nothing here is medical advice.")

BASE_URL = "https://mistertranslation.com/health/"
SITE_URL = "https://mistertranslation.com"
BASE = "/health"

# Cookie-less, no-consent-banner analytics, same account as the other three so
# there's one dashboard for the whole domain. Set to None to disable entirely.
GOATCOUNTER_CODE = "mistertranslation"

# The Regimen's front-matter vocabulary. The Ledger's minus `live` (nothing here
# rebuilds itself from a data feed) — an entry has no stars, no place, no chart.
KNOWN_KEYS = {"title", "date", "tags", "summary", "meta_desc",
              "hero", "hero_alt", "hero_credit", "draft"}
REQUIRED_KEYS = {"title", "date", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70

# A tag page listing a single entry is a near-duplicate of that entry — nothing
# for a searcher to land on that the entry itself doesn't already answer. The
# pages are still BUILT and still work; they are just held back from the
# sitemap until enough entries share the tag to make the page its own answer.
TAG_INDEX_MIN = 2

# The front-page tag filter bar: a tag earns a visible chip by RECURRING; the
# rest fold behind a "+N more" disclosure (see build_finance.py for the measured
# reasoning — a young blog's one-off tags outnumber its entries).
TAG_BAR_MIN_COUNT = 2
TAG_BAR_MAX_CHIPS = 18

# How many tiles show on the front page before older ones fold behind
# "Show more". No standing pages compete for these slots here.
FRONT_TILE_LIMIT = 6

# The sibling publications — both blogs link here and this links to both. The
# Bible project is reached via the root hub, same as from the other two.
SIBLINGS = (
    ("The Librarian's Ledger", "https://mistertranslation.com/finance/",
     "What the world's money is actually in"),
    ("The Librarian Abroad", "https://mistertranslation.com/travel/",
     "Notes from the road and the table"),
)

# The same FormSubmit endpoint the other two blogs post to, so every publication
# lands in one inbox; `_subject` is what tells them apart. Safe to reuse: a shared
# inbox is not a shared page, and the hash is already committed in this same
# public repo. A form rather than comments, for the reasons set out at length in
# build_travel.py.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"


ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "health")
ENTRY_SRC = os.path.join(ROOT, "source", "health")

# Mint-teal. Chosen against the three colours it has to sit beside in a shared
# nav/footer/hub: the Ledger's Bitcoin amber (#f7931a), the travel blog's
# terracotta (#e8865c) and the Bible project's gold (#e8c968) are all warm, so
# the fourth publication reads as its own thing only if it's cool. Not the
# Ledger's semantic green/red (this blog has no up/down tables, so no collision
# to worry about), and bright enough (~10:1 on the #060b14 ground) to carry a
# link colour.
ACCENT = "#3fd2a8"


# ────────────────────────────────────────────────────────────────── entries ──

def esc(s):
    return html.escape(str(s), quote=True)


def load_entries(include_drafts=False):
    """Read source/health/*.html into entry dicts, newest first.

    Shares blogkit's front-matter parser with the other two blogs but not
    their vocabulary — see KNOWN_KEYS above.
    """
    if not os.path.isdir(ENTRY_SRC):
        return []
    entries = []
    for fn in sorted(os.listdir(ENTRY_SRC)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue
        with open(os.path.join(ENTRY_SRC, fn), encoding="utf-8") as fh:
            meta, body = blogkit.parse_front_matter(
                fh.read(), "source/health/" + fn, KNOWN_KEYS, REQUIRED_KEYS)

        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.html$", fn)
        if not m:
            raise ValueError("source/health/%s: name must be YYYY-MM-DD-slug.html" % fn)
        date = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        slug = m.group(4)
        if meta["date"].strip() != date.isoformat():
            raise ValueError(
                "source/health/%s: `date: %s` disagrees with the filename (%s). "
                "This is what stops an entry filing itself under the wrong year."
                % (fn, meta["date"], date.isoformat()))

        draft = meta.get("draft", "").strip().lower() in ("true", "yes", "1")
        if draft and not include_drafts:
            continue

        entries.append({
            "slug": slug,
            "file": slug + ".html",
            "date": date,
            "title": meta["title"],
            "summary": meta["summary"],
            "meta_desc": meta.get("meta_desc", "").strip(),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "hero": meta.get("hero", "").strip(),
            "hero_alt": meta.get("hero_alt", "").strip(),
            "hero_credit": meta.get("hero_credit", "").strip(),
            "draft": draft,
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


def tag_index(entries):
    """{tag: [entries]} — every tag that appears on a live entry, newest first."""
    out = {}
    for e in entries:
        for t in e["tags"]:
            out.setdefault(t, []).append(e)
    return out


# ──────────────────────────────────────────────────────────────────── chrome ──

def _nav(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    # Two links. The Ledger's nav is seven because it has six standing boards;
    # this has none, and padding a nav with links to nowhere would only make the
    # publication look like it's pretending to be bigger than it is. "Ask" is
    # reached from the footer and the per-entry prompt, same as on the Ledger.
    return ('<nav class="nav">'
            '<a href="index.html"%s>Writing</a>'
            '<a href="about.html"%s>About</a>'
            '</nav>' % (cls("home"), cls("about")))


def _chrome(active=""):
    """Header used by every page in the publication — brand, search, nav.

    Same construction as build_finance._chrome: the nav collapses into a menu
    below 760px via the CSS-only checkbox hack (no JavaScript, so it can't
    break), and the search box is a REAL form (GET, name="q") so it works with
    JS off by navigating to the front page with ?q=…; the front page's own
    script filters live and reads a handed-over ?q=.
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
            '<span class="wm">The Librarian\'s <span class="em">Regimen</span></span></a>'
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

    The medical sentence is the whole reason this publication's legal line is
    not a copy of the Ledger's: the failure mode there is a reader buying
    something; the failure mode here is a reader stopping a medication."""
    return ('<p class="legal">© %d %s. Nothing on this site is medical, nutritional or '
            'health advice, and no reply from Mr. Librarian is either. This site is one '
            'reader\'s reading of published research — not a diagnosis, not a treatment, '
            'not a recommendation to start, stop or change anything — and it does not '
            'replace a conversation with a clinician who knows you. Studies are '
            'summarised in good faith from public sources and may be misread, '
            'superseded or simply wrong; check the originals before relying on '
            'anything here. No drug, product, company or organization named on this '
            'site has endorsed it or is affiliated with it.</p>'
            % (datetime.now(timezone.utc).year, esc(SITE_NAME)))


def _foot(hits_path=None):
    """`hits_path` (e.g. "/health/about.html") gets its own live-fetched view
    count appended (per-path GoatCounter counter via `_hits_widget`). `None`
    (the index page, which shows its own "N visits" line in-body) or a
    zero-hit path renders nothing — fail-silent, like every other call site."""
    hits = _hits_widget(hits_path, " views") if hits_path else ""
    hits_bit = " · %s" % hits if hits else ""
    sibs = " · ".join('<a href="%s">%s</a>' % (url, esc(name)) for name, url, _ in SIBLINGS)
    return ('<footer>%s · <a href="about.html">About</a> · '
            '<a href="tags.html">All tags</a> · <a href="ask.html">Ask a question</a> · '
            '<a href="feed.xml">RSS</a> · %s · '
            'nothing here is medical advice%s%s</footer>'
            % (esc(SITE_NAME), sibs, hits_bit, _legal()))


def _shell_hits_path(url):
    """Best-effort "/health/<file>.html" for `_foot`'s view-count widget, derived
    from the same absolute `url` every `_shell` caller already passes. Returns
    None for a url with no filename (the index page's bare BASE_URL)."""
    name = url.rstrip("/").rsplit("/", 1)[-1]
    return "%s/%s" % (BASE, name) if "." in name else None


FRONT_HERO_IMG = "tacuinum-cabbage-harvest.jpg"
FRONT_HERO_ALT = ("A page from a fifteenth-century Tacuinum sanitatis: in a walled garden, a "
                  "man in a rose-coloured coat lifts a basket heaped with cabbages onto his "
                  "head while a woman in blue holds the gate")
FRONT_HERO_CREDIT = (
    'Harvesting cabbages, from Ibn Butlan\'s <i>Tacuinum sanitatis</i> — an eleventh-century '
    'Arabic handbook of health, here in a Latin copy painted around 1445–1450 '
    '(Bibliothèque nationale de France, Latin 9333, f. 53). The genre that gave this '
    'publication its name: a <i>regimen</i> was the whole of how you lived. Public domain, via '
    '<a href="https://commons.wikimedia.org/wiki/File:Tacuinum_Sanitatis-cabbage_harvest.jpg" '
    'rel="noopener" target="_blank">Wikimedia Commons</a> / '
    '<a href="https://gallica.bnf.fr/ark:/12148/btv1b105072169" rel="noopener" '
    'target="_blank">Gallica</a>.')


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


def _ask_nudge(e):
    """_comment_box() for a published entry. A DRAFT (--drafts preview only)
    keeps a form-based nudge instead — its URL is unlisted and not meant to be
    posted publicly to X."""
    if e["draft"]:
        return ('<div class="respond">'
                '<p><strong>Got a question?</strong> Something here you want pushed on, '
                'or think I have wrong? <a href="ask.html?re=%s">Ask Mr. Librarian</a> — '
                'it goes straight to my desk.</p></div>'
                % urllib.parse.quote(e["title"]))
    full_url = "%s%s.html" % (BASE_URL, e["slug"])
    return _comment_box(e["title"], full_url)


def _mednote():
    """The per-entry disclaimer, under the tags on every entry. Deliberately a
    sentence a person would say rather than a legal block — the legal block is
    in the footer already; this one is meant to be read."""
    return ('<p class="mednote">This is one reader\'s reading of the research, not medical '
            'advice. If something here touches on your own health, take it to a clinician '
            'who knows you — and <a href="about.html">read how these entries are put '
            'together</a>.</p>')


# ──────────────────────────────────────────── entry-page recirculation ──

def _related_entries(e, pool, limit=4):
    """Entries to offer at the foot of `e`, best first: ranked by shared-tag
    count, ties broken by recency, topped up with the most recent so the block
    is never short. `pool` is the LIVE entry list — a draft must never surface
    here (unlisted and noindexed by contract)."""
    def tags_of(o):
        return {t.lower() for t in o.get("tags", ())}

    mine = tags_of(e)
    others = [o for o in pool if o["file"] != e["file"] and not o["draft"]]
    others.sort(key=lambda o: o["date"], reverse=True)
    others.sort(key=lambda o: len(mine & tags_of(o)), reverse=True)
    return others[:limit]


def _related_block(e, pool):
    """"Keep reading" — reuses `_tile`/`_front_item` rather than a private card
    so it can never drift from the front page's typography."""
    picks = _related_entries(e, pool)
    if not picks:
        return ""
    tiles = "\n".join(
        _tile(_front_item(href=o["file"],
                          label=blogkit.pretty_date(o["date"]).upper(),
                          title=o["title"], desc=_entry_desc(o),
                          date=o["date"], tags=o.get("tags", ())))
        for o in picks)
    return ('  <section class="readnext">\n'
            '    <h2>Keep reading</h2>\n'
            '    <div class="tilegrid">\n%s\n    </div>\n'
            '  </section>' % tiles)


def build_entry_page(e, pool=()):
    """Render one entry."""
    date_line = blogkit.pretty_date(e["date"]).upper()
    hits_path = None if e["draft"] else "%s/%s" % (BASE, e["file"])
    desc = _entry_desc(e)
    url = BASE_URL + e["file"]
    banner = ('<div class="draftban">🔒 <b>Draft preview</b> — not published. This page '
              'is not linked from the site and is absent from the feed.</div>'
              if e["draft"] else "")
    noindex = '<meta name="robots" content="noindex,nofollow"/>\n' if e["draft"] else ""
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
<meta name="twitter:card" content="summary"/>
<style>%(css)s</style>%(goat)s
</head>
<body>
<div class="wrap">
  %(chrome)s
  %(banner)s
  <article class="entry">
    <h1 class="etitle">%(title)s</h1>
    <p class="edate">%(date)s</p>
    %(hero)s
%(body)s
    %(tags)s
    %(mednote)s
  </article>
  %(nudge)s
%(related)s
  <p class="backlink"><a href="index.html">← Back to the Regimen</a></p>
%(foot)s
</div>
</body>
</html>
""" % {
        "title": esc(e["title"]),
        "site": esc(SITE_NAME),
        "desc": esc(desc),
        "noindex": noindex,
        "url": url,
        "css": CSS.replace("__ACCENT__", ACCENT),
        "goat": _goatcounter(),
        "chrome": _chrome("home"),
        "banner": banner,
        "date": date_line,
        "hero": _entry_hero(e),
        "body": e["body"],
        "tags": _tag_chips(e),
        "mednote": _mednote(),
        "nudge": _ask_nudge(e),
        "related": _related_block(e, pool),
        "foot": _foot(hits_path),
    }


def _entry_card(e):
    return ('    <a class="ecard" href="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]), blogkit.pretty_date(e["date"]).upper(),
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
    (e.g. "/health/about.html"). Fails SILENT on any error or a zero-hit path."""
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
       "css": (CSS + extra_css).replace("__ACCENT__", ACCENT),
       "js": ("<script>\n%s\n</script>\n" % extra_js.replace("__ACCENT__", ACCENT)
              if extra_js else ""),
       "chrome": _chrome(active), "body": body,
       "foot": _foot(_shell_hits_path(url)), "goat": _goatcounter()}


# ───────────────────────────────────────────────────────────────────── pages ──

def build_about():
    """Who is writing, how an entry is worked, and — above all — what this is
    not. The Ledger gets away without an About page because its boards explain
    themselves in their own methods panels; a health publication cannot. This
    is the page the footer's "nothing here is medical advice" and every entry's
    .mednote point at."""
    body = """  <section class="asklede">
    <h1 class="wtitle">About the Regimen</h1>
    <p class="wsub">Health, nutrition and medicine, one question at a time — read from the
    studies, by a reader.</p>
  </section>

  <div class="panel">
    <h2>What this is</h2>
    <p>A notebook of questions about the body, worked through properly. Each entry starts
    from one question a reasonable person might actually ask — what causes this, does that
    help, how much, compared with what — and goes to the primary literature to answer it:
    clinical guidelines, systematic reviews and meta-analyses, randomised trials, and the
    cohort studies underneath them, in roughly that order of trust. What comes back is
    written up plainly, with the working shown and the sources listed at the end of every
    entry, so nothing here has to be taken on faith.</p>
    <p>I am a reader, not a clinician. That is the whole posture of the site, and it is why
    every page says so.</p>
  </div>

  <div class="panel">
    <h2>What this is not</h2>
    <p><b>It is not medical advice, and no reply from me is either.</b> Nothing here is a
    diagnosis, a treatment, or a recommendation to start, stop or change anything you take
    or do. If an entry touches on your own health, the right next step is a conversation
    with a clinician who knows you — your history, your other conditions, your other
    medications — none of which a page on the internet can know.</p>
    <p>It is also not settled. Studies get superseded, retracted and misread — including by
    me. Every entry links its sources so you can check them, and being told I have got
    something wrong is the most useful message anyone can send.</p>
  </div>

  <div class="panel">
    <h2>How an entry is worked</h2>
    <ul>
      <li><b>One question, stated up front.</b> Not "everything about X" — one thing a
      person would actually want to know, answered as directly as the evidence allows.</li>
      <li><b>Primary sources, ranked.</b> A guideline or a systematic review outranks a
      single trial; a trial outranks an observational study; a mechanism or an animal study
      is a reason to look, not an answer. Where the best available evidence is weak, the
      entry says so rather than rounding it up.</li>
      <li><b>Numbers, not adjectives.</b> How many people, how big the effect, over how long,
      compared with what. "Significantly reduces" tells you nothing; "cut recurrence from
      about half to about a third over five years, in roughly two hundred people" tells you
      something.</li>
      <li><b>"What the evidence says" is kept separate from "what I'd do."</b> The second is
      one person's judgment about one person's circumstances, and it is labelled as such.</li>
      <li><b>Sources at the end of every entry</b>, linked, so the reading can be checked and
      the entry corrected.</li>
    </ul>
  </div>

  <div class="panel">
    <h2>Why "Regimen"</h2>
    <p>The word is older than it sounds. A <i>regimen sanitatis</i> — a rule of health — was
    a whole medieval genre: handbooks that took the body as something you kept, like a
    garden, through what you ate and drank, how you slept, how you moved, the air you
    breathed, and what you took when something went wrong. Ibn Butlan's eleventh-century
    <i>Tacuinum sanitatis</i>, whose page of cabbage-pickers sits at the top of the front
    page, is one of them. Those books were confident, comprehensive, and frequently wrong.
    The idea here is to keep their scope — the whole of how you live, not just the pills —
    and lose their confidence: show the working, cite the studies, and say how sure anyone
    can honestly be.</p>
  </div>

  <div class="panel expect">
    <h2>Reaching me</h2>
    <p>Every entry ends with a button that opens a public reply on X, and a search that finds
    what other readers have said about the same page. For anything not tied to one entry —
    a question, a correction, a study I should have read — there is
    <a href="ask.html">a form that goes straight to my desk</a>. Please read what it
    <a href="ask.html#expect">can and can't be used for</a> first.</p>
  </div>
"""
    return _shell(title="About — %s" % SITE_NAME,
                  desc="What The Librarian's Regimen is, how each entry is worked from the "
                       "primary literature, and why none of it is medical advice.",
                  url="%sabout.html" % BASE_URL, active="about", body=body)


def build_ask():
    """The one place a reader can reach the librarian about the writing.

    Posts to FormSubmit — no backend, no database, no cookie. The `re` query
    parameter carries which entry the reader came from and is filled in
    client-side.

    ⚠️ The expectations paragraph is not boilerplate. On a publication about
    health the question it will attract most is "should I take / stop / try X?",
    and it is the one question that must never get an answer here — not out of
    caution but because answering it would be practising medicine on a stranger
    whose history is unknown. Saying so on the form is kinder than saying it in
    a reply, and it steers people toward the questions that can be answered well.
    """
    body = """  <section class="asklede">
    <h1 class="wtitle">Ask Mr. Librarian</h1>
    <p class="wsub">A question about something written here, a correction, or a study you
    think I have misread. It goes straight to my desk.</p>
  </section>

  <div class="panel">
    <form action="%(endpoint)s" method="POST" class="askform">
      <input type="hidden" name="_subject" value="The Librarian's Regimen — a question from a reader"/>
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
          placeholder="Which trial is that number from? Did you see the newer review? Why did you weight the cohort study so lightly?"></textarea>
      </label>
      <button class="btn" type="submit">Send it</button>
      <p class="formnote">Sending shows a quick captcha to keep the robots out, then brings
      you back here. Nothing is posted publicly — messages go to my inbox and I read all
      of them.</p>
    </form>
  </div>

  <div class="panel expect" id="expect">
    <h2>What I can and can't answer</h2>
    <p><b>Ask me</b> where a number came from, why I trusted one study over another, to
    point me at research I have missed, or to tell me I have got a fact wrong — those last
    two are the most useful messages anyone sends.</p>
    <p><b>Don't ask me</b> whether you should take something, stop taking something, or
    what your symptoms mean. I am not going to answer that, and you should be wary of anyone
    on the internet who would: they do not know your history, your other conditions, or
    what else you take. Nothing on this site is medical advice and no reply from me will be
    either. If it is about your own health, please take it to a clinician who knows you.</p>
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
""" % {"endpoint": FORM_ENDPOINT, "next": "%sthanks.html" % BASE_URL}

    return _shell(title="Ask Mr. Librarian — %s" % SITE_NAME,
                  desc="Ask a question about something written on %s, point me at a study "
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


def build_front(entries):
    """The publication's front page: what has been written, newest first — as a
    bounded grid of tiles with a list view, a tag filter bar, and the header
    search, all client-side over one pool. Same construction as the Ledger's
    front page minus the standing-page tiles."""
    pool = [_front_item(href=e["file"], label=blogkit.pretty_date(e["date"]).upper(),
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
            return ('<button class="%s" data-tag="%s" title="%d %s">%s</button>'
                    % (cls, blogkit.tag_slug(t), n, "entry" if n == 1 else "entries", esc(t)))

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

    # A brand-new publication has nothing to list yet. Say so in a sentence
    # rather than rendering an empty grid with a view toggle over nothing.
    if not pool:
        viewbar = ""
        loadmore = ""
        empty_note = ('    <p class="empty first">The first entry is being written. '
                      '<a href="feed.xml">Subscribe to the feed</a> to catch it, or read '
                      '<a href="about.html">how the entries are put together</a> meanwhile.</p>\n')
    else:
        empty_note = ""
        viewbar = ('<div class="viewbar" id="viewbar">View: '
                   '<button class="viewbtn on" data-view="cards" type="button">\U0001F5C2 Cards</button>'
                   '<button class="viewbtn" data-view="list" type="button">\U0001F4CB List</button></div>')
        loadmore = ('<div class="loadmorewrap" id="loadMoreWrap" hidden>'
                    '<button class="loadmore" id="loadMoreBtn" type="button">Show more</button>'
                    '<div class="viewcount" id="viewCount"></div></div>')
    pagination_js = ("""
(function(){
  var TILE_FIRST = %d, TILE_STEP = 12, LIST_FIRST = 20, LIST_STEP = 40;
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
      more.textContent = '− fewer';
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
""" % FRONT_TILE_LIMIT)

    index_hits = _hits_widget("%s/index.html" % BASE, " visits to this page")
    index_hits_html = ('\n  <p class="pagehits">%s</p>' % index_hits) if index_hits else ""
    intro = '  <p class="tag ftag">%s</p>\n' % esc(TAGLINE)
    return _shell(
        title="%s — %s" % (SITE_NAME, TAGLINE),
        desc=BLURB, url=BASE_URL, active="home",
        body="""%s%s  <section class="writing">
%s    %s
    %s
    <p class="empty" id="searchEmpty" hidden>No entries match that search.</p>
    <div class="tilegrid" id="tiles">
%s
    </div>%s
    %s
  </section>%s
%s
""" % (_front_hero(), intro, empty_note, chips, viewbar, tiles, archive_html, loadmore,
       index_hits_html, _comment_box(SITE_NAME, BASE_URL)),
        extra_js=pagination_js)


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
   the shared cool wash up top, plus a warm accent-toned glow centred on the
   viewport so a soft light sits behind whatever cards are on screen. */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(120% 80% at 50% -8%,rgba(94,179,214,.10),transparent 60%),
    radial-gradient(70% 60% at 50% 48%,rgba(63,210,168,.13),transparent 72%)}
.wrap{position:relative;z-index:1;max-width:1060px;margin:0 auto;padding:0 22px 72px}
header{padding:46px 0 8px;text-align:center}
.brand{display:inline-flex;align-items:center;gap:14px;text-decoration:none;color:inherit}
.bmark{width:61px;height:61px;flex:0 0 61px;overflow:visible}
h1{margin:0;font-size:31px;font-weight:400;letter-spacing:.01em}

/* Animated mark: a mortar and pestle, ringed by a circle — the apothecary's
   sign, the one object that covers food, medicine and the preparing of both.
   Same construction as the Ledger's lighthouse: the halo (`.bmark-glow`) is a
   blurred RING drawn behind everything, radius already outside the crisp
   ring's r=21, so the light appears past the icon's edge and never inside it.
   The pestle rocks gently about its own tip inside the bowl
   (`animation-direction:alternate` retraces the same arc rather than
   snapping); the bowl is drawn OVER the pestle's lower half so the tip reads
   as inside the mortar. No transform-box override — for an SVG child a plain
   px transform-origin resolves against the viewBox. Respects reduced-motion. */
.bmark-glow{filter:blur(8px);transform-origin:33px 33px;
  animation:bmarkGlow 4.2s ease-in-out infinite}
.bmark-pestle{transform-origin:31px 41px;
  animation:bmarkGrind 2.6s ease-in-out infinite alternate}
@keyframes bmarkGlow{
  0%,100%{opacity:.32;transform:scale(.92)}
  50%{opacity:.7;transform:scale(1.12)}
}
@keyframes bmarkGrind{
  0%{transform:rotate(-7deg)}
  100%{transform:rotate(9deg)}
}
@media (prefers-reduced-motion:reduce){
  .bmark-glow,.bmark-pestle{animation:none}
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
footer{margin:52px 0 0;padding-top:22px;border-top:1px solid #131b27;text-align:center;
  color:#6e7d92;font-size:13.5px;font-family:ui-sans-serif,system-ui,sans-serif}
.legal{margin:14px auto 0;max-width:560px;color:#3f4c5f;font-size:10.5px;line-height:1.6;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
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
/* object-position sits a little above centre: on the Tacuinum page the two
   figures' heads and the basket of cabbages are in the upper-middle of the
   frame (the basket's top edge at ~15% of the height, the two faces at ~36%),
   and the library stamp is at the bottom — the band should show the former
   and never the latter. Measured against the 300px band on a 1000px-wide
   image: 26% shows the basket and both faces. */
.fronthero img{display:block;width:100%;height:300px;object-fit:cover;
  object-position:center 26%;border-radius:14px;border:1px solid #1b2534}
.fronthero figcaption{margin:11px 4px 0;color:#7f8fa6;font-size:13px;font-style:italic;
  line-height:1.55;text-align:center}
.fronthero figcaption a{color:#8b9ab0}
@media (max-width:720px){
  .fronthero img{height:170px;border-radius:10px}
  .fronthero figcaption{font-size:12px}
}

/* ── nav + cross-publication links ───────────────────────────────────────── */
header.hsm{display:flex;align-items:center;justify-content:space-between;gap:18px;
  flex-wrap:wrap;padding:26px 0 8px;border-bottom:1px solid #131b27;margin-bottom:4px}
.nav{display:flex;align-items:center;gap:20px;flex-wrap:wrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:13px}
.nav a{color:#93a4bd;text-decoration:none}
.nav a:hover{color:#e8eef7}
.nav a.on{color:__ACCENT__}

/* Collapsible on narrow screens via the CSS-only checkbox hack (see
   _chrome()'s docstring). */
.navcb{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
label.navtoggle{display:none;cursor:pointer;color:#93a4bd;
  padding:9px;border-radius:8px;align-items:center;justify-content:center}
label.navtoggle svg rect{fill:currentColor}
label.navtoggle:hover{color:#e8eef7;background:rgba(255,255,255,.05)}
.navcb:checked + label.navtoggle{color:__ACCENT__}
.navcb:focus-visible + label.navtoggle{outline:2px solid __ACCENT__;outline-offset:1px}

.hgroup{position:relative;display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  justify-content:flex-end;margin-left:auto}
.headersearch{margin:0}
.headersearch input[type=search]{
  width:150px;font:14px/1.3 Georgia,'Iowan Old Style','Palatino Linotype',serif;
  color:#e8eef7;background:#0d1521;border:1px solid #1e2938;border-radius:999px;
  padding:8px 15px;-webkit-appearance:none;appearance:none;transition:width .15s ease}
.headersearch input[type=search]::-webkit-search-cancel-button{display:none}
.headersearch input[type=search]::placeholder{color:#5a6b80}
.headersearch input[type=search]:focus{outline:none;width:190px;border-color:__ACCENT__;
  box-shadow:0 0 0 3px rgba(63,210,168,.14)}

@media (max-width:760px){
  label.navtoggle{display:flex}
  .hgroup .nav{display:none;position:absolute;right:0;top:calc(100% + 10px);z-index:30;
    flex-direction:column;align-items:stretch;gap:1px;min-width:210px;
    background:#0e1522;border:1px solid #1e2938;border-radius:12px;padding:8px;
    box-shadow:0 16px 40px rgba(0,0,0,.5)}
  .navcb:checked ~ .nav{display:flex}
  .hgroup .nav a{padding:10px 12px;border-radius:8px}
  .hgroup .nav a:hover{background:rgba(255,255,255,.05)}
  .hgroup .nav a.on{background:rgba(63,210,168,.10)}
}
@media (max-width:480px){
  header.hsm{flex-wrap:wrap}
  .hgroup{order:1;flex-wrap:wrap}
  .headersearch{order:2;flex:1 1 100%}
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
.draftban{margin:16px 0 0;padding:11px 15px;border:1px solid #7a5a2a;border-radius:9px;
  background:#1a1408;color:#e2c489;font-size:14.5px;
  font-family:ui-sans-serif,system-ui,sans-serif}
.entry{max-width:760px;margin:22px auto 0}
.etitle{font-size:33px;font-weight:400;line-height:1.22;margin:0 0 10px;letter-spacing:.01em}
.edate{margin:0 0 26px;color:#5a6b80;font-size:11px;letter-spacing:.12em;
  font-family:ui-sans-serif,system-ui,sans-serif}
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
/* The "what the evidence says" box — the entry's answer, set apart. */
.entry .verdict{margin:32px 0 0;padding:20px 24px;border-left:3px solid __ACCENT__;
  border-radius:0 10px 10px 0;background:#0a141c}
.entry .verdict p{margin:0 0 12px}
.entry .verdict p:last-child{margin:0}
/* The "what I'd do" box — one person's judgment, labelled as such and kept
   visibly distinct from the evidence box above it (amber, not the accent). */
.entry .mine{margin:24px 0 0;padding:18px 24px;border-left:3px solid #e2c489;
  border-radius:0 10px 10px 0;background:#12110b}
.entry .mine p{margin:0 0 12px}
.entry .mine p:last-child{margin:0}
.entry .half-note{color:#7f8fa6;font-size:14.5px;font-style:italic}
.entry hr{border:0;border-top:1px solid #1b2534;margin:34px 0}
/* Sources: every entry ends with one. Smaller and quieter than the prose, but
   real links — the whole point is that they can be followed. */
.entry ol.sources{font-size:14.5px;line-height:1.6;color:#a9b7c9;padding-left:26px}
.entry ol.sources li{margin:0 0 9px}
.entry ol.sources a{word-break:break-word}
.tags{margin:34px 0 0;display:flex;flex-wrap:wrap;gap:7px}
.tg{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12px;color:#8b9ab0;
  border:1px solid #1e2938;border-radius:999px;padding:4px 11px;background:#0a111c}
.mednote{margin:26px 0 0;padding:12px 16px;border:1px dashed #22384a;border-radius:9px;
  color:#7f8fa6;font-size:13.5px;line-height:1.6;font-style:italic;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.mednote a{color:#8b9ab0}
.backlink{max-width:760px;margin:34px auto 0;font-family:ui-sans-serif,system-ui,sans-serif;
  font-size:14.5px}

/* ── the writing list ────────────────────────────────────────────────────── */
.writing{margin:52px 0 0}
.wtitle{margin:0 0 6px;font-size:23px;font-weight:400;color:#e8eef7}
.wsub{margin:0 0 20px;color:#93a4bd;font-size:15px;font-style:italic}
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
.archive .ec-d{display:inline;flex:none;min-width:9.5em;margin-bottom:0}
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

# The mark: a mortar and pestle in the same 66×66 frame, ring and halo as the
# Ledger's lighthouse, so the two brands sit at the same visual weight in a
# shared nav. Drawn pestle-first so the bowl covers its lower half. No <defs>
# (no gradient, no clip) so it can be inlined on the root hub next to the
# lighthouse without an id collision.
MARK_SVG = """<svg class="bmark" viewBox="0 0 66 66" fill="none" aria-hidden="true">
  <circle class="bmark-glow" cx="33" cy="33" r="24" fill="none" stroke="__ACCENT__" stroke-width="5"/>
  <g class="bmark-pestle">
    <g transform="rotate(30 31 41)">
      <rect x="28.7" y="18" width="4.6" height="24" rx="2.3" fill="#f2f5f9"/>
      <circle cx="31" cy="18.2" r="3.1" fill="__ACCENT__"/>
    </g>
  </g>
  <path d="M20 36 Q20 49 33 49 Q46 49 46 36 Z" fill="#f2f5f9"/>
  <rect x="24" y="41.2" width="18" height="2.2" fill="__ACCENT__" opacity=".85"/>
  <rect x="18.2" y="33.6" width="29.6" height="3.8" rx="1.9" fill="#f2f5f9"/>
  <rect x="27" y="48.4" width="12" height="3" rx="1.3" fill="#d9e0ea"/>
  <circle cx="33" cy="33" r="21" stroke="__ACCENT__" stroke-width="1.4" opacity=".6"/>
</svg>"""


# ──────────────────────────────────────────────────────────────────── build ──

def build_sitemap(entries, tags):
    """A sitemap is the discovery plan — robots.txt advertises this file. Tag
    pages appear only once they carry TAG_INDEX_MIN entries; submitting a page
    we have marked noindex would be asking Google to index something we told it
    not to."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, today), ("%sabout.html" % BASE_URL, today),
            ("%sask.html" % BASE_URL, today)]
    for e in entries:
        urls.append(("%s%s" % (BASE_URL, e["file"]), e["date"].isoformat()))
    for tag, es in sorted(tags.items()):
        if len(es) >= TAG_INDEX_MIN:
            urls.append(("%stag-%s.html" % (BASE_URL, blogkit.tag_slug(tag)),
                         max(x["date"] for x in es).isoformat()))
    body = "\n".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>" % u
        for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + "\n</urlset>\n")


def _prune_stale_tag_pages(tags):
    """Delete tag pages whose tag no longer appears on any entry. Scoped hard to
    health/tag-*.html so it can never reach another publication's output."""
    keep = {"tag-%s.html" % blogkit.tag_slug(t) for t in tags}
    for fn in os.listdir(OUT):
        if fn.startswith("tag-") and fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(OUT, fn))
            print("  (removed stale tag page: %s)" % fn)


def check_entries(entries):
    """Refuse to build on the mistakes that are invisible once shipped. A hard
    failure rather than a warning: a warning printed during a build nobody
    reads is not a check.

    The last check is this publication's own: an entry with no Sources list is
    an entry that asks to be taken on faith, which is the one thing the About
    page promises never to do."""
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
        if d in seen:
            problems.append("%s: identical search description to %s" % (e["slug"], seen[d]))
        seen[d] = e["slug"]
        if 'class="sources"' not in e["body"]:
            problems.append("%s: no <ol class=\"sources\"> — every entry cites what it "
                            "read (see source/health/_template.html)" % e["slug"])
    if problems:
        sys.exit("build refused:\n  " + "\n  ".join(problems))


def main():
    include_drafts = "--drafts" in sys.argv

    entries = load_entries(include_drafts=include_drafts)
    live = [e for e in entries if not e["draft"]]
    check_entries(entries)

    tags = tag_index(live)
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(live))
    write("about.html", build_about())
    write("ask.html", build_ask())
    write("thanks.html", build_thanks())

    for e in entries:
        # `live`, not `entries`: "Keep reading" may only advertise published
        # entries, never a draft (unlisted + noindexed by contract).
        write(e["file"], build_entry_page(e, live))
    for tag, es in tags.items():
        write("tag-%s.html" % blogkit.tag_slug(tag),
              build_tag_page(tag, es, len(es) >= TAG_INDEX_MIN))
    tl = build_tag_list(tags)
    if tl:
        write("tags.html", tl)
    write("feed.xml", blogkit.build_feed(live, site_name=SITE_NAME, site_url=SITE_URL,
                                         base=BASE, blurb=BLURB))
    write("sitemap.xml", build_sitemap(live, tags))

    _prune_stale_tag_pages(tags)

    indexable = sum(1 for v in tags.values() if len(v) >= TAG_INDEX_MIN)
    print("built /health/ — %d entr%s (%d live), %d tag page%s (%d indexable, %d held "
          "back at <%d entries)"
          % (len(entries), "y" if len(entries) == 1 else "ies", len(live),
             len(tags), "" if len(tags) == 1 else "s", indexable,
             len(tags) - indexable, TAG_INDEX_MIN))
    for e in entries:
        print("  %s  %-38s %s" % (e["date"], e["file"], "[DRAFT]" if e["draft"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build /ask/ — Dear Mr. Librarian, reader questions about the Bible project answered
one at a time.

    python3 build_ask.py

STANDARD LIBRARY ONLY, same discipline as build_health.py/build_finance.py/
build_travel.py. An entry is a file on disk; the build is a pure function of
source/ask/.

WHY THIS EXISTS, AND WHY IT'S NOT A SEVENTH CARD ON THE HUB
─────────────────────────────────────────────────────────
Dear Mr. Librarian used to live inside the Bible project's own template
(ask.html, built by build.py) — a static digest of answered questions with no
dates, no tags, no sources list, no "keep reading," styled and generated
exactly like a Bible reference page because it WAS one. Split out 2026-09-19
(Michael's call) to give it the structure the other five blogs have (own home,
dated entries, tags, sources, recirculation, its own feed) — while explicitly
staying OFF the mistertranslation.com hub's card grid and out of the other
five blogs' sibling footer cross-link line. It is reachable exactly one way:
the Bible project's own "📖 Dear Mr. Librarian" nav link. That is deliberate,
not an oversight — see ASK_BLOG_TODO.md for the reasoning.

WHAT THIS IS A COPY OF, AND WHAT IT DELIBERATELY ISN'T
──────────────────────────────────────────────────────
Structurally the writing half of build_health.py/build_finance.py: front
matter via blogkit, entry pages with a dateline/tags/sources/"Keep reading",
a tile-grid front page, per-tag pages, RSS, sitemap, the X comment layer, a
FormSubmit ask page. What it deliberately DOESN'T have, given this is 7 posts
today, not 70: the siblings' view-toggle/load-more pagination and live tag
FILTER bar (JS state management that earns its keep once an archive is long
enough to need trimming — not yet here; a plain tile grid plus a static
/tags.html is the honest amount of machinery for the size of this thing).
English only — there is no Spanish "Dear Mr. Librarian" and no plan for one.

STYLING: this is the one blog on the domain that links the Bible project's
own shared style.css rather than inlining its own copy, on purpose — it's
visually part of that project (same gold/parchment theme, same brand mark),
just structured like the others underneath. ask/style.css layers on the
handful of classes style.css doesn't have yet (entry dateline, tile grid,
tag chips, per-tag archive cards).

Sources: every entry's citations are INTERNAL — the specific Bible chapters/
verses/translator's-notes it leans on, not external reporting (unlike the
Ledger, this doesn't route through outside news). check_entries() below
enforces that every entry ends with a real <ol class="sources"> for exactly
that reason, generated automatically from the chapter links already IN the
entry body — never hand-typed, so it can't drift from what the post actually
cites, and never fabricated. A handful of these entries (the Newton post,
most obviously) would also support REAL external citations one day; that is
a follow-up content task, not something to invent here without verified
sources (see ASK_BLOG_TODO.md).
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

import blogkit

SITE_NAME = "Dear Mr. Librarian"
TAGLINE = "Reader questions about the Bible project, answered one at a time"
BLURB = ("Reader questions about the translation — a word-choice, the text, the canon, a "
         "comparison between versions — answered one at a time, the way everything in this "
         "project is done: sourced, compared, and left for you to weigh rather than settled "
         "from the desk.")

SITE_URL = "https://mistertranslation.com"
BASE_URL = "https://mistertranslation.com/ask/"
BASE = "/ask"
BIBLE_URL = "https://mistertranslation.com/bible.html"

GOATCOUNTER_CODE = "mistertranslation"
ADSENSE_CLIENT = "ca-pub-2001206283779660"

KNOWN_KEYS = {"title", "date", "tags", "summary", "meta_desc", "draft"}
REQUIRED_KEYS = {"title", "date", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70

TAG_INDEX_MIN = 2          # a tag page below this stays built but noindex'd
FRONT_HERO_IMG = "../img/great-isaiah-scroll.jpg"
FRONT_HERO_ALT = ("Two columns of the Great Isaiah Scroll from Qumran — dense hand-written "
                   "Hebrew on warm parchment, with an ancient crack running between the sheets")
FRONT_HERO_CREDIT = ('The Great Isaiah Scroll — Qumran, 2nd century BC. Photograph: Ardon Bar '
                      'Hama — via <a href="https://commons.wikimedia.org/wiki/File:Great_Isaiah_Scroll.jpg" '
                      'rel="noopener" target="_blank">Wikimedia Commons</a> · public domain (detail).')

FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "ask")
ENTRY_SRC = os.path.join(ROOT, "source", "ask")

CSS_VER = blogkit.asset_ver(ROOT, "style.css")

# Same inline favicon as the Bible project (build.py's FAVICON) -- not a file,
# so no ../img/ reference is needed or correct here.
FAVICON = ("data:image/svg+xml," + html.escape(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 46 46'>"
    "<circle cx='23' cy='23' r='22.5' fill='#0b1929'/>"
    "<rect x='9' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='33.4' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='12.6' y='14.5' width='20.8' height='17' fill='#efe6cf'/>"
    "<path d='M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z' fill='#e8c968'/></svg>", quote=True))


def esc(s):
    return html.escape(str(s), quote=True)


# ────────────────────────────────────────────────────────────────── entries ──

def load_entries(include_drafts=False):
    """Read source/ask/*.html into entry dicts, newest first."""
    if not os.path.isdir(ENTRY_SRC):
        return []
    entries = []
    for fn in sorted(os.listdir(ENTRY_SRC)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue
        with open(os.path.join(ENTRY_SRC, fn), encoding="utf-8") as fh:
            meta, body = blogkit.parse_front_matter(
                fh.read(), "source/ask/" + fn, KNOWN_KEYS, REQUIRED_KEYS)
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.html$", fn)
        if not m:
            raise ValueError("source/ask/%s: name must be YYYY-MM-DD-slug.html" % fn)
        date = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        slug = m.group(4)
        if meta["date"].strip() != date.isoformat():
            raise ValueError(
                "source/ask/%s: `date: %s` disagrees with the filename (%s)."
                % (fn, meta["date"], date.isoformat()))
        draft = meta.get("draft", "").strip().lower() in ("true", "yes", "1")
        if draft and not include_drafts:
            continue
        body = _add_sources(body)
        entries.append({
            "slug": slug,
            "file": slug + ".html",
            "date": date,
            "title": meta["title"],
            "summary": meta["summary"],
            "meta_desc": meta.get("meta_desc", "").strip(),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "draft": draft,
            "body": body,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


_CHAPTER_LINK_RE = re.compile(r'href="([a-z0-9]+(?:-[a-z0-9]+)*-\d+)\.html(?:#[^"]*)?"')


def _add_sources(body):
    """Append an auto-generated <ol class="sources"> naming every distinct Bible
    chapter this entry links to, in first-appearance order, plus the project's
    standing 7-version shelf note. Never hand-authored, so it can't drift from
    what the entry actually cites, and never invents an external citation the
    entry doesn't really have (see the module docstring)."""
    if 'class="sources"' in body:
        return body
    seen, chapters = set(), []
    for href in _CHAPTER_LINK_RE.findall(body):
        if href not in seen:
            seen.add(href)
            chapters.append(href)
    if not chapters:
        return body
    items = "\n".join(
        '  <li><a href="../%s.html">%s</a></li>'
        % (h, h.rsplit("-", 1)[0].replace("-", " ").title() + " " + h.rsplit("-", 1)[1])
        for h in chapters)
    items += ('\n  <li>Compared against the translation’s seven-version shelf — the NIV, '
              'the KJV, the Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the American '
              'Standard Version, and the New World Translation. See '
              '<a href="../about.html">how the translation is made</a>.</li>')
    return body.rstrip() + '\n\n<h2>Read in the text</h2>\n<ol class="sources">\n%s\n</ol>' % items


def _entry_desc(e):
    return blogkit.meta_desc(e["meta_desc"], e["summary"], META_DESC_MIN, META_DESC_MAX)


def _tag_file(tag):
    return "tag-%s.html" % blogkit.tag_slug(tag)


def _tag_chips(e):
    if not e["tags"]:
        return ""
    chips = "".join('<a class="tg" href="%s">%s</a>' % (_tag_file(t), esc(t)) for t in e["tags"])
    return '<div class="tags">%s</div>' % chips


def tag_index(entries):
    out = {}
    for e in entries:
        for t in e["tags"]:
            out.setdefault(t, []).append(e)
    return out


# ──────────────────────────────────────────────────────────────────── chrome ──

# Same scroll mark as the Bible project (visual continuity — this blog is
# structured like a sibling but themed as part of the translation project).
MARK_SVG = """<svg class="mtlib-icon" viewBox="0 0 46 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<circle cx="23" cy="23" r="22.5" fill="#0b1929"/>
<circle cx="23" cy="23" r="22.5" fill="none" stroke="#e8c968" stroke-width="0.7" opacity="0.4"/>
<g class="scr-sheet">
  <rect x="12.6" y="14.5" width="20.8" height="17" fill="#efe6cf"/>
  <g stroke="#8a7ab0" stroke-width="1.1" stroke-linecap="round">
    <line x1="15.5" y1="19" x2="30.5" y2="19"/>
    <line x1="15.5" y1="23" x2="30.5" y2="23"/>
    <line x1="15.5" y1="27" x2="26.5" y2="27"/>
  </g>
</g>
<rect class="scr-roll-l" x="9" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
<rect class="scr-roll-r" x="33.4" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
<path class="scr-quill" d="M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z" fill="#e8c968"/>
</svg>"""


def _chrome(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    return ('<header class="askhead">'
            '<a class="brand" href="index.html">%s<span class="wm">Dear Mr. <span class="em">Librarian</span></span></a>'
            '<nav class="nav">'
            '<a href="index.html"%s>Home</a>'
            '<a href="tags.html"%s>Tags</a>'
            '<a href="ask.html"%s>Ask a question</a>'
            '<a href="%s">← The Bible</a>'
            '</nav></header>'
            % (MARK_SVG, cls("home"), cls("tags"), cls("ask"), BIBLE_URL))


def _foot(hits_path=None):
    hits = blogkit.dim_attrs  # unused placeholder guard against accidental shadowing
    year = datetime.now(timezone.utc).year
    hitswidget = _hits_widget(hits_path, " views") if hits_path else ""
    hits_bit = " · %s" % hitswidget if hitswidget else ""
    return ('<footer class="askfoot">'
            '<p>Dear Mr. Librarian is part of <a href="%s">The MisterLibrarian Bible Project</a> — '
            'reader questions about the translation, answered one at a time.</p>'
            '<p><a href="tags.html">All tags</a> · <a href="ask.html">Ask a question</a> · '
            '<a href="feed.xml">RSS</a> · <a href="%s">Mr. Librarian’s Bible</a>%s</p>'
            '<p class="legal">© %d The MisterLibrarian Bible Project. '
            '<a href="%s">Privacy policy</a>.</p>'
            '</footer>' % (BIBLE_URL, BIBLE_URL, hits_bit, year,
                            "https://mistertranslation.com/privacy.html"))


def _front_hero():
    return ('<div class="fronthero"><figure><img src="%s" alt="%s" loading="eager"/>'
            '<figcaption>%s</figcaption></figure></div>'
            % (FRONT_HERO_IMG, esc(FRONT_HERO_ALT), FRONT_HERO_CREDIT))


def _comment_box(title, url):
    comment = blogkit.x_comment_url(title, url)
    search = blogkit.x_search_url(url)
    return ('<div class="notebtns">'
            '<a class="respond-btn respond-btn-primary" href="%s" target="_blank" rel="noopener">\U0001F4AC Comment on X</a>'
            '<a class="respond-btn respond-btn-secondary" href="%s" target="_blank" rel="noopener">\U0001F50D See what others said</a>'
            '</div>' % (comment, search))


def _related_entries(e, pool, limit=4):
    def tags_of(o):
        return {t.lower() for t in o.get("tags", ())}
    mine = tags_of(e)
    others = [o for o in pool if o["file"] != e["file"] and not o["draft"]]
    others.sort(key=lambda o: o["date"], reverse=True)
    others.sort(key=lambda o: len(mine & tags_of(o)), reverse=True)
    return others[:limit]


def _tile(e):
    data_tags = " ".join(blogkit.tag_slug(t) for t in e["tags"])
    return ('    <a class="tile" href="%s" data-search="%s" data-tags="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]),
                          esc((e["title"] + " " + e["summary"]).lower()), esc(data_tags),
                          blogkit.pretty_date(e["date"]).upper(), esc(e["title"]), esc(e["summary"])))


def _related_block(e, pool):
    picks = _related_entries(e, pool)
    if not picks:
        return ""
    tiles = "\n".join(_tile(o) for o in picks)
    return ('  <section class="readnext">\n    <h2>Keep reading</h2>\n'
            '    <div class="tilegrid">\n%s\n    </div>\n  </section>' % tiles)


def build_entry_page(e, pool=()):
    date_line = blogkit.pretty_date(e["date"]).upper()
    hits_path = "%s/%s" % (BASE, e["file"])
    desc = _entry_desc(e)
    url = BASE_URL + e["file"]
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
<meta name="twitter:card" content="summary"/>
<link rel="icon" href="%(favicon)s"/>
<link rel="stylesheet" href="../style.css?v=%(cssver)s"/>
<link rel="stylesheet" href="style.css?v=%(askver)s"/>%(goat)s
</head>
<body class="askblog">
<div class="wrap">
%(chrome)s
<article class="entry">
  <h1 class="etitle">%(title)s</h1>
  <p class="edate">%(date)s</p>
%(body)s
  %(tags)s
</article>
%(nudge)s
%(related)s
<p class="backlink"><a href="index.html">← Back to Dear Mr. Librarian</a></p>
%(foot)s
</div>
</body>
</html>
""" % {
        "title": esc(e["title"]), "site": esc(SITE_NAME), "desc": esc(desc), "url": url,
        "favicon": FAVICON,
        "cssver": CSS_VER, "askver": blogkit.asset_ver(ROOT, "ask/style.css"),
        "goat": _goatcounter(), "chrome": _chrome(""), "date": date_line,
        "body": e["body"], "tags": _tag_chips(e),
        "nudge": _comment_box(e["title"], url), "related": _related_block(e, pool),
        "foot": _foot(hits_path),
    }


def _entry_card(e):
    return ('    <a class="ecard" href="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]), blogkit.pretty_date(e["date"]).upper(),
                          esc(e["title"]), esc(e["summary"])))


def _goatcounter():
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>'
            f'\n<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>')


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
<meta property="og:type" content="%(ogtype)s"/>
<meta property="og:site_name" content="%(site)s"/>
<meta property="og:title" content="%(title)s"/>
<meta property="og:description" content="%(desc)s"/>
<meta property="og:url" content="%(url)s"/>
<meta name="twitter:card" content="summary"/>
<link rel="icon" href="%(favicon)s"/>
<link rel="stylesheet" href="../style.css?v=%(cssver)s"/>
<link rel="stylesheet" href="style.css?v=%(askver)s"/>%(goat)s
</head>
<body class="askblog">
<div class="wrap">
%(chrome)s
%(body)s
%(foot)s
</div>
</body>
</html>
""" % {
        "title": esc(title), "desc": esc(desc), "robots": robots, "url": url,
        "site": esc(SITE_NAME), "ogtype": og_type, "favicon": FAVICON,
        "cssver": CSS_VER,
        "askver": blogkit.asset_ver(ROOT, "ask/style.css"), "goat": _goatcounter(),
        "chrome": _chrome(active), "body": body, "foot": _foot(),
    }


def build_front(entries):
    tiles = "\n".join(_tile(e) for e in entries)
    counts = {}
    for e in entries:
        for t in e["tags"]:
            counts[t] = counts.get(t, 0) + 1
    chips = "".join(
        '<a class="chip" href="%s">%s <span class="chipn">%d</span></a>'
        % (_tag_file(t), esc(t), n) for t, n in sorted(counts.items(), key=lambda kv: kv[0].lower()))
    filters = ('<div class="filters">%s</div>' % chips) if chips else ""
    empty = "" if entries else '<p class="empty">The first question is being answered.</p>'
    return _shell(
        title="%s — %s" % (SITE_NAME, TAGLINE), desc=BLURB, url=BASE_URL, active="home",
        og_type="website",
        body="""%s<p class="tag ftag">%s</p>
<section class="writing">
%s%s
<div class="tilegrid">
%s
</div>
</section>
%s""" % (_front_hero(), esc(TAGLINE), filters, empty, tiles, _comment_box(SITE_NAME, BASE_URL)))


def build_tag_page(tag, entries, indexable):
    slug = blogkit.tag_slug(tag)
    n = len(entries)
    desc = "%d question%s tagged %s from %s." % (n, "" if n == 1 else "s", tag, SITE_NAME)
    cards = "\n".join(_entry_card(e) for e in entries)
    return _shell(
        title="%s — %s" % (tag, SITE_NAME), desc=desc,
        url="%stag-%s.html" % (BASE_URL, slug), noindex=not indexable,
        body="""<section class="writing">
<h1 class="wtitle">%s</h1>
<p class="wsub">%d question%s tagged <b>%s</b>. <a href="index.html">All questions</a>.</p>
%s
</section>""" % (esc(tag), n, "" if n == 1 else "s", esc(tag), cards))


def build_tag_list(tags):
    if not tags:
        return None
    rows = "\n".join(
        '<a class="eirow" href="%s"><span class="ei-name">%s</span>'
        '<span class="tgn">×%d</span></a>' % (_tag_file(t), esc(t), len(es))
        for t, es in sorted(tags.items(), key=lambda kv: kv[0].lower()))
    return _shell(
        title="All tags — %s" % SITE_NAME,
        desc="Every tag used across Dear Mr. Librarian.", url=BASE_URL + "tags.html",
        body="""<section class="writing">
<h1 class="wtitle">All tags</h1>
<p class="wsub">%d tag%s so far. <a href="index.html">All questions</a>.</p>
<div class="panel eilist">
%s
</div>
</section>""" % (len(tags), "" if len(tags) == 1 else "s", rows))


def build_ask_page():
    body = """<section class="writing">
<h1 class="wtitle">Ask Mr. Librarian a question</h1>
<p class="wsub">A question about the project, a translation choice you'd argue with, a chapter
request, or something you've always wondered about the text — send it in. Good questions
become Dear Mr. Librarian posts (anonymously unless you say otherwise), and reader questions
are exactly how this series grows.</p>
<div class="panel">
  <form action="%s" method="POST" class="askform">
    <input type="hidden" name="_subject" value="Ask Mr. Librarian — a question from the site"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="%sthanks.html"/>
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>
    <label>Your name <span class="opt">(optional)</span>
      <input type="text" name="name" placeholder="However you'd like to be credited — or leave blank"/>
    </label>
    <label>Your email <span class="opt">(optional — only needed if you'd like a reply)</span>
      <input type="email" name="email" placeholder="you@example.com"/>
    </label>
    <label>Your question <span class="req">(required)</span>
      <textarea name="question" required rows="7"
        placeholder="Ask anything — a verse, a word choice, a comparison between versions, what's coming next…"></textarea>
    </label>
    <button class="btn" type="submit">Send to the librarian's desk</button>
    <p class="formnote">Sending shows a quick captcha (keeps the robots out of the library), then
    brings you back here. Nothing is posted publicly — questions go straight to Mr. Librarian's desk.</p>
  </form>
</div>
</section>""" % (FORM_ENDPOINT, BASE_URL)
    return _shell(title="Ask a question — %s" % SITE_NAME,
                  desc="Send Mr. Librarian a question about the translation, a verse, or the "
                       "project — good questions become Dear Mr. Librarian posts.",
                  url=BASE_URL + "ask.html", active="ask", body=body)


def build_thanks():
    body = """<section class="writing">
<h1 class="wtitle">\U0001F4EC It's on the librarian's desk</h1>
<div class="panel prose">
<p><strong>Your question is in.</strong> Thank you — reader questions are the lifeblood of
Dear Mr. Librarian, and every one gets read. If yours becomes a post, it will appear anonymously
unless you asked otherwise; if you left an email, you may get a reply directly.</p>
<p>Meanwhile, <a href="index.html">read what's been answered so far</a>.</p>
</div>
</section>"""
    return _shell(title="Question received — %s" % SITE_NAME,
                  desc="Your question is on Mr. Librarian's desk.",
                  url=BASE_URL + "thanks.html", noindex=True, body=body)


def build_sitemap(entries, tags):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, today), (BASE_URL + "ask.html", today), (BASE_URL + "tags.html", today)]
    for e in entries:
        urls.append((BASE_URL + e["file"], e["date"].isoformat()))
    for tag, es in sorted(tags.items()):
        if len(es) >= TAG_INDEX_MIN:
            urls.append(("%stag-%s.html" % (BASE_URL, blogkit.tag_slug(tag)),
                         max(x["date"] for x in es).isoformat()))
    rows = "\n".join("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>" % u
                     for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + rows + "\n</urlset>\n")


def _prune_stale_tag_pages(tags):
    keep = {"tag-%s.html" % blogkit.tag_slug(t) for t in tags}
    for fn in os.listdir(OUT):
        if fn.startswith("tag-") and fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(OUT, fn))
            print("  (removed stale tag page: %s)" % fn)


def check_entries(entries):
    problems = []
    seen = {}
    for e in entries:
        d = _entry_desc(e)
        if len(d) > META_DESC_MAX:
            problems.append("%s: description is %d chars (max %d)" % (e["slug"], len(d), META_DESC_MAX))
        if not e["tags"]:
            problems.append("%s: no tags" % e["slug"])
        if d in seen:
            problems.append("%s: identical search description to %s" % (e["slug"], seen[d]))
        seen[d] = e["slug"]
        if 'class="sources"' not in e["body"]:
            problems.append("%s: no <ol class=\"sources\"> — every entry cites what it "
                            "references (see _add_sources)" % e["slug"])
    if problems:
        sys.exit("build refused:\n  " + "\n  ".join(problems))


def main():
    include_drafts = "--drafts" in sys.argv
    entries = load_entries(include_drafts=include_drafts)
    live = [e for e in entries if not e["draft"]]
    check_entries(entries)
    tags = tag_index(live)

    os.makedirs(OUT, exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(live))
    write("ask.html", build_ask_page())
    write("thanks.html", build_thanks())
    for e in entries:
        write(e["file"], build_entry_page(e, live))
    for tag, es in tags.items():
        write("tag-%s.html" % blogkit.tag_slug(tag), build_tag_page(tag, es, len(es) >= TAG_INDEX_MIN))
    tl = build_tag_list(tags)
    if tl:
        write("tags.html", tl)
    write("feed.xml", blogkit.build_feed(live, site_name=SITE_NAME, site_url=SITE_URL,
                                         base="/ask", blurb=BLURB))
    write("sitemap.xml", build_sitemap(live, tags))
    _prune_stale_tag_pages(tags)

    indexable = sum(1 for v in tags.values() if len(v) >= TAG_INDEX_MIN)
    print("built /ask/ — %d entries (%d live), %d tag pages (%d indexable, %d held back at <%d entries)"
          % (len(entries), len(live), len(tags), indexable, len(tags) - indexable, TAG_INDEX_MIN))
    for e in entries:
        print("  %s  %-30s %s" % (e["date"], e["file"], "[DRAFT] " if e["draft"] else ""))
    return 0


if __name__ == "__main__":
    _rc = main()
    try:
        import build_hub; build_hub.refresh()
    except Exception as _e:
        print("build_hub: %s" % _e)
    sys.exit(_rc)

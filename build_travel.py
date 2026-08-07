#!/usr/bin/env python3
"""Build "The Librarian Abroad" — Mr. Librarian's travel & food blog.

This is a SEPARATE, SELF-CONTAINED site that happens to share a domain with the
Bible project. It publishes to /travel/ on mistertranslation.com and is
DELIBERATELY NOT LINKED to or from the Bible site: no nav entry, no footer link,
no card on the home page, and nothing in here points back. The two projects share
a domain and nothing else — separate builder, separate stylesheet, separate
header/footer, separate wordmark.

    python3 build_travel.py            # build published posts
    python3 build_travel.py --drafts   # include posts marked `draft: true`
    git add travel source/travel && git commit && git push

Adding a post = drop one file in source/travel/ named YYYY-MM-DD-some-slug.html,
give it front matter, rebuild. The index, tag filters, prev/next chain, RSS feed
and sitemap all update from that one file.

Front matter is a block of `key: value` lines, ended by a line of `---`:

    title: A Long Lunch in Lisbon
    date: 2026-07-20
    place: Lisbon, Portugal
    tags: food, portugal, seafood
    hero: lisbon-lunch.jpg
    hero_alt: A tiled table with grilled sardines and a glass of vinho verde
    summary: One plate of sardines, and the two hours it took to eat them.
    draft: false
    ---
    <p>Body HTML goes here…</p>

⚠ WHY THIS DOESN'T TOUCH build.py: the Bible builder writes only to the repo root
and never globs or deletes outside its own outputs, so /travel/ is safe alongside
it. Keep it that way — do not import from build.py or library_data.py, and do not
add a link between the two sites.
"""
import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import os
import re
import urllib.parse
import xml.sax.saxutils as sax

import blogkit

# ---------------------------------------------------------------- identity ---

# Rename the blog by editing these three lines and rebuilding. Nothing else
# hardcodes the name.
SITE_NAME = "The Librarian Abroad"
TAGLINE = "Travels, meals, and musings by Mr. Librarian"
BLURB = ("Notes from the road and from the table — what was worth the trip, "
         "what was worth the plate, and what wasn't.")

SITE_URL = "https://mistertranslation.com"
BASE = "/travel"                     # published under this path
OG_IMAGE = f"{SITE_URL}{BASE}/img/og-default.png"

# Cookie-less, no-consent-banner analytics, same account as the Bible site so
# there's one dashboard. This is invisible to readers and creates NO public link
# between the two sites. Set to None to disable entirely.
GOATCOUNTER_CODE = "mistertranslation"

# FormSubmit alias for the "write to the librarian" form — the SAME activated
# endpoint the Bible site uses, so there was nothing to set up and it worked from
# the first deploy. Both sites land in one inbox; the _subject line below is what
# tells them apart. A shared INBOX is not a shared page: this creates no public
# link between the two sites.
#
# Chosen over a comment system deliberately (2026-07-25). A static site has no
# backend, so real comments would mean Disqus (ads + tracking, which would break
# the About page's promise), Giscus (readers need a GitHub account — wrong
# audience for a food blog), or something self-hosted (a server to maintain).
# All of them also bring an unending spam-moderation chore to a notebook that is
# written irregularly by design. A form has the reach and none of the upkeep.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

# Repo behind the "Publish this entry" button on a draft preview (_publish_box).
# Only used to build that one link; nothing else here knows about GitHub.
PUBLISH_REPO = "michaelkrewson/misterlibrarian"

# -------------------------------------------------------- meta description ---

# `summary:` is written for the index card and the RSS feed, where a couple of
# full sentences read well. A search result is not that: Google shows about 155
# characters and cuts the rest mid-word. Measured at 13 entries, TWELVE were
# over — so on almost every page the half that would earn the click was the half
# being thrown away. Same class of bug the Bible side hit in July, arriving from
# the other direction: there the boilerplate was too long, here the good part is
# simply too far back.
#
# So the description is derived, not reused: take whole sentences from the
# summary while they fit. A complete thought that stops early beats a longer one
# the search engine amputates. An entry can override with `meta_desc:` when the
# derived version isn't the angle worth leading on.
META_DESC_MAX = 155
META_DESC_MIN = 70


def _meta_desc(p):
    return blogkit.meta_desc(p.get("meta_desc"), p["summary"],
                             META_DESC_MIN, META_DESC_MAX)


# ------------------------------------------------------------- tag filters ---

# The entry template asks for a tag per DISH, by name — "brussels sprouts",
# "cacio e pepe" — which is deliberate and worth keeping: it is what lets a
# reader who wants every sprout on the site click one pill and get them. The
# side effect is a very long tail. Measured at 13 entries: 46 unique tags, 32 of
# them used exactly once, growing ~3.5 tags per entry. Rendered flat that is a
# few hundred chips above the first card.
#
# So the bar shows only tags that RECUR, and folds the rest away behind a
# "+N more" toggle. Nothing is lost: the long tail is still one click away, it
# is still linked from the foot of every entry, and the header search already
# composes with it. The tail is for ARRIVING at (a search, a pill on a post),
# not for browsing — nobody scans an index for "hollandaise".
TAG_BAR_MIN_COUNT = 2    # a tag earns a visible slot by appearing more than once
TAG_BAR_MAX_CHIPS = 18   # ...and the bar stays bounded however big the blog gets

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "source", "travel")
OUT_DIR = os.path.join(ROOT, "travel")

# Fields a post may declare. Anything else in the front matter is an error —
# better a loud typo than a silently-ignored `sumary:` line.
KNOWN_KEYS = {
    "title", "date", "place", "tags", "hero", "hero_alt", "hero_credit",
    "summary", "draft", "stars", "subject", "subject_type", "meta_desc",
}
REQUIRED_KEYS = {"title", "date", "summary"}

# ------------------------------------------------------------ the star scale ---
#
# "Librarian's Stars" — 1 to 5, half-steps allowed, and OPTIONAL: a notes entry
# isn't a review and gets none.
#
# ⚠ THE WHOLE POINT IS THAT IT DISCRIMINATES. A scale where everything the writer
# enjoyed gets 5 carries no information — that is how restaurant ratings on the
# big sites ended up averaging 4.6 and meaning nothing. So each level is given a
# published meaning (rendered on the About page), THREE is defined as a good meal
# rather than a mediocre one, and the labels below are the contract with the
# reader. Five has to stay rare or it stops being worth printing.
RATING_LABELS = {
    5.0: "Worth crossing a city for",
    4.5: "Very nearly the top of the shelf",
    4.0: "I'll be going back on purpose",
    3.5: "Better than good",
    3.0: "Glad I went",
    2.5: "Some of it worked",
    2.0: "Fine. Something was off, or it wasn't for me",
    1.5: "Disappointing",
    1.0: "Wouldn't return",
    0.5: "Avoid",
}

# -------------------------------------------------------------- bookmarked ---
#
# A running list of places spotted but not yet eaten at — a page in the book
# turned down to come back to, not a place put off. Not a post (there is no
# meal to review yet, so no stars), just a running shelf. When a place here
# actually gets eaten at, write its real entry in source/travel/ and delete its
# dict below — the two are meant to be mutually exclusive, not duplicated.
#
# Each entry: name, place, why (one or two sentences — what tipped us off),
# link (the place's own site, optional), added (the date it went on the list),
# and an optional photos list of {img, alt} dicts (img is a filename already
# processed into travel/img/ — same convention as a post's figures).
BOOKMARKED = [
    {
        "name": "Chuckie Pies",
        "place": "370 First Street, Lake Oswego, Oregon",
        "why": ("Neapolitan-style pies, walked past midday on a Sunday food crawl — "
                 "it doesn't open until 4pm, so that was that. The window had two "
                 "things taped to it worth remembering: The Oregonian's 2026 Reader's "
                 "Choice, voted a top-3 pizza spot in Portland, and a local ribbon for "
                 "Best Pizza from the Lake Oswego Review. Going back on purpose, at "
                 "the right hour this time."),
        "link": "https://chuckiepies.com",
        "added": dt.date(2026, 7, 26),
        "photos": [
            {"img": "chuckie-pies-sign.jpg",
             "alt": "The Chuckie Pies hanging sign, a gold C-and-fork mark beside the name in gold letters on a black background"},
            {"img": "chuckie-pies-interior.jpg",
             "alt": "The dark wood, herringbone-floor dining room at Chuckie Pies, empty tables set for dinner, a please-wait-to-be-seated sign on the host stand"},
            {"img": "chuckie-pies-awards.jpg",
             "alt": "A yellow poster on the door reading Chuckie Pies, Voted Best Pizza, beside two award ribbons"},
        ],
    },
]


def _maps_link(address):
    """One URL that works as 'get directions' everywhere: opens the native Maps
    app on iOS or Android if one's installed, else Google Maps in a browser.
    No per-platform detection needed — this is Google's own universal format.
    """
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(address)}"


def _directions_link(address):
    return (f'<a class="directions" href="{_maps_link(address)}" rel="noopener" '
            f'target="_blank">📍 Get directions</a>')


def _asset_ver(rel):
    """Short content hash of a static asset, appended to its URL so a CSS edit is
    never masked by a stale browser cache. (Same trick the Bible builder uses.)"""
    return blogkit.asset_ver(OUT_DIR, rel)


# ------------------------------------------------------------------- chrome ---

# A plate that is also a compass — the blog's mark. Deliberately nothing like the
# Bible project's scroll: different shape, no shared glyph.
#
# The needle ANIMATES: it swings past north and settles, the way a real compass
# does when you stop walking, then rests for most of the cycle. Deliberately not
# a continuous spin — a needle that never settles reads as a loading spinner.
# The CSS honours prefers-reduced-motion and drops it entirely.
COMPASS_SVG = """<svg class="mark" viewBox="0 0 48 48" width="62" height="62" aria-hidden="true">
  <circle cx="24" cy="24" r="21" fill="#0d1520" stroke="var(--terra)" stroke-width="2"/>
  <circle cx="24" cy="24" r="15.5" fill="none" stroke="rgba(232,201,104,.35)" stroke-width="1.2"/>
  <g class="needle">
    <path d="M24 9.5 L27.4 20.6 L38.5 24 L27.4 27.4 L24 38.5 L20.6 27.4 L9.5 24 L20.6 20.6 Z"
          fill="var(--terra)"/>
  </g>
  <circle cx="24" cy="24" r="3.4" fill="var(--olive)"/>
  <circle cx="24" cy="24" r="1.3" fill="#0d1520"/>
</svg>"""


def header(active=""):
    """Site header. NOTE: every link here is relative and stays inside /travel/ —
    there is intentionally no route from this blog to the Bible project.

    The search box lives here, not just on the index page, so it's reachable
    from anywhere on the site — a post page, About, wherever. It's a REAL form
    (action="index.html", GET, name="q") on purpose: submitting it works even
    with JS off, or from a page that has no cards to filter client-side, by
    just navigating to the index with ?q=… in the URL. index.html's own script
    then does two extra things JS-only: filters live as you type instead of
    waiting for Enter, and reads a ?q= it was handed on arrival and applies it
    immediately, so a search that starts on a post page lands already-filtered.
    """
    def cls(k):
        return ' class="on"' if k == active else ""
    return f"""<header class="site-head">
  {'<h1 class="brandwrap">' if active == "home" else '<div class="brandwrap">'}
  <a class="brand" href="index.html">
    {COMPASS_SVG}
    <span class="brand-name">The Librarian <span class="abroad">Abroad</span></span>
  </a>
  {'</h1>' if active == "home" else '</div>'}
  <form class="headersearch" action="index.html" method="get" role="search">
    <input type="search" name="q" id="headerSearch" placeholder="Search entries…" aria-label="Search past entries"/>
  </form>
  <div class="rule"></div>
  <div class="tag">{TAGLINE}</div>
  <details class="mobmenu">
    <summary>\U00002630 Menu</summary>
    <div class="mobmenu-panel">
      <a href="index.html"{cls('home')}>Latest</a>
      <a href="index.html#archive">Archive</a>
      <a href="bookmarked.html"{cls('bookmarked')}>📑 Bookmarked</a>
      <a href="write.html"{cls('write')}>✉️ Write</a>
      <a href="about.html"{cls('about')}>About</a>
      <a href="feed.xml">RSS</a>
      <a class="sib" href="https://mistertranslation.com/finance/" title="What the world's money is actually in">The Librarian's Ledger →</a>
      <div class="mobmenu-sep"></div>
      <span class="share-widget"></span>
    </div>
  </details>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Latest</a>
    <a href="index.html#archive">Archive</a>
    <a href="bookmarked.html"{cls('bookmarked')}>📑 Bookmarked</a>
    <a href="write.html"{cls('write')}>✉️ Write</a>
    <a href="about.html"{cls('about')}>About</a>
    <a href="feed.xml" title="Subscribe by RSS">RSS</a>
    <a class="sib" href="https://mistertranslation.com/finance/" title="What the world's money is actually in">The Librarian's Ledger →</a>
    <span class="share-widget"></span>
  </nav>
</header>"""


FOOTER = f"""<footer class="site-foot">
  <p>{SITE_NAME} — {BLURB}</p>
  <p><a href="index.html">Latest</a> · <a href="bookmarked.html">Bookmarked</a> ·
  <a href="write.html">Write to the librarian</a> ·
  <a href="about.html">About</a> · <a href="feed.xml">RSS</a></p>
  <p class="sibfoot"><a href="https://mistertranslation.com/finance/">The Librarian's Ledger</a>
  — the other one, about money.</p>
</footer>"""


def _goatcounter():
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


def _og(title, desc, url="", image=""):
    img = image or OG_IMAGE
    t = html.escape(title, quote=True)
    d = html.escape(desc or BLURB, quote=True)
    tags = [
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}"/>',
        f'<meta property="og:type" content="{"article" if url else "website"}"/>',
        f'<meta property="og:title" content="{t}"/>',
        f'<meta property="og:description" content="{d}"/>',
        f'<meta property="og:image" content="{img}"/>',
        '<meta name="twitter:card" content="summary_large_image"/>',
        f'<meta name="twitter:title" content="{t}"/>',
        f'<meta name="twitter:description" content="{d}"/>',
        f'<meta name="twitter:image" content="{img}"/>',
    ]
    if url:
        # A directory index answers at BOTH /travel/ and /travel/index.html.
        # build_sitemap() submits the directory form — it is the one a person
        # would share — so the canonical has to agree with it. When it did not,
        # the sitemap said "index this" while the page replied "no, the real
        # one is index.html", and Google resolves that by dropping the
        # submitted URL as "alternate page with proper canonical tag". On the
        # blog's single most important URL. Found 2026-08-01, days after the
        # sitemap was submitted.
        path = "" if url == "index.html" else url
        full = f"{SITE_URL}{BASE}/{path}"
        tags.insert(0, f'<link rel="canonical" href="{full}"/>')
        tags.append(f'<meta property="og:url" content="{full}"/>')
    return "\n" + "\n".join(tags)


def page(title, body, active="", desc="", url="", image="", noindex=False):
    css_v = _asset_ver("style.css")
    share_v = _asset_ver("share.js")
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    # noindex is for pages that exist only as a destination (the post-submit
    # thank-you); they're not content and shouldn't turn up in a search result.
    r = '\n<meta name="robots" content="noindex,follow"/>' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}{r}{_og(title, desc, url, image)}
<link rel="icon" href="img/favicon.svg"/>
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_NAME, quote=True)}" href="feed.xml"/>
<link rel="stylesheet" href="style.css?v={css_v}"/>{_goatcounter()}
</head>
<body>
<div class="wrap">
{header(active)}
<script src="share.js?v={share_v}" defer></script>
{body}
{FOOTER}
</div>
</body>
</html>
"""


# -------------------------------------------------------------- post loading ---

FNAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)\.html$")

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# A ceiling, not a real limit — a normal entry (even a long one, ~9-12K chars
# of plain text) is indexed in full, because a search box that quietly can't
# find a word that's genuinely on the page is worse than a slightly heavier
# index.html. This only exists to stop one pathological post (a full menu
# transcript, a pasted transcript) from blowing the card's markup out
# indefinitely. See build_index()'s `search` var for the real scaling note.
SEARCH_BODY_CHARS = 20_000


def _plain_text(body_html):
    return blogkit.plain_text(body_html)


def parse_front_matter(text, where):
    """Split `key: value` front matter from the HTML body.

    Fails LOUDLY on an unknown or missing key — a post that silently loses its
    summary or date would quietly ship a broken card and a broken feed entry.
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
        if k not in KNOWN_KEYS:
            raise ValueError(
                f"{where}:{i}: unknown front-matter key {k!r}. "
                f"Known keys: {', '.join(sorted(KNOWN_KEYS))}")
        meta[k] = v.strip()
    missing = REQUIRED_KEYS - set(meta)
    if missing:
        raise ValueError(f"{where}: missing required front matter: {', '.join(sorted(missing))}")
    return meta, body.lstrip("\n")


def load_posts(include_drafts=False):
    """Read source/travel/*.html into post dicts, newest first."""
    if not os.path.isdir(SRC_DIR):
        return []
    posts = []
    for fn in sorted(os.listdir(SRC_DIR)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue          # `_template.html` and friends are never published
        m = FNAME_RE.match(fn)
        if not m:
            raise ValueError(
                f"source/travel/{fn}: filename must be YYYY-MM-DD-slug.html "
                f"(lowercase slug, digits and dashes only)")
        file_date, slug = m.group(1), m.group(2)
        path = os.path.join(SRC_DIR, fn)
        with open(path, encoding="utf-8") as f:
            meta, body = parse_front_matter(f.read(), f"source/travel/{fn}")

        is_draft = meta.get("draft", "").lower() in ("1", "true", "yes")
        if is_draft and not include_drafts:
            continue

        # The filename date is the sort key and must agree with the front matter —
        # two dates that disagree is exactly how a post ends up filed in the wrong
        # year with a correct-looking byline.
        if meta["date"] != file_date:
            raise ValueError(
                f"source/travel/{fn}: front-matter date {meta['date']!r} does not match "
                f"the filename date {file_date!r}")
        try:
            date = dt.date.fromisoformat(file_date)
        except ValueError:
            raise ValueError(f"source/travel/{fn}: date must be YYYY-MM-DD")

        # Stars are optional, but a malformed one is an error rather than a
        # silently-dropped rating — a review that quietly loses its score is worse
        # than a build that stops.
        stars = None
        if meta.get("stars", "").strip():
            try:
                stars = float(meta["stars"])
            except ValueError:
                raise ValueError(f"source/travel/{fn}: stars must be a number, got {meta['stars']!r}")
            if stars not in RATING_LABELS:
                raise ValueError(
                    f"source/travel/{fn}: stars must be one of "
                    f"{', '.join(str(k) for k in sorted(RATING_LABELS))} — got {stars}")

        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        posts.append({
            "stars": stars,
            "subject": meta.get("subject", "").strip(),
            "subject_type": meta.get("subject_type", "Restaurant").strip() or "Restaurant",
            "slug": slug,
            "file": f"{slug}.html",
            "date": date,
            "title": meta["title"],
            "place": meta.get("place", ""),
            "tags": tags,
            "hero": meta.get("hero", ""),
            "hero_alt": meta.get("hero_alt", ""),
            "hero_credit": meta.get("hero_credit", ""),
            "summary": meta["summary"],
            "meta_desc": meta.get("meta_desc", ""),
            "draft": is_draft,
            "body": body,
            # Lowercased haystack for the on-page search box — title/place/tags/
            # summary in full (short, and exactly the fields a reader searches
            # by), body text capped at SEARCH_BODY_CHARS so a long post can't
            # blow up every card's markup. See build_search_data() for why this
            # rides in the page rather than a separate fetched index.
            "search": _WS_RE.sub(" ", " ".join([
                meta["title"], meta.get("place", ""), meta.get("tags", ""),
                meta["summary"], _plain_text(body)[:SEARCH_BODY_CHARS],
            ])).strip().lower(),
        })

    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    if len({p["slug"] for p in posts}) != len(posts):
        raise ValueError("two posts share a slug — slugs must be unique across all dates")
    return posts


# ------------------------------------------------------------------ rendering ---

def _pretty_date(d):
    return blogkit.pretty_date(d)


def _stars_svg(value, size=22):
    """Five stars, gold for earned and outlined for not, with a real half state.

    Inline SVG rather than the ★/☆ characters: those render at wildly different
    weights across platforms and cannot do halves at all. A gradient with a hard
    stop at 50% gives an exact half star everywhere.
    """
    pts = ("M12 2.6l2.95 5.98 6.6.96-4.78 4.66 1.13 6.57L12 17.66 "
           "6.1 20.77l1.13-6.57L2.45 9.54l6.6-.96z")
    out = [f'<span class="stars" role="img" aria-label="{value} out of 5 stars">']
    for i in range(1, 6):
        if value >= i:
            fill = "var(--gold)"
        elif value >= i - 0.5:
            fill = f"url(#half{size})"
        else:
            fill = "none"
        out.append(
            f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true">'
            f'<path d="{pts}" fill="{fill}" stroke="var(--gold)" stroke-width="1.4"'
            f' stroke-linejoin="round"/></svg>')
    out.append("</span>")
    return "".join(out)


def _half_defs(size=22):
    """One shared gradient definition per page — referenced by any half star."""
    return (f'<svg width="0" height="0" aria-hidden="true" focusable="false"><defs>'
            f'<linearGradient id="half{size}"><stop offset="50%" stop-color="var(--gold)"/>'
            f'<stop offset="50%" stop-color="transparent"/></linearGradient></defs></svg>')


def _rating_block(p, size=22):
    """The rating as it appears at the top of a post."""
    if p["stars"] is None:
        return ""
    label = RATING_LABELS[p["stars"]]
    n = int(p["stars"]) if p["stars"] == int(p["stars"]) else p["stars"]
    return (f'<div class="rating">{_stars_svg(p["stars"], size)}'
            f'<span class="ratingnum">{n}<span class="of">/5</span></span>'
            f'<span class="ratinglabel">{html.escape(label)}</span>'
            f'<a class="ratinghelp" href="about.html#stars" '
            f'title="What the stars mean">?</a></div>')


def _rating_key():
    """The published meaning of each level, rendered for the About page."""
    return "\n    ".join(
        f'<tr><td>{_stars_svg(v, 18)}</td>'
        f'<td class="rk-num"><strong>{int(v) if v == int(v) else v}</strong></td>'
        f'<td>{html.escape(RATING_LABELS[v])}</td></tr>'
        for v in (5.0, 4.0, 3.0, 2.0, 1.0))


def _tag_slug(t):
    return blogkit.tag_slug(t)


def _img_dims(filename):
    return blogkit.img_dims(os.path.join(OUT_DIR, "img"), filename)


def _dim_attrs(filename):
    return blogkit.dim_attrs(os.path.join(OUT_DIR, "img"), filename)


def _hero_img(p, cls="hero", eager=False):
    """`eager` marks the one image that is the page's LCP element.

    A lazy-loaded LCP image is a well-known own goal: the browser defers the
    very thing the score is measured against. The entry page's hero and the
    index's first card are the only two that qualify — everything further down
    stays lazy, which is what makes lazy loading worth having at all."""
    if not p["hero"]:
        return ""
    alt = html.escape(p["hero_alt"] or p["title"], quote=True)
    credit = (f'<figcaption class="credit">{html.escape(p["hero_credit"])}</figcaption>'
              if p["hero_credit"] else "")
    load = ('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
    return (f'<figure class="{cls}">'
            f'<img src="img/{html.escape(p["hero"], quote=True)}" alt="{alt}"'
            f'{_dim_attrs(p["hero"])} {load}/>'
            f'{credit}</figure>')


_IMG_TAG_RE = re.compile(r'<img\s([^>]*?)src="img/([^"]+)"([^>]*?)>', re.I)


def _add_img_dims(body):
    """Inject width/height into the hand-written <figure> images in an entry.

    The body is the author's own HTML, so this is the only place the dimensions
    can be added without asking them to hand-count pixels for every photo. Skips
    any tag that already declares a width, so an explicit choice always wins."""
    def sub(m):
        before, src, after = m.group(1), m.group(2), m.group(3)
        if "width=" in (before + after).lower():
            return m.group(0)
        return f'<img {before}src="img/{src}"{after}{_dim_attrs(src)}>'
    return _IMG_TAG_RE.sub(sub, body)


def _hits_id(path):
    return "hits-" + re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def _hits_widget(path, suffix=""):
    """A small, inline view-count chip — GoatCounter's public PER-PATH counter
    (same account as the Bible site, so this rides the one already-configured
    dashboard), fetched client-side. `path` is the page's own path from the
    domain root, e.g. "/travel/foo.html" — NOT the bare filename, since
    GoatCounter records whatever `location.pathname` actually was for a visit,
    and every internal link here is relative (so index.html always resolves to
    the full /travel/index.html path, never the bare "/travel/").

    Same resilience contract as the Bible site's site-wide stats box
    (build.py's _stats_box): don't gate on response.ok — GoatCounter 404s a
    thin/zero-data path even though the JSON body is still valid — and fail
    SILENT (hide the chip) on any error rather than leave a stuck "—" behind.
    A brand-new page with zero hits yet is exactly this case, so it should
    just not show a count until there's a real one to show.
    """
    if not GOATCOUNTER_CODE:
        return ""
    hid = _hits_id(path)
    encoded = urllib.parse.quote(path, safe="")
    return f"""<span class="hits" id="{hid}">👁 <span id="{hid}-n">—</span>{html.escape(suffix)}</span>
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


def _meta_line(p, show_hits=False):
    bits = [f'<time datetime="{p["date"].isoformat()}">{_pretty_date(p["date"])}</time>']
    if p["place"]:
        bits.append(f'<span class="place">📍 {html.escape(p["place"])}</span>')
    if p["draft"]:
        bits.append('<span class="draftflag">DRAFT — not published</span>')
    # Hits are skipped on a draft: it's an unlisted preview, not a real page
    # visitors land on, so a view count there would be nearly meaningless noise.
    if show_hits and not p["draft"]:
        bits.append(_hits_widget(f"{BASE}/{p['file']}", " views"))
    return '<div class="postmeta">' + " · ".join(bits) + "</div>"


def _tag_pills(p):
    if not p["tags"]:
        return ""
    return ('<div class="tags">'
            + "".join(
                f'<a class="pill" href="index.html?tag={_tag_slug(t)}">'
                f'{html.escape(t)}</a>'
                for t in p["tags"])
            + "</div>")


def post_card(p, eager=False):
    data_tags = " ".join(_tag_slug(t) for t in p["tags"])
    stars = (f'<div class="cardrating">{_stars_svg(p["stars"], 17)}</div>'
             if p["stars"] is not None else "")
    return f"""<article class="card" data-tags="{html.escape(data_tags, quote=True)}" data-stars="{p['stars'] if p['stars'] is not None else -1}" data-search="{html.escape(p['search'], quote=True)}">
  <a class="cardlink" href="{p['file']}">
    {_hero_img(p, 'thumb', eager=eager)}
    <div class="cardbody">
      {_meta_line(p)}
      {stars}
      <h2>{html.escape(p['title'])}</h2>
      <p class="summary">{html.escape(p['summary'])}</p>
      {_tag_pills(p)}
    </div>
  </a>
</article>"""


def build_index(posts):
    if not posts:
        cards = ('<p class="empty">Nothing published yet. Add a file to '
                 '<code>source/travel/</code> and rebuild.</p>')
        chips = ""
        search = ""
        archive = ""
    else:
        # Only the first card is eager: it is the index's LCP element. The rest
        # stay lazy, which is the whole point of having lazy loading.
        cards = "\n".join(post_card(p, eager=(i == 0)) for i, p in enumerate(posts))
        counts = collections.Counter(t for p in posts for t in p["tags"])
        all_tags = sorted(counts, key=str.lower)
        chips = ""
        if all_tags:
            # Which tags earn a visible slot. Threshold first (a tag proves it is
            # a theme by recurring), then a hard cap by frequency so the bar can
            # never grow without bound — at a few hundred entries "used twice"
            # would itself be a wall. Both lists render alphabetically: a chip
            # should be where you last saw it, not move around as counts shift.
            shown = [t for t in all_tags if counts[t] >= TAG_BAR_MIN_COUNT]
            if len(shown) > TAG_BAR_MAX_CHIPS:
                keep = set(sorted(shown, key=lambda t: (-counts[t], t.lower()))
                           [:TAG_BAR_MAX_CHIPS])
                shown = [t for t in all_tags if t in keep]
            shown_set = set(shown)
            rare = [t for t in all_tags if t not in shown_set]

            def _chip(t, is_rare=False):
                n = counts[t]
                # A weight cue rather than a tag cloud: the frequent tags read a
                # little stronger so the bar still says what the blog is mostly
                # about, but every chip keeps a full-size tap target and the same
                # contrast. Nothing is de-emphasised below the base style.
                cls = "chip"
                if is_rare:
                    cls += " rare"
                elif n >= 5:
                    cls += " w3"
                elif n >= 3:
                    cls += " w2"
                return (f'<button class="{cls}" data-tag="{_tag_slug(t)}" '
                        f'title="{n} {"entry" if n == 1 else "entries"}">'
                        f'{html.escape(t)}</button>')

            more = ""
            if rare:
                more = (f'<button class="chip more" id="tagMore" type="button" '
                        f'aria-expanded="false" aria-controls="filters" '
                        f'data-count="{len(rare)}">+ {len(rare)} more</button>')
            chips = ('<div class="filters" id="filters">'
                     '<button class="chip on" data-tag="">All</button>'
                     + "".join(_chip(t) for t in shown)
                     + more
                     + "".join(_chip(t, is_rare=True) for t in rare)
                     + "</div>")
        # The INPUT itself lives in the header now (see header() — reachable from
        # every page). This is just where the live result count shows up once a
        # search is active. Client-side only — no separate index file to fetch,
        # keep in sync, or go stale between builds. Each card already carries its
        # own searchable text in data-search (see post_card()), so this scales the
        # same way the tag filter already does: more cards on one page, not more
        # infrastructure. If the archive ever gets big enough that shipping every
        # card's text is itself a problem, that's the point to switch to a
        # fetched JSON index — not before.
        search = '<div class="searchcount" id="searchCount"></div>'
        rows = "\n".join(
            f'<li><time datetime="{p["date"].isoformat()}">{p["date"].isoformat()}</time>'
            f'<a href="{p["file"]}">{html.escape(p["title"])}</a>'
            + (f'<span class="place">{html.escape(p["place"])}</span>' if p["place"] else "")
            + (f'<span class="archstars">{_stars_svg(p["stars"], 14)}</span>'
               if p["stars"] is not None else "")
            + "</li>"
            for p in posts)
        archive = f"""<section class="panel" id="archive">
  <h2>Archive</h2>
  <ul class="archive">
{rows}
  </ul>
</section>"""

    rated = [p for p in posts if p["stars"] is not None]
    sortbar = ("" if len(rated) < 2 else
               '<div class="sortbar" id="sortbar">Sort: '
               '<button class="sortbtn on" data-sort="date">Newest</button>'
               '<button class="sortbtn" data-sort="stars">Highest rated</button></div>')

    index_hits = _hits_widget(f"{BASE}/index.html", " visits to this page")
    index_hits_html = f'\n  <p class="pagehits">{index_hits}</p>' if index_hits else ""
    body = f"""<section class="lede lede-home">
  <p>{html.escape(BLURB)}</p>{index_hits_html}
</section>
{_half_defs(17)}{_half_defs(14)}
{search}
{chips}
{sortbar}
<div class="cards" id="cards">
{cards}
</div>
<p class="empty" id="searchEmpty" hidden>No entries match that search.</p>
{archive}
<script>
// Search box (in the header, reachable from every page — see header() in
// build_travel.py) + tag filter, combined. Both narrow the SAME card list, so
// a query and a tag chip compose (AND, not OR): typing "ramen" while the
// "oregon" chip is on shows only cards matching both. Pure client-side — no
// per-tag or per-query pages to generate, keep in sync, or leave behind.
(function(){{
  var cards = Array.prototype.slice.call(document.querySelectorAll('#cards .card'));
  var filterBar = document.getElementById('filters');
  var input = document.getElementById('headerSearch');
  var count = document.getElementById('searchCount');
  var empty = document.getElementById('searchEmpty');
  var activeTag = '';
  var query = '';

  function apply(){{
    var shown = 0;
    cards.forEach(function(card){{
      var tags = (card.dataset.tags || '').split(/\\s+/);
      var tagOk = !activeTag || tags.indexOf(activeTag) !== -1;
      var textOk = !query || (card.dataset.search || '').indexOf(query) !== -1;
      var show = tagOk && textOk;
      card.style.display = show ? '' : 'none';
      if (show) shown++;
    }});
    if (empty) empty.hidden = shown > 0;
    if (count) count.textContent = query
      ? (shown + ' of ' + cards.length + (cards.length === 1 ? ' entry' : ' entries'))
      : '';
  }}

  // Unfold the long tail of tags. Kept separate from the filter handler below
  // because this button is a disclosure, not a filter — it must never become
  // the active tag or it would blank the card list.
  function openTags(){{
    if (!filterBar) return;
    var more = document.getElementById('tagMore');
    filterBar.classList.add('tags-open');
    if (more) {{
      more.setAttribute('aria-expanded', 'true');
      more.textContent = '\\u2212 fewer';
    }}
  }}

  if (filterBar) {{
    filterBar.addEventListener('click', function(e){{
      var b = e.target.closest('.chip');
      if (!b) return;
      if (b.id === 'tagMore') {{
        if (filterBar.classList.contains('tags-open')) {{
          filterBar.classList.remove('tags-open');
          b.setAttribute('aria-expanded', 'false');
          b.textContent = '+ ' + b.dataset.count + ' more';
        }} else {{
          openTags();
        }}
        return;
      }}
      activeTag = b.dataset.tag;
      filterBar.querySelectorAll('.chip').forEach(function(c){{ c.classList.toggle('on', c === b); }});
      apply();
    }});
  }}

  if (input) {{
    // Live as you type, so Enter is never required — but the input still sits
    // inside a real <form action="index.html">, which is what makes searching
    // from a POST PAGE work (plain GET navigation, no JS needed there). Here,
    // already on the index, that same submit would just reload the page with
    // an unchanged ?q=, so it's swallowed — the input event already applied it.
    var form = input.form;
    if (form) form.addEventListener('submit', function(e){{ e.preventDefault(); }});

    input.addEventListener('input', function(){{
      query = input.value.trim().toLowerCase();
      apply();
      var url = new URL(location.href);
      if (query) url.searchParams.set('q', input.value); else url.searchParams.delete('q');
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    }});

    // Arriving here FROM another page's header search lands as index.html?q=…
    // — pick that up and apply it immediately rather than showing everything
    // until the reader retypes what they already searched.
    var handed = new URLSearchParams(location.search).get('q');
    if (handed) {{
      input.value = handed;
      query = handed.trim().toLowerCase();
      apply();
    }}
  }}

  // Arriving from a tag pill at the foot of an entry lands as index.html?tag=<slug>
  // — the same plain-GET handoff the header search uses, so a post page needs no
  // JS of its own. Only honoured if a chip with that slug actually exists, so a
  // stale or hand-typed tag shows everything rather than an empty page.
  var handedTag = new URLSearchParams(location.search).get('tag');
  if (handedTag && filterBar) {{
    var match = filterBar.querySelector('.chip[data-tag="' + handedTag + '"]');
    if (match) {{
      // Most tags are dish names used once, so the chip handed over here is
      // usually one of the folded ones. Unfold, or the reader sees a filtered
      // list with no visible chip explaining why — and no obvious way back.
      if (match.classList.contains('rare')) openTags();
      activeTag = handedTag;
      filterBar.querySelectorAll('.chip').forEach(function(c){{
        c.classList.toggle('on', c === match);
      }});
      apply();
    }}
  }}
}})();

// Re-order the cards by rating. Pure DOM shuffle — no second page to keep in sync,
// and unrated entries (a notes post is not a review) always sink to the bottom.
(function(){{
  var bar = document.getElementById('sortbar');
  if (!bar) return;
  var wrap = document.getElementById('cards');
  var original = Array.prototype.slice.call(wrap.children);
  bar.addEventListener('click', function(e){{
    var b = e.target.closest('.sortbtn');
    if (!b) return;
    bar.querySelectorAll('.sortbtn').forEach(function(x){{ x.classList.toggle('on', x === b); }});
    var list = original.slice();
    if (b.dataset.sort === 'stars') {{
      list.sort(function(a, c){{
        return (parseFloat(c.dataset.stars) || -1) - (parseFloat(a.dataset.stars) || -1);
      }});
    }}
    list.forEach(function(el){{ wrap.appendChild(el); }});
  }});
}})();
</script>"""
    return page(SITE_NAME, body, active="home", desc=BLURB, url="index.html")


def _post_article(p, extra=""):
    """The actual entry: title, rating, hero, body, tags. Shared by the real
    published post page and the unlisted draft preview (build_draft_previews)
    so the two can never drift apart — `extra` is where each caller hangs
    whatever comes before it (nothing, or a draft banner)."""
    # schema.org Review — this is what puts a star rating on the search
    # result itself, which matters a great deal for a blog nothing links to.
    ld = ""
    if p["stars"] is not None:
        # ⚠ UNESCAPE before this goes into JSON. Front matter is written for
        # HTML, so a subject like "Boulangerie &amp; Patisserie" is correct
        # there — but JSON-LD is not HTML, and passing it through raw published
        # the business name to Google with a literal "&amp;" in it.
        subject = html.unescape(p["subject"] or p["title"])
        url = f"{SITE_URL}{BASE}/{p['file']}"
        hero_url = f"{SITE_URL}{BASE}/img/{p['hero']}" if p["hero"] else ""
        ld = "\n<script type=\"application/ld+json\">" + json.dumps({
            "@context": "https://schema.org",
            "@type": "Review",
            "itemReviewed": {
                "@type": p["subject_type"],
                "name": subject,
                **({"address": html.unescape(p["place"])} if p["place"] else {}),
            },
            "reviewRating": {"@type": "Rating", "ratingValue": p["stars"],
                             "bestRating": 5, "worstRating": 1},
            "author": {"@type": "Person", "name": "Mr. Librarian"},
            "datePublished": p["date"].isoformat(),
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "url": url,
            # The headline and photo are what a rich result actually shows; a
            # Review with neither renders as a bare star row.
            "name": html.unescape(p["title"]),
            **({"image": hero_url} if hero_url else {}),
            **({"reviewBody": html.unescape(p["summary"])} if p.get("summary") else {}),
        }, ensure_ascii=False) + "</script>"
        # Breadcrumbs let the result show "The Librarian Abroad › <entry>"
        # instead of a bare URL. Cheap, and this site has exactly one level.
        ld += "\n<script type=\"application/ld+json\">" + json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME,
                 "item": f"{SITE_URL}{BASE}/"},
                {"@type": "ListItem", "position": 2,
                 "name": html.unescape(p["title"])},
            ],
        }, ensure_ascii=False) + "</script>"

    return f"""{extra}<article class="post">{ld}
  {_half_defs()}
  <h1>{html.escape(p['title'])}</h1>
  {_meta_line(p, show_hits=True)}
  {_rating_block(p)}
  {_hero_img(p, eager=True)}
  <div class="postbody">
{_add_img_dims(p['body'])}
  </div>
  {_tag_pills(p)}
</article>"""


def _respond_nudge(p):
    # Per-post nudge: the reach of comments without running a comment system.
    # The title rides along in `re=` so a message says which entry prompted it.
    return (
        '<div class="respond">'
        '<p><strong>Been here?</strong> Think I got it wrong, or know where I '
        f'should have gone instead? <a href="write.html?re={urllib.parse.quote(p["title"])}">'
        'Write to the librarian</a> — it goes straight to my desk.</p>'
        '</div>')


def build_post_pages(posts):
    out = []
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None      # posts are newest-first
        older = posts[i + 1] if i + 1 < len(posts) else None
        nav = []
        if older:
            nav.append(f'<a class="prev" href="{older["file"]}">← {html.escape(older["title"])}</a>')
        if newer:
            nav.append(f'<a class="next" href="{newer["file"]}">{html.escape(newer["title"])} →</a>')
        navbar = f'<nav class="postnav">{"".join(nav)}</nav>' if nav else ""

        body = f"""{_post_article(p)}
{_respond_nudge(p)}
{navbar}
<p class="backlink"><a href="index.html">← All entries</a></p>"""

        img = f"{SITE_URL}{BASE}/img/{p['hero']}" if p["hero"] else ""
        out.append((p["file"],
                    page(f"{p['title']} — {SITE_NAME}", body,
                         desc=_meta_desc(p), url=p["file"], image=img)))
    return out


# ------------------------------------------------------------- draft previews ---
#
# "Draft" means not on the index, not in the archive, not in the sitemap, not
# in the RSS feed — but Michael still needs to actually SEE a finished entry
# somewhere before deciding to publish it, and "run build_travel.py --drafts
# and read the HTML" isn't that for anyone on a phone. So every draft ALSO
# gets a real, deployed preview page — same live site, same styling, one
# click from a phone — reachable ONLY by direct link. It follows the exact
# posture the whole /travel/ blog already uses relative to the Bible project
# (README: "deliberately not linked… discovery is via the sitemap only"):
# unlinked from every nav/footer/index/archive, `noindex` on every page, and
# simply absent from sitemap.xml/feed.xml (both already build from
# load_posts(include_drafts=False), so this needs no change there). That is
# NOT real access control — anyone who has or guesses the URL can open it —
# consistent with how the rest of this blog already trades that for "no
# backend, no login, still just git push".
#
# Preview pages live at travel/draft-<slug>.html — a SIBLING of the real post
# pages, not a subdirectory — specifically so every relative link and
# <img src="img/…"> already written into a post's body just works unchanged;
# nesting under travel/drafts/ would have silently broken every image on
# every draft. DRAFTS_INDEX_FILE is the one page that lists them, for a
# single bookmarkable "what's waiting on me" URL.

DRAFTS_INDEX_FILE = "drafts.html"


def _draft_preview_file(slug):
    return f"draft-{slug}.html"


def _draft_banner():
    return (
        '<div class="draftbanner">🔒 <strong>Draft preview</strong> — not '
        "published. This page isn't linked from the site and won't appear in "
        f'search or the RSS feed. <a href="{DRAFTS_INDEX_FILE}">All drafts →</a></div>\n')


def _publish_box(p):
    """The "Publish this entry" button at the foot of a draft preview.

    A static page cannot flip its own front matter, so this is a HAND-OFF, not
    a form: the button opens a pre-filled GitHub issue titled `publish: <slug>`
    and .github/workflows/publish-draft.yml does the actual work
    (tools/publish_draft.py -> build_travel.py -> commit -> Pages redeploys).

    Why an issue rather than the page calling an API directly: the only way a
    static page can write to a repo is by carrying a token, and BOTH this site
    and the repo are PUBLIC. A push token pasted into a public page — or parked
    in localStorage on a phone — is a repo takeover waiting to happen, and it
    would also hand write access to anyone who found a draft URL. An issue link
    carries no secret whatsoever: the authorisation is an ordinary GitHub login,
    and the workflow re-checks SERVER-SIDE that the issue author is the repo
    owner. So a stranger who finds this page and opens the same issue publishes
    nothing at all; they have just filed an issue.

    It costs one extra tap (GitHub's own "Create") and that tap is the
    confirmation step, which on a button whose whole job is "make this public"
    is a feature rather than friction.
    """
    live = f"{SITE_URL}{BASE}/{p['file']}"
    draft_url = f"{SITE_URL}{BASE}/{_draft_preview_file(p['slug'])}"
    body = (
        f"Publishing **{p['title']}**.\n\n"
        "Opening this issue *is* the whole action — press **Create** and the "
        "publish workflow flips `draft: false`, rebuilds `/travel/`, and pushes. "
        "It will comment here and close itself once the entry is live.\n\n"
        f"- Draft: {draft_url}\n"
        f"- Goes live at: {live}\n\n"
        "Nothing to fill in."
    )
    q = urllib.parse.urlencode({"title": f"publish: {p['slug']}", "body": body})
    return (
        '<div class="publishbox">\n'
        "  <strong>Read it, happy with it?</strong>\n"
        f'  <a class="pubbtn" href="https://github.com/{PUBLISH_REPO}/issues/new?{q}"'
        ' target="_blank" rel="noopener">✓ Publish this entry</a>\n'
        '  <span class="pubnote">Opens GitHub with everything filled in — press '
        "<em>Create</em> there and it's live in about a minute. Only you can: the "
        "workflow checks server-side that the request came from you.</span>\n"
        "</div>\n")


def build_draft_previews(all_posts):
    out = []
    for p in all_posts:
        if not p["draft"]:
            continue
        body = f"""{_post_article(p, extra=_draft_banner())}
{_publish_box(p)}
{_respond_nudge(p)}
<p class="backlink"><a href="{DRAFTS_INDEX_FILE}">← All drafts</a></p>"""
        out.append((_draft_preview_file(p["slug"]),
                    page(f"[DRAFT] {p['title']} — {SITE_NAME}", body,
                         desc=p["summary"], noindex=True)))
    return out


def build_drafts_index(all_posts):
    drafts = [p for p in all_posts if p["draft"]]
    if not drafts:
        listing = '<p class="empty">Nothing in draft right now.</p>'
    else:
        rows = "\n".join(
            f'<li><time datetime="{p["date"].isoformat()}">{p["date"].isoformat()}</time>'
            f'<a href="{_draft_preview_file(p["slug"])}">{html.escape(p["title"])}</a>'
            + (f'<span class="place">{html.escape(p["place"])}</span>' if p["place"] else "")
            + "</li>"
            for p in drafts)
        listing = f'<ul class="archive">\n{rows}\n  </ul>'
    body = f"""<section class="lede">
  <h1>Drafts</h1>
  <p>Unpublished entries, previewed here before they go out. Nothing on this
  page is linked from the rest of the site or shows up in search — bookmark
  it if you want a fixed place to check back.</p>
</section>
<div class="panel">
{listing}
</div>"""
    return page(f"Drafts — {SITE_NAME}", body,
                desc="Unpublished entries, for preview only.", noindex=True)


def _prune_leaked_draft_pages(current_draft_slugs):
    """Remove a REAL <slug>.html left behind for a post that is still a draft.

    A `--drafts` preview build writes every draft out at its real published URL
    — that's the point of the preview — but write() only ever adds files, so the
    next plain build leaves that page sitting in travel/ as a live, indexable
    page for an unpublished entry. It's orphaned (nothing links to it, and it's
    absent from the index, feed and sitemap), which is exactly what makes it
    easy to miss and commit. This has now happened twice: the orphaned
    travel/in-n-out-vancouver.html noted in _prune_stale_draft_previews, and
    travel/our-lady-of-sorrows.html from the 2026-07-29 preview build.

    Only ever touches a slug whose post is a draft RIGHT NOW, and only on a
    non-`--drafts` build, so it can never delete a legitimately published page.
    """
    if not os.path.isdir(OUT_DIR):
        return
    for slug in sorted(current_draft_slugs):
        path = os.path.join(OUT_DIR, slug + ".html")
        if os.path.exists(path):
            os.remove(path)
            print(f"  (removed leaked draft page: {slug}.html — it is still a draft)")


def _prune_stale_draft_previews(current_draft_slugs):
    """Remove a preview page left behind by a post that's since been published
    or deleted — write() only ever adds files, so without this a stale
    draft-<slug>.html (with a stale [DRAFT] title, pointing at content that
    may since have changed under the real published URL) would just sit there
    forever. Same class of bug as the orphaned travel/in-n-out-vancouver.html
    from the local --drafts preview build a few commits back."""
    if not os.path.isdir(OUT_DIR):
        return
    for fn in os.listdir(OUT_DIR):
        if not (fn.startswith("draft-") and fn.endswith(".html")):
            continue
        slug = fn[len("draft-"):-len(".html")]
        if slug not in current_draft_slugs:
            os.remove(os.path.join(OUT_DIR, fn))
            print(f"  (removed stale draft preview: {fn})")


def _bookmarked_photos(item):
    photos = item.get("photos") or []
    if not photos:
        return ""
    figs = "\n".join(
        f'    <img src="img/{html.escape(p["img"], quote=True)}" '
        f'alt="{html.escape(p["alt"], quote=True)}" loading="lazy"/>'
        for p in photos)
    return f'\n  <div class="bmphotos">\n{figs}\n  </div>'


def _bookmarked_card(item):
    directions = _directions_link(item["place"]) if item.get("place") else ""
    link = ""
    if item.get("link"):
        link = (f'\n    <a class="visit" href="{html.escape(item["link"], quote=True)}" '
                f'rel="noopener">Visit their site →</a>')
    photos = _bookmarked_photos(item)
    return f"""<li>
    <h3>{html.escape(item['name'])}</h3>
    <span class="place">{html.escape(item['place'])}</span>
    <p>{html.escape(item['why'])}</p>{photos}
    <span class="added">spotted {item['added'].isoformat()}</span>
    {directions}{link}
  </li>"""


def build_bookmarked():
    """A running shelf of places worth going back for, not yet reviewed.

    Deliberately not a post: there's no meal to score yet, so no stars, no
    verdict box — just the name, the place, why it caught our eye, and
    whatever photos we already have. Add to BOOKMARKED above; when a place
    actually gets eaten, write its real entry and remove it from here.
    """
    if BOOKMARKED:
        items = "\n".join(_bookmarked_card(i) for i in
                           sorted(BOOKMARKED, key=lambda i: i["added"], reverse=True))
        list_html = f'<ul class="bookmarklist">\n{items}\n</ul>'
    else:
        list_html = '<p class="empty">Nothing bookmarked right now.</p>'

    body = f"""<section class="lede">
  <h1>Bookmarked</h1>
  <p>Places spotted, recommended, or walked past with a window worth a second
  look — turned down like a page, to come back to. No stars yet, because
  there's no meal to score. When one of these actually gets eaten, it
  graduates into a real entry.</p>
</section>
{list_html}"""
    return page(f"Bookmarked — {SITE_NAME}", body, active="bookmarked",
                desc="Places worth going back for — spotted but not yet reviewed.",
                url="bookmarked.html")


def build_about():
    body = f"""<section class="lede">
  <h1>About</h1>
</section>
{_half_defs(18)}
<div class="panel prose">
  <p>{html.escape(BLURB)} This is a personal notebook — where we went, what we ate,
  what it cost in time and shoe leather, and whether it was worth it. No sponsored
  posts, no press trips. Once in a while there's a disclosed affiliate link, when it's
  directly relevant to what I'm actually writing about — always flagged plainly right
  where it appears, never folded in silently. If something was disappointing, it still
  says so.</p>

  <p>Photographs are my own unless credited otherwise. Places and prices were true on
  the day I wrote them down and probably aren't any more — check before you go.</p>

  <h2 id="stars">Librarian's Stars</h2>
  <p>Entries that review somewhere carry a rating out of five. Notes and odds and ends
  don't — not everything is a verdict.</p>
  <p>A scale is worth nothing unless it can say no, and the failure mode is obvious: if
  everywhere I enjoyed gets five, the number stops carrying information at all. That is
  how the big review sites ended up averaging four-and-a-half out of five and telling you
  nothing. So the levels below are a contract. <strong>Three stars is a good meal.</strong>
  Five is meant to stay rare.</p>
  <table class="ratingkey">
    {_rating_key()}
  </table>
  <p class="half-note">Half stars exist for the places that sit between two of these.</p>

  <h2 id="bookmarked">Bookmarked</h2>
  <p><a href="bookmarked.html">This page</a> is a page turned down to come back to —
  places spotted, recommended, or walked past with a window worth a second look, filed
  there until there's time to actually sit down and eat. No stars yet, because there's
  no meal to score. Once one of them gets eaten, it graduates into a real entry and
  comes off the shelf.</p>

  <h2>Following along</h2>
  <p>There's an <a href="feed.xml">RSS feed</a> if you'd like new entries to come to you.
  There's no newsletter, no tracking beyond an anonymous, cookie-less page counter, and
  nothing here is for sale.</p>

  <h2>A note on timing</h2>
  <p>Entries generally go up after I'm home again, not while I'm away.</p>
</div>"""
    return page(f"About — {SITE_NAME}", body, active="about",
                desc=f"About {SITE_NAME}.", url="about.html")


def build_write():
    """The one place readers can reach the librarian.

    A form, not a comment thread — see the note on FORM_ENDPOINT. It posts to
    FormSubmit, so there is no backend, no database and no cookie. The `re`
    query parameter carries which entry the reader was reading (set by the
    per-post nudge) and is filled in client-side.
    """
    body = f"""<section class="lede">
  <h1>Write to the librarian</h1>
  <p>Been somewhere in here? Think I got it wrong? Know the place I should have gone
  instead? This goes straight to my desk.</p>
</section>

<div class="panel">
  <form action="{FORM_ENDPOINT}" method="POST" class="askform">
    <input type="hidden" name="_subject" value="The Librarian Abroad — a note from a reader"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="{SITE_URL}{BASE}/thanks.html"/>
    <!-- Honeypot: a real person never sees this, a bot fills it in. -->
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>

    <label>Which entry is this about? <span class="opt">(optional)</span>
      <input type="text" name="entry" id="entryField"
             placeholder="Leave blank if it's not about a particular one"/>
    </label>
    <label>Your name <span class="opt">(optional)</span>
      <input type="text" name="name" placeholder="However you'd like to be known — or leave blank"/>
    </label>
    <label>Your email <span class="opt">(optional — only if you'd like a reply)</span>
      <input type="email" name="email" placeholder="you@example.com"/>
    </label>
    <label>Your message <span class="req">(required)</span>
      <textarea name="message" required rows="7"
        placeholder="A correction, a recommendation, an argument about the chashu…"></textarea>
    </label>
    <button class="btn" type="submit">Send it</button>
    <p class="formnote">Sending shows a quick captcha to keep the robots out, then brings you
    back here. Nothing is posted publicly — messages go straight to my inbox, and I read all
    of them.</p>
  </form>
</div>

<script>
// Pre-fill "which entry" when a reader arrives from the link at the foot of a post.
// Set with .value (never innerHTML) so a crafted URL can't inject markup.
(function(){{
  try {{
    var re = new URLSearchParams(location.search).get('re');
    var f = document.getElementById('entryField');
    if (re && f) f.value = re.slice(0, 200);
  }} catch (e) {{}}
}})();
</script>"""
    return page(f"Write to the librarian — {SITE_NAME}", body, active="write",
                desc="Send a note, a correction or a recommendation to Mr. Librarian.",
                url="write.html")


def build_thanks():
    body = """<section class="lede">
  <h1>It's on the desk</h1>
</section>
<div class="panel prose">
  <p><strong>Your note is in.</strong> Thank you — I read everything that arrives, and a
  good tip about somewhere I haven't been is the most useful thing anyone sends.</p>
  <p>If you left an email and it wants an answer, you'll get one. Meanwhile the
  <a href="index.html">rest of the entries</a> are here.</p>
</div>"""
    # noindex: this page only exists as somewhere to land after submitting.
    return page(f"Message received — {SITE_NAME}", body,
                desc="Your note is on the librarian's desk.", noindex=True)


def _rfc822(d):
    return blogkit.rfc822(d)


def build_feed(posts):
    """RSS 2.0 — the blog's own front door for readers who follow it directly.

    Deliberately summary-only (no full post body): the point is to bring readers to
    the page, and a summary feed can't leak half-formatted HTML into someone's reader.
    """
    items = []
    for p in posts[:30]:
        link = f"{SITE_URL}{BASE}/{p['file']}"
        desc = p["summary"] + (f" ({p['place']})" if p["place"] else "")
        cats = "".join(f"    <category>{sax.escape(t)}</category>\n" for t in p["tags"])
        items.append(f"""  <item>
    <title>{sax.escape(p['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{_rfc822(p['date'])}</pubDate>
    <description>{sax.escape(desc)}</description>
{cats}  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{sax.escape(SITE_NAME)}</title>
  <link>{SITE_URL}{BASE}/</link>
  <atom:link href="{SITE_URL}{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{sax.escape(BLURB)}</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


def build_sitemap(posts):
    """A sitemap is not optional here — it IS the discovery plan.

    Nothing on the web links to this blog (that is the point), so a crawler has no
    path to it. Submit this file once in Google Search Console. Without it, or an
    inbound link from somewhere, these pages are effectively invisible.
    """
    newest = posts[0]["date"] if posts else dt.date.today()
    bookmarked_newest = max((i["added"] for i in BOOKMARKED), default=newest)
    urls = [(f"{SITE_URL}{BASE}/", newest),
            (f"{SITE_URL}{BASE}/bookmarked.html", bookmarked_newest),
            (f"{SITE_URL}{BASE}/about.html", newest),
            (f"{SITE_URL}{BASE}/write.html", newest)]
    urls += [(f"{SITE_URL}{BASE}/{p['file']}", p["date"]) for p in posts]
    body = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{d.isoformat()}</lastmod></url>" for u, d in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
"""


# ----------------------------------------------------------------------- main ---

def write(rel, text):
    path = os.path.join(OUT_DIR, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def check_seo(posts):
    """Every entry must carry its own search-facing metadata. Fails the build.

    The rule Michael asked for (2026-08-01): a post does not go up without its
    SEO being right. Enforcing it in the builder rather than in a habit is the
    only version that survives a busy week — it applies to a draft preview as
    much as to a publish, so a problem surfaces while the entry is still being
    written, not months later in Search Console.

    Most of the value here is STRUCTURAL and therefore automatic: an entry
    inherits its meta description (_meta_desc), Review + BreadcrumbList JSON-LD
    (_post_article), canonical, OG/Twitter card, image dimensions and an eager
    hero simply by existing. This guard exists so that stays true.

    What it deliberately does NOT check is the editorial half — whether a
    heading leads with the words a person would actually type. No build can
    judge that; it lives in the checklist in source/travel/_template.html.

    WARN vs FAIL: it fails only on things that are unambiguously broken and
    always fixable in the front matter. A missing hero is a warning, because a
    notes entry legitimately has no photograph."""
    fail, warn, seen = [], [], {}
    for p in posts:
        who = p["slug"]
        d = _meta_desc(p)
        if len(d) > META_DESC_MAX:
            fail.append(f"  {who}: meta description {len(d)} chars — search will cut it "
                        f"(shorten `summary:`, or set `meta_desc:`)")
        if len(d) < META_DESC_MIN:
            fail.append(f"  {who}: meta description only {len(d)} chars — too thin to earn "
                        f"a click (lengthen `summary:`, or set `meta_desc:`)")
        key = d[:60].lower()
        if key in seen:
            fail.append(f"  {who}: description opens identically to {seen[key]} — "
                        f"duplicate descriptions compete with each other")
        seen[key] = who

        if not p["tags"]:
            fail.append(f"  {who}: no `tags:` — nothing to file it under, and the tag "
                        f"pills are this site's only internal linking")
        if p["hero"] and not p["hero_alt"]:
            fail.append(f"  {who}: `hero:` without `hero_alt:` — the hero is the OG "
                        f"image and the one photo Google indexes by name")
        # Body images: alt is both the accessibility contract and how an image
        # earns anything in image search. A decorative <img> has no place here.
        for tag in re.findall(r'<img\s[^>]*>', p["body"], re.I):
            if not re.search(r'\balt="[^"]{4,}"', tag):
                src = (re.search(r'src="([^"]*)"', tag) or [None, "?"])[1]
                fail.append(f"  {who}: <img> with no useful alt text — {src}")
        if not p["hero"]:
            warn.append(f"  {who}: no `hero:` — shared links get no preview image")
        if len(p["title"]) > 60:
            warn.append(f"  {who}: title {len(p['title'])} chars — the "
                        f"'— {SITE_NAME}' suffix will be cut in results")
    if warn:
        print("SEO notes:")
        print("\n".join(warn))
    if fail:
        raise SystemExit("SEO check failed — an entry would ship without its "
                         "search metadata:\n" + "\n".join(fail))


def check_canonicals():
    """Every URL in the sitemap must agree with that page's own canonical.

    A sitemap that submits one URL while the page names a different one is
    self-contradicting, and Google resolves it by dropping the submitted URL.
    It is silent — the sitemap reports as "success", the pages look fine, and
    the URL simply never indexes. Ours did exactly this on /travel/ for the
    first few days after submission.

    Runs on the BUILT output, after everything is written, because that is the
    only place the two are actually comparable."""
    sm_path = os.path.join(OUT_DIR, "sitemap.xml")
    if not os.path.exists(sm_path):
        return
    bad = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", open(sm_path, encoding="utf-8").read()):
        rel = loc[len(f"{SITE_URL}{BASE}/"):] or "index.html"
        fp = os.path.join(OUT_DIR, rel)
        if not os.path.exists(fp):
            bad.append(f"  {loc}: in the sitemap but no such file was built")
            continue
        doc = open(fp, encoding="utf-8").read()
        m = re.search(r'<link rel="canonical" href="([^"]+)"', doc)
        if not m:
            bad.append(f"  {loc}: no canonical")
        elif m.group(1) != loc:
            bad.append(f"  {loc}: canonical disagrees -> {m.group(1)}")
        if re.search(r'<meta name="robots"[^>]*noindex', doc, re.I):
            bad.append(f"  {loc}: noindex, but submitted in the sitemap")
    if bad:
        raise SystemExit("Sitemap/canonical check failed — submitted URLs that "
                         "contradict their own pages:\n" + "\n".join(bad))


def main():
    ap = argparse.ArgumentParser(description="Build The Librarian Abroad (/travel/).")
    ap.add_argument("--drafts", action="store_true",
                    help="fold drafts into the real index/archive too — local preview only")
    args = ap.parse_args()

    all_posts = load_posts(include_drafts=True)
    posts = all_posts if args.drafts else [p for p in all_posts if not p["draft"]]
    # Before anything is written, and over ALL posts including drafts — an entry
    # should fail this while it is still being drafted, not on the day it ships.
    check_seo(all_posts)
    os.makedirs(os.path.join(OUT_DIR, "img"), exist_ok=True)

    write("index.html", build_index(posts))
    write("bookmarked.html", build_bookmarked())
    write("about.html", build_about())
    write("write.html", build_write())
    write("thanks.html", build_thanks())
    for fn, doc in build_post_pages(posts):
        write(fn, doc)
    write("feed.xml", build_feed(posts))
    write("sitemap.xml", build_sitemap(posts))

    # Always on, regardless of --drafts: this is what makes a draft checkable
    # from the LIVE site (see the big comment above build_draft_previews), so
    # a plain `python3 build_travel.py` before a normal commit keeps it in
    # sync without a separate step to remember.
    draft_slugs = {p["slug"] for p in all_posts if p["draft"]}
    for fn, doc in build_draft_previews(all_posts):
        write(fn, doc)
    write(DRAFTS_INDEX_FILE, build_drafts_index(all_posts))
    _prune_stale_draft_previews(draft_slugs)
    if not args.drafts:
        _prune_leaked_draft_pages(draft_slugs)

    # After everything is written: the sitemap and the pages must not disagree.
    check_canonicals()

    drafts = len(draft_slugs)
    print("built {} post(s){} -> {}".format(
        len(posts),
        " (including {} draft(s))".format(drafts) if drafts and args.drafts else "",
        OUT_DIR))
    for p in posts:
        print("  {}  {:<34} {}{}".format(
            p["date"], p["file"], p["title"], "   [DRAFT]" if p["draft"] else ""))
    if args.drafts:
        print("\n⚠ --drafts is a LOCAL PREVIEW build. Re-run without it before committing.")
    if drafts:
        print("\n{} draft(s) previewable at {}/{} once pushed:".format(
            drafts, BASE, DRAFTS_INDEX_FILE))
        for p in all_posts:
            if p["draft"]:
                print("  {}{}/{}".format(SITE_URL, BASE, _draft_preview_file(p["slug"])))


if __name__ == "__main__":
    main()

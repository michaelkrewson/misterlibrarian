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
import datetime as dt
import hashlib
import html
import json
import os
import re
import urllib.parse
import xml.sax.saxutils as sax

# ---------------------------------------------------------------- identity ---

# Rename the blog by editing these three lines and rebuilding. Nothing else
# hardcodes the name.
SITE_NAME = "The Librarian Abroad"
TAGLINE = "Travels and meals, kept by Mr. Librarian"
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

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "source", "travel")
OUT_DIR = os.path.join(ROOT, "travel")

# Fields a post may declare. Anything else in the front matter is an error —
# better a loud typo than a silently-ignored `sumary:` line.
KNOWN_KEYS = {
    "title", "date", "place", "tags", "hero", "hero_alt", "hero_credit",
    "summary", "draft", "stars", "subject", "subject_type",
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


def _asset_ver(rel):
    """Short content hash of a static asset, appended to its URL so a CSS edit is
    never masked by a stale browser cache. (Same trick the Bible builder uses.)"""
    try:
        with open(os.path.join(OUT_DIR, rel), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:10]
    except OSError:
        return "0"


# ------------------------------------------------------------------- chrome ---

# A plate that is also a compass — the blog's mark. Deliberately nothing like the
# Bible project's scroll: different shape, different palette, no shared glyph.
COMPASS_SVG = """<svg class="mark" viewBox="0 0 48 48" width="46" height="46" aria-hidden="true">
  <circle cx="24" cy="24" r="21" fill="#fdf6ea" stroke="#c25e3a" stroke-width="2"/>
  <circle cx="24" cy="24" r="15.5" fill="none" stroke="#e0c9a6" stroke-width="1.2"/>
  <path d="M24 9.5 L27.4 20.6 L38.5 24 L27.4 27.4 L24 38.5 L20.6 27.4 L9.5 24 L20.6 20.6 Z"
        fill="#c25e3a" opacity="0.9"/>
  <circle cx="24" cy="24" r="3.4" fill="#6b7a4a"/>
  <circle cx="24" cy="24" r="1.3" fill="#fdf6ea"/>
</svg>"""


def header(active=""):
    """Site header. NOTE: every link here is relative and stays inside /travel/ —
    there is intentionally no route from this blog to the Bible project."""
    def cls(k):
        return ' class="on"' if k == active else ""
    return f"""<header class="site-head">
  <a class="brand" href="index.html">
    {COMPASS_SVG}
    <span class="brand-name">The Librarian <span class="abroad">Abroad</span></span>
  </a>
  <div class="rule"></div>
  <div class="tag">{TAGLINE}</div>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Latest</a>
    <a href="index.html#archive">Archive</a>
    <a href="write.html"{cls('write')}>✉️ Write</a>
    <a href="about.html"{cls('about')}>About</a>
    <a href="feed.xml" title="Subscribe by RSS">RSS</a>
  </nav>
</header>"""


FOOTER = f"""<footer class="site-foot">
  <p>{SITE_NAME} — {BLURB}</p>
  <p><a href="index.html">Latest</a> · <a href="write.html">Write to the librarian</a> ·
  <a href="about.html">About</a> · <a href="feed.xml">RSS</a></p>
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
        full = f"{SITE_URL}{BASE}/{url}"
        tags.insert(0, f'<link rel="canonical" href="{full}"/>')
        tags.append(f'<meta property="og:url" content="{full}"/>')
    return "\n" + "\n".join(tags)


def page(title, body, active="", desc="", url="", image="", noindex=False):
    css_v = _asset_ver("style.css")
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
{body}
{FOOTER}
</div>
</body>
</html>
"""


# -------------------------------------------------------------- post loading ---

FNAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)\.html$")


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
            "draft": is_draft,
            "body": body,
        })

    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    if len({p["slug"] for p in posts}) != len(posts):
        raise ValueError("two posts share a slug — slugs must be unique across all dates")
    return posts


# ------------------------------------------------------------------ rendering ---

def _pretty_date(d):
    # %-d is a GNU/BSD extension; fall back to the zero-padded form elsewhere.
    try:
        return d.strftime("%B %-d, %Y")
    except ValueError:
        return d.strftime("%B %d, %Y")


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
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def _hero_img(p, cls="hero"):
    if not p["hero"]:
        return ""
    alt = html.escape(p["hero_alt"] or p["title"], quote=True)
    credit = (f'<figcaption class="credit">{html.escape(p["hero_credit"])}</figcaption>'
              if p["hero_credit"] else "")
    return (f'<figure class="{cls}">'
            f'<img src="img/{html.escape(p["hero"], quote=True)}" alt="{alt}" loading="lazy"/>'
            f'{credit}</figure>')


def _meta_line(p):
    bits = [f'<time datetime="{p["date"].isoformat()}">{_pretty_date(p["date"])}</time>']
    if p["place"]:
        bits.append(f'<span class="place">📍 {html.escape(p["place"])}</span>')
    if p["draft"]:
        bits.append('<span class="draftflag">DRAFT — not published</span>')
    return '<div class="postmeta">' + " · ".join(bits) + "</div>"


def _tag_pills(p):
    if not p["tags"]:
        return ""
    return ('<div class="tags">'
            + "".join(f'<span class="pill">{html.escape(t)}</span>' for t in p["tags"])
            + "</div>")


def post_card(p):
    data_tags = " ".join(_tag_slug(t) for t in p["tags"])
    stars = (f'<div class="cardrating">{_stars_svg(p["stars"], 17)}</div>'
             if p["stars"] is not None else "")
    return f"""<article class="card" data-tags="{html.escape(data_tags, quote=True)}" data-stars="{p['stars'] if p['stars'] is not None else -1}">
  <a class="cardlink" href="{p['file']}">
    {_hero_img(p, 'thumb')}
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
        archive = ""
    else:
        cards = "\n".join(post_card(p) for p in posts)
        all_tags = sorted({t for p in posts for t in p["tags"]}, key=str.lower)
        chips = ""
        if all_tags:
            chips = ('<div class="filters" id="filters">'
                     '<button class="chip on" data-tag="">All</button>'
                     + "".join(
                         f'<button class="chip" data-tag="{_tag_slug(t)}">{html.escape(t)}</button>'
                         for t in all_tags)
                     + "</div>")
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

    body = f"""<section class="lede">
  <h1>{html.escape(SITE_NAME)}</h1>
  <p>{html.escape(BLURB)}</p>
</section>
{_half_defs(17)}{_half_defs(14)}
{chips}
{sortbar}
<div class="cards" id="cards">
{cards}
</div>
{archive}
<script>
// Tag filter — pure client-side, so there are no per-tag pages to generate,
// keep in sync, or leave behind when a tag stops being used.
(function(){{
  var bar = document.getElementById('filters');
  if (!bar) return;
  bar.addEventListener('click', function(e){{
    var b = e.target.closest('.chip');
    if (!b) return;
    var want = b.dataset.tag;
    bar.querySelectorAll('.chip').forEach(function(c){{ c.classList.toggle('on', c === b); }});
    document.querySelectorAll('#cards .card').forEach(function(card){{
      var tags = (card.dataset.tags || '').split(/\\s+/);
      card.style.display = (!want || tags.indexOf(want) !== -1) ? '' : 'none';
    }});
  }});
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

        # Per-post nudge: the reach of comments without running a comment system.
        # The title rides along in `re=` so a message says which entry prompted it.
        respond = (
            '<div class="respond">'
            '<p><strong>Been here?</strong> Think I got it wrong, or know where I '
            f'should have gone instead? <a href="write.html?re={urllib.parse.quote(p["title"])}">'
            'Write to the librarian</a> — it goes straight to my desk.</p>'
            '</div>')

        # schema.org Review — this is what puts a star rating on the search
        # result itself, which matters a great deal for a blog nothing links to.
        ld = ""
        if p["stars"] is not None:
            ld = "\n<script type=\"application/ld+json\">" + json.dumps({
                "@context": "https://schema.org",
                "@type": "Review",
                "itemReviewed": {
                    "@type": p["subject_type"],
                    "name": p["subject"] or p["title"],
                    **({"address": p["place"]} if p["place"] else {}),
                },
                "reviewRating": {"@type": "Rating", "ratingValue": p["stars"],
                                 "bestRating": 5, "worstRating": 1},
                "author": {"@type": "Person", "name": "Mr. Librarian"},
                "datePublished": p["date"].isoformat(),
                "publisher": {"@type": "Organization", "name": SITE_NAME},
            }, ensure_ascii=False) + "</script>"

        body = f"""<article class="post">{ld}
  {_half_defs()}
  <h1>{html.escape(p['title'])}</h1>
  {_meta_line(p)}
  {_rating_block(p)}
  {_hero_img(p)}
  <div class="postbody">
{p['body']}
  </div>
  {_tag_pills(p)}
</article>
{respond}
{navbar}
<p class="backlink"><a href="index.html">← All entries</a></p>"""

        img = f"{SITE_URL}{BASE}/img/{p['hero']}" if p["hero"] else ""
        out.append((p["file"],
                    page(f"{p['title']} — {SITE_NAME}", body,
                         desc=p["summary"], url=p["file"], image=img)))
    return out


def build_about():
    body = f"""<section class="lede">
  <h1>About</h1>
</section>
{_half_defs(18)}
<div class="panel prose">
  <p>{html.escape(BLURB)} This is a personal notebook — where we went, what we ate,
  what it cost in time and shoe leather, and whether it was worth it. No sponsored
  posts, no affiliate links, no press trips. If something was disappointing, it says so.</p>

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
    return dt.datetime(d.year, d.month, d.day, 12, 0, 0).strftime("%a, %d %b %Y %H:%M:%S +0000")


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
    urls = [(f"{SITE_URL}{BASE}/", newest),
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


def main():
    ap = argparse.ArgumentParser(description="Build The Librarian Abroad (/travel/).")
    ap.add_argument("--drafts", action="store_true",
                    help="include posts marked `draft: true` (local preview only)")
    args = ap.parse_args()

    posts = load_posts(include_drafts=args.drafts)
    os.makedirs(os.path.join(OUT_DIR, "img"), exist_ok=True)

    write("index.html", build_index(posts))
    write("about.html", build_about())
    write("write.html", build_write())
    write("thanks.html", build_thanks())
    for fn, doc in build_post_pages(posts):
        write(fn, doc)
    write("feed.xml", build_feed(posts))
    write("sitemap.xml", build_sitemap(posts))

    drafts = sum(1 for p in posts if p["draft"])
    print("built {} post(s){} -> {}".format(
        len(posts),
        " (including {} draft(s))".format(drafts) if drafts else "",
        OUT_DIR))
    for p in posts:
        print("  {}  {:<34} {}{}".format(
            p["date"], p["file"], p["title"], "   [DRAFT]" if p["draft"] else ""))
    if args.drafts:
        print("\n⚠ --drafts is a LOCAL PREVIEW build. Re-run without it before committing.")


if __name__ == "__main__":
    main()

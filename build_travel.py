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
import os
import re
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

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "source", "travel")
OUT_DIR = os.path.join(ROOT, "travel")

# Fields a post may declare. Anything else in the front matter is an error —
# better a loud typo than a silently-ignored `sumary:` line.
KNOWN_KEYS = {
    "title", "date", "place", "tags", "hero", "hero_alt", "hero_credit",
    "summary", "draft",
}
REQUIRED_KEYS = {"title", "date", "summary"}


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
    <a href="about.html"{cls('about')}>About</a>
    <a href="feed.xml" title="Subscribe by RSS">RSS</a>
  </nav>
</header>"""


FOOTER = f"""<footer class="site-foot">
  <p>{SITE_NAME} — {BLURB}</p>
  <p><a href="index.html">Latest</a> · <a href="about.html">About</a> ·
  <a href="feed.xml">RSS</a></p>
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


def page(title, body, active="", desc="", url="", image=""):
    css_v = _asset_ver("style.css")
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}{_og(title, desc, url, image)}
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

        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        posts.append({
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
    return f"""<article class="card" data-tags="{html.escape(data_tags, quote=True)}">
  <a class="cardlink" href="{p['file']}">
    {_hero_img(p, 'thumb')}
    <div class="cardbody">
      {_meta_line(p)}
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
            + "</li>"
            for p in posts)
        archive = f"""<section class="panel" id="archive">
  <h2>Archive</h2>
  <ul class="archive">
{rows}
  </ul>
</section>"""

    body = f"""<section class="lede">
  <h1>{html.escape(SITE_NAME)}</h1>
  <p>{html.escape(BLURB)}</p>
</section>
{chips}
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

        body = f"""<article class="post">
  <h1>{html.escape(p['title'])}</h1>
  {_meta_line(p)}
  {_hero_img(p)}
  <div class="postbody">
{p['body']}
  </div>
  {_tag_pills(p)}
</article>
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
<div class="panel prose">
  <p>{html.escape(BLURB)} This is a personal notebook — where we went, what we ate,
  what it cost in time and shoe leather, and whether it was worth it. No sponsored
  posts, no affiliate links, no press trips. If something was disappointing, it says so.</p>

  <p>Photographs are my own unless credited otherwise. Places and prices were true on
  the day I wrote them down and probably aren't any more — check before you go.</p>

  <h2>Following along</h2>
  <p>There's an <a href="feed.xml">RSS feed</a> if you'd like new entries to come to you.
  There's no newsletter, no tracking beyond an anonymous, cookie-less page counter, and
  nothing here is for sale.</p>

  <h2>A note on timing</h2>
  <p>Entries generally go up after I'm home again, not while I'm away.</p>
</div>"""
    return page(f"About — {SITE_NAME}", body, active="about",
                desc=f"About {SITE_NAME}.", url="about.html")


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
            (f"{SITE_URL}{BASE}/about.html", newest)]
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

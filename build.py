#!/usr/bin/env python3
"""Build the MisterLibrarian Bible Project static site.

Single source of truth: mstr-trader's dashboard/mister_translation.html
(each chapter lives there as a <div class="chapter-panel" id="chapter-genN">
block). This script extracts every chapter panel and regenerates the public
site: one page per chapter with prev/next navigation, a Table of Contents
with live progress, the home page, and the Ask Mr. Librarian posts.

Usage:
    python3 build.py [--source /path/to/mister_translation.html]

After adding a new chapter to the source file, re-run this and push.
"""
import argparse
import hashlib
import html
import json
import math
import os
import re
from collections import defaultdict

from library_data import (DICTIONARY, ENCYCLOPEDIA, XREFS, VIDEO_CREDITS, VIDEO_QUEUE,
                           LINK_OVERRIDES, VERSE_OF_DAY)

OUT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOURCE = os.path.join(OUT, "source", "mister_translation.html")


def _asset_ver(name):
    """Short content hash of a static asset, for cache-busting its URL on every build
    (so a style.css edit can never be masked by a stale browser/CDN cache again)."""
    try:
        with open(os.path.join(OUT, name), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:10]
    except OSError:
        return "0"


CSS_VER = _asset_ver("style.css")
JS_VER = _asset_ver("player-clips.js")
AUDIO_JS_VER = _asset_ver("audio-reader.js")

SITE_NAME = "The MisterLibrarian Bible Project"
TAGLINE = "Catalogued &amp; compared, one chapter at a time"
SITE_URL = "https://michaelkrewson.github.io/misterlibrarian"

# FormSubmit endpoint for the Ask-a-Question form. This is the activated form's
# random alias (delivers to the librarian's gmail without exposing the address in
# the page source). Verified working 2026-07-10 via a test submission.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

# GoatCounter — free, open-source, cookie-less analytics (no consent banner needed;
# see https://www.goatcounter.com). Sign up, enable "Allow adding visitor counts on
# your website" in Settings > Integrations, and set this to your site code (the
# CODE in CODE.goatcounter.com). Leave as None and every tracking hook below is a
# silent no-op — the site behaves exactly as it does today.
GOATCOUNTER_CODE = "mistertranslation"

# Chapter registry: slug -> (book, chapter number, one-line teaser).
# Add a line here when a new chapter lands in the source file.
CHAPTERS = [
    ("gen1", "Genesis", 1, "The seven days — day one, the vault, and the image of God."),
    ("gen2", "Genesis", 2, "The sabbath, the divine name arrives, and “side,” not “rib.”"),
    ("gen3", "Genesis", 3, "The serpent, the fall, and the naked/crafty pun that spans the chapter break."),
    ("gen4", "Genesis", 4, "Cain and Abel, the first murder, and “am I my brother’s keeper?”"),
    ("gen5", "Genesis", 5, "Ten generations, one drumbeat — and the one man who never dies."),
    ("gen6", "Genesis", 6, "The sons of God, the Nephilim, the LORD’s regret, and the ark."),
    ("gen7", "Genesis", 7, "The flood: creation run in reverse, and “the LORD shut him in.”"),
    ("gen8", "Genesis", 8, "God remembers Noah — the raven, the dove, and the first altar."),
    ("gen9", "Genesis", 9, "Meat and blood, the first law, and the bow hung in the clouds."),
    ("gen10", "Genesis", 10, "The Table of Nations: the whole known world, drawn as one family tree."),
    ("gen11", "Genesis", 11, "Babel and babble — and the quiet road to Ur."),
    ("gen12", "Genesis", 12, "Lekh lekha: the call of Abram, and Egypt as the Exodus in miniature."),
    ("gen13", "Genesis", 13, "Abram and Lot part ways — the land too small for both, and the Hebrew word for “separate” that decides everything."),
    ("john1", "John", 1, "The Word made flesh — the Prologue and its “was God / a god,” the Lamb of God, and the first disciples."),
]
NEXT_UP = "Genesis 14"         # (legacy; nav is now book-scoped in nav_strip)
TOTAL_BIBLE_CHAPTERS = 1189

BOOKS_OT = [("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
    ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
    ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
    ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
    ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
    ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4)]
BOOKS_NT = [("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
    ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
    ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
    ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6),
    ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
    ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
    ("3 John", 1), ("Jude", 1), ("Revelation", 22)]

# --- book-aware helpers (multi-book support) -------------------------------
# The site began Genesis-only; these let a second book (John, …) coexist without
# breaking the live genesis-N.html URLs. A library ref is (ch, v) for Genesis
# (back-compat) or (book, ch, v) for any book; `_ref` normalizes to (book, ch, v).
BOOK_TOTAL = {name: n for name, n in BOOKS_OT + BOOKS_NT}
_NT_BOOKS = {name for name, _ in BOOKS_NT}
_BOOK_ABBR = {"Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
              "Deuteronomy": "Deut", "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke",
              "John": "John", "Acts": "Acts", "Romans": "Rom", "Revelation": "Rev"}


def book_slug(book):
    """URL slug for a book: 'Genesis' -> 'genesis', '1 John' -> '1-john'."""
    return book.lower().replace(" ", "-")


def chapter_filename(book, ch):
    return f"{book_slug(book)}-{ch}.html"


def book_abbr(book):
    return _BOOK_ABBR.get(book, book)


def _is_nt(book):
    return book in _NT_BOOKS


def _ref(r):
    """Normalize a library ref: (ch, v) -> Genesis; (book, ch, v) -> that book."""
    return (r[0], r[1], r[2]) if len(r) == 3 else ("Genesis", r[0], r[1])


# Normalize library-data refs to (book, ch, v) once, at load, so every consumer
# below unpacks a uniform triple. Genesis entries keep their bare (ch, v) tuples
# in library_data.py and normalize here to book="Genesis".
for _e in ENCYCLOPEDIA:
    _e["refs"] = [_ref(r) for r in _e["refs"]]
XREFS_N = [(_ref(a), _ref(b), why) for (a, b, why) in XREFS]


FAVICON = ("data:image/svg+xml," + html.escape(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 46 46'>"
    "<circle cx='23' cy='23' r='22.5' fill='#0b1929'/>"
    "<rect x='9' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='33.4' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='12.6' y='14.5' width='20.8' height='17' fill='#efe6cf'/>"
    "<path d='M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z' fill='#e8c968'/></svg>", quote=True))

SCROLL_SVG = """<svg class="mtlib-icon" viewBox="0 0 46 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="23" cy="23" r="22.5" fill="#0b1929"/>
  <circle cx="23" cy="23" r="22.5" fill="none" stroke="#e8c968" stroke-width="0.7" opacity="0.4"/>
  <rect x="9" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="33.4" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="12.6" y="14.5" width="20.8" height="17" fill="#efe6cf"/>
  <g stroke="#8a7ab0" stroke-width="1.1" stroke-linecap="round">
    <line x1="15.5" y1="19" x2="30.5" y2="19"/>
    <line x1="15.5" y1="23" x2="30.5" y2="23"/>
    <line x1="15.5" y1="27" x2="26.5" y2="27"/>
  </g>
  <path d="M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z" fill="#e8c968"/>
</svg>"""


def header(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    return f"""<header class="site-head">
  <a class="brand" href="index.html">
    {SCROLL_SVG}
    <span class="brand-name">The Mister<span class="lib">Librarian</span> Bible Project</span>
  </a>
  <div class="rule"></div>
  <div class="tag">{TAGLINE}</div>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Home</a>
    <a href="toc.html"{cls('toc')}>Table of Contents</a>
    <a href="reading.html"{cls('reading')}>📗 My Reading</a>
    <a href="library.html"{cls('library')}>📚 Library</a>
    <a href="ask-enoch.html"{cls('ask')}>Ask Mr. Librarian</a>
    <a href="contact.html"{cls('contact')}>✉️ Ask a Question</a>
    <a href="about.html"{cls('about')}>About</a>
  </nav>
</header>"""


FOOTER = """<footer class="site-foot">
  <p>The MisterLibrarian Bible Project — a fresh translation of the Bible into modern English, made from
  the original Hebrew (the Masoretic Text) one chapter at a time, with translator's notes comparing every
  choice against seven landmark versions. Kept by Mr. Librarian; translated with Claude.</p>
  <p><a href="toc.html">Table of Contents</a> · <a href="reading.html">My Reading</a> · <a href="library.html">Library</a> · <a href="contact.html">Ask Mr. Librarian a question</a> · <a href="about.html">About the project</a></p>
</footer>"""


def _goatcounter_script():
    """Sitewide, cookie-less visit tracking (GoatCounter) injected into every page's <head>.
    No-op until GOATCOUNTER_CODE is set above."""
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


def _stats_box():
    """Live 'Site Traffic' box for the About page — fetches GoatCounter's public,
    unauthenticated site-wide TOTAL counter JSON and renders it client-side (no iframe,
    no GoatCounter branding). NB: GoatCounter's counter endpoints return HTTP 404 for a
    thin/zero-data path even though the JSON body is still valid — so this deliberately
    parses the body regardless of status code, and only hides the box if the fetch itself
    fails outright (network error, ad-blocker, or not yet configured) or the body is
    unparseable. Learned the hard way: an earlier version checked response.ok first, which
    made the box silently vanish on every load."""
    if not GOATCOUNTER_CODE:
        return ""
    return f"""<div class="panel statsbox" id="statsbox">
  <div class="stats-label">\U0001F4CA Site Traffic</div>
  <div class="stats-num" id="statsNum">\u2014</div>
  <div class="stats-sub">site visits, all-time \u00b7 tracked anonymously via
  <a href="https://www.goatcounter.com" rel="noopener">GoatCounter</a> \u2014 no cookies, no personal
  data, nothing sold</div>
</div>
<script>
(function(){{
  fetch("https://{GOATCOUNTER_CODE}.goatcounter.com/counter/TOTAL.json")
    .then(function(r){{ return r.json(); }})
    .then(function(d){{
      var el = document.getElementById("statsNum");
      if (el && d && d.count) el.textContent = d.count;
      else {{ var b = document.getElementById("statsbox"); if (b) b.style.display = "none"; }}
    }})
    .catch(function(){{
      var b = document.getElementById("statsbox");
      if (b) b.style.display = "none";
    }});
}})();
</script>"""


def page(title, body, active="", desc=""):
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}
<link rel="icon" href="{FAVICON}"/>
<link rel="stylesheet" href="style.css?v={CSS_VER}"/>{_goatcounter_script()}
</head>
<body>
<div class="wrap">
{header(active)}
<script src="reading.js"></script>
<script src="player-clips.js?v={JS_VER}"></script>
<script src="audio-reader.js?v={AUDIO_JS_VER}"></script>
<script src="https://www.youtube.com/iframe_api"></script>
{body}
{FOOTER}
</div>
</body>
</html>
"""


def extract_source(source_path):
    src = open(source_path, encoding="utf-8").read()
    chapters = {}
    for slug, _, _, _ in CHAPTERS:
        m = re.search(
            r'<div class="chapter-panel[^"]*" id="chapter-%s">(.*?)</div><!-- /chapter-%s -->'
            % (slug, slug), src, re.S)
        if not m:
            raise SystemExit(f"chapter panel {slug} not found in source")
        chapters[slug] = m.group(1).strip()
    return chapters


def clean_chapter(content):
    # In-page chapter-switch links (showChapter) -> real chapter-page links; the nav strip covers movement.
    slug_to_file = {slug: chapter_filename(book, num) for slug, book, num, _ in CHAPTERS}
    content = re.sub(
        r'<a href="#" onclick="showChapter\(\'([a-z0-9]+)\'[^"]*"[^>]*>([^<]+)</a>',
        lambda m: f'<a href="{slug_to_file.get(m.group(1), "toc.html")}">{m.group(2)}</a>', content)
    return content


# ---------------------------------------------------------------- library ---

def verse_anchor(ch, v):
    """Anchor id used in the source markup: chapter 1 is bare vN, others vCH-N."""
    return f"v{v}" if ch == 1 else f"v{ch}-{v}"


def verse_url(book, ch, v):
    return f"{chapter_filename(book, ch)}#{verse_anchor(ch, v)}"


_YT_ID_RE = re.compile(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})")


def youtube_embed(url, title):
    """A responsive, privacy-enhanced YouTube embed (falls back to a plain link if the id can't be parsed)."""
    m = _YT_ID_RE.search(url)
    if not m:
        return f'<p><a href="{html.escape(url, quote=True)}" rel="noopener">▶ {html.escape(title)}</a></p>'
    vid = m.group(1)
    return f"""<div class="vembed">
  <div class="vembed-frame">
    <iframe src="https://www.youtube-nocookie.com/embed/{vid}"
      title="{html.escape(title, quote=True)}" loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  </div>
  <div class="vembed-title">{html.escape(title)}</div>
</div>"""


def _atlas_zoom(span):
    """Rough OSM zoom level for a "view larger map" link, derived from the bbox span
    in degrees (a tight excavated-site span -> high zoom; a broad region -> low)."""
    z = round(9 - math.log2(max(span, 0.02)))
    return max(3, min(17, z))


def osm_embed(lat, lon, span, label, caption=None):
    """A key-less, officially-supported OpenStreetMap embed (no Google API/billing
    needed for a static site) centered on (lat, lon), with a bbox span_degrees wide.

    `caption` (already-escaped HTML) renders directly under the map frame, above the
    "view larger" link — the readable-English fix for OSM's Middle East labels, which
    are mostly Arabic-script only with no `name:en` fallback for anything but a
    handful of major cities."""
    half = span / 2.0
    bbox = f"{lon - half:.4f},{lat - half:.4f},{lon + half:.4f},{lat + half:.4f}"
    marker = f"{lat:.4f},{lon:.4f}"
    zoom = _atlas_zoom(span)
    view_url = f"https://www.openstreetmap.org/?mlat={lat:.4f}&mlon={lon:.4f}#map={zoom}/{lat:.4f}/{lon:.4f}"
    cap_html = f'<div class="atlas-caption">{caption}</div>' if caption else ""
    return f"""<div class="mapembed">
  <div class="mapembed-frame">
    <iframe src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={marker}"
      title="{html.escape(label, quote=True)}" loading="lazy"></iframe>
  </div>
  {cap_html}
  <div class="mapembed-link"><a href="{view_url}" rel="noopener">View larger map on OpenStreetMap →</a></div>
</div>"""


def _build_alias_index():
    """alias word/phrase -> [entry, ...] candidate encyclopedia entries."""
    index = defaultdict(list)
    for e in ENCYCLOPEDIA:
        for alias in e.get("aliases", [e["name"]]):
            index[alias].append(e)
    return index


_ALIAS_INDEX = _build_alias_index()
_ALIAS_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(w) for w in
                       sorted(_ALIAS_INDEX, key=len, reverse=True)) + r')\b')
def _norm_override(o):
    # (ch, v, word, idx, slug) -> Genesis; (book, ch, v, word, idx, slug) -> that book.
    if len(o) == 6:
        b, ch, v, w, i, s = o
        return (b, ch, v, w, i), s
    ch, v, w, i, s = o
    return ("Genesis", ch, v, w, i), s


_OVERRIDE_MAP = dict(_norm_override(o) for o in LINK_OVERRIDES)
_SLUG_TO_ENTRY = {e["slug"]: e for e in ENCYCLOPEDIA}
_VERSE_ENG_BLOCK = re.compile(
    r'(id="(v(?:\d+-)?\d+)"[^>]*>.*?<div class="eng">)(.*?)(</div>)', re.S)


def inject_encyclopedia_links(content, book, ch):
    """Turn the first mention per chapter of each ENCYCLOPEDIA entry (by its
    `name` or any `aliases`) into a link to its encyclopedia.html entry.

    Only ENCYCLOPEDIA entries are linked, never DICTIONARY terms (those are
    Hebrew concept-words whose English rendering varies verse to verse, so a
    literal-string match on them would be unreliable). Resolution order for
    a matched word: (1) an explicit LINK_OVERRIDES pin for this exact
    (chapter, verse, word, occurrence-within-verse); (2) if only one entry
    claims that word at all, use it; (3) if several entries share the word
    (e.g. "Haran" the man and "Haran" the city), prefer whichever one's own
    `refs` list already includes this verse. Anything still unresolved is
    left as plain text rather than guessed at. Each entry links only once
    per chapter — later mentions in the same chapter stay plain, so the
    first sighting of "Eden" carries the link and the page isn't peppered
    with repeats of the same one.
    """
    linked_slugs = set()

    def verse_block(m):
        prefix, vid, eng_html, suffix = m.group(1), m.group(2), m.group(3), m.group(4)
        vnum = int(vid.rsplit("-", 1)[-1] if "-" in vid else vid[1:])
        seen_in_verse = defaultdict(int)

        def word_match(wm):
            word = wm.group(1)
            seen_in_verse[word] += 1
            occurrence = seen_in_verse[word]
            # Only entities that actually appear in THIS book are eligible, so a
            # Genesis entry can never link inside John (or vice versa).
            candidates = [c for c in _ALIAS_INDEX[word]
                          if any(rb == book for (rb, rc, rv) in c["refs"])]
            slug = _OVERRIDE_MAP.get((book, ch, vnum, word, occurrence))
            if slug is None:
                if len(candidates) == 1:
                    slug = candidates[0]["slug"]
                else:
                    ref_hits = [c["slug"] for c in candidates if (book, ch, vnum) in c["refs"]]
                    slug = ref_hits[0] if len(ref_hits) == 1 else None
            if slug is None or slug in linked_slugs:
                return word
            linked_slugs.add(slug)
            name = html.escape(_SLUG_TO_ENTRY[slug]["name"], quote=True)
            return (f'<a class="eterm" href="encyclopedia.html#{slug}" '
                    f'title="{name} — see the Encyclopedia">{word}</a>')

        return prefix + _ALIAS_PATTERN.sub(word_match, eng_html) + suffix

    return _VERSE_ENG_BLOCK.sub(verse_block, content)


def inject_xrefs(content, book, ch):
    """Append ⤷ cross-reference chips inside each verse block this (book, ch) owns.
    Same-book targets show a bare `12:2` chip (unchanged from the Genesis-only era);
    cross-book targets show a `Gen 1:1` / `John 1:1` chip so the link is unambiguous."""
    by_verse = defaultdict(list)   # verse in THIS chapter -> [((tbook, tch, tv), why), ...]
    for (ab, ac, av), (bb, bc, bv), why in XREFS_N:
        if ab == book and ac == ch:
            by_verse[av].append(((bb, bc, bv), why))
        if bb == book and bc == ch:
            by_verse[bv].append(((ab, ac, av), why))
    for v, links in sorted(by_verse.items()):
        anchor = verse_anchor(ch, v)
        marker = f'id="{anchor}"'
        i = content.find(marker)
        if i < 0:
            continue
        # the verse block closes with the first '</div></div>' after its id
        j = content.find("</div></div>", i)
        if j < 0:
            continue
        chips = ""
        for (tb, tc, tv), why in links:
            lbl = f"{tc}:{tv}" if tb == book else f"{book_abbr(tb)} {tc}:{tv}"
            chips += (f'<a class="xref" href="{verse_url(tb, tc, tv)}" '
                      f'title="{html.escape(why, quote=True)}">⤷ {lbl}</a>')
        block = f'<div class="xrefs"><span class="xr-label">cross-refs</span>{chips}</div>'
        content = content[:j] + block + content[j:]
    return content


# A video clip is authored right AFTER the verse it belongs to
# (<div class="vclip"> immediately following the verse's closing </div>). Left
# there it renders BELOW that verse's divider line, so a reader mistakes it for
# the next verse's clip. This pulls each clip INSIDE the verse it follows — just
# before the verse-closing </div>, after any cross-ref chips — so it sits above
# the divider and clearly belongs to the verse above it. Runs for every chapter,
# so clips can keep being authored the simple way.
_CLIP_INTO_VERSE = re.compile(r'</div>\s*(<div class="vclip"[^>]*></div>)')


def move_clips_into_verses(content):
    return _CLIP_INTO_VERSE.sub(lambda m: m.group(1) + "</div>", content)


_STOPWORDS = set("""
a an and are as at be but by for from he her him his i in into is it its let me my not of on or our
so that the their them then there they this to was we were will with you your all any because if
when who whom whose what which shall may your yours out up down over under after before again very
came come go went said says do did done had has have how than too these those upon them one two
""".split())


def extract_verses_english(chapters):
    """Return [(book, ch, v, plain_english_text), ...] for every verse in every chapter."""
    rows = []
    for slug, book, num, _ in CHAPTERS:
        content = chapters[slug]
        for m in re.finditer(
                r'id="(v(?:\d+-)?\d+)".*?<div class="eng">(.*?)</div>', content, re.S):
            anchor, eng = m.group(1), m.group(2)
            vnum = int(anchor.rsplit("-", 1)[-1] if "-" in anchor else anchor[1:])
            text = re.sub(r"<[^>]+>", " ", eng)
            text = html.unescape(text)
            text = re.sub(r"\s*note\s*$", "", text.strip())
            text = re.sub(r"\s+", " ", text)
            rows.append((book, num, vnum, text))
    return rows


def build_concordance(chapters):
    rows = extract_verses_english(chapters)
    index = defaultdict(list)          # word -> [(book, ch, v), ...]
    for book, ch, v, text in rows:
        seen = set()
        for raw in re.findall(r"[A-Za-z][A-Za-z'’\-]*", text):
            w = raw.lower().strip("'’-")
            if len(w) < 3 or w in _STOPWORDS or w in seen:
                continue
            seen.add(w)
            index[w].append((book, ch, v))
    words = sorted(index.keys())
    total_refs = sum(len(vs) for vs in index.values())

    letters = sorted({w[0].upper() for w in words})
    jump = " ".join(f'<a href="#L{L}">{L}</a>' for L in letters)
    sections = []
    cur = None
    for w in words:
        L = w[0].upper()
        if L != cur:
            if cur is not None:
                sections.append("</div>")
            sections.append(f'<h2 id="L{L}">{L}</h2><div class="panel conc">')
            cur = L
        refs = index[w]
        links = " ".join(
            f'<a href="{verse_url(b, c, v)}">{book_abbr(b)} {c}:{v}</a>' for b, c, v in refs)
        sections.append(
            f'<div class="cw"><span class="cw-w">{html.escape(w)}</span>'
            f'<span class="cw-n">×{len(refs)}</span>'
            f'<span class="cw-refs">{links}</span></div>')
    if cur is not None:
        sections.append("</div>")

    body = f"""<h1 class="pagetitle">🔠 Concordance</h1>
<p class="lede">Every significant English word in the translation so far, with every verse it appears in —
<strong>{len(words)} words, {total_refs} occurrences, generated automatically from the translation text
itself</strong> each time a chapter is added (common function words are skipped). Because it indexes THIS
translation, it reflects this project's actual renderings: look up <em>vault</em>, not <em>firmament</em>.</p>
<p class="lede jump">Jump to: {jump}</p>
{''.join(sections)}"""
    out = page(f"Concordance — {SITE_NAME}", body, active="library",
               desc="Auto-generated concordance of the MisterLibrarian translation — every significant "
                    "word, every verse, rebuilt as each chapter is added.")
    open(os.path.join(OUT, "concordance.html"), "w", encoding="utf-8").write(out)
    return len(words), total_refs


def build_dictionary():
    entries = sorted(DICTIONARY, key=lambda e: e[1].lower())
    items = []
    for slug, term, orig, translit, gloss, ref in entries:
        book, ch, v = _ref(ref)
        script_cls = "dgreek" if _is_nt(book) else "dheb"   # Greek renders LTR, Hebrew RTL
        items.append(f"""<div class="dentry" id="{slug}">
  <div class="dhead"><span class="dterm">{html.escape(term)}</span>
    <span class="{script_cls}">{orig}</span> <span class="dtr">{html.escape(translit)}</span></div>
  <p>{gloss} <a class="dref" href="{verse_url(book, ch, v)}">→ first discussed at {book_abbr(book)} {ch}:{v}</a></p>
</div>""")
    body = f"""<h1 class="pagetitle">📖 Dictionary</h1>
<p class="lede">The original-language words this translation has met so far — Hebrew for the Tanakh, Greek for
the New Testament — <strong>{len(entries)} terms</strong>, each added the chapter its translator's note first
discussed it, with a link back to that discussion. This is a reader's glossary of the actual working
vocabulary, not an abridged lexicon.</p>
<div class="panel dict">
{''.join(items)}
</div>"""
    out = page(f"Dictionary — {SITE_NAME}", body, active="library",
               desc="A growing dictionary of the Hebrew terms behind the MisterLibrarian translation, "
                    "added chapter by chapter.")
    open(os.path.join(OUT, "dictionary.html"), "w", encoding="utf-8").write(out)
    return len(entries)


def build_encyclopedia():
    places = [e for e in ENCYCLOPEDIA if e["kind"] == "place"]
    people = [e for e in ENCYCLOPEDIA if e["kind"] in ("person", "people")]

    def render(entries):
        out = []
        for e in sorted(entries, key=lambda x: x["name"].lower()):
            refs = " ".join(f'<a href="{verse_url(b, c, v)}">{book_abbr(b)} {c}:{v}</a>' for b, c, v in e["refs"])
            if e.get("videos"):
                vids = "".join(youtube_embed(u, t) for t, u in e["videos"])
            else:
                vids = ('<div class="evids-empty">▶ No films on the shelf yet — archaeology and '
                        'geography videos get added here as Mr. Librarian finds good ones.</div>')
            out.append(f"""<div class="eentry" id="{e['slug']}">
  <div class="ehead">{html.escape(e['name'])}</div>
  <p>{e['desc']}</p>
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {vids}
</div>""")
        return "".join(out)

    credit_html = ""
    for c in VIDEO_CREDITS:
        credit_html += f"""<div class="vcredit">
  <div class="vcredit-h">🎥 Video source: <a href="{html.escape(c['url'], quote=True)}" rel="noopener">{html.escape(c['channel'])}</a>, {html.escape(c['person'])}</div>
  <p>{c['blurb']}</p>
</div>"""

    queue_rows = "".join(
        f"""<div class="qrow"><div class="qrow-t"><a href="{html.escape(u, quote=True)}" rel="noopener">▶ {html.escape(t)}</a></div>
  <div class="qrow-target">→ {html.escape(target)}</div>
  <div class="qrow-note">{html.escape(note)}</div></div>"""
        for t, u, target, note in VIDEO_QUEUE)
    queue_section = ""
    if VIDEO_QUEUE:
        queue_section = f"""<h2>🎬 Coming to the encyclopedia</h2>
<p class="lede">Videos already found and credited to Expedition Bible, waiting for the translation to
reach the book or chapter they belong to — logged here so nothing gets lost between now and then.</p>
<div class="panel qlist">{queue_rows}</div>"""

    body = f"""<h1 class="pagetitle">🏺 Encyclopedia</h1>
<p class="lede">The people and places the translation has reached — <strong>{len(places)} places,
{len(people)} people</strong> — each entry linked to every verse where it appears, with a growing film
shelf of archaeology and geography footage embedded directly on the entries they illuminate.</p>

{credit_html}

<h2>Places</h2>
<div class="panel ency">{render(places)}</div>

<h2>People</h2>
<div class="panel ency">{render(people)}</div>

{queue_section}"""
    out = page(f"Encyclopedia — {SITE_NAME}", body, active="library",
               desc="People and places of the MisterLibrarian translation — every entry verse-linked, "
                    "with embedded archaeology videos credited to Expedition Bible.")
    open(os.path.join(OUT, "encyclopedia.html"), "w", encoding="utf-8").write(out)
    return len(places), len(people)


def build_atlas():
    """One page, organized chapter-by-chapter (not place-by-place like the
    encyclopedia) so a chapter's Atlas toggle can jump straight to `atlas.html#genesis-N`.
    Reuses ENCYCLOPEDIA's existing (chapter, verse) refs — no new authoring needed to
    know which places belong to which chapter."""
    places = [e for e in ENCYCLOPEDIA if e["kind"] == "place"]
    n_mapped = sum(1 for e in places if e.get("coords"))

    by_chapter = defaultdict(dict)  # (book, chapter num) -> {slug: first_verse}
    for e in places:
        for b, c, v in e["refs"]:
            key = (b, c)
            if e["slug"] not in by_chapter[key] or v < by_chapter[key][e["slug"]]:
                by_chapter[key][e["slug"]] = v

    sections = []
    for slug, book, num, teaser in CHAPTERS:
        entries = sorted(by_chapter.get((book, num), {}).items(), key=lambda kv: kv[1])
        if entries:
            place_html = []
            for pslug, _first_v in entries:
                e = _SLUG_TO_ENTRY[pslug]
                refs = " ".join(f'<a href="{verse_url(b, c, v)}">{book_abbr(b)} {c}:{v}</a>' for b, c, v in e["refs"])
                if e.get("coords"):
                    lat, lon, span = e["coords"]
                    badge = ' <span class="atlas-approx">approximate</span>' if e.get("approx") else ""
                    caption = f'📍 <strong>{html.escape(e["name"])}</strong>'
                    if e.get("modern"):
                        caption += f' — modern-day {html.escape(e["modern"])}'
                    map_html = osm_embed(lat, lon, span, e["name"], caption=caption)
                else:
                    badge = ""
                    map_html = ('<div class="atlas-nomap">📍 No fixed point plotted — the location is genuinely '
                                "undetermined (see the note above), so this shows no guessed pin.</div>")
                place_html.append(f"""<div class="atlas-place" id="atlas-{e['slug']}">
  <div class="atlas-place-h"><a href="encyclopedia.html#{e['slug']}">{html.escape(e['name'])}</a>{badge}</div>
  <p>{e['desc']}</p>
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {map_html}
  <div class="atlas-overlay-empty">🗺️ No ancient-world overlay on the shelf yet for this site — a period map
  showing how the region actually looked in the biblical world gets added here as Mr. Librarian curates one,
  the same way the encyclopedia's film shelf grows.</div>
</div>""")
            body_html = "".join(place_html)
        else:
            body_html = '<div class="atlas-empty">No places are named in this chapter yet — nothing to map.</div>'
        sections.append(f"""<div class="atlas-chapter" id="{book_slug(book)}-{num}">
  <div class="atlas-chhead"><a href="{chapter_filename(book, num)}">{book} {num}</a>
    <span class="atlas-chteaser">{html.escape(teaser)}</span></div>
  {body_html}
</div>""")

    body = f"""<h1 class="pagetitle">🗺️ Atlas</h1>
<p class="lede">Every place the translation has named so far, mapped chapter by chapter —
<strong>{n_mapped} of {len(places)} places</strong> located on a live map (a handful are genuinely debated or
unidentified, and say so rather than guess a pin). Jump here straight from any chapter's toggle bar, or browse
chapter by chapter below. Where Expedition Bible's Joel Kramer stakes out a specific site — Eden and Havilah via
the Pishon, Sodom and Gomorrah at Tall el-Hammam — that identification is the one plotted, credited in the
place's own note. An <strong>ancient-world overlay</strong> — how each region actually looked in the biblical
world, not just today — is a shelf still being built; it starts empty and fills in as real sources are curated,
the same honest way the encyclopedia's film shelf grows.</p>

{''.join(sections)}"""
    out = page(f"Atlas — {SITE_NAME}", body, active="library",
               desc="A chapter-by-chapter atlas of the MisterLibrarian Bible Project — every named place mapped, "
                    "with an ancient-world overlay shelf still growing.")
    open(os.path.join(OUT, "atlas.html"), "w", encoding="utf-8").write(out)
    return n_mapped, len(places)


def build_library(stats):
    n_words, n_refs, n_dict, n_places, n_people, n_xrefs, n_mapped, n_atlas_places = stats
    body = f"""<h1 class="pagetitle">📚 The Library</h1>
<p class="lede">The reference room of the project — every shelf grows automatically or by hand as each
chapter is translated, so the library is always exactly as deep as the translation itself.</p>

<div class="cardgrid">
  <a class="card" href="concordance.html"><div class="card-t">🔠 Concordance</div>
  <div class="card-d">{n_words} words · {n_refs} occurrences — every significant English word in the
  translation, indexed to every verse. Generated automatically from the text at every build.</div></a>
  <a class="card" href="dictionary.html"><div class="card-t">📖 Dictionary</div>
  <div class="card-d">{n_dict} Hebrew terms — the working vocabulary behind the translation, each linked
  to the note that first discussed it.</div></a>
  <a class="card" href="encyclopedia.html"><div class="card-t">🏺 Encyclopedia</div>
  <div class="card-d">{n_places} places · {n_people} people — verse-linked entries, with a film shelf on
  every place for archaeology &amp; geography videos.</div></a>
  <a class="card" href="atlas.html"><div class="card-t">🗺️ Atlas</div>
  <div class="card-d">{n_mapped} of {n_atlas_places} places mapped so far, chapter by chapter — a live map
  for every located site, with an ancient-world overlay shelf still growing.</div></a>
</div>

<h2>Cross-references</h2>
<div class="panel prose">
  <p><strong>{n_xrefs} connections and counting.</strong> The translator's notes keep catching the text
  quoting itself — the naked/crafty pun across the Genesis 2/3 break, "desire and mastery" recurring from
  Eve to Cain, Babel's grasped-at name answered by Abram's given one. Each of those connections is now a
  live link: look for the <span class="xref" style="cursor:default">⤷ 11:4</span> chips under verses on
  the chapter pages — every link runs both directions, and hovering shows why the two verses are
  connected. New chains are added as each chapter lands.</p>
</div>

<h2>Where this library is heading</h2>
<div class="panel prose">
  <p><strong>🔴 Red letters.</strong> When this project reaches the Gospels, the words of Jesus will be
  set in red — the plan is declared now so the convention is ready the day Matthew begins. (The Hebrew
  Bible's direct divine speech stays in ordinary type, as in nearly all red-letter editions.)</p>
  <p><strong>▶ The film shelf.</strong> Every place entry in the encyclopedia has a slot for curated
  archaeology and geography videos — excavations, site walk-throughs, museum pieces. Mr. Librarian
  curates; the encyclopedia is where they live.</p>
  <p><strong>🗺️ Ancient-world overlays.</strong> The atlas's live maps show where these places sit today;
  a period-accurate overlay — cities, kingdoms, and borders as they stood in the biblical world — is the
  next layer, added site by site as real sources are found rather than guessed at.</p>
  <p><strong>⤷ Deeper cross-references.</strong> As the translation grows, the chains multiply — and
  once multiple books exist, they'll connect across books the way study Bibles do, but built only from
  connections this project's own notes have actually argued for.</p>
  <p><strong>🔠 A Hebrew concordance.</strong> The current concordance indexes the English; a
  Hebrew-side index (every occurrence of <em>nefesh</em>, every <em>toldot</em>) is the natural next
  shelf.</p>
</div>"""
    out = page(f"Library — {SITE_NAME}", body, active="library",
               desc="The reference room of the MisterLibrarian Bible Project: concordance, dictionary, "
                    "encyclopedia, and cross-references — all growing with the translation.")
    open(os.path.join(OUT, "library.html"), "w", encoding="utf-8").write(out)


def nav_strip(book, num, position):
    """Book-scoped prev/next: chain within the SAME book. At a book's first
    published chapter, an NT book links back to the New Testament intro; at its
    last published chapter, show the next chapter of that book as coming-soon."""
    same = sorted(n for (_s, b, n, _t) in CHAPTERS if b == book)
    i = same.index(num)
    prev_html = ""
    if i > 0:
        prev_html = f'<a href="{chapter_filename(book, same[i - 1])}">◄ {book} {same[i - 1]}</a>'
    elif _is_nt(book):
        prev_html = '<a href="new-testament.html">◄ New Testament</a>'
    if i < len(same) - 1:
        next_html = f'<a href="{chapter_filename(book, same[i + 1])}">{book} {same[i + 1]} ►</a>'
    elif num < BOOK_TOTAL.get(book, num):
        next_html = f'<span class="dis">{book} {num + 1} (coming soon)</span>'
    else:
        next_html = ""
    return (f'<div class="chnav {position}"><div class="side left">{prev_html}</div>'
            f'<div class="mid"><a href="toc.html">\U0001F4DC Table of Contents</a></div>'
            f'<div class="side right">{next_html}</div></div>')


def build_chapter_pages(chapters):
    for slug, book, num, teaser in CHAPTERS:
        content = clean_chapter(chapters[slug])
        content = inject_encyclopedia_links(content, book, num)
        content = inject_xrefs(content, book, num)
        content = move_clips_into_verses(content)
        orig_lang = "Greek" if _is_nt(book) else "Hebrew"   # the Hide-original toggle label
        # A pre-generated narration MP3 (audio/<book>-N.mp3) is preferred when
        # present; otherwise the Listen button reads the page aloud in the
        # browser. gen_audio.py produces those files.
        mp3_rel = f"audio/{book_slug(book)}-{num}.mp3"
        audio_attr = f' data-audio="{mp3_rel}"' if os.path.exists(os.path.join(OUT, mp3_rel)) else ""
        toggle = (f'<div class="togglebar">'
                  f'<button class="tgl tgl-read" id="readtgl">Mark as read</button>'
                  f'<div class="tgl-group">'
                  f'<button class="tgl tgl-audio" id="audiotgl"{audio_attr}>🔊 Listen</button>'
                  f'<button class="tgl" id="hebtgl" onclick="toggleHeb()">Hide {orig_lang}</button>'
                  f'<a class="tgl" href="atlas.html#{book_slug(book)}-{num}">🗺️ Atlas</a>'
                  f'</div>'
                  f'</div>')
        body = f"""{nav_strip(book, num, 'top')}
{toggle}
<article class="chapter">
{content}
</article>
{nav_strip(book, num, 'bottom')}
<script>
function toggleHeb(){{
  var hidden = document.body.classList.toggle("hide-heb");
  document.getElementById("hebtgl").textContent = hidden ? "Show {orig_lang}" : "Hide {orig_lang}";
  try{{ localStorage.setItem("mtlib_hideheb", hidden ? "1" : "0"); }}catch(e){{}}
}}
(function(){{ try{{
  if (localStorage.getItem("mtlib_hideheb") === "1"){{
    document.body.classList.add("hide-heb");
    document.getElementById("hebtgl").textContent = "Show {orig_lang}";
  }}
}}catch(e){{}} }})();
(function(){{
  var slug = "{slug}";
  var btn = document.getElementById("readtgl");
  function render(){{
    var isRead = !!mtlibGetRead()[slug];
    btn.textContent = isRead ? "\\u2713 Read" : "Mark as read";
    btn.classList.toggle("done", isRead);
  }}
  btn.addEventListener("click", function(){{
    mtlibSetRead(slug, !mtlibGetRead()[slug]);
    render();
  }});
  render();
}})();
</script>"""
        src = "the Greek (the critical Greek New Testament)" if _is_nt(book) else "the Hebrew (Masoretic Text)"
        desc = (f"{book} {num} translated fresh from {src}, with verse-by-verse "
                f"notes comparing NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and "
                f"NWT. {teaser}")
        out = page(f"{book} {num} — {SITE_NAME}", body, desc=desc)
        open(os.path.join(OUT, chapter_filename(book, num)), "w", encoding="utf-8").write(out)


def build_toc():
    done = len(CHAPTERS)
    pct = round(done / TOTAL_BIBLE_CHAPTERS * 1000) / 10

    pub = defaultdict(set)          # book -> {published chapter numbers}
    book_seen = []                  # books with published chapters, first-seen order
    for _s, book, num, _t in CHAPTERS:
        if book not in pub:
            book_seen.append(book)
        pub[book].add(num)

    def book_chip(name, n):
        if name in pub:
            return f'<span class="book book-active">{name} <b>{len(pub[name])}/{n}</b></span>'
        return f'<span class="book">{name} <i>{n}</i></span>'
    ot = "".join(book_chip(n, c) for n, c in BOOKS_OT)
    nt = "".join(book_chip(n, c) for n, c in BOOKS_NT)
    rows = "".join(
        f'<a class="chrow" href="{chapter_filename(book, num)}"><span class="chrow-n">{book} {num}</span>'
        f'<span class="chrow-t">{teaser}</span></a>'
        for _, book, num, teaser in CHAPTERS)

    # a "Now Reading" chip grid for each in-progress book
    now_reading = []
    for book in book_seen:
        total = BOOK_TOTAL.get(book, max(pub[book]))
        chips = "".join(
            (f'<a class="chch chch-done" href="{chapter_filename(book, i)}">{i}</a>'
             if i in pub[book] else f'<span class="chch">{i}</span>')
            for i in range(1, total + 1))
        now_reading.append(f'''<h2>Now Reading — {book}</h2>
<div class="panel">
  <div class="now-reading"><span class="nr-badge">In Progress</span>
  <span class="nr-book">{book} · {len(pub[book])} of {total} chapters</span></div>
  <div class="chgrid">{chips}</div>
</div>''')
    now_reading_html = "\n".join(now_reading)
    body = f"""<h1 class="pagetitle">\U0001F4DC Table of Contents</h1>
<p class="lede">Every chapter of the translation, tracked as it's finished. Gold numbers are published
and link to their chapter; everything else is still ahead.</p>

<h2>Progress</h2>
<div class="panel">
  <div class="progress-row">
    <div class="progress-num"><span>{done}</span> of {TOTAL_BIBLE_CHAPTERS} chapters</div>
    <div class="progress-label">{pct}% of the Bible</div>
  </div>
  <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>
</div>

<h2>Published chapters</h2>
<div class="panel chlist">
{rows}
</div>

{now_reading_html}

<h2>All 66 Books</h2>
<div class="panel">
  <div class="testament">Old Testament · 39 books</div>
  <div class="bookgrid">{ot}</div>
  <div class="testament">New Testament · 27 books</div>
  <p class="muted" style="margin:2px 0 12px"><a href="new-testament.html">📜 Introduction to the New Testament — the Greek Scriptures →</a></p>
  <div class="bookgrid">{nt}</div>
</div>"""
    out = page(f"Table of Contents — {SITE_NAME}", body, active="toc",
               desc="Progress tracker for the MisterLibrarian Bible Project: every published chapter of "
                    "the fresh-from-the-Hebrew translation, and everything still ahead.")
    open(os.path.join(OUT, "toc.html"), "w", encoding="utf-8").write(out)


def votd_entries(chapters):
    """Verse-of-the-day candidates, with the actual quote pulled live from the
    translation text (never hand-typed) so it can never drift from the chapter
    page. A candidate referencing a not-yet-published verse is silently
    skipped, so this list is safe to grow ahead of the translation."""
    text_by_ref = {(b, c, v): t for b, c, v, t in extract_verses_english(chapters)}
    entries = []
    for e in VERSE_OF_DAY:
        book, ch, v, blurb = e if len(e) == 4 else ("Genesis", e[0], e[1], e[2])
        text = text_by_ref.get((book, ch, v))
        if not text:
            continue
        entries.append({"ref": f"{book} {ch}:{v}", "text": text, "blurb": blurb,
                         "href": verse_url(book, ch, v)})
    return entries


def build_reading():
    rows = "".join(
        f'<label class="rrow" data-slug="{slug}" data-href="{chapter_filename(book, num)}">'
        f'<input type="checkbox" class="rchk"/>'
        f'<span class="rrow-n">{book} {num}</span>'
        f'<span class="rrow-t">{teaser}</span></label>'
        for slug, book, num, teaser in CHAPTERS)
    body = f"""<h1 class="pagetitle">\U0001F4D7 My Reading</h1>
<p class="lede">Track your own progress through the translation as it's published. Checked chapters are
remembered <strong>only in this browser</strong> — a bit of localStorage, nothing ever sent anywhere, no
account needed. Come back after a new chapter lands and pick up right where you left off. (You can also
check a chapter off directly from its own page, next to the Hide Hebrew toggle.)</p>

<div class="panel" id="continueBox" style="display:none"></div>

<h2>Your progress</h2>
<div class="panel">
  <div class="progress-row">
    <div class="progress-num"><span id="rDone">0</span> of {len(CHAPTERS)} read</div>
    <div class="progress-label" id="rPct">0%</div>
  </div>
  <div class="bar"><div class="bar-fill" id="rBar" style="width:0%"></div></div>
</div>

<h2>Chapters</h2>
<div class="panel chlist rlist">
{rows}
</div>

<p class="muted" style="margin-top:14px;font-size:12px"><a href="#" id="resetLink">Reset my progress</a></p>

<script>
(function(){{
  var rows = document.querySelectorAll(".rrow");
  function render(){{
    var read = mtlibGetRead();
    var done = 0, firstUnread = null;
    rows.forEach(function(r){{
      var slug = r.dataset.slug;
      var chk = r.querySelector(".rchk");
      var isRead = !!read[slug];
      chk.checked = isRead;
      r.classList.toggle("rrow-done", isRead);
      if (isRead) done++;
      else if (!firstUnread) firstUnread = r;
    }});
    var total = rows.length;
    var pct = total ? Math.round(done / total * 100) : 0;
    document.getElementById("rDone").textContent = done;
    document.getElementById("rPct").textContent = pct + "%";
    document.getElementById("rBar").style.width = pct + "%";
    var cbox = document.getElementById("continueBox");
    if (firstUnread){{
      var label = firstUnread.querySelector(".rrow-n").textContent;
      cbox.style.display = "block";
      cbox.innerHTML = '<div class="muted" style="margin-bottom:8px">Continue where you left off</div>' +
        '<a class="btn" href="' + firstUnread.dataset.href + '">Read ' + label + ' \\u2192</a>';
    }} else if (total) {{
      cbox.style.display = "block";
      cbox.innerHTML = '<div class="muted">You\\u2019re caught up \\u2014 every published chapter is ' +
        'read. Come back when the next one lands.</div>';
    }}
  }}
  rows.forEach(function(r){{
    r.querySelector(".rchk").addEventListener("change", function(e){{
      mtlibSetRead(r.dataset.slug, e.target.checked);
      render();
    }});
  }});
  document.getElementById("resetLink").addEventListener("click", function(e){{
    e.preventDefault();
    if (confirm("Reset your reading progress on this device?")){{
      try{{ localStorage.removeItem("mtlib_read"); }}catch(err){{}}
      render();
    }}
  }});
  render();
}})();
</script>"""
    out = page(f"My Reading — {SITE_NAME}", body, active="reading",
               desc="Track your own progress through The MisterLibrarian Bible Project, chapter by "
                    "chapter — kept privately in your browser, no account needed.")
    open(os.path.join(OUT, "reading.html"), "w", encoding="utf-8").write(out)


def build_index(chapters):
    latest = CHAPTERS[-1]
    cards = "".join(
        f'<a class="card" href="{chapter_filename(book, num)}"><div class="card-t">{book} {num}</div>'
        f'<div class="card-d">{teaser}</div></a>'
        for _, book, num, teaser in reversed(CHAPTERS))
    votd_json = json.dumps(votd_entries(chapters), ensure_ascii=False).replace("</", "<\\/")
    ch_json = json.dumps(
        [{"slug": slug, "label": f"{book} {num}", "href": chapter_filename(book, num)}
         for slug, book, num, _ in CHAPTERS])
    body = f"""<section class="hero">
  <h1>A new translation of the Bible,<br/>made one chapter at a time.</h1>
  <p>Welcome. This project translates the Bible into modern English directly from the original Hebrew —
  the Masoretic Text, reproduced verse-by-verse alongside the new rendering so every choice can be checked
  against the source. Beneath each chapter sit <strong>translator's notes, verse by verse</strong>,
  explaining each decision and comparing it against seven landmark versions: the NIV, the KJV, the
  Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the American Standard Version, and the New World
  Translation.</p>
  <p>No verse is smoothed over, no difficulty hidden: where the Hebrew puns, the translation puns or the
  notes confess it can't; where the text is uncertain or the manuscripts disagree, the notes say so plainly.
  The work advances one chapter per sitting — follow along from the beginning, or jump in at the newest
  chapter.</p>
  <div class="hero-cta">
    <a class="btn" href="genesis-1.html">Start at Genesis 1</a>
    <a class="btn btn-2" href="{chapter_filename(latest[1], latest[2])}">Newest: {latest[1]} {latest[2]}</a>
  </div>
</section>

<div class="panel votd" id="votd">
  <div class="votd-label">Verse of the Day · from this translation</div>
  <div class="votd-q" id="votdText">—</div>
  <div class="votd-ref" id="votdRef"></div>
  <div class="votd-blurb" id="votdBlurb"></div>
  <a class="votd-link" id="votdLink" href="#">Read it in context →</a>
</div>

<div class="panel" id="continueBox" style="display:none;margin-top:14px"></div>

<h2>Chapters — newest first</h2>
<div class="cardgrid">
{cards}
</div>

<h2>From the desk</h2>
<div class="cardgrid">
  <a class="card" href="new-testament.html"><div class="card-t">\U0001F4DC The New Testament</div>
  <div class="card-d">Crossing from Hebrew into Greek: the critical text, the manuscript apparatus behind the translation, and the method for the Greek Scriptures.</div></a>
  <a class="card" href="reading.html"><div class="card-t">\U0001F4D7 My Reading</div>
  <div class="card-d">Track your own progress through the translation, chapter by chapter — kept privately in your browser.</div></a>
  <a class="card" href="ask-enoch.html"><div class="card-t">\U0001F4D6 Ask Mr. Librarian</div>
  <div class="card-d">Why isn't the Book of Enoch in this translation? A reader asked; here's the answer.</div></a>
  <a class="card" href="about.html"><div class="card-t">ℹ️ About the project</div>
  <div class="card-d">The method, the seven-version shelf, and what "essentially literal, modern register" means here.</div></a>
</div>

<script>
var MTLIB_VOTD = {votd_json};
var MTLIB_CHAPTERS = {ch_json};
(function(){{
  if (!MTLIB_VOTD.length) return;
  var now = new Date();
  var doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
  var v = MTLIB_VOTD[doy % MTLIB_VOTD.length];
  document.getElementById("votdText").textContent = "\\u201c" + v.text + "\\u201d";
  document.getElementById("votdRef").textContent = "\\u2014 " + v.ref;
  document.getElementById("votdBlurb").textContent = v.blurb;
  document.getElementById("votdLink").href = v.href;
}})();
(function(){{
  var read = mtlibGetRead();
  var done = 0, firstUnread = null;
  MTLIB_CHAPTERS.forEach(function(c){{
    if (read[c.slug]) done++;
    else if (!firstUnread) firstUnread = c;
  }});
  var cbox = document.getElementById("continueBox");
  if (done === 0) return;
  cbox.style.display = "block";
  if (firstUnread){{
    cbox.innerHTML = '<div class="muted" style="margin-bottom:8px">Continue where you left off</div>' +
      '<a class="btn btn-2" href="' + firstUnread.href + '">Read ' + firstUnread.label + ' \\u2192</a>';
  }} else {{
    cbox.innerHTML = '<div class="muted">You\\u2019re caught up on every published chapter \\u2014 nice ' +
      'work. Come back when the next one lands, or revisit your <a href="reading.html">reading progress</a>.</div>';
  }}
}})();
</script>"""
    out = page(SITE_NAME, body, active="home",
               desc="A fresh translation of the Bible into modern English, made from the original Hebrew "
                    "one chapter at a time, with verse-by-verse notes comparing seven landmark versions.")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)


def build_about():
    body = f"""<h1 class="pagetitle">About the project</h1>
<div class="panel prose">
  <p><strong>What this is.</strong> A fresh translation of the Bible into modern English, made one chapter
  at a time, directly from the <strong>Masoretic Text</strong> — the traditional Hebrew text of the Bible,
  as printed at <a href="https://mechon-mamre.org" rel="noopener">Mechon-Mamre</a>. The pointed Hebrew is
  reproduced verse-by-verse on every chapter page (a Hide&nbsp;Hebrew toggle is there for English-only
  reading), so every choice is checkable against the source.</p>
  <p><strong>The philosophy: essentially literal, in a natural modern register.</strong> Keep the Hebrew's
  word-plays, repetitions and structure wherever English can bear them; where it can't, say so in the notes
  rather than silently smoothing it over. Where the text is genuinely uncertain — a word that appears once
  in the whole Bible, a line the ancient manuscripts disagree on — the notes say that too, instead of
  pretending to a confidence the evidence doesn't support.</p>
  <p><strong>The seven-version shelf.</strong> Below every chapter, verse-by-verse translator's notes
  compare this translation's choices against seven landmark versions, chosen to span the full range of
  translation philosophy and history:</p>
  <div class="shelf">
    <div class="sv"><b>NIV</b> New International Version (2011) — committee, dynamic-leaning.</div>
    <div class="sv"><b>KJV</b> King James Version (1611) — the classic; built on Tyndale and Geneva.</div>
    <div class="sv"><b>DRB</b> Douay-Rheims (Challoner) — English of the Latin Vulgate; the historic Catholic text.</div>
    <div class="sv"><b>TLB</b> The Living Bible (1971) — Kenneth Taylor's one-man paraphrase.</div>
    <div class="sv"><b>GNV</b> Geneva Bible (1599) — the Reformation study Bible, before the KJV.</div>
    <div class="sv"><b>ASV</b> American Standard Version (1901) — famously literal.</div>
    <div class="sv"><b>NWT</b> New World Translation (1984) — the Watch Tower Society's translation.</div>
  </div>
  <p style="margin-top:14px"><strong>Honesty note.</strong> This translation is made by Claude (Anthropic's
  AI) working from the pointed Hebrew, guided and edited by Mr. Librarian. It is a study rendering, not the
  product of a translation committee — treat the notes as the argument for each choice, and check them
  against the shelf. Quotations from copyrighted versions are kept to brief phrases for comparison; the
  KJV, Geneva, Douay-Rheims, and ASV are public domain.</p>
  <p><strong>The name.</strong> A librarian's job is to catalogue, source, and compare — not to preach.
  That's the ethos here: every claim sourced, every alternative shown, disagreements between traditions
  presented rather than settled.</p>
  <p><strong>Privacy.</strong> The <a href="index.html">home page</a>'s Verse of the Day and the
  <a href="reading.html">My Reading</a> progress tracker both run entirely in your own browser (a bit of
  localStorage) — there's no login and no server-side record of what you've read; clear your browser
  data and it's gone, same as any other private note to yourself. The one thing that <em>is</em> measured
  is an anonymous, cookie-less visit count — no personal data, no cross-site tracking, nothing sold,
  no consent banner needed because none of that happens.{" That's it, live, right below." if GOATCOUNTER_CODE else ""}</p>
  {_stats_box()}
</div>"""
    out = page(f"About — {SITE_NAME}", body, active="about",
               desc="How the MisterLibrarian Bible Project works: translated from the Masoretic Hebrew, "
                    "essentially literal in a modern register, compared against seven landmark versions.")
    open(os.path.join(OUT, "about.html"), "w", encoding="utf-8").write(out)


def build_new_testament():
    """The heading page for the New Testament / Greek Scriptures — an intro to the
    crossing from Hebrew into Greek, the full source-text apparatus the translation
    will consult, an honest account of how a body of thousands of manuscripts is
    actually weighed, and what carries over from the Hebrew chapters. A living page:
    edit this function as the method for the Greek Scriptures develops."""
    body = """<h1 class="pagetitle">The New Testament</h1>
<div class="nt-intro">
<p class="lede nt-lede">Here the project crosses a threshold — out of the Hebrew of the Tanakh and into the
<strong>Koine Greek of the New Testament</strong>, what a number of traditions call the
<em>Greek Scriptures</em>. The ethos doesn't change; the language, the manuscripts, and one or two famous
arguments do. This page is the reference desk for that crossing: the texts we translate from, how a body of
roughly 5,800 Greek manuscripts is actually weighed, and what carries over from the Hebrew chapters. It's a
<strong>living page</strong> — updated as the method for the Greek Scriptures takes shape.</p>

<figure class="ms-figure">
  <img src="img/p52-john-rylands.jpg" width="960" height="1280" loading="lazy"
    alt="Papyrus 52 (P52), the Rylands fragment — a scrap of the Gospel of John 18:31–33 in Greek, c. 125–150 CE"/>
  <figcaption>
    <span class="ms-name">P52 — the Rylands fragment</span>
    A scrap of <em>John 18:31–33</em> in Greek, c. 125–150 CE — the oldest surviving piece of any New
    Testament book, and part of the very Gospel this phase begins with.
    <span class="ms-credit">John Rylands Library, Manchester — via
    <a href="https://commons.wikimedia.org/wiki/File:Manchester,_John_Rylands_Library_Ms_Greek_P_457_(Papyrus_52)_recto_John_18,_31-33.jpg" rel="noopener">Wikimedia Commons</a> · public domain</span>
  </figcaption>
</figure>

<div class="panel prose nt-panel1">
  <h2 style="margin-top:2px">What changes, and what stays</h2>
  <p><strong>What changes.</strong> The source language is now Greek, not Hebrew. And the source <em>text</em>
  works differently: the Hebrew chapters translate one remarkably standardized traditional text (the Masoretic
  Text). The Greek New Testament has no single such text — instead there are thousands of manuscripts, the
  oldest on papyrus from within a century or so of the writing, and the base for translation is a
  <strong>critical text</strong> that weighs them against one another. One more thing changes: the
  <strong>words of Jesus will be set in red</strong>, the convention this library has promised since Genesis.</p>
  <p><strong>What stays.</strong> Everything that makes this a librarian's Bible and not a preacher's.
  Essentially literal, in a natural modern register. The same <strong>seven-version shelf</strong> under every
  chapter — the NIV, KJV, Douay-Rheims, Living Bible, 1599 Geneva, ASV, and NWT all carry the New Testament,
  so the comparison continues unbroken. The <strong>neutrality rule</strong>: where traditions divide, the
  notes give the readings with their pedigrees and <em>don't vote</em>. The <strong>echo system</strong> —
  and here it grows a new dimension, because the New Testament quotes the Old on nearly every page, so the
  cross-references will finally run between books. And the honesty habits: where a word is uncertain or the
  manuscripts disagree, the notes say so plainly instead of pretending to a confidence the evidence can't
  support.</p>
</div>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The source texts</h2>
  <p>The base for translation is the <strong>critical Greek New Testament</strong> in the Nestle tradition —
  an <em>eclectic</em> text that doesn't reprint any one manuscript but reconstructs, variant by variant, the
  earliest recoverable reading, resting mainly on the oldest Alexandrian witnesses. Alongside it the notes
  consult the printed critical editions and the primary manuscripts behind them:</p>

  <h3>Printed critical editions</h3>
  <div class="shelf">
    <div class="sv"><b>Nestle</b> Novum Testamentum Graece, 18th ed. (1948) — the eclectic Greek text in the
    line that became the modern standard.</div>
    <div class="sv"><b>Bover</b> José María Bover's critical Greek New Testament — a Catholic scholar's
    independent edition.</div>
    <div class="sv"><b>Merk</b> Augustinus Merk's Novum Testamentum Graece et Latine — Greek with the Latin
    alongside.</div>
  </div>

  <h3>The great uncials — the 4th-century codices</h3>
  <div class="shelf">
    <div class="sv"><b>Vaticanus (B / 03)</b> mid-4th century (c. 325–350) — one of the two great uncial
    codices, and a chief pillar of the Alexandrian text.</div>
    <div class="sv"><b>Sinaiticus (א / 01)</b> mid-4th century (c. 330–360), found at St Catherine's
    Monastery on Sinai — a nearly complete New Testament.</div>
  </div>

  <h3>The early papyri — 2nd and 3rd centuries</h3>
  <p>Older still than the codices, and the reason we can say the Alexandrian text is early and not a late
  editorial invention:</p>
  <div class="shelf">
    <div class="sv"><b>P52</b> (the Rylands fragment) — a scrap of <em>John 18</em>, c. 125–150, the oldest
    known fragment of any New Testament book.</div>
    <div class="sv"><b>P66</b> (Bodmer II) — a substantial portion of <em>John</em>, c. 200.</div>
    <div class="sv"><b>P75</b> (Bodmer XIV–XV) — <em>Luke and John</em>, c. 175–225, textually almost
    identical to Vaticanus though ~150 years older, which is how we know that text isn't a late recension.</div>
    <div class="sv"><b>P46</b> (Chester Beatty II) — the <em>letters of Paul</em>, c. 200.</div>
  </div>

  <h3>The early versions</h3>
  <p>Independent early translations corroborate the Greek from the outside: the <strong>Latin</strong> — the
  Vulgate, which is exactly what the Douay-Rheims on our shelf renders into English — along with the
  <strong>Coptic</strong> (Egyptian) and <strong>Syriac</strong> traditions. When a Greek reading turns up
  already carried in a 3rd- or 4th-century version in another language, that is a second, independent vote for
  its antiquity.</p>
  <p class="muted" style="margin-top:10px">A practical note: you weigh the witnesses that actually preserve
  the book in front of you. The John papyri (P52, P66, P75) are gold for the Gospel of John and silent about
  Paul; P46 is the reverse. And though the two great codices carry the Greek Old Testament too, both are
  missing early Genesis — Vaticanus begins at Genesis 46:28 — which is why the Hebrew chapters lean on the
  printed critical Septuagint rather than on B and א directly.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">Isn't weighing thousands of manuscripts impossible?</h2>
  <p>It sounds impossible — around 5,800 Greek manuscripts, plus thousands more in Latin, lectionaries, and
  quotations in the early writers, and somewhere near 400,000 points of variation among them. But you never
  weigh them flat, one vote each, and four things collapse the problem down to something a person can hold:</p>
  <ul class="prose-list">
    <li><strong>Manuscripts cluster into families, so you weigh <em>streams</em>, not copies.</strong> The
    overwhelming majority are late, medieval copies of copies, and they group into a few text-types —
    Alexandrian (the earliest, P75 and the great codices), Byzantine (the vast late majority), and Western. A
    thousand near-identical late copies count as roughly one witness with a thousand fingerprints.</li>
    <li><strong>Almost every variant is trivial.</strong> Spelling, a slip of the pen, a swapped word order
    (Greek is inflected, so order rarely changes the meaning). Of all those variants, the ones that are both
    <em>meaningful and viable</em> — a real reading, with real support, that changes the sense — are well
    under one percent; the ones that would actually alter an English translation are fewer still.</li>
    <li><strong>The weighing is principled, not brute force.</strong> Two questions decide each real variant:
    which reading best <em>explains how the others arose</em> (a scribe is likelier to smooth a hard reading
    than to roughen an easy one), and which has the <em>oldest and most widely spread</em> support. This is
    what the critical editions above have already carried out.</li>
    <li><strong>The genuinely combinatorial part is now done by computer.</strong> The modern critical editions
    use a method called the CBGM to model the family tree of variants across the whole tradition — precisely
    the part that would be impossible by hand.</li>
  </ul>
  <p>So the honest bottom line: you don't adjudicate 5,800 manuscripts — you read a critical apparatus that
  has already done the weighing, and it shows you the handful of variants that matter for each verse, with
  their pedigrees. The amount of text in real doubt is small, and the few large disputed passages are famous
  and openly flagged in every serious edition — the longer ending of Mark (16:9–20), the woman caught in
  adultery (John 7:53–8:11), the "Johannine Comma" (1 John 5:7–8). Nothing hidden; the notes will mark them
  when we reach them.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The first test: John 1:1</h2>
  <p>The New Testament opens, fittingly, on the project's hardest neutrality problem. The Gospel of John begins
  <span class="greek">Ἐν ἀρχῇ ἦν ὁ λόγος</span> — "In the beginning was the Word" — deliberately echoing the
  first words of Genesis, and then reaches its famous crux: <span class="greek">καὶ θεὸς ἦν ὁ λόγος</span>.
  Most versions render it "and the Word was God"; the New World Translation reads "and the Word was <em>a
  god</em>." That difference turns on a fine point of Greek grammar — a predicate noun with no article, standing
  before its verb — and it is exactly the kind of place this project exists to handle honestly. When John 1
  is posted, the note will lay out the grammar and the readings <strong>with their pedigrees, and won't cast a
  vote</strong>. That is the method the whole Old Testament has followed, carried across the threshold intact.</p>
</div>

<div class="panel">
  <p style="margin:0 0 6px"><strong>The Greek Scriptures begin with the Gospel of John.</strong></p>
  <p class="muted" style="margin:0 0 12px">Its first chapter — the Prologue, John the Baptist's testimony, and
  the calling of the first disciples — is now live, the first to arrive with the full apparatus above behind it:
  from the Prologue's "was God / a god" to the manuscript decision at John 1:18, where the earliest papyri decide
  the reading.</p>
  <a class="btn" href="john-1.html">Read John 1 →</a>
</div>"""
    out = page(f"The New Testament — {SITE_NAME}", body, active="nt",
               desc="Introducing the New Testament (the Greek Scriptures) in The MisterLibrarian Bible "
                    "Project: the critical Greek text and manuscript apparatus behind the translation "
                    "(Vaticanus, Sinaiticus, the early papyri P52/P66/P75/P46), how thousands of manuscripts "
                    "are weighed, and what carries over from the Hebrew.")
    open(os.path.join(OUT, "new-testament.html"), "w", encoding="utf-8").write(out)


def build_ask_enoch():
    body = """<h1 class="pagetitle">\U0001F4D6 Ask Mr. Librarian</h1>
<h2 style="margin-top:4px">Why isn't the Book of Enoch in this translation?</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>"Why did you not include the Book of Enoch in your translation of the Bible?"</p>
</div>

<div class="panel prose">
  <p>This project's source text has been the <strong>Masoretic Hebrew Bible</strong> — the Tanakh, pointed
  Hebrew and all — since the very first line of the very first chapter. The Book of Enoch was never part of
  that corpus to begin with. There's no Masoretic Hebrew text of Enoch to translate from; it doesn't survive
  complete in Hebrew at all. The only complete text is in Ge'ez (classical Ethiopic), with fragments of the
  original Aramaic and some Greek turning up among the Dead Sea Scrolls and elsewhere. So leaving it out
  wasn't a judgment call about whether it belongs — it was outside this project's stated method before the
  question of canon ever came up.</p>
  <p>The broader canon question is genuinely interesting, though. Enoch isn't in the Jewish canon, the
  Protestant 66-book list this project's Table of Contents is built around, or even the Catholic
  Deuterocanon (the extra books the Douay-Rheims tradition includes — Tobit, Judith, Maccabees, and so on —
  don't include it either). The one tradition where it actually <em>is</em> canonical scripture is the
  <strong>Ethiopian Orthodox Tewahedo Church</strong>, which is often the detail people miss — it's not that
  Enoch was universally rejected, it's that one major, ancient Christian tradition kept it and the others
  didn't.</p>
  <p>And it wasn't obscure or forgotten in the meantime. Multiple Aramaic copies of it turned up at Qumran
  among the Dead Sea Scrolls, so it was clearly in real circulation in Second Temple Judaism. And the New
  Testament itself references it — the epistle of <strong>Jude, verses 14–15</strong>, cites "Enoch, the
  seventh from Adam" prophesying judgment, language that traces straight back to Enoch's text. So whatever
  the reasons different communities eventually settled their canons the way they did (and scholars don't
  agree on one tidy explanation — theories range from its pseudepigraphal authorship claim, to discomfort
  with its angelology and cosmology, to it simply falling outside the criteria later rabbinic and church
  authorities used), it was clearly read and taken seriously by people in a position to know it well.</p>
  <p>Two places in this translation touch Enoch's world directly: the man himself — "Enoch walked with God,
  and then he was not there, for God took him" — appears in <a href="genesis-5.html#v5-21">Genesis
  5:21–24</a>, the two-verse mystery from which the later book grew; and the "sons of God" episode the Book
  of Enoch expands so dramatically opens <a href="genesis-6.html#v6-1">Genesis 6</a>.</p>
  <p>If this project ever extends to it, that's a real possibility — but it would be a different kind of
  undertaking than the Hebrew chapters posted so far, since it means working from Ge'ez and the
  Aramaic/Greek fragments instead of pointed Masoretic Hebrew, and being upfront that it sits outside the
  Tanakh and the Protestant canon this translation has otherwise followed.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">Have a question about the project, a translation choice, or
  what's coming next? Reader questions are exactly how this series grows — the next one could be yours.</p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Ask Mr. Librarian: the Book of Enoch — {SITE_NAME}", body, active="ask",
               desc="Why the Book of Enoch isn't part of this Bible translation: the Masoretic source "
                    "text, the canon question, the Ethiopian exception, and the Dead Sea Scrolls.")
    open(os.path.join(OUT, "ask-enoch.html"), "w", encoding="utf-8").write(out)


def build_contact():
    body = f"""<h1 class="pagetitle">✉️ Ask Mr. Librarian a question</h1>
<p class="lede">A question about the project, a translation choice you'd argue with, a chapter request,
or something you've always wondered about the text — send it in. Good questions become
<a href="ask-enoch.html">Ask Mr. Librarian</a> posts (anonymously unless you say otherwise), and reader
questions are exactly how that series grows.</p>

<div class="panel">
  <form action="{FORM_ENDPOINT}" method="POST" class="askform">
    <input type="hidden" name="_subject" value="Ask Mr. Librarian — a question from the site"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="{SITE_URL}/thanks.html"/>
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
    <p class="formnote">Sending shows a quick captcha (keeps the robots out of the library), then brings
    you back here. Nothing is posted publicly — questions go straight to Mr. Librarian's desk.</p>
  </form>
</div>"""
    out = page(f"Ask a question — {SITE_NAME}", body, active="contact",
               desc="Send Mr. Librarian a question about the translation, a verse, or the project — "
                    "good questions become Ask Mr. Librarian posts.")
    open(os.path.join(OUT, "contact.html"), "w", encoding="utf-8").write(out)


def build_thanks():
    body = """<h1 class="pagetitle">📬 It's on the librarian's desk</h1>
<div class="panel prose">
  <p><strong>Your question is in.</strong> Thank you — reader questions are the lifeblood of the
  <a href="ask-enoch.html">Ask Mr. Librarian</a> series, and every one gets read. If yours becomes a post,
  it will appear anonymously unless you asked otherwise; if you left an email, you may get a reply
  directly.</p>
  <p>Meanwhile, the shelves are open: the <a href="toc.html">Table of Contents</a> has every chapter
  published so far.</p>
</div>"""
    out = page(f"Question received — {SITE_NAME}", body,
               desc="Your question is on Mr. Librarian's desk.")
    open(os.path.join(OUT, "thanks.html"), "w", encoding="utf-8").write(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    args = ap.parse_args()
    chapters = extract_source(args.source)
    build_chapter_pages(chapters)
    build_toc()
    build_reading()
    build_index(chapters)
    build_about()
    build_new_testament()
    build_ask_enoch()
    build_contact()
    build_thanks()
    n_words, n_refs = build_concordance(chapters)
    n_dict = build_dictionary()
    n_places, n_people = build_encyclopedia()
    n_mapped, n_atlas_places = build_atlas()
    build_library((n_words, n_refs, n_dict, n_places, n_people, len(XREFS), n_mapped, n_atlas_places))
    print(f"built {len(CHAPTERS)} chapters + core pages + library "
          f"(concordance {n_words}w/{n_refs}refs, dict {n_dict}, ency {n_places}p/{n_people}pp, "
          f"atlas {n_mapped}/{n_atlas_places} mapped, xrefs {len(XREFS)}) from {args.source}")


if __name__ == "__main__":
    main()

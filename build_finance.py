#!/usr/bin/env python3
"""Build /finance/ — a standing board of the world's largest assets by market cap.

    python3 build_finance.py

STANDARD LIBRARY ONLY, deliberately. The network lives in tools/fetch_asset_board.py,
which writes source/finance/asset_board.json; this reads that file and renders HTML.
Keeping the split means the build has no dependencies to install, cannot fail on a
Yahoo outage, and works offline — and it is the same property build_travel.py has.

THREE PUBLICATIONS, ONE DOMAIN, NO LINKS BETWEEN THEM
────────────────────────────────────────────────────
mistertranslation.com now serves three separate things that share only a hostname:
the Bible project at the root (build.py), The Librarian Abroad at /travel/
(build_travel.py), and this at /finance/. None of them links to another, on purpose.

This builder writes ONLY inside finance/ and never globs or deletes anywhere else,
which is the same discipline that lets the other two coexist safely. build.py's only
glob is a read-only meta-description audit scoped to the repo root plus dict/, ency/,
atlas/ and routes/ — it has never touched travel/ and will not touch finance/.

RENAMING
────────
Edit SITE_NAME / TAGLINE / BLURB below. Nothing else hardcodes the name.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

import blogkit

SITE_NAME = "The Librarian's Ledger"
TAGLINE = "What the world's money is actually in"
BLURB = ("A standing count of the largest assets on earth — gold, silver, the biggest "
         "public companies, and Bitcoin — ranked by what the market says they are worth, "
         "and refreshed through the day.")

BASE_URL = "https://mistertranslation.com/finance/"
SITE_URL = "https://mistertranslation.com"
BASE = "/finance"

# The Ledger's front-matter vocabulary. Deliberately NOT the travel blog's: an
# entry here has no stars, no subject and no place, because it is writing about
# money rather than a review of somewhere you can go.
KNOWN_KEYS = {"title", "date", "tags", "summary", "meta_desc",
              "hero", "hero_alt", "hero_credit", "draft"}
REQUIRED_KEYS = {"title", "date", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70


ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source", "finance", "asset_board.json")
OUT = os.path.join(ROOT, "finance")
ENTRY_SRC = os.path.join(ROOT, "source", "finance")

ACCENT = "#5eb3d6"   # steel cyan — deliberately NOT green or red, which the table
                     # uses semantically for up and down.

# Monogram colours for anything with no cached logo. Picked by name hash so a given
# company always gets the same one.
MONO = ["#5eb3d6", "#c98f5e", "#8f8fd6", "#5ec98f", "#c95e8f", "#c9b45e"]


# ─────────────────────────────────────────────────────────── formatting helpers ──

def money_cap(v):
    """29895000000000.0 -> '$29.895 T'."""
    if v >= 1e12:
        return f"${v / 1e12:,.3f} T"
    if v >= 1e9:
        return f"${v / 1e9:,.1f} B"
    return f"${v / 1e6:,.0f} M"


def money_px(v):
    """Prices: comma-grouped whole dollars once they are large enough not to need cents."""
    return f"${v:,.0f}" if v >= 1000 else f"${v:,.2f}"


def pct(v):
    return "—" if v is None else f"{v:+.2f}%"


def _logo_slug(domain):
    """Must match slug() in tools/finance_logos.py."""
    return domain.split(".")[0].lower()


def esc(s):
    return html.escape(str(s), quote=True)


# ────────────────────────────────────────────────────────────────── components ──

def sparkline(vals, width=132, height=30):
    """A 30-day close series as an inline SVG polyline.

    Inline rather than an <img> because it is a handful of bytes, needs no request,
    and inherits the page's colours. Coloured by the direction of the whole window,
    which is what the shape is actually telling you.
    """
    pts = [v for v in (vals or []) if isinstance(v, (int, float))]
    if len(pts) < 2:
        return '<span class="nosp">—</span>'
    lo, hi = min(pts), max(pts)
    span = (hi - lo) or 1.0
    step = width / (len(pts) - 1)
    coords = " ".join(
        f"{i * step:.1f},{height - 3 - ((v - lo) / span) * (height - 6):.1f}"
        for i, v in enumerate(pts))
    up = pts[-1] >= pts[0]
    colour = "#4ade80" if up else "#f87171"
    return (f'<svg class="spark" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" aria-hidden="true" focusable="false">'
            f'<polyline points="{coords}" fill="none" stroke="{colour}" '
            f'stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/></svg>')


def mark(a):
    """Logo, emoji, or a coloured monogram — in that order of preference."""
    domain = a.get("domain")
    if domain:
        slug = _logo_slug(domain)
        if os.path.exists(os.path.join(OUT, "img", f"{slug}.png")):
            return (f'<img class="mk" src="img/{esc(slug)}.png" alt="" '
                    f'width="28" height="28" loading="lazy"/>')
    if a.get("emoji"):
        return f'<span class="mk mk-e" aria-hidden="true">{esc(a["emoji"])}</span>'
    name = a.get("name", "?")
    colour = MONO[sum(ord(c) for c in name) % len(MONO)]
    return (f'<span class="mk mk-m" aria-hidden="true" '
            f'style="background:{colour}22;color:{colour};border-color:{colour}55">'
            f'{esc(name[0].upper())}</span>')


def row(a, btc_rank):
    is_btc = a.get("symbol") == "BTC"
    is_metal = a.get("kind") == "metal"
    cls = " class=\"btc\"" if is_btc else (" class=\"metal\"" if is_metal else "")
    ch = a.get("change_pct")
    ch_cls = "flat" if ch is None else ("up" if ch >= 0 else "down")
    return f"""      <tr{cls}>
        <td class="rk">{a['rank']}</td>
        <td class="as"><span class="asw">{mark(a)}<span class="nm"><span class="n1">{esc(a['name'])}</span><span class="n2">{esc(a['symbol'])}</span></span></span></td>
        <td class="mc">{money_cap(a['market_cap'])}</td>
        <td class="px">{money_px(a['price'])}</td>
        <td class="ch {ch_cls}">{pct(ch)}</td>
        <td class="sp">{sparkline(a.get('spark'))}</td>
        <td class="wh">{esc(a.get('country') or '')}</td>
      </tr>"""



# ───────────────────────────────────────────────────────────────── entries ───

def load_entries(include_drafts=False):
    """Read source/finance/*.html into entry dicts, newest first.

    Shares blogkit's front-matter parser with the travel blog but not its
    vocabulary — see KNOWN_KEYS above.
    """
    if not os.path.isdir(ENTRY_SRC):
        return []
    entries = []
    for fn in sorted(os.listdir(ENTRY_SRC)):
        if not fn.endswith(".html") or fn.startswith("_"):
            continue
        with open(os.path.join(ENTRY_SRC, fn), encoding="utf-8") as fh:
            meta, body = blogkit.parse_front_matter(
                fh.read(), "source/finance/" + fn, KNOWN_KEYS, REQUIRED_KEYS)

        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.html$", fn)
        if not m:
            raise ValueError("source/finance/%s: name must be YYYY-MM-DD-slug.html" % fn)
        date = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        slug = m.group(4)
        if meta["date"].strip() != date.isoformat():
            raise ValueError(
                "source/finance/%s: `date: %s` disagrees with the filename (%s). "
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


def _tag_chips(e):
    """Tags render as plain chips, not links.

    There are no tag pages yet, and generating one page per tag for a
    publication with a couple of entries would be a pile of near-empty
    thin-content pages — worse for a reader and worse in search than no tag
    pages at all. Add them when the archive earns them.
    """
    if not e["tags"]:
        return ""
    chips = "".join('<span class="tg">%s</span>' % esc(t) for t in e["tags"])
    return '<div class="tags">%s</div>' % chips


def _entry_hero(e):
    if not e["hero"]:
        return ""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), e["hero"])
    cap = "<figcaption>%s</figcaption>" % esc(e["hero_credit"]) if e["hero_credit"] else ""
    return ('<figure class="hero"><img src="img/%s" alt="%s"%s loading="eager"/>%s</figure>'
            % (esc(e["hero"]), esc(e["hero_alt"]), dims, cap))


def build_entry_page(e):
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
<style>%(css)s</style>
</head>
<body>
<div class="wrap">
  <header class="hsm">
    <a class="brand" href="index.html">%(mark)s<span class="wm">The Librarian's <span class="em">Ledger</span></span></a>
  </header>
  %(banner)s
  <article class="entry">
    <h1 class="etitle">%(title)s</h1>
    <p class="edate">%(date)s</p>
    %(hero)s
%(body)s
    %(tags)s
  </article>
  <p class="backlink"><a href="index.html">← Back to the Ledger</a></p>
  <footer>
    %(site)s · <a href="feed.xml">RSS</a> · nothing here is investment advice
  </footer>
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
        "mark": MARK_SVG.replace("__ACCENT__", ACCENT),
        "banner": banner,
        "date": blogkit.pretty_date(e["date"]).upper(),
        "hero": _entry_hero(e),
        "body": e["body"],
        "tags": _tag_chips(e),
    }


def _entry_card(e):
    return ('    <a class="ecard" href="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]), blogkit.pretty_date(e["date"]).upper(),
                          esc(e["title"]), esc(e["summary"])))


def build_writing_section(entries):
    if not entries:
        return ""
    return ('\n  <section class="writing">\n'
            '    <h2 class="wh">Writing</h2>\n'
            '    <p class="wsub">Occasional pieces about money, custody, and the '
            'machinery underneath both. <a href="feed.xml">RSS</a>.</p>\n'
            '%s\n  </section>\n' % "\n".join(_entry_card(e) for e in entries))


# ─────────────────────────────────────────────────────────────────────── page ──

CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#060b14;color:#e8eef7;
  font:16px/1.65 Georgia,'Iowan Old Style','Palatino Linotype',serif;
  -webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(120% 80% at 50% -8%,rgba(94,179,214,.10),transparent 60%)}
.wrap{position:relative;z-index:1;max-width:1060px;margin:0 auto;padding:0 22px 72px}
header{padding:46px 0 8px;text-align:center}
.brand{display:inline-flex;align-items:center;gap:14px;text-decoration:none;color:inherit}
.bmark{width:46px;height:46px;flex:0 0 46px}
h1{margin:0;font-size:31px;font-weight:400;letter-spacing:.01em}
h1 .em{color:__ACCENT__;font-style:italic}
.tag{margin:12px 0 0;color:#93a4bd;font-size:15px;font-style:italic}
.lede{margin:30px auto 0;max-width:760px;color:#b9c6d8;font-size:16.5px}
.lede b{color:#e8eef7;font-weight:400}
.hl{color:__ACCENT__}
.stamp{margin:22px 0 26px;text-align:center;color:#7f8fa6;font-size:13.5px;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.stamp .dot{color:#3f4c5f;margin:0 8px}

/* The table is the one element that can be intrinsically wider than a phone.
   Letting it scroll inside its own box is what stops it stretching .wrap and
   pushing the whole page sideways — the prose must never overflow because a
   number column did. */
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
.board{width:100%;border-collapse:collapse;
  font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}
.board th{text-align:left;font-weight:500;font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:#6e7d92;padding:0 12px 10px;border-bottom:1px solid #1b2534}
.board td{padding:11px 12px;border-bottom:1px solid #131b27;font-size:15px;vertical-align:middle}
.board tr:last-child td{border-bottom:0}
.rk{color:#6e7d92;font-variant-numeric:tabular-nums;width:44px}
.asw{display:flex;align-items:center;gap:11px;min-width:0}
.mk{width:28px;height:28px;flex:0 0 28px;border-radius:7px;object-fit:contain;background:#0d1521}
.mk-e,.mk-m{display:inline-flex;align-items:center;justify-content:center;
  font-size:16px;border:1px solid #1e2938;font-family:ui-sans-serif,system-ui,sans-serif}
.mk-m{font-weight:600}
.nm{display:flex;flex-direction:column;line-height:1.25;min-width:0}
.n1{font-weight:600;color:#e8eef7}
.n2{font-size:11.5px;color:#6e7d92;letter-spacing:.05em}
.mc{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.px,.ch{font-variant-numeric:tabular-nums;color:#a9b7c9;white-space:nowrap}
.ch.up{color:#4ade80}.ch.down{color:#f87171}.ch.flat{color:#6e7d92}
.sp{width:140px}.spark{display:block}.nosp{color:#3f4c5f}
.wh{text-align:right;font-size:17px;width:52px}
tr.btc{background:linear-gradient(90deg,rgba(247,147,26,.10),rgba(247,147,26,.02))}
tr.btc .n1{color:#f7931a}
tr.metal{background:rgba(255,255,255,.018)}

.panel{margin:44px 0 0;padding:24px 26px;border:1px solid #1b2534;border-radius:12px;
  background:#0a111c}
.panel h2{margin:0 0 12px;font-size:19px;font-weight:400;color:#e8eef7}
.panel p{margin:0 0 12px;color:#b9c6d8;font-size:15px}
.panel p:last-child{margin-bottom:0}
.panel code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13.5px;
  color:__ACCENT__;background:#0e1724;padding:1px 6px;border-radius:4px}
.panel ul{margin:0 0 12px;padding-left:20px;color:#b9c6d8;font-size:15px}
.panel li{margin:0 0 6px}
footer{margin:52px 0 0;padding-top:22px;border-top:1px solid #131b27;text-align:center;
  color:#6e7d92;font-size:13.5px;font-family:ui-sans-serif,system-ui,sans-serif}

/* ── entries ─────────────────────────────────────────────────────────────── */
header.hsm{padding:30px 0 6px;text-align:left}
header.hsm .brand{gap:11px}
header.hsm .bmark{width:34px;height:34px;flex:0 0 34px}
.wm{font-size:20px;letter-spacing:.01em}
.wm .em{color:__ACCENT__;font-style:italic}
a{color:__ACCENT__}
.draftban{margin:16px 0 0;padding:11px 15px;border:1px solid #7a5a2a;border-radius:9px;
  background:#1a1408;color:#e2c489;font-size:14.5px;
  font-family:ui-sans-serif,system-ui,sans-serif}
.entry{max-width:760px;margin:22px auto 0}
.etitle{font-size:33px;font-weight:400;line-height:1.22;margin:0 0 10px;letter-spacing:.01em}
.edate{margin:0 0 26px;color:#6e7d92;font-size:12px;letter-spacing:.13em;
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
.entry .verdict{margin:32px 0 0;padding:20px 24px;border-left:3px solid #4ade80;
  border-radius:0 10px 10px 0;background:#0a141c}
.entry .verdict p{margin:0 0 12px}
.entry .verdict p:last-child{margin:0}
.entry .half-note{color:#7f8fa6;font-size:14.5px;font-style:italic}
.entry hr{border:0;border-top:1px solid #1b2534;margin:34px 0}
.tags{margin:34px 0 0;display:flex;flex-wrap:wrap;gap:7px}
.tg{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12px;color:#8b9ab0;
  border:1px solid #1e2938;border-radius:999px;padding:4px 11px;background:#0a111c}
.backlink{max-width:760px;margin:34px auto 0;font-family:ui-sans-serif,system-ui,sans-serif;
  font-size:14.5px}

/* ── the writing list on the board page ──────────────────────────────────── */
.writing{margin:52px 0 0}
.wh{margin:0 0 6px;font-size:23px;font-weight:400;color:#e8eef7}
.wsub{margin:0 0 20px;color:#93a4bd;font-size:15px;font-style:italic}
.ecard{display:block;text-decoration:none;padding:18px 20px;margin:0 0 12px;
  border:1px solid #1b2534;border-radius:11px;background:#0a111c;transition:border-color .15s}
.ecard:hover{border-color:#2f4257}
.ec-d{display:block;color:#6e7d92;font-size:11.5px;letter-spacing:.13em;
  font-family:ui-sans-serif,system-ui,sans-serif;margin-bottom:6px}
.ec-t{display:block;color:#e8eef7;font-size:20px;line-height:1.3;margin-bottom:7px}
.ec-s{display:block;color:#a9b7c9;font-size:15px;line-height:1.6}

@media (max-width:720px){
  .etitle{font-size:26px}
  .entry p,.entry ul,.entry ol{font-size:16px}
  .ec-t{font-size:18px}
}

@media (max-width:720px){
  .wrap{padding:0 15px 56px}
  h1{font-size:25px}
  .board th,.board td{padding:10px 7px}
  .sp,th.sp,.wh,th.wh{display:none}       /* sparkline + flag are the first to go */
  .n2{display:none}
  .board td{font-size:14px}
  .mk{width:24px;height:24px;flex:0 0 24px}
}
@media (max-width:560px){
  .px,th.px{display:none}                 /* on a phone, rank + name + cap + today */
  .n1{font-size:14px}
}
"""

MARK_SVG = """<svg class="bmark" viewBox="0 0 46 46" fill="none" aria-hidden="true">
  <circle cx="23" cy="23" r="21" stroke="__ACCENT__" stroke-width="1.5" opacity=".55"/>
  <rect x="13" y="26" width="5.4" height="10" rx="1.2" fill="__ACCENT__" opacity=".55"/>
  <rect x="20.3" y="19" width="5.4" height="17" rx="1.2" fill="__ACCENT__" opacity=".8"/>
  <rect x="27.6" y="12" width="5.4" height="24" rx="1.2" fill="__ACCENT__"/>
</svg>"""


def build_page(board, entries=()):
    writing = build_writing_section(list(entries))
    assets = board.get("assets", [])
    btc_rank = board.get("btc_rank")
    consts = board.get("constants", {})

    btc_line = ""
    if btc_rank:
        btc_line = (f'<span class="dot">·</span>'
                    f'<span class="hl">Bitcoin is the #{btc_rank} largest asset on earth</span>')

    rows = "\n".join(row(a, btc_rank) for a in assets)

    desc = (f"The largest assets in the world by market capitalisation — gold, silver, "
            f"the biggest public companies and Bitcoin"
            + (f", where Bitcoin currently ranks #{btc_rank}" if btc_rank else "") + ".")

    gold_t = consts.get("gold_tonnes")
    silver_t = consts.get("silver_tonnes")
    btc_c = consts.get("btc_circulating")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{esc(SITE_NAME)} — the biggest assets in the world</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{BASE_URL}"/>
<link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)}" href="feed.xml"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="{esc(SITE_NAME)}"/>
<meta property="og:title" content="{esc(SITE_NAME)} — the biggest assets in the world"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:url" content="{BASE_URL}"/>
<meta name="twitter:card" content="summary"/>
<style>{CSS.replace("__ACCENT__", ACCENT)}</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="brand">{MARK_SVG.replace("__ACCENT__", ACCENT)}<h1>The Librarian's <span class="em">Ledger</span></h1></span>
    <p class="tag">{esc(TAGLINE)}</p>
  </header>

  <p class="lede">{esc(BLURB)}</p>

  <p class="stamp">Updated {esc(board.get('generated', '—'))}{btc_line}</p>

  <div class="tw">
  <table class="board">
    <thead>
      <tr>
        <th class="rk">#</th>
        <th class="as">Asset</th>
        <th class="mc">Market cap</th>
        <th class="px">Price</th>
        <th class="ch">Today</th>
        <th class="sp">30 days</th>
        <th class="wh">Where</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
  </div>

  <div class="panel">
    <h2>How these numbers are made</h2>
    <p>A market capitalisation is just a price multiplied by a count of the thing. For a
    company that count is public and exact. For gold and Bitcoin it is an estimate, so
    the working is shown here rather than asked to be taken on faith:</p>
    <ul>
      <li><b>Companies</b> — market cap as reported for the listed shares.</li>
      <li><b>Gold</b> — spot price × <code>{gold_t:,} tonnes</code> of above-ground stock,
      converted at 32,150.7466 troy ounces per tonne.</li>
      <li><b>Silver</b> — the same arithmetic on <code>{silver_t:,} tonnes</code>. Silver's
      above-ground figure is the softest number on this page; estimates differ a great deal
      depending on whether industrial silver that has been used up is counted.</li>
      <li><b>Bitcoin</b> — price × <code>{btc_c:,}</code> coins in circulation, a number
      that creeps slowly upward toward its 21 million limit.</li>
    </ul>
    <p>The tonnage and supply constants move slowly and are refreshed about once a year;
    prices and company values refresh through the day. The 30-day line is a shape, not a
    scale — each one is drawn to its own high and low, so two sparklines cannot be compared
    against each other.</p>
    <p>This is a curated list, not every asset on earth: the metals, Bitcoin, and the
    large companies that sit near enough to Bitcoin's rank to give it context. Nothing here
    is investment advice, and nothing here is for sale.</p>
  </div>

  {writing}
  <footer>
    {esc(SITE_NAME)} · built {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ·
    <a href="feed.xml">RSS</a> · figures from public market data
  </footer>
</div>
</body>
</html>
"""


def build_sitemap(entries=()):
    """A sitemap is not optional here — it IS the discovery plan.

    Nothing links to this publication (that is the point), so a crawler has no
    path in. robots.txt advertises this file; without it these pages are
    effectively invisible.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = ['  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
            '    <changefreq>daily</changefreq>\n  </url>' % (BASE_URL, today)]
    for e in entries:
        urls.append('  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n'
                    '  </url>' % (BASE_URL, e["file"], e["date"].isoformat()))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def main():
    include_drafts = "--drafts" in sys.argv

    if not os.path.exists(SRC):
        sys.exit("no source/finance/asset_board.json — run tools/fetch_asset_board.py first")

    with open(SRC, encoding="utf-8") as fh:
        board = json.load(fh)

    assets = board.get("assets") or []
    if not assets:
        sys.exit("asset_board.json has no assets — refusing to build an empty board")

    entries = load_entries(include_drafts=include_drafts)
    live = [e for e in entries if not e["draft"]]

    check_entries(entries)

    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_page(board, live))
    for e in entries:
        with open(os.path.join(OUT, e["file"]), "w", encoding="utf-8") as fh:
            fh.write(build_entry_page(e))
    with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(blogkit.build_feed(live, site_name=SITE_NAME, site_url=SITE_URL,
                                    base=BASE, blurb=BLURB))
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(build_sitemap(live))

    missing = [a["name"] for a in assets
               if a.get("domain")
               and not os.path.exists(os.path.join(OUT, "img", _logo_slug(a["domain"]) + ".png"))]

    print("built /finance/ — %d assets, Bitcoin #%s, data %s"
          % (len(assets), board.get("btc_rank"), board.get("generated")))
    print("  %d entr%s (%d live%s)"
          % (len(entries), "y" if len(entries) == 1 else "ies", len(live),
             ", %d draft" % (len(entries) - len(live)) if len(entries) != len(live) else ""))
    for e in entries:
        print("  %s  %-38s %s" % (e["date"], e["file"], "[DRAFT]" if e["draft"] else ""))
    if missing:
        print("  monogram fallback (no cached logo): %s" % ", ".join(missing))
    return 0


def check_entries(entries):
    """Refuse to build on the SEO mistakes that are invisible once shipped.

    Deliberately a hard failure rather than a warning, for the same reason the
    travel builder does it: a warning printed during a build nobody reads is not
    a check. Scoped to what a build can actually judge.
    """
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
    if problems:
        sys.exit("build refused:\n  " + "\n  ".join(problems))


if __name__ == "__main__":
    sys.exit(main())

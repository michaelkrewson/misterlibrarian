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

import html
import json
import os
import sys
from datetime import datetime, timezone

SITE_NAME = "The Librarian's Ledger"
TAGLINE = "What the world's money is actually in"
BLURB = ("A standing count of the largest assets on earth — gold, silver, the biggest "
         "public companies, and Bitcoin — ranked by what the market says they are worth, "
         "and refreshed through the day.")

BASE_URL = "https://mistertranslation.com/finance/"

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source", "finance", "asset_board.json")
OUT = os.path.join(ROOT, "finance")

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


def build_page(board):
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

  <footer>
    {esc(SITE_NAME)} · built {datetime.now(timezone.utc).strftime('%Y-%m-%d')} ·
    figures from public market data
  </footer>
</div>
</body>
</html>
"""


def build_sitemap():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
  </url>
</urlset>
"""


def main():
    if not os.path.exists(SRC):
        sys.exit("no source/finance/asset_board.json — run tools/fetch_asset_board.py first")

    with open(SRC, encoding="utf-8") as fh:
        board = json.load(fh)

    assets = board.get("assets") or []
    if not assets:
        sys.exit("asset_board.json has no assets — refusing to build an empty board")

    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_page(board))
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(build_sitemap())

    missing = [a["name"] for a in assets
               if a.get("domain")
               and not os.path.exists(os.path.join(OUT, "img", f"{_logo_slug(a['domain'])}.png"))]

    print(f"built /finance/ — {len(assets)} assets, Bitcoin #{board.get('btc_rank')}, "
          f"data {board.get('generated')}")
    if missing:
        print(f"  monogram fallback (no cached logo): {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

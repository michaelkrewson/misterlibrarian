#!/usr/bin/env python3
"""Build /finance/ — a standing board of the world's largest assets by market cap.

    python3 build_finance.py

STANDARD LIBRARY ONLY, deliberately. The network lives in tools/fetch_asset_board.py,
which writes source/finance/asset_board.json; this reads that file and renders HTML.
Keeping the split means the build has no dependencies to install, cannot fail on a
Yahoo outage, and works offline — and it is the same property build_travel.py has.

THREE PUBLICATIONS, ONE DOMAIN
─────────────────────────────
mistertranslation.com serves three separate things: the Bible project at the root
(build.py), The Librarian Abroad at /travel/ (build_travel.py), and this at
/finance/. The two blogs LINK TO EACH OTHER (Michael's call, 2026-08-07) — nav,
footer, and the odd entry-to-entry reference. The Bible project links to neither
and is linked from neither; that separation is the one that must hold.

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
import urllib.parse
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
#
# `live: true` opts a single entry into the substitution pass in
# _render_live_entry() below — its body may contain {{BTC_*}} tokens that get
# replaced with figures freshly derived from asset_board.json on EVERY build,
# so the entry rebuilds itself hourly right alongside the board. Every other
# entry ignores this key entirely; a body with no tokens is untouched by it.
KNOWN_KEYS = {"title", "date", "tags", "summary", "meta_desc",
              "hero", "hero_alt", "hero_credit", "draft", "live"}
REQUIRED_KEYS = {"title", "date", "summary"}
META_DESC_MAX = 155
META_DESC_MIN = 70

# A tag page listing a single entry is a near-duplicate of that entry: nothing
# for a searcher to land on that the entry itself doesn't already answer. The
# pages are still BUILT and still work — a reader clicking a tag gets what they
# asked for — they are just held back from the index (and out of the sitemap)
# until enough entries share the tag to make the page its own answer.
TAG_INDEX_MIN = 2

# The sibling publication. The Bible project at the root is deliberately NOT
# linked from here and must not be — see the README. These two are.
SIBLING_NAME = "The Librarian Abroad"
SIBLING_URL = "https://mistertranslation.com/travel/"
SIBLING_BLURB = "Travels, meals, and musings"

# The same FormSubmit endpoint the travel blog posts to, so both publications
# land in one inbox; `_subject` is what tells them apart. Reusing it is safe on
# both counts that matter: a shared inbox is not a shared page, so it creates no
# public link between the sites, and the hash is already committed in
# build_travel.py in this same public repo, so nothing new is exposed.
#
# A form rather than comments, for the reasons set out at length in
# build_travel.py: a static site has no backend, and every real comment system
# means ads, a GitHub account, or a server to keep alive — plus a permanent
# spam-moderation chore on a publication written irregularly by design.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"


ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source", "finance", "asset_board.json")
BTC_SRC = os.path.join(ROOT, "source", "finance", "bitcoin_stats.json")
OUT = os.path.join(ROOT, "finance")
ENTRY_SRC = os.path.join(ROOT, "source", "finance")

# Bitcoin amber (2026-09-03, Michael's call — was steel cyan #5eb3d6). Still
# deliberately NOT green or red: the table uses those semantically for up and down,
# and an accent that collides with them makes a rising row unreadable.
#
# ⚠️ The one thing to preserve if this ever changes again: this publication and
# The Librarian Abroad share a nav, and the sibling link renders in that blog's own
# accent (#e8865c, a soft terracotta). Amber and terracotta are far enough apart to
# stay legible side by side — a softer orange here would not be.
ACCENT = "#f7931a"

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



# ──────────────────────────────────────────────────────────── bitcoin, live ──
#
# The one entry in this publication whose numbers are correct only for an
# instant — see source/finance/2026-08-08-how-many-bitcoins-are-there.html.
# Its whole point is that Bitcoin's supply is exact arithmetic, not an
# estimate, so the entry rebuilds that arithmetic from board data on every
# run instead of freezing it at publish time. Everything here is pure — no
# network, nothing yfinance-shaped — because compute() in
# tools/fetch_asset_board.py already did the one thing that needed a network
# call (the live block height) and stamped its result into
# asset_board.json's `constants`. This just does arithmetic on that output.

# Bitcoin's true spendable maximum supply. A fixed mathematical constant —
# see tools/fetch_asset_board.py's _btc_supply_sats() for the derivation —
# not something that needs recomputing each run. 50 BTC under the
# "20,999,999.9769" figure quoted almost everywhere: that number includes
# the genesis block's nominal reward, which was never actually spendable.
BTC_TRUE_MAX = 20_999_949.9769
BTC_HALVING_INTERVAL = 210_000
BTC_INITIAL_SUBSIDY = 50.0
BTC_ZERO_REWARD_BLOCK = 33 * BTC_HALVING_INTERVAL   # 6,930,000

# Every halving to date, exact — historical fact, not an estimate, sourced
# from the blocks' own timestamps. Anything past the last entry here is in
# the future and gets extrapolated at Bitcoin's nominal 10-minutes-a-block
# target instead, by _btc_era_date() below, which is careful to say so.
BTC_KNOWN_HALVINGS = [
    (0, dt.date(2009, 1, 3)),          # genesis block
    (210_000, dt.date(2012, 11, 28)),  # 1st halving: 50 -> 25 BTC
    (420_000, dt.date(2016, 7, 9)),    # 2nd halving: 25 -> 12.5 BTC
    (630_000, dt.date(2020, 5, 11)),   # 3rd halving: 12.5 -> 6.25 BTC
    (840_000, dt.date(2024, 4, 20)),   # 4th halving: 6.25 -> 3.125 BTC
]


def _btc_era_date(block):
    """(date, is_exact) for the block height a halving era starts at.

    Exact for every era that has already happened (the dates above, straight
    off the chain). For a future era this extrapolates from the last known
    halving at Bitcoin's nominal 10-minutes-a-block target — real block
    times vary, so `is_exact=False` is the whole reason this returns a pair
    instead of just a date: every caller has to decide how to label a guess.
    """
    for b, d in BTC_KNOWN_HALVINGS:
        if b == block:
            return d, True
    last_b, last_d = BTC_KNOWN_HALVINGS[-1]
    if block < last_b:
        for (b0, d0), (b1, d1) in zip(BTC_KNOWN_HALVINGS, BTC_KNOWN_HALVINGS[1:]):
            if b0 <= block <= b1:
                frac = (block - b0) / (b1 - b0)
                return d0 + dt.timedelta(days=(d1 - d0).days * frac), True
        return last_d, True
    minutes = (block - last_b) * 10
    return last_d + dt.timedelta(minutes=minutes), False


def _btc_live_stats(board):
    """Everything the live entry's tokens need, derived from board data — or
    None if the board can't supply the one thing that can't be derived (a
    live block height), in which case the caller leaves the entry as it last
    successfully built rather than publish a broken or misleading page.
    Mirrors the fail-safe fetch_asset_board.py already uses: a bad run keeps
    the last good output instead of going blank.
    """
    consts = board.get("constants", {})
    supply = consts.get("btc_circulating")
    height = consts.get("btc_block_height")
    if supply is None or height is None:
        return None

    remaining = BTC_TRUE_MAX - supply
    pct = supply / BTC_TRUE_MAX * 100
    epoch = height // BTC_HALVING_INTERVAL
    reward = BTC_INITIAL_SUBSIDY / (2 ** epoch) if epoch < 40 else 0.0
    next_block = (epoch + 1) * BTC_HALVING_INTERVAL
    blocks_to_go = next_block - height
    months_to_go = blocks_to_go * 10 / 60 / 24 / 30.44
    zero_date, _ = _btc_era_date(BTC_ZERO_REWARD_BLOCK)

    return {
        "supply": supply,
        "height": height,
        "pct": pct,
        "remaining": remaining,
        "epoch": epoch,
        "reward": reward,
        "next_halving_block": next_block,
        "blocks_to_go": blocks_to_go,
        "months_to_go": months_to_go,
        "daily_new": reward * 144,
        "daily_next": (reward / 2) * 144,
        "zero_reward_year": zero_date.year,
        "stamp": board.get("generated", "recently"),
    }


def _btc_era_bar_label(era):
    """'2012–2016' for a settled era, '2024–~2028' for the current one (a
    known start, an estimated end), '~2028–~2032' once both ends are
    guesses. Every bar gets one of these — the hand-drawn original this
    replaces only ever labelled the first bar, which was a real bug.
    """
    start, start_exact = _btc_era_date(era * BTC_HALVING_INTERVAL)
    end, end_exact = _btc_era_date((era + 1) * BTC_HALVING_INTERVAL)
    lo = str(start.year) if start_exact else "~%d" % start.year
    hi = str(end.year) if end_exact else "~%d" % end.year
    return "%s–%s" % (lo, hi)


def _btc_supply_bar_svg(stats):
    """The 'how much of it exists' bar, regenerated from live stats on every
    build. Same house style as the rest of this publication's figures — dark
    card, Georgia serif, bitcoin-orange fill — just computed now instead of
    hand-drawn, because the numbers move.
    """
    pct = stats["pct"]
    mined_w = 760 * pct / 100
    return ("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img"
     aria-label="Bar showing Bitcoin's total possible supply: %(pct).2f percent, or
     %(supply)s coins, already mined; the remaining coins, about %(remaining)s, still to
     be created">
  <rect width="900" height="340" fill="#0a0f1a"/>
  <text x="70" y="42" font-family="Georgia, 'Times New Roman', serif" font-size="21"
        fill="#e8dfd2">Bitcoin's total possible supply, right now</text>
  <text x="70" y="88" font-family="ui-sans-serif, system-ui, sans-serif" font-size="12"
        letter-spacing="0.12em" fill="#f7931a">ALREADY MINED</text>
  <text x="70" y="110" font-family="Georgia, 'Times New Roman', serif" font-size="19"
        font-weight="bold" fill="#e8dfd2">%(supply)s BTC</text>
  <rect x="70" y="126" width="760" height="60" rx="10" fill="#161f2e"/>
  <rect x="70" y="126" width="%(mined_w).2f" height="60" rx="10" fill="#f7931a" opacity="0.92"/>
  <rect x="70" y="126" width="760" height="60" rx="10" fill="none"
        stroke="rgba(255,255,255,.12)" stroke-width="1.5"/>
  <text x="410" y="162" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif"
        font-size="22" font-weight="bold" fill="#0a0f1a">%(pct).2f%% already exists</text>
  <line x1="70" y1="204" x2="830" y2="204" stroke="rgba(255,255,255,.18)" stroke-width="1.5"/>
  <line x1="450" y1="199" x2="450" y2="209" stroke="rgba(255,255,255,.18)" stroke-width="1.5"/>
  <text x="70" y="228" font-family="Georgia, serif" font-size="13.5" fill="#94a3b8">0</text>
  <text x="450" y="228" text-anchor="middle" font-family="Georgia, serif" font-size="13.5"
        fill="#94a3b8">10,500,000</text>
  <text x="830" y="228" text-anchor="end" font-family="Georgia, serif" font-size="13.5"
        fill="#94a3b8">≈21,000,000 — the hard cap</text>
  <text x="830" y="278" text-anchor="end" font-family="ui-sans-serif, system-ui, sans-serif"
        font-size="12" letter-spacing="0.12em" fill="#94a3b8">STILL TO BE MINED</text>
  <text x="830" y="300" text-anchor="end" font-family="Georgia, 'Times New Roman', serif"
        font-size="17" fill="#e8dfd2">%(remaining)s BTC — over roughly the next 114 years</text>
  <text x="70" y="326" font-family="Georgia, serif" font-size="14" fill="#94a3b8"
        font-style="italic">As of block %(height)s. That bar's right edge ticks a little
  further every ten minutes, forever slowing, never quite finishing.</text>
</svg>""") % {
        "pct": pct, "supply": "{:,.0f}".format(stats["supply"]),
        "remaining": "{:,.0f}".format(stats["remaining"]),
        "height": "{:,}".format(stats["height"]), "mined_w": mined_w,
    }


def _btc_halving_staircase_svg(stats):
    """The reward-by-era staircase, with a real date range under EVERY bar
    (not just the first — a bug in the hand-drawn original this replaces)
    and the current era pointed out live.
    """
    max_h = 230.0
    bars = []
    for era in range(8):
        reward = BTC_INITIAL_SUBSIDY / (2 ** era)
        h = max_h * reward / BTC_INITIAL_SUBSIDY
        x = 70 + era * 95
        y = 340 - h
        label = _btc_era_bar_label(era)
        is_current = era == stats["epoch"]
        reward_s = "{:g}".format(reward)
        fill_op = "0.95" if is_current else "0.85"
        # Cream, not the site accent: the bars are already bitcoin-orange, so
        # since the accent went amber (2026-09-03) an accent-coloured marker
        # would be invisible against the very bar it is meant to single out.
        stroke = ' stroke="#e8dfd2" stroke-width="2.5"' if is_current else ""
        bars.append(
            '<rect x="%.1f" y="%.2f" width="70" height="%.2f" rx="3" '
            'fill="#f7931a" opacity="%s"%s/>' % (x, y, h, fill_op, stroke))
        # A short bar can't hold its own reward label inside it, so short
        # bars get the number below (next to the date range); only the two
        # tallest get it inside, in dark text on the orange fill.
        if h > 40:
            bars.append(
                '<text x="%.1f" y="%.2f" text-anchor="middle" '
                'font-family="Georgia, serif" font-size="14" font-weight="bold" '
                'fill="#0a0f1a">%s</text>' % (x + 35, y + 20, reward_s))
        else:
            bars.append(
                '<text x="%.1f" y="357" text-anchor="middle" font-family="Georgia, serif" '
                'font-size="11.5" fill="#94a3b8">%s</text>' % (x + 35, reward_s))
        bars.append(
            '<text x="%.1f" y="373" text-anchor="middle" '
            'font-family="ui-sans-serif, system-ui, sans-serif" font-size="10.5" '
            'fill="#6e7d92">%s</text>' % (x + 35, label))
        if is_current:
            bars.append(
                '<line x1="%.1f" y1="285" x2="%.1f" y2="%.2f" stroke="#e8dfd2" '
                'stroke-width="1.6"/>'
                '<text x="%.1f" y="255" text-anchor="middle" '
                'font-family="ui-sans-serif, system-ui, sans-serif" font-size="12.5" '
                'font-weight="bold" letter-spacing="0.08em" fill="#e8dfd2">WE ARE '
                'HERE</text>'
                '<text x="%.1f" y="273" text-anchor="middle" font-family="Georgia, serif" '
                'font-size="13.5" fill="#e8dfd2">%s BTC / block</text>'
                % (x + 35, x + 35, y - 15, x + 35, x + 35, reward_s))
    bars_svg = "\n  ".join(bars)
    return ("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 460" role="img"
     aria-label="Staircase chart of Bitcoin's block reward across eight eras, each exactly
     half the one before, with a real date range under every bar and the current era
     marked WE ARE HERE">
  <rect width="900" height="460" fill="#0a0f1a"/>
  <text x="450" y="46" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif"
        font-size="21" fill="#e8dfd2">Every halving is worth exactly half of the one before it</text>
  <text x="450" y="70" text-anchor="middle" font-family="Georgia, serif" font-size="14"
        fill="#94a3b8" font-style="italic">block reward, by era — each era is 210,000 blocks,
  roughly four years</text>
  <line x1="60" y1="340" x2="880" y2="340" stroke="rgba(255,255,255,.22)" stroke-width="1.5"/>
  %(bars)s
  <line x1="812" y1="339" x2="850" y2="339" stroke="rgba(255,255,255,.18)" stroke-width="1.2"
        stroke-dasharray="2,4"/>
  <text x="830" y="400" text-anchor="middle" font-family="Georgia, serif" font-size="14.5"
        fill="#94a3b8" font-style="italic">and more halvings</text>
  <text x="830" y="420" text-anchor="middle" font-family="Georgia, serif" font-size="14.5"
        fill="#94a3b8" font-style="italic">after that, until</text>
  <text x="830" y="440" text-anchor="middle" font-family="Georgia, serif" font-size="14.5"
        fill="#94a3b8" font-style="italic">≈%(zero_year)s</text>
  <text x="60" y="415" font-family="Georgia, serif" font-size="14" fill="#94a3b8">
    Half a coin, half again — never zero, until the reward finally can't be divided any further.
  </text>
</svg>""") % {"bars": bars_svg, "zero_year": stats["zero_reward_year"]}


def _btc_template(body, stats):
    """Substitute every {{BTC_*}} token in an entry body with a freshly
    computed value. Plain string .replace(), not str.format() — the body is
    prose that may one day contain a literal curly brace, and .replace() is
    a silent no-op for any token this stats dict doesn't touch, which is
    exactly the safety property a templated ENTRY needs (every other entry
    in this publication has none of these tokens and is untouched by this).
    """
    tokens = {
        "{{BTC_SUPPLY}}": "{:,.0f}".format(stats["supply"]),
        "{{BTC_HEIGHT}}": "{:,}".format(stats["height"]),
        "{{BTC_PCT}}": "{:.2f}".format(stats["pct"]),
        "{{BTC_REMAINING}}": "{:,.0f}".format(stats["remaining"]),
        "{{BTC_REWARD}}": "{:g}".format(stats["reward"]),
        "{{BTC_DAILY}}": "{:.0f}".format(stats["daily_new"]),
        "{{BTC_DAILY_NEXT}}": "{:.0f}".format(stats["daily_next"]),
        "{{BTC_NEXT_HALVING_BLOCK}}": "{:,}".format(stats["next_halving_block"]),
        "{{BTC_BLOCKS_TO_GO}}": "{:,}".format(stats["blocks_to_go"]),
        "{{BTC_MONTHS_TO_GO}}": "{:.0f}".format(stats["months_to_go"]),
        "{{BTC_ZERO_YEAR}}": str(stats["zero_reward_year"]),
        "{{BTC_STAMP}}": stats["stamp"],
        "{{BTC_SUPPLY_BAR_SVG}}": _btc_supply_bar_svg(stats),
        "{{BTC_HALVING_SVG}}": _btc_halving_staircase_svg(stats),
    }
    for token, value in tokens.items():
        body = body.replace(token, value)
    return body


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
        live = meta.get("live", "").strip().lower() in ("true", "yes", "1")

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
            "live": live,
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


def _nav(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    return ('<nav class="nav">'
            '<a href="index.html"%s>Writing</a>'
            '<a href="board.html"%s>Asset Board</a>'
            '<a href="bitcoin.html"%s>Bitcoin Board</a>'
            '<a href="ask.html"%s>Ask</a>'
            '<a href="feed.xml">RSS</a>'
            '<a class="sib" href="%s" title="%s">%s →</a>'
            '</nav>' % (cls("home"), cls("board"), cls("bitcoin"), cls("ask"),
                        SIBLING_URL, esc(SIBLING_BLURB), esc(SIBLING_NAME)))


def _chrome(active=""):
    """Header used by every page in the publication."""
    return ('<header class="hsm">'
            '<a class="brand" href="index.html">%s'
            '<span class="wm">The Librarian\'s <span class="em">Ledger</span></span></a>'
            '%s</header>' % (MARK_SVG.replace("__ACCENT__", ACCENT), _nav(active)))


def _foot():
    return ('<footer>%s · <a href="board.html">The Asset Board</a> · '
            '<a href="bitcoin.html">The Bitcoin Board</a> · '
            '<a href="tags.html">All tags</a> · <a href="ask.html">Ask a question</a> · '
            '<a href="feed.xml">RSS</a> · <a href="%s">%s</a> · '
            'nothing here is investment advice</footer>'
            % (esc(SITE_NAME), SIBLING_URL, esc(SIBLING_NAME)))


def _entry_hero(e):
    if not e["hero"]:
        return ""
    dims = blogkit.dim_attrs(os.path.join(OUT, "img"), e["hero"])
    cap = "<figcaption>%s</figcaption>" % esc(e["hero_credit"]) if e["hero_credit"] else ""
    return ('<figure class="hero"><img src="img/%s" alt="%s"%s loading="eager"/>%s</figure>'
            % (esc(e["hero"]), esc(e["hero_alt"]), dims, cap))


def _ask_nudge(e):
    """The reach of a comments section without running one. The entry title rides
    along in `re=` so a message arrives saying what prompted it."""
    return ('<div class="respond">'
            '<p><strong>Got a question?</strong> Something here you want pushed on, '
            'or think I have wrong? <a href="ask.html?re=%s">Ask Mr. Librarian</a> — '
            'it goes straight to my desk.</p></div>'
            % urllib.parse.quote(e["title"]))


def build_entry_page(e, board=None):
    """Render one entry. Returns None for a `live: true` entry when board
    data can't supply a live block height (see _btc_live_stats) — the
    caller's job in that case is to leave the file exactly as it last
    successfully built, never to overwrite it with something broken or
    silently wrong.
    """
    body = e["body"]
    date_line = blogkit.pretty_date(e["date"]).upper()
    if e.get("live"):
        stats = _btc_live_stats(board or {})
        if stats is None:
            return None
        body = _btc_template(body, stats)
        date_line += (' <span class="live-stamp">· numbers refreshed %s, straight from '
                      'the chain</span>' % esc(stats["stamp"]))

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
  %(nudge)s
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
        "date": date_line,
        "hero": _entry_hero(e),
        "body": body,
        "tags": _tag_chips(e),
        "nudge": _ask_nudge(e),
    }


def _entry_card(e):
    return ('    <a class="ecard" href="%s">\n'
            '      <span class="ec-d">%s</span>\n'
            '      <span class="ec-t">%s</span>\n'
            '      <span class="ec-s">%s</span>\n'
            '    </a>' % (esc(e["file"]), blogkit.pretty_date(e["date"]).upper(),
                          esc(e["title"]), esc(e["summary"])))


def _shell(*, title, desc, url, body, active="", noindex=False, og_type="website",
           extra_css="", extra_js=""):
    """`extra_css`/`extra_js` exist so one page's chrome does not become every
    page's weight. Every page inlines its whole stylesheet (no external CSS file
    to fetch), so a Bitcoin-board-only grid appended to the shared CSS would ride
    along on all thirty pages that never use a line of it."""
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
<style>%(css)s</style>
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
       # The accent is substituted in the SCRIPT too, not just the stylesheet.
       # Page JavaScript that builds SVG has to name the colour somewhere, and
       # a sentinel left in reaches the browser as a colour it cannot parse —
       # which silently paints the thing black rather than erroring.
       "js": ("<script>\n%s\n</script>\n" % extra_js.replace("__ACCENT__", ACCENT)
              if extra_js else ""),
       "chrome": _chrome(active), "body": body, "foot": _foot()}



def build_ask():
    """The one place a reader can reach the librarian about money writing.

    Posts to FormSubmit, so there is no backend, no database and no cookie. The
    `re` query parameter carries which entry the reader came from (set by the
    per-entry nudge) and is filled in client-side.

    ⚠️ The expectations paragraph is not boilerplate. This is a publication about
    money, so "what should I buy?" is the question it will attract most, and it
    is the one question that must never get an answer here — not out of caution
    but because answering it would be giving individual financial advice to a
    stranger whose circumstances are unknown. Saying so on the form is kinder
    than saying it in a reply, and it steers people toward the questions that
    can actually be answered well.
    """
    body = """  <section class="asklede">
    <h1 class="wtitle">Ask Mr. Librarian</h1>
    <p class="wsub">A question about something written here, a correction, or a number
    you think is wrong. It goes straight to my desk.</p>
  </section>

  <div class="panel">
    <form action="%(endpoint)s" method="POST" class="askform">
      <input type="hidden" name="_subject" value="The Librarian's Ledger — a question from a reader"/>
      <input type="hidden" name="_template" value="table"/>
      <input type="hidden" name="_next" value="%(next)s"/>
      <!-- Honeypot: a real person never sees this, a bot fills it in. -->
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>

      <label>What is this about? <span class="opt">(optional)</span>
        <input type="text" name="entry" id="entryField"
               placeholder="An entry, the board, or leave blank"/>
      </label>
      <label>Your name <span class="opt">(optional)</span>
        <input type="text" name="name" placeholder="However you'd like to be known — or leave blank"/>
      </label>
      <label>Your email <span class="opt">(optional — only if you'd like a reply)</span>
        <input type="email" name="email" placeholder="you@example.com"/>
      </label>
      <label>Your question <span class="req">(required)</span>
        <textarea name="message" required rows="7"
          placeholder="Why is silver's number the softest on the board? What actually happens if a hardware wallet maker goes under?"></textarea>
      </label>
      <button class="btn" type="submit">Send it</button>
      <p class="formnote">Sending shows a quick captcha to keep the robots out, then brings
      you back here. Nothing is posted publicly — messages go to my inbox and I read all
      of them.</p>
    </form>
  </div>

  <div class="panel expect">
    <h2>What I can and can't answer</h2>
    <p><b>Ask me</b> how a number on the board is worked out, why I think an estimate is
    soft, what I actually do about something and why, or to tell me I have got a fact
    wrong — that last one is the most useful message anyone sends.</p>
    <p><b>Don't ask me</b> what to buy, when to buy it, or what to do with your money.
    I am not going to answer that, and you should be wary of anyone who would: they do
    not know your circumstances, your taxes, or what would keep you up at night. Nothing
    on this site is investment advice and no reply from me will be either.</p>
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
                  desc="Ask a question about something written on %s, or tell me I have "
                       "a number wrong." % SITE_NAME,
                  url="%sask.html" % BASE_URL, active="ask", body=body)


def build_thanks():
    body = """  <section class="asklede">
    <h1 class="wtitle">It's on the desk</h1>
  </section>
  <div class="panel">
    <p><b>Your question is in.</b> Thank you — I read everything that arrives, and
    being told I have a number wrong is the most useful thing anyone sends.</p>
    <p>If you left an email and it wants an answer, you'll get one. Meanwhile there is
    <a href="index.html">the rest of the writing</a>, and
    <a href="board.html">the board</a>.</p>
  </div>
"""
    # noindex: this page exists only as somewhere to land after submitting.
    return _shell(title="Question received — %s" % SITE_NAME,
                  desc="Your question is on the librarian's desk.",
                  url="%sthanks.html" % BASE_URL, body=body, noindex=True)


def build_front(entries, board, stats=None):
    """The publication's front page: what has been written, newest first.

    The board used to live here and has moved to its own page. It is a standing
    reference that rewrites itself every few hours, not a piece of writing, and
    keeping it at the top pushed the actual entries below the fold on a laptop —
    which is a strange thing for a publication to do to its own writing.
    """
    btc = board.get("btc_rank")
    board_line = ("Gold, silver, the biggest public companies and Bitcoin, ranked by "
                  "what the market says they are worth")
    if btc:
        board_line += " — Bitcoin currently sits at #%d" % btc
    board_card = """    <a class="ecard board-card" href="board.html">
      <span class="ec-d">STANDING PAGE · UPDATED THROUGH THE DAY</span>
      <span class="ec-t">The Asset Board</span>
      <span class="ec-s">%s.</span>
    </a>""" % esc(board_line)

    # The Bitcoin board's card only appears once there is a board to link to. A
    # card promising a live page, pointing at a file the build never wrote
    # because the network was down, is worse than no card.
    if stats and stats.get("tip", {}).get("height"):
        btc_line = ("Block height, supply, difficulty, the mempool and the next "
                    "halving — the network's own numbers, live while you watch")
        board_card += """
    <a class="ecard board-card" href="bitcoin.html">
      <span class="ec-d">STANDING PAGE · LIVE</span>
      <span class="ec-t">The Bitcoin Board</span>
      <span class="ec-s">%s.</span>
    </a>""" % esc(btc_line)

    cards = "\n".join(_entry_card(e) for e in entries)
    intro = '  <p class="tag ftag">%s</p>\n' % esc(TAGLINE)
    return _shell(
        title="%s — %s" % (SITE_NAME, TAGLINE),
        desc=BLURB, url=BASE_URL, active="home",
        body="""%s  <section class="writing">
%s
%s
  </section>
""" % (intro, board_card, cards))


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
    """Every tag, as one browsable page. The thing that makes a tag system
    usable once there are more tags than fit in a sidebar."""
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
/* 760px is this publication's reading measure (see .lede and .entry). Without
   it the methods panel inherits the full 1,016px column and sets prose about
   145 characters to the line, which is roughly twice a comfortable measure. */
.panel p,.panel ul{max-width:760px}
.panel p{margin:0 0 12px;color:#b9c6d8;font-size:15px}
.panel p:last-child{margin-bottom:0}
.panel code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13.5px;
  color:__ACCENT__;background:#0e1724;padding:1px 6px;border-radius:4px}
.panel ul{margin:0 0 12px;padding-left:20px;color:#b9c6d8;font-size:15px}
.panel li{margin:0 0 6px}
footer{margin:52px 0 0;padding-top:22px;border-top:1px solid #131b27;text-align:center;
  color:#6e7d92;font-size:13.5px;font-family:ui-sans-serif,system-ui,sans-serif}
.ftag{margin:20px 0 26px;color:#93a4bd;font-size:15px;font-style:italic;text-align:center}

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

/* ── nav + cross-publication link ────────────────────────────────────────── */
header.hsm{display:flex;align-items:center;justify-content:space-between;gap:18px;
  flex-wrap:wrap;padding:26px 0 8px;border-bottom:1px solid #131b27;margin-bottom:4px}
.nav{display:flex;align-items:center;gap:20px;flex-wrap:wrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:14.5px}
.nav a{color:#93a4bd;text-decoration:none}
.nav a:hover{color:#e8eef7}
.nav a.on{color:__ACCENT__}
.nav a.sib{color:#7f8fa6;padding-left:20px;border-left:1px solid #1e2938;font-style:italic}
.nav a.sib:hover{color:#e8865c}          /* the other publication's own accent */

.btitle{font-size:31px;font-weight:400;margin:26px 0 12px;letter-spacing:.01em}
.board-card{border-color:#22384a}
.board-card .ec-d{color:__ACCENT__}

/* ── tags ────────────────────────────────────────────────────────────────── */
a.tg{text-decoration:none;transition:border-color .15s,color .15s}
a.tg:hover{border-color:__ACCENT__;color:#e8eef7}
.taglist{gap:9px}
.taglist .tg{font-size:13.5px;padding:6px 13px}
.tgn{color:#5a6b80;margin-left:6px;font-variant-numeric:tabular-nums}

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
.edate .live-stamp{letter-spacing:normal;text-transform:none;font-style:italic;color:#5a6b80}
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
.wtitle{margin:0 0 6px;font-size:23px;font-weight:400;color:#e8eef7}
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


BOARD_BODY_TEMPLATE = """  <div class="tw">
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
%(rows)s
    </tbody>
  </table>
  </div>

  <div class="panel">
    <h2>How these numbers are made</h2>
    <p>A market capitalisation is just a price multiplied by a count of the thing. For a
    company that count is public and exact. For gold and silver it is a genuine estimate.
    For Bitcoin, it turns out not to be a guess at all — it can be computed exactly from
    public information anyone can check. The working for all four is shown here rather
    than asked to be taken on faith:</p>
    <ul>
      <li><b>Companies</b> — market cap as reported for the listed shares.</li>
      <li><b>Gold</b> — spot price × <code>%(gold)s tonnes</code> of above-ground stock,
      converted at 32,150.7466 troy ounces per tonne.</li>
      <li><b>Silver</b> — the same arithmetic on <code>%(silver)s tonnes</code>. Silver's
      above-ground figure is the softest number on this page; estimates differ a great deal
      depending on whether industrial silver that has been used up is counted.</li>
      <li><b>Bitcoin</b> — price × <code>%(btcc)s</code> coins, computed exactly from
      block height <code>%(btch)s</code> and Bitcoin's own halving schedule. Not an
      estimate — <a href="how-many-bitcoins-are-there.html">the arithmetic is worked
      out here →</a>.</li>
    </ul>
    <p>Gold and silver's tonnage estimates move slowly and are refreshed about once a
    year. Everything else on this board — prices, company values, and now Bitcoin's exact
    coin count — refreshes roughly hourly. The 30-day line is a shape, not a scale — each
    one is drawn to its own high and low, so two sparklines cannot be compared against
    each other.</p>
    <p>This is a curated list, not every asset on earth: the metals, Bitcoin, and the
    large companies that sit near enough to Bitcoin's rank to give it context. Nothing here
    is investment advice, and nothing here is for sale.</p>
  </div>

"""


def build_board(board):
    """The standing asset board. Its own page since 2026-08-07 — it was the front
    page, but a publication's front page should be its writing."""
    assets = board.get("assets", [])
    btc_rank = board.get("btc_rank")
    consts = board.get("constants", {})
    gold_t = consts.get("gold_tonnes")
    silver_t = consts.get("silver_tonnes")
    btc_c = consts.get("btc_circulating")
    btc_h = consts.get("btc_block_height")

    btc_line = ""
    if btc_rank:
        btc_line = ('<span class="dot">·</span><span class="hl">Bitcoin is the '
                    '#%d largest asset on earth</span>' % btc_rank)
    rows = "\n".join(row(a, btc_rank) for a in assets)

    desc = ("The largest assets in the world by market capitalisation — gold, silver, "
            "the biggest public companies and Bitcoin"
            + (", where Bitcoin currently ranks #%d" % btc_rank if btc_rank else "") + ".")

    body = """  <h1 class="btitle">The Asset Board</h1>
  <p class="lede">%(blurb)s</p>
  <p class="stamp">Updated %(gen)s%(btc)s</p>
%(table)s
""" % {"blurb": esc(BLURB), "gen": esc(board.get("generated", "—")),
       "btc": btc_line, "table": BOARD_BODY_TEMPLATE % {"rows": rows,
                                                        "gold": "{:,}".format(gold_t),
                                                        "silver": "{:,}".format(silver_t),
                                                        "btcc": "{:,}".format(btc_c),
                                                        "btch": ("{:,}".format(btc_h)
                                                                 if btc_h else "the current block")}}

    # The <title> keeps the descriptive phrase the H1 used to carry. "The Asset
    # Board" is what it is CALLED (and now has a sibling it must be told apart
    # from); "the biggest assets in the world" is what anyone actually searches
    # for, and dropping it from the title to match the shorter H1 would trade a
    # real search term for a house name nobody is looking up yet.
    return _shell(title="The Asset Board — the biggest assets in the world",
                  desc=desc, url="%sboard.html" % BASE_URL, active="board", body=body)


# ───────────────────────────────────────────────────────── the Bitcoin board ──
#
# A standing page for the network's own numbers, the way board.html is a standing
# page for the world's assets. Rendered from source/finance/bitcoin_stats.json
# (tools/fetch_bitcoin_stats.py) plus asset_board.json for the gold comparison.
#
# THREE KINDS OF NUMBER LIVE ON THIS PAGE AND THEY ARE NOT THE SAME KIND OF TRUE.
# The page says which is which, in its own methods panel, because a dashboard that
# presents an hourly snapshot, a live poll and a deterministic clock in identical
# type is quietly lying about two of them:
#   1. COMPUTED — supply, halvings, milestones. Bitcoin's issuance is a public rule;
#      these are arithmetic on the live block height and are exact.
#   2. POLLED   — price, height, mempool, fees, difficulty, hash rate. Baked at
#      build time and then refreshed in the reader's browser (see BB_JS).
#   3. SNAPSHOT — chain size, all-time totals, Lightning. Hourly at best, and
#      Lightning's own upstream snapshot can be days old, so it carries its date.

SATS = 100_000_000
TYPICAL_TX_VBYTES = 141    # 1 input, 2 outputs, native segwit — the ordinary case


def _n(v, dp=0):
    """Comma-grouped, or an em dash when the source did not answer. Never 0:
    a zero that means "we don't know" is the most expensive kind of wrong on a
    page like this."""
    return "—" if v is None else f"{v:,.{dp}f}"


def _usd(v, dp=0):
    return "—" if v is None else f"${v:,.{dp}f}"


def _hashrate_fmt(v):
    """907647359369144800000 -> '907.6 EH/s'."""
    if not v:
        return "—"
    for unit, size in (("ZH/s", 1e21), ("EH/s", 1e18), ("PH/s", 1e15), ("TH/s", 1e12)):
        if v >= size:
            return f"{v / size:,.1f} {unit}"
    return f"{v:,.0f} H/s"


def _bytes_fmt(v):
    if not v:
        return "—"
    for unit, size in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6)):
        if v >= size:
            return f"{v / size:,.1f} {unit}"
    return f"{v:,.0f} B"


def _clock(seconds):
    """'588d 04:11:22'. The pre-JavaScript paint of every countdown on the page,
    so the numbers are right for a reader with scripting off — they simply do
    not tick."""
    if seconds is None or seconds < 0:
        return "—"
    d, rem = divmod(int(seconds), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return ("%sd " % f"{d:,}" if d else "") + "%02d:%02d:%02d" % (h, m, s)


def _ago(seconds):
    if seconds is None or seconds < 0:
        return "—"
    seconds = int(seconds)
    if seconds < 60:
        return "%ds ago" % seconds
    if seconds < 3600:
        return "%dm %ds ago" % (seconds // 60, seconds % 60)
    return "%dh %dm ago" % (seconds // 3600, seconds % 3600 // 60)


def _btc_height_at_supply(target_btc):
    """The first block at which cumulative issuance reaches `target_btc`.

    The inverse of the subsidy sum, and the only way to date a supply
    milestone: "when was 95% of all bitcoin issued" is a question about a block
    height, which _btc_era_date() can then turn into a date.
    """
    target = int(round(target_btc * SATS))
    total = 0
    for epoch in range(64):
        subsidy = (50 * SATS) >> epoch
        if subsidy == 0:
            return None
        lo = max(1, epoch * BTC_HALVING_INTERVAL)
        hi = epoch * BTC_HALVING_INTERVAL + BTC_HALVING_INTERVAL - 1
        blocks = hi - lo + 1
        if total + blocks * subsidy >= target:
            return lo + -(-(target - total) // subsidy) - 1
        total += blocks * subsidy
    return None


def _bb_milestone(fraction):
    """'≈March 12, 2035' — the ≈ is load-bearing. Every date past the last real
    halving is extrapolated at Bitcoin's 10-minute target, and real blocks do
    not keep to it."""
    h = _btc_height_at_supply(BTC_TRUE_MAX * fraction)
    if h is None:
        return "—"
    d, exact = _btc_era_date(h)
    return ("" if exact else "≈") + blogkit.pretty_date(d)


def _bb_chart(points, w=320, h=62, cls="bbchart"):
    """A wide area chart from [[timestamp, value], …], scaled to its own range.

    Same honesty caveat as the board's sparklines: this is a SHAPE, not a scale.
    It carries no axis because it is drawn between its own high and low, so two
    of these cannot be compared against each other.
    """
    vals = [p[1] for p in (points or [])
            if isinstance(p, list) and len(p) == 2 and isinstance(p[1], (int, float))]
    if len(vals) < 3:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    step = w / (len(vals) - 1)
    pts = " ".join("%.1f,%.1f" % (i * step, h - 4 - (v - lo) / span * (h - 8))
                   for i, v in enumerate(vals))
    # ACCENT, not the __ACCENT__ sentinel: _shell only substitutes that inside the
    # stylesheet, so a placeholder left in the body reaches the browser as a colour
    # it cannot parse and the chart paints itself black. (Which it did, once.)
    return ('<svg class="%s" viewBox="0 0 %d %d" preserveAspectRatio="none" '
            'aria-hidden="true" focusable="false">'
            '<polygon points="0,%d %s %d,%d" fill="%s" opacity=".14"/>'
            '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.7" '
            'stroke-linejoin="round" stroke-linecap="round" '
            'vector-effect="non-scaling-stroke"/></svg>'
            % (cls, w, h, h, pts, w, h, ACCENT, pts, ACCENT))


def _bb_row(label, value, vid=None, note=None, cls=""):
    """One label/value line. `vid` is the id the live layer writes into — a row
    without one is a number that genuinely cannot change between builds."""
    return ('<div class="bbrow"><span class="bbk">%s%s</span>'
            '<span class="bbv%s"%s>%s</span></div>'
            % (esc(label),
               '<span class="bbn">%s</span>' % esc(note) if note else "",
               (" " + cls) if cls else "",
               ' id="%s"' % vid if vid else "", value))


def _bb_card(title, rows, extra=""):
    return ('  <section class="bbc">\n    <h2>%s</h2>\n%s%s\n  </section>'
            % (esc(title), "\n".join("    " + r for r in rows if r), extra))


# The coin in the page title. Drawn as geometry rather than set as the ₿
# character (U+20BF) on purpose: that codepoint arrived in Unicode 10 and is
# still missing from plenty of installed fonts, including some builds of the
# Georgia this publication sets its headings in. A tofu box in an <h1> is worse
# than no icon at all, and a path renders identically everywhere.
BB_COIN_SVG = """<span class="bbmark" aria-hidden="true"><svg viewBox="0 0 44 44">
  <defs>
    <linearGradient id="bbCoinFace" x1="0.15" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#ffd694"/>
      <stop offset="46%" stop-color="__ACCENT__"/>
      <stop offset="100%" stop-color="#a85c07"/>
    </linearGradient>
    <linearGradient id="bbCoinRim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffe3b4"/>
      <stop offset="100%" stop-color="#7d4304"/>
    </linearGradient>
  </defs>
  <circle cx="22" cy="22" r="21" fill="url(#bbCoinRim)"/>
  <circle cx="22" cy="22" r="18.4" fill="url(#bbCoinFace)"/>
  <g stroke="#fffaf0" fill="none">
    <!-- The prongs run UNDER the letter and are drawn first, so the bowls'
         bars cap them cleanly. Round ends; the letter's own strokes are butt
         ended, because a round cap on the stem overshoots the top bar and
         leaves a bump on the left shoulder. -->
    <g stroke-width="2.2" stroke-linecap="round">
      <path d="M16.9 8.7v5.4M23.4 8.7v5.4M16.9 29.9v5.4M23.4 29.9v5.4"/>
    </g>
    <g stroke-width="3.4" stroke-linecap="butt" stroke-linejoin="round">
      <path d="M16.9 13.6v16.8"/>
      <!-- The bars start at the stem's OUTER edge (16.9 − 3.4/2 = 15.2), not at
           its centre line: starting at the centre leaves the letter's top edge
           1.7 higher to the right of x=16.9 than to the left of it, which reads
           as a shelf cut out of the left shoulder. -->
      <path d="M15.2 13.6h7a4.05 4.05 0 010 8.1H15.2"/>
      <path d="M15.2 21.7h7.8a4.35 4.35 0 010 8.7H15.2"/>
    </g>
  </g>
</svg></span>"""


BB_CSS = """
/* ── The Bitcoin Board ────────────────────────────────────────────────────────
   Appended to that one page only (see _shell's extra_css), because every page
   here inlines its whole stylesheet and thirty pages should not carry a grid
   none of them draws. Namespaced .bb* so it can never reach the asset table. */
/* The coin, and the glow behind it. The glow is a separate blurred layer
   rather than a shadow on the SVG so it can breathe on its own timing without
   the coin itself moving — a title that pulses is a title that is hard to
   read. Sized in em, so it tracks the heading at every breakpoint. */
.bbmark{position:relative;display:inline-flex;align-items:center;justify-content:center;
  width:1.16em;height:1.16em;margin-right:.34em;vertical-align:-.17em}
.bbmark::before{content:"";position:absolute;inset:-58%;border-radius:50%;
  background:radial-gradient(circle,rgba(247,147,26,.60) 0%,rgba(247,147,26,.34) 32%,
    rgba(247,147,26,.10) 55%,rgba(247,147,26,0) 72%);
  animation:bbglow 4.2s ease-in-out infinite}
.bbmark svg{position:relative;width:100%;height:100%;display:block;
  filter:drop-shadow(0 1px 7px rgba(247,147,26,.60))}
@keyframes bbglow{0%,100%{opacity:.6;transform:scale(.92)}
  50%{opacity:1;transform:scale(1.08)}}

.bblede{margin:10px 0 0;color:#b9c6d8;font-size:16.5px;max-width:780px}
.bbstamp{margin:15px 0 0;color:#7f8fa6;font-size:13.5px;display:flex;
  align-items:center;gap:9px;flex-wrap:wrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbdot{width:8px;height:8px;border-radius:50%;background:#4ade80;flex:0 0 8px;
  animation:bbpulse 2.6s ease-out infinite}
.bbdot.off{background:#6e7d92;animation:none}
@keyframes bbpulse{0%{box-shadow:0 0 0 0 rgba(74,222,128,.5)}
  70%{box-shadow:0 0 0 7px rgba(74,222,128,0)}
  100%{box-shadow:0 0 0 0 rgba(74,222,128,0)}}
.bbsep{color:#3f4c5f}

.bbhero{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0 0}
.bbh{padding:17px 19px;border:1px solid #24303f;border-radius:13px;
  background:linear-gradient(158deg,#111927 0%,#0a111c 64%)}
.bbh-l{font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:#7f8fa6;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbh-v{margin-top:8px;font-size:28px;line-height:1.1;color:#e8eef7;
  letter-spacing:-.01em;font-variant-numeric:tabular-nums;white-space:nowrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbh-v.am{color:__ACCENT__}
.bbh-s{margin-top:8px;font-size:13px;color:#93a4bd;line-height:1.45}

.bbgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(298px,1fr));
  gap:16px;margin:16px 0 0;align-items:start}
.bbc{border:1px solid #1b2534;border-radius:13px;background:#0a111c;padding:16px 19px}
.bbc h2{margin:0 0 8px;font-size:11.5px;letter-spacing:.15em;text-transform:uppercase;
  font-weight:500;color:__ACCENT__;border:0;padding:0;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbrow{display:flex;align-items:baseline;justify-content:space-between;gap:16px;
  padding:8px 0;border-bottom:1px solid #131b27}
.bbrow:last-child{border-bottom:0}
.bbk{color:#93a4bd;font-size:14.5px;line-height:1.35}
.bbn{display:block;color:#5a6b80;font-size:12px;font-style:italic}
.bbv{color:#e8eef7;font-size:15px;font-weight:600;white-space:nowrap;
  font-variant-numeric:tabular-nums;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbv.am{color:__ACCENT__}.bbv.up{color:#4ade80}.bbv.down{color:#f87171}
/* The flash is the whole "it is alive" signal, so it is deliberately a
   background wash and not a colour change: recolouring the digits makes a
   number that merely refreshed look like a number that moved. */
.bbflash{animation:bbflash 1.4s ease-out}
@keyframes bbflash{0%{background:rgba(247,147,26,.30)}100%{background:transparent}}

.bbbar{margin:13px 0 5px;height:9px;border-radius:999px;background:#151f2c;
  overflow:hidden}
.bbbar i{display:block;height:100%;border-radius:999px;background:__ACCENT__;
  transition:width .6s ease}
.bbbarl{display:flex;justify-content:space-between;gap:12px;color:#6e7d92;
  font-size:12px;font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbchart{margin:12px 0 2px;display:block;width:100%;height:62px}

/* ── the full-width market card ──────────────────────────────────────────── */
.bbwide{grid-column:1/-1}
.bbctl{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;
  justify-content:space-between;margin:4px 0 2px}
.bbbtns{display:flex;flex-wrap:wrap;gap:5px}
.bbb{font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:11.5px;
  letter-spacing:.05em;color:#8b9ab0;background:#0d1521;border:1px solid #1e2938;
  border-radius:7px;padding:5px 9px;cursor:pointer;
  transition:color .14s,border-color .14s,background .14s}
.bbb:hover{color:#e8eef7;border-color:#3a4f66}
.bbb.on{color:#0a111c;font-weight:700;background:__ACCENT__;border-color:__ACCENT__}
/* Each average keeps its own colour on its own button, so the legend IS the
   control — there is no separate key to read against the lines. */
.bbb.m50.on{background:#5eb3d6;border-color:#5eb3d6}
.bbb.m100.on{background:#a78bfa;border-color:#a78bfa}
.bbb.m200.on{background:#e8dfd2;border-color:#e8dfd2}
.bbb.lg.on{background:#4b5f77;border-color:#4b5f77;color:#eef4fb}
.bbchartwrap{position:relative;margin:8px 0 0}
.bbchartwrap svg{display:block;width:100%;height:310px;touch-action:pan-y}
.bbax{fill:#6e7d92;font-size:11px;font-family:ui-sans-serif,system-ui,sans-serif}
.bbgrid-l{stroke:#131b27;stroke-width:1}
.bbcross{stroke:#3f4c5f;stroke-width:1;stroke-dasharray:3 3}
.bbread{position:absolute;top:4px;pointer-events:none;white-space:nowrap;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:12.5px;
  color:#93a4bd;background:rgba(8,14,24,.92);border:1px solid #24303f;
  border-radius:9px;padding:7px 11px;display:none;line-height:1.55}
.bbread b{color:#e8eef7;font-variant-numeric:tabular-nums}
.bbread i{font-style:normal}
.bbnote{margin:8px 0 0;color:#6e7d92;font-size:12.5px;font-style:italic}
.bbstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(166px,1fr));
  gap:4px 20px;margin:12px 0 0;border-top:1px solid #131b27;padding-top:13px}
.bbst{padding:5px 0}
.bbst-l{color:#93a4bd;font-size:13px;line-height:1.35}
.bbst-n{color:#5a6b80;font-size:11.5px;font-style:italic}
.bbst-v{margin-top:3px;color:#e8eef7;font-size:16.5px;font-weight:600;
  font-variant-numeric:tabular-nums;
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
.bbst-v.am{color:__ACCENT__}
@media (max-width:640px){.bbchartwrap svg{height:240px}}
.bbchips{display:flex;flex-wrap:wrap;gap:7px;margin:11px 0 2px}
.bbchip{font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:12px;
  color:#8b9ab0;border:1px solid #1e2938;border-radius:999px;padding:5px 11px;
  background:#0d1521}
.bbchip b{color:#e8eef7;font-variant-numeric:tabular-nums;font-weight:600}
.bbmore{margin:12px 0 0;font-size:13.5px}
.bbasof{margin:11px 0 0;color:#5a6b80;font-size:12.5px;font-style:italic;
  line-height:1.5}

@media (max-width:900px){.bbhero{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){
  .bbhero{grid-template-columns:1fr}
  .bbh-v{font-size:26px}
  .bbgrid{grid-template-columns:1fr}
}

/* Two things here animate forever — the title's glow and the live dot. Both are
   decoration on a number, so both stop for a reader who has asked the system to
   stop moving things.
   ⚠️ This block must stay LAST. Everything in it matches with the same
   specificity as the rule it is overriding, so placed higher up it loses to the
   later declaration and silently does nothing — which is exactly what it did on
   the first attempt (the glow obeyed, the dot kept pulsing). */
@media (prefers-reduced-motion:reduce){
  .bbmark::before{animation:none;opacity:.8}
  .bbdot{animation:none}
}
"""


BB_JS = """
// The Bitcoin Board's live layer.
//
// The page ships complete: every number below is already rendered server-side
// from the hourly snapshot, and this only ever OVERWRITES a value with a fresher
// one. So a reader with JavaScript off, or a mempool.space that is down, gets a
// correct page with an honest "as of" stamp rather than a grid of dashes.
//
// Two clocks, deliberately:
//   fast (60s)  price, chain tip, mempool, fee estimates — things that move
//   slow (5min) difficulty and hash rate — things that cannot move faster
// Both are skipped while the tab is hidden, which is both polite to a free
// public API and pointless to do otherwise.
(function () {
  "use strict";
  var API = "https://mempool.space/api";
  var S = __SEED__;
  var fails = 0, lastOk = Date.now();

  function $(id) { return document.getElementById(id); }

  function set(id, txt, flash) {
    var el = $(id);
    if (!el || txt == null || el.textContent === txt) return;
    el.textContent = txt;
    if (flash) {
      el.classList.remove("bbflash");
      void el.offsetWidth;               // restart the animation, not queue it
      el.classList.add("bbflash");
    }
  }

  function n(v, dp) {
    if (v == null || !isFinite(v)) return "\\u2014";
    dp = dp || 0;
    return v.toLocaleString("en-US",
      { minimumFractionDigits: dp, maximumFractionDigits: dp });
  }
  function usd(v, dp) { return v == null ? "\\u2014" : "$" + n(v, dp); }

  function clock(sec) {
    if (sec == null || sec < 0) return "\\u2014";
    sec = Math.floor(sec);
    var d = Math.floor(sec / 86400), h = Math.floor((sec % 86400) / 3600),
        m = Math.floor((sec % 3600) / 60), s = sec % 60;
    var p = function (x) { return (x < 10 ? "0" : "") + x; };
    return (d ? n(d) + "d " : "") + p(h) + ":" + p(m) + ":" + p(s);
  }

  function ago(sec) {
    if (sec == null || sec < 0) return "\\u2014";
    sec = Math.floor(sec);
    if (sec < 60) return sec + "s ago";
    if (sec < 3600) return Math.floor(sec / 60) + "m " + (sec % 60) + "s ago";
    return Math.floor(sec / 3600) + "h " + Math.floor((sec % 3600) / 60) + "m ago";
  }

  // Bitcoin Core's consensus subsidy rule, summed in whole satoshis — the same
  // arithmetic tools/fetch_bitcoin_stats.py runs server-side, so the supply on
  // screen stays exact between builds instead of freezing at the last one.
  // Note Math.floor(50e8 / 2^e) rather than a shift: 5,000,000,000 overflows
  // JavaScript's 32-bit bitwise operators, and >> would silently wrap it.
  // The total (~2.1e15) is comfortably inside the 2^53 a Number holds exactly.
  function supplyBtc(height) {
    var total = 0;
    for (var e = 0; e < 34; e++) {
      var subsidy = Math.floor(5000000000 / Math.pow(2, e));
      if (subsidy <= 0) break;
      var lo = Math.max(1, e * 210000);
      var hi = Math.min(height, e * 210000 + 209999);
      if (hi >= lo) total += (hi - lo + 1) * subsidy;
    }
    return total / 1e8;
  }

  function render() {
    var price = S.price, h = S.height;
    var supply = supplyBtc(h);
    var cap = price ? supply * price : null;
    var epoch = Math.floor(h / 210000);
    var subsidy = 50 / Math.pow(2, epoch);

    set("bbPrice", usd(price), true);
    set("bbBlock", n(h), true);
    set("bbIssued", n(supply));
    set("bbIssuedPct", (supply / S.maxSupply * 100).toFixed(2) + "%");
    if (price) set("bbSats", n(Math.round(1e8 / price)) + " satoshis to the dollar");

    set("mPrice", usd(price), true);
    set("mCap", cap ? "$" + n(cap / 1e12, 3) + " T" : "\\u2014", true);
    set("mSatsD", price ? n(Math.round(1e8 / price)) : "\\u2014");
    if (price && S.athUsd) {
      set("mAthDown", ((price - S.athUsd) / S.athUsd * 100).toFixed(1) + "%");
      set("mAthDays", n(Math.floor((Date.now() / 1000 - S.athTs) / 86400)) + " days");
    }
    if (price && S.goldPx) set("mGoldOz", n(price / S.goldPx, 1) + " oz");
    if (cap && S.goldCap) set("mGoldPct", (cap / S.goldCap * 100).toFixed(2) + "%");

    set("sIssued", n(supply) + " BTC");
    set("sPct", (supply / S.maxSupply * 100).toFixed(2) + "%");
    set("sLeft", n(S.maxSupply - supply) + " BTC");
    var bar = $("sBar");
    if (bar) bar.style.width = (supply / S.maxSupply * 100).toFixed(2) + "%";
    set("hEpoch", "no. " + (epoch + 1));
    set("hSubsidy", n(subsidy, 3) + " BTC");
    set("hBlocks", n(S.halvingBlock - h) + " blocks");
    set("sPerDay", n(subsidy * 144, 1) + " BTC");

    if (S.hashrate) set("dHash", S.hashrate);
    if (S.difficulty) set("dDiff", n(S.difficulty / 1e12, 1) + " T");
    if (S.retarget) {
      var r = S.retarget;
      var prog = $("dProg");
      if (prog && r.progressPercent != null) {
        prog.style.width = r.progressPercent.toFixed(1) + "%";
      }
      if (r.progressPercent != null) {
        set("dProgTxt", r.progressPercent.toFixed(1) + "% through this epoch");
      }
      if (r.remainingBlocks != null) set("dLeft", n(r.remainingBlocks) + " blocks");
      if (r.difficultyChange != null) {
        set("dChange", (r.difficultyChange >= 0 ? "+" : "") +
            r.difficultyChange.toFixed(2) + "%");
      }
      if (r.timeAvg) set("dBlockTime", (r.timeAvg / 60000).toFixed(1) + " min");
    }

    if (S.mempool) {
      set("pCount", n(S.mempool.count), true);
      set("pVsize", n(S.mempool.vsize / 1e6, 1) + " MvB");
      set("pBlocks", n(Math.ceil(S.mempool.vsize / 1e6)) + " blocks");
      if (price && S.mempool.total_fee != null) {
        set("pFees", usd(S.mempool.total_fee / 1e8 * price));
      }
    }
    if (S.fees) {
      set("fFast", n(S.fees.fastestFee));
      set("fHalf", n(S.fees.halfHourFee));
      set("fHour", n(S.fees.hourFee));
      set("fEcon", n(S.fees.economyFee));
      set("fMin", n(S.fees.minimumFee));
      if (price) {
        set("pTypical", "$" + (S.fees.halfHourFee * """ + str(TYPICAL_TX_VBYTES) + """
          / 1e8 * price).toFixed(2));
      }
    }
    set("cHeight", n(h));
  }

  function tick() {
    var now = Date.now() / 1000;
    if (S.tipTs) set("bbSince", ago(now - S.tipTs));
    // Counted from the LAST BLOCK, not from page load, so the clock re-bases
    // itself every time a block lands instead of drifting all afternoon.
    var base = S.tipTs || now;
    set("bbHalving", clock(base + (S.halvingBlock - S.height) * 600 - now));
    if (S.retarget && S.retarget.estimatedRetargetDate) {
      set("dRetarget", clock(S.retarget.estimatedRetargetDate / 1000 - now));
    }
    var stale = fails > 2;
    set("bbLive", stale
      ? "live updates paused \\u2014 showing the last good reading"
      : "live \\u00b7 refreshed " + ago((Date.now() - lastOk) / 1000));
    var dot = $("bbDot");
    if (dot) dot.className = stale ? "bbdot off" : "bbdot";
  }

  function j(path) {
    return fetch(API + path, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).catch(function () { return null; });
  }

  function fast() {
    if (document.hidden) return;
    Promise.all([j("/v1/blocks"), j("/mempool"),
                 j("/v1/fees/recommended"), j("/v1/prices")]).then(function (r) {
      var ok = false;
      if (r[0] && r[0][0] && r[0][0].height) {
        S.height = r[0][0].height; S.tipTs = r[0][0].timestamp; ok = true;
      }
      if (r[1] && r[1].count != null) { S.mempool = r[1]; ok = true; }
      if (r[2] && r[2].minimumFee != null) { S.fees = r[2]; ok = true; }
      if (r[3] && r[3].USD) { S.price = r[3].USD; ok = true; }
      if (ok) { fails = 0; lastOk = Date.now(); } else { fails++; }
      render(); tick();
      if (ok) chartFollowLive();
    });
  }

  function slow() {
    if (document.hidden) return;
    Promise.all([j("/v1/difficulty-adjustment"),
                 j("/v1/mining/hashrate/3d")]).then(function (r) {
      if (r[0] && r[0].remainingBlocks != null) S.retarget = r[0];
      if (r[1] && r[1].currentHashrate) {
        S.hashrate = fmtHash(r[1].currentHashrate);
        S.difficulty = r[1].currentDifficulty;
      }
      render();
    });
  }

  function fmtHash(v) {
    var units = [["ZH/s", 1e21], ["EH/s", 1e18], ["PH/s", 1e15], ["TH/s", 1e12]];
    for (var i = 0; i < units.length; i++) {
      if (v >= units[i][1]) return n(v / units[i][1], 1) + " " + units[i][0];
    }
    return n(v) + " H/s";
  }

  // ── the price chart ──────────────────────────────────────────────────────
  //
  // Three sources feed one chart, chosen by how far back the range reaches:
  //   weekly  the whole history, baked into this page. Also the ONLY input to
  //           the moving averages — they are 50/100/200-WEEK averages, so they
  //           are a rolling mean over 50/100/200 of these points, full stop.
  //   daily   two years, baked in. Anything from a month to a year.
  //   cb      Coinbase candles, fetched only if a reader asks for 1H/1D/1W.
  //           Baking minute resolution would be pointless — it is stale the
  //           moment it is committed — so those three ranges are live or they
  //           say they are unavailable. They never quietly show daily data
  //           relabelled as an hour.
  var RANGES = {
    "1H":  {span: 3600,         src: "cb", gran: 60},
    "1D":  {span: 86400,        src: "cb", gran: 300},
    "1W":  {span: 7 * 86400,    src: "cb", gran: 3600},
    "1M":  {span: 30 * 86400,   src: "daily"},
    "3M":  {span: 91 * 86400,   src: "daily"},
    "6M":  {span: 182 * 86400,  src: "daily"},
    "YTD": {span: null,         src: "daily"},
    "1Y":  {span: 365 * 86400,  src: "daily"},
    "3Y":  {span: 1095 * 86400, src: "weekly"},
    "10Y": {span: 3652 * 86400, src: "weekly"},
    "ALL": {span: null,         src: "weekly"}
  };
  var MACOL = {50: "#5eb3d6", 100: "#a78bfa", 200: "#e8dfd2"};
  var MON = ["Jan","Feb","Mar","Apr","May","Jun",
             "Jul","Aug","Sep","Oct","Nov","Dec"];
  var CH = {range: "1Y", ma: {}, log: false, logPinned: false, intraday: {},
            pending: {}, note: "", draw: null};
  var maCache = {};

  function maSeries(p) {
    if (maCache[p]) return maCache[p];
    var w = S.weekly || [], out = [], sum = 0;
    for (var i = 0; i < w.length; i++) {
      sum += w[i][1];
      if (i >= p) sum -= w[i - p][1];
      if (i >= p - 1) out.push([w[i][0], sum / p]);
    }
    maCache[p] = out;
    return out;
  }

  function crop(s, from, to) {
    var out = [];
    for (var i = 0; i < s.length; i++) {
      if (s[i][0] >= from && s[i][0] <= to) out.push(s[i]);
    }
    return out;
  }

  // Linear interpolation, so a moving average still draws across a window too
  // short to contain one of its weekly points. On a one-hour view the 200-week
  // average is a flat line — which is exactly what it is, to within a week.
  function sampleAt(s, ts) {
    if (!s.length) return null;
    if (ts <= s[0][0]) return s[0][1];
    if (ts >= s[s.length - 1][0]) return s[s.length - 1][1];
    var lo = 0, hi = s.length - 1;
    while (hi - lo > 1) {
      var m = (lo + hi) >> 1;
      if (s[m][0] <= ts) lo = m; else hi = m;
    }
    var a = s[lo], b = s[hi];
    return a[1] + (b[1] - a[1]) * ((ts - a[0]) / (b[0] - a[0] || 1));
  }

  function coinbase(key, gran) {
    if (CH.pending[key]) return;
    CH.pending[key] = 1;
    fetch("https://api.exchange.coinbase.com/products/BTC-USD/candles" +
          "?granularity=" + gran, {cache: "no-store"})
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (rows) {
        // [time, low, high, open, close, volume], newest first.
        CH.intraday[key] = rows.map(function (c) { return [c[0], c[4]]; })
          .sort(function (a, b) { return a[0] - b[0]; });
      })
      .catch(function () { CH.intraday[key] = []; })
      .then(function () { CH.pending[key] = 0; drawChart(); });
  }

  function niceStep(raw) {
    var mag = Math.pow(10, Math.floor(Math.log10(raw))), n = raw / mag;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * mag;
  }

  // `step` is the gap between neighbouring ticks, and it decides the precision:
  // rounding $81,200 and $81,900 both to "$81k" prints the same label twice and
  // makes the axis unreadable, which is what a one-hour view did at first.
  // Below $1 the trailing zeros are stripped so the axis does not mix "$0.050"
  // with "$1.0" in the same column.
  function axisPx(v, step) {
    if (v >= 1e6) return "$" + n(v / 1e6, v >= 1e7 ? 0 : 1) + "M";
    if (v >= 1e3) {
      var dp = !step ? 0 : step < 100 ? 2 : step < 500 ? 1 : 0;
      return "$" + n(v / 1e3, dp) + "k";
    }
    if (v >= 10) return "$" + n(Math.round(v));
    return "$" + String(+v.toFixed(v >= 1 ? 2 : 4));
  }

  function p2(x) { return (x < 10 ? "0" : "") + x; }

  function axisDate(ts, span) {
    var d = new Date(ts * 1000);
    if (span <= 2 * 86400) return p2(d.getHours()) + ":" + p2(d.getMinutes());
    if (span <= 120 * 86400) return d.getDate() + " " + MON[d.getMonth()];
    if (span <= 1200 * 86400) return MON[d.getMonth()] + " " + d.getFullYear();
    return "" + d.getFullYear();
  }

  function fullDate(ts, span) {
    var d = new Date(ts * 1000);
    var day = d.getDate() + " " + MON[d.getMonth()] + " " + d.getFullYear();
    return span <= 2 * 86400
      ? day + ", " + p2(d.getHours()) + ":" + p2(d.getMinutes())
      : day;
  }

  function esc2(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }

  function drawChart() {
    var svg = $("bbChart"), wrap = $("bbChartWrap"), note = $("bbChartNote");
    if (!svg || !wrap) return;
    var key = CH.range, r = RANGES[key];
    var W = Math.max(320, wrap.clientWidth || 900);
    var H = svg.clientHeight || 310;
    // Both of these are width-dependent because a phone cannot hold a desktop
    // axis: five "Mon YYYY" labels across 358px overlap into gibberish, which
    // is what this drew at 390px before the divisor moved with the width.
    var L = W < 480 ? 46 : 62, R = 14, T = 12, B = 26;
    var nx = W < 420 ? 2 : W < 700 ? 3 : 4;

    var pts;
    if (r.src === "cb") {
      pts = CH.intraday[key];
      if (!pts) { coinbase(key, r.gran); pts = null; }
    } else {
      pts = (r.src === "weekly" ? S.weekly : S.daily) || [];
    }

    if (!pts || pts.length < 2) {
      svg.innerHTML = '<text class="bbax" x="' + L + '" y="' + (H / 2) +
        '">' + (pts ? "That range is not available right now."
                    : "Loading\\u2026") + '</text>';
      if (note) note.textContent = pts
        ? "Coinbase did not answer, so the intraday view is empty. " +
          "Every other range is drawn from data already in this page."
        : "";
      CH.draw = null;
      return;
    }

    var last = pts[pts.length - 1][0];
    var from;
    if (key === "ALL") from = pts[0][0];
    else if (key === "YTD") {
      var d0 = new Date(last * 1000);
      from = new Date(d0.getFullYear(), 0, 1).getTime() / 1000;
    } else from = last - r.span;
    var win = crop(pts, from, last + 1);
    if (win.length < 2) win = pts.slice(-2);

    var x0 = win[0][0], x1 = win[win.length - 1][0];
    var span = x1 - x0 || 1;

    var mas = [];
    [50, 100, 200].forEach(function (p) {
      if (!CH.ma[p]) return;
      var s = maSeries(p);
      if (!s.length) return;
      var body = crop(s, x0, x1), line = body.slice();
      // Meet the window edges ONLY where the average actually exists.
      // Extending it RIGHT is honest — the newest value is the average now, and
      // a weekly series can trail the present by up to a week. Extending it
      // LEFT is not: before its first point there were fewer than 50 (or 100,
      // or 200) weeks of Bitcoin to average, and a flat line reaching back to
      // 2010 claims an average that had nothing behind it. That is what the
      // first cut of this drew.
      var end = s[s.length - 1];
      if (x0 > s[0][0]) line.unshift([x0, sampleAt(s, x0)]);
      if (x1 > end[0]) line.push([x1, end[1]]);
      else if (body.length && x1 > body[body.length - 1][0]) {
        line.push([x1, sampleAt(s, x1)]);
      }
      if (line.length > 1) mas.push({p: p, pts: line, col: MACOL[p]});
    });

    var lo = Infinity, hi = -Infinity;
    win.forEach(function (p) { if (p[1] < lo) lo = p[1]; if (p[1] > hi) hi = p[1]; });
    mas.forEach(function (m) {
      m.pts.forEach(function (p) { if (p[1] < lo) lo = p[1]; if (p[1] > hi) hi = p[1]; });
    });

    var useLog = CH.log && lo > 0;
    if (useLog) { lo /= 1.12; hi *= 1.12; }
    else { var pad = (hi - lo) * 0.06 || hi * 0.02 || 1; lo -= pad; hi += pad;
           if (lo < 0) lo = 0; }
    var t = function (v) { return useLog ? Math.log10(Math.max(v, 1e-9)) : v; };
    var ty0 = t(lo), ty1 = t(hi), tspan = (ty1 - ty0) || 1;
    var X = function (ts) { return L + (W - L - R) * (ts - x0) / span; };
    var Y = function (v) { return T + (H - T - B) * (1 - (t(v) - ty0) / tspan); };

    var yticks = [], st = null;
    if (useLog) {
      var d1 = Math.floor(Math.log10(lo)), d2 = Math.ceil(Math.log10(hi));
      for (var dd = d1; dd <= d2; dd++) {
        [1, 2, 5].forEach(function (m) {
          var v = m * Math.pow(10, dd);
          if (v >= lo && v <= hi) yticks.push(v);
        });
      }
      while (yticks.length > 7) {
        yticks = yticks.filter(function (v, i) { return i % 2 === 0; });
      }
    } else {
      st = niceStep((hi - lo) / 4);
      for (var v0 = Math.ceil(lo / st) * st; v0 <= hi; v0 += st) yticks.push(v0);
    }

    var parts = [];
    yticks.forEach(function (v) {
      var y = Y(v).toFixed(1);
      parts.push('<line class="bbgrid-l" x1="' + L + '" y1="' + y +
                 '" x2="' + (W - R) + '" y2="' + y + '"/>');
      parts.push('<text class="bbax" x="' + (L - 8) + '" y="' + (+y + 3.5) +
                 '" text-anchor="end">' + axisPx(v, st) + '</text>');
    });
    for (var i = 0; i <= nx; i++) {
      var ts = x0 + span * i / nx, x = X(ts).toFixed(1);
      parts.push('<text class="bbax" x="' + x + '" y="' + (H - 8) +
                 '" text-anchor="' +
                 (i === 0 ? "start" : i === nx ? "end" : "middle") + '">' +
                 axisDate(ts, span) + '</text>');
    }

    var line = win.map(function (p) {
      return X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1);
    }).join(" ");
    parts.push('<polygon points="' + X(x0).toFixed(1) + "," + (H - B) + " " +
               line + " " + X(x1).toFixed(1) + "," + (H - B) +
               '" fill="__ACCENT__" opacity=".10"/>');
    mas.forEach(function (m) {
      parts.push('<polyline points="' + m.pts.map(function (p) {
        return X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1);
      }).join(" ") + '" fill="none" stroke="' + m.col +
        '" stroke-width="1.4" stroke-linejoin="round" opacity=".85"/>');
    });
    parts.push('<polyline points="' + line + '" fill="none" stroke="__ACCENT__" ' +
               'stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round"/>');
    parts.push('<g id="bbHover"></g>');

    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.innerHTML = parts.join("");
    CH.draw = {win: win, mas: mas, X: X, Y: Y, x0: x0, x1: x1, span: span,
               W: W, H: H, L: L, R: R, T: T, B: B};

    if (note) {
      note.textContent =
        (r.src === "cb" ? "Live candles from Coinbase, refreshed with the rest of "
                          + "the page."
         : r.src === "daily" ? "Daily closes."
         : "Weekly closes, back to July 2010.") +
        (mas.length ? "  The averages are weekly, so on a short range they are "
                      + "nearly flat \\u2014 which is what a 200-week average is."
                    : "") +
        (useLog ? "  Logarithmic axis." : "");
    }
  }

  function onHover(ev) {
    var d = CH.draw, g = $("bbHover"), read = $("bbRead"), svg = $("bbChart");
    if (!d || !g || !read || !svg) return;
    var box = svg.getBoundingClientRect();
    var px = (ev.clientX - box.left) * (d.W / box.width);
    if (px < d.L || px > d.W - d.R) { onLeave(); return; }
    var ts = d.x0 + (px - d.L) / (d.W - d.L - d.R) * d.span;
    var best = d.win[0], bd = Infinity;
    for (var i = 0; i < d.win.length; i++) {
      var dist = Math.abs(d.win[i][0] - ts);
      if (dist < bd) { bd = dist; best = d.win[i]; }
    }
    var hx = d.X(best[0]), hy = d.Y(best[1]);
    g.innerHTML = '<line class="bbcross" x1="' + hx.toFixed(1) + '" y1="' + d.T +
      '" x2="' + hx.toFixed(1) + '" y2="' + (d.H - d.B) + '"/>' +
      '<circle cx="' + hx.toFixed(1) + '" cy="' + hy.toFixed(1) +
      '" r="3.4" fill="__ACCENT__" stroke="#0a111c" stroke-width="1.4"/>';
    var html = '<i>' + esc2(fullDate(best[0], d.span)) + '</i><br><b>' +
      usd(Math.round(best[1] * 100) / 100, best[1] < 10 ? 2 : 0) + '</b>';
    d.mas.forEach(function (m) {
      var v = sampleAt(m.pts, best[0]);
      if (v == null) return;
      html += '<br><span style="color:' + m.col + '">' + m.p + 'W</span> ' +
              usd(Math.round(v), 0);
    });
    read.innerHTML = html;
    read.style.display = "block";
    var w = read.offsetWidth || 120;
    var leftPx = (hx / d.W) * box.width + 14;
    if (leftPx + w > box.width - 4) leftPx = (hx / d.W) * box.width - w - 14;
    read.style.left = Math.max(2, leftPx) + "px";
  }

  function onLeave() {
    var g = $("bbHover"), read = $("bbRead");
    if (g) g.innerHTML = "";
    if (read) read.style.display = "none";
  }

  function syncChartButtons() {
    var rs = document.querySelectorAll("#bbRanges .bbb");
    for (var i = 0; i < rs.length; i++) {
      rs[i].classList.toggle("on", rs[i].getAttribute("data-r") === CH.range);
    }
    [50, 100, 200].forEach(function (p) {
      var b = document.querySelector('.bbb[data-ma="' + p + '"]');
      if (b) b.classList.toggle("on", !!CH.ma[p]);
    });
    var lg = $("bbLog");
    if (lg) lg.classList.toggle("on", CH.log);
  }

  function setRange(k) {
    CH.range = k;
    // Log is chosen for you on the ranges where a linear axis is useless — a
    // sixteen-year Bitcoin chart on a linear scale is a flat line with a spike
    // on the end — and left alone once you have said what you want.
    if (!CH.logPinned) CH.log = (k === "3Y" || k === "10Y" || k === "ALL");
    syncChartButtons();
    drawChart();
  }

  function wireChart() {
    var rs = document.querySelectorAll("#bbRanges .bbb");
    for (var i = 0; i < rs.length; i++) {
      rs[i].addEventListener("click", function () {
        setRange(this.getAttribute("data-r"));
      });
    }
    [50, 100, 200].forEach(function (p) {
      var b = document.querySelector('.bbb[data-ma="' + p + '"]');
      if (!b) return;
      b.addEventListener("click", function () {
        CH.ma[p] = !CH.ma[p];
        syncChartButtons();
        drawChart();
      });
    });
    var lg = $("bbLog");
    if (lg) lg.addEventListener("click", function () {
      CH.log = !CH.log; CH.logPinned = true;
      syncChartButtons(); drawChart();
    });
    var svg = $("bbChart");
    if (svg) {
      svg.addEventListener("mousemove", onHover);
      svg.addEventListener("mouseleave", onLeave);
    }
    var t;
    window.addEventListener("resize", function () {
      clearTimeout(t); t = setTimeout(drawChart, 140);
    });
    setRange(CH.range);
  }

  // The newest point in a baked series is "the close so far" for that day or
  // week, so moving it to the live price is what those series MEAN — not a
  // fabricated extra point. Anything older is history and is never touched.
  function chartFollowLive() {
    if (!S.price) return;
    [S.daily, S.weekly].forEach(function (s) {
      if (s && s.length) s[s.length - 1][1] = S.price;
    });
    maCache = {};
    var r = RANGES[CH.range];
    if (r && r.src === "cb") { CH.intraday[CH.range] = null; }
    drawChart();
  }

  tick();
  setInterval(tick, 1000);
  setInterval(fast, 60000);
  setInterval(slow, 300000);
  fast(); slow();
  wireChart();
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) { fast(); slow(); }
  });
})();
"""


def build_bitcoin_board(stats, board):
    """The Bitcoin Board. Returns None when there is no live block height —
    same contract as build_entry_page's live entry: leave the last good page
    on disk rather than publish one full of dashes."""
    tip = (stats or {}).get("tip") or {}
    height = tip.get("height")
    if not height:
        return None

    now = datetime.now(timezone.utc).timestamp()
    price = stats.get("price_usd")
    supply = stats["supply_sats"] / SATS
    cap = supply * price if price else None
    epoch = height // BTC_HALVING_INTERVAL
    subsidy = BTC_INITIAL_SUBSIDY / (2 ** epoch)
    halving_block = (epoch + 1) * BTC_HALVING_INTERVAL
    blocks_to_halving = halving_block - height
    halving_date, _ = _btc_era_date(halving_block)
    issued_pct = supply / BTC_TRUE_MAX * 100
    per_day = subsidy * 144
    annual_pct = per_day * 365 / supply * 100 if supply else None
    s2f = supply / (per_day * 365) if per_day else None

    ath = stats.get("ath") or {}
    ath_usd, ath_ts = ath.get("usd"), ath.get("ts")
    gold = next((a for a in board.get("assets", []) if a.get("symbol") == "GOLD"), {})
    gold_px, gold_cap = gold.get("price"), gold.get("market_cap")

    rt = stats.get("retarget") or {}
    hr = stats.get("hashrate") or {}
    mp = stats.get("mempool") or {}
    fees = stats.get("fees") or {}
    rw = stats.get("reward_144") or {}
    ln = stats.get("lightning") or {}
    ch = stats.get("chain") or {}

    # ── hero ──────────────────────────────────────────────────────────────
    hero = [
        ("Price", _usd(price), "bbPrice",
         '<span id="bbSats">%s</span>'
         % (_n(round(SATS / price)) + " satoshis to the dollar" if price else "—")),
        ("Block height", _n(height), "bbBlock",
         'last block <span id="bbSince">%s</span>'
         % _ago(now - tip["timestamp"] if tip.get("timestamp") else None)),
        # The unit lives in the sub-line, not the value: "20,079,200 BTC" is wide
        # enough to wrap this tile onto two lines and strand the "BTC" on its own.
        ("Bitcoin issued", _n(supply), "bbIssued",
         'BTC <span class="bbsep">·</span> <span id="bbIssuedPct">%.2f%%</span> of '
         'every coin there will ever be' % issued_pct),
        ("Next halving", _clock(blocks_to_halving * 600), "bbHalving",
         'at block %s <span class="bbsep">·</span> ≈%s'
         % (_n(halving_block), blogkit.pretty_date(halving_date))),
    ]
    hero_html = "\n".join(
        '    <div class="bbh"><div class="bbh-l">%s</div>'
        '<div class="bbh-v am" id="%s">%s</div><div class="bbh-s">%s</div></div>'
        % (esc(label), vid, value, sub) for label, value, vid, sub in hero)

    # ── cards ─────────────────────────────────────────────────────────────
    cards = []

    stat_blocks = [
        ("Price", None, _usd(price), "mPrice", "am"),
        ("Market capitalisation", None, money_cap(cap) if cap else "—", "mCap", ""),
        ("Satoshis to the dollar", None,
         _n(round(SATS / price)) if price else "—", "mSatsD", ""),
        ("All-time high",
         blogkit.pretty_date(datetime.fromtimestamp(ath_ts, timezone.utc).date())
         if ath_ts else None, _usd(ath_usd), None, ""),
        ("Down from that high", None,
         "%.1f%%" % ((price - ath_usd) / ath_usd * 100)
         if price and ath_usd else "—", "mAthDown", ""),
        ("Days since that high", None,
         _n((now - ath_ts) // 86400) + " days" if ath_ts else "—", "mAthDays", ""),
        ("One bitcoin, priced in gold", None,
         _n(price / gold_px, 1) + " oz" if price and gold_px else "—", "mGoldOz", ""),
        ("Against all the gold ever mined", None,
         "%.2f%%" % (cap / gold_cap * 100) if cap and gold_cap else "—",
         "mGoldPct", ""),
    ]
    stats_html = "".join(
        '<div class="bbst"><div class="bbst-l">%s%s</div>'
        '<div class="bbst-v%s"%s>%s</div></div>'
        % (esc(label), '<span class="bbst-n"> · %s</span>' % esc(note) if note else "",
           (" " + cls) if cls else "", ' id="%s"' % vid if vid else "", value)
        for label, note, value, vid, cls in stat_blocks)

    ranges = ["1H", "1D", "1W", "1M", "3M", "6M", "YTD", "1Y", "3Y", "10Y", "ALL"]
    range_btns = "".join(
        '<button type="button" class="bbb r%s" data-r="%s">%s</button>'
        % (r, r, r) for r in ranges)
    ma_btns = "".join(
        '<button type="button" class="bbb m%d" data-ma="%d">%dW</button>' % (p, p, p)
        for p in (50, 100, 200))

    cards.append(
        '  <section class="bbc bbwide">\n'
        '    <h2>The market</h2>\n'
        '    <div class="bbctl">\n'
        '      <div class="bbbtns" id="bbRanges">' + range_btns + '</div>\n'
        '      <div class="bbbtns">' + ma_btns +
        '<button type="button" class="bbb lg" id="bbLog" '
        'title="Logarithmic price axis — the only way a sixteen-year Bitcoin '
        'chart shows anything before 2017">LOG</button></div>\n'
        '    </div>\n'
        '    <div class="bbchartwrap" id="bbChartWrap">\n'
        '      <svg id="bbChart" role="img" aria-label="Bitcoin price over the '
        'selected period, with optional 50, 100 and 200 week moving averages">'
        '</svg>\n'
        '      <div class="bbread" id="bbRead"></div>\n'
        '    </div>\n'
        '    <p class="bbnote" id="bbChartNote"></p>\n'
        '    <div class="bbstats">' + stats_html + '</div>\n'
        '  </section>')

    cards.append(_bb_card("The supply", [
        _bb_row("Issued so far", _n(supply) + " BTC", "sIssued"),
        _bb_row("Of the 21 million", "%.2f%%" % issued_pct, "sPct", cls="am"),
        _bb_row("Still to be mined", _n(BTC_TRUE_MAX - supply) + " BTC", "sLeft"),
        _bb_row("New coins a day", _n(per_day, 1) + " BTC", "sPerDay"),
        _bb_row("Annual issuance", "%.2f%%" % annual_pct if annual_pct else "—", None,
                "as a share of the coins that already exist"),
        _bb_row("Years of issuance held in the stock",
                _n(s2f, 0) if s2f else "—", None,
                "the stock-to-flow ratio, as a fact rather than a forecast"),
    ], ('<div class="bbbar"><i id="sBar" style="width:%.2f%%"></i></div>'
        '<div class="bbbarl"><span>0</span><span>21,000,000</span></div>'
        '<p class="bbmore"><a href="how-many-bitcoins-are-there.html">'
        'How that number is worked out, exactly →</a></p>') % issued_pct))

    cards.append(_bb_card("Halvings", [
        _bb_row("Reward era", "no. %d" % (epoch + 1), "hEpoch",
                "each one is 210,000 blocks, about four years"),
        _bb_row("Reward per block now", _n(subsidy, 3) + " BTC", "hSubsidy"),
        _bb_row("After the next halving", _n(subsidy / 2, 4) + " BTC"),
        _bb_row("Blocks to go", _n(blocks_to_halving) + " blocks", "hBlocks"),
        _bb_row("Expected date", "≈" + blogkit.pretty_date(halving_date), None,
                "at Bitcoin's ten-minute target; real blocks vary"),
        _bb_row("The last one that pays anything", "≈%d" % _btc_era_date(
            BTC_ZERO_REWARD_BLOCK)[0].year, None, "block 6,930,000"),
    ]))

    fee_share = (rw.get("fee_sats") / rw["reward_sats"] * 100
                 if rw.get("reward_sats") else None)
    cards.append(_bb_card("Difficulty and mining", [
        _bb_row("Hash rate", _hashrate_fmt(hr.get("current")), "dHash", cls="am"),
        _bb_row("Difficulty",
                _n(hr.get("difficulty") / 1e12, 1) + " T" if hr.get("difficulty")
                else "—", "dDiff"),
        _bb_row("Blocks to the next retarget",
                _n(rt.get("remaining_blocks")) + " blocks"
                if rt.get("remaining_blocks") is not None else "—", "dLeft"),
        _bb_row("Expected change",
                ("%+.2f%%" % rt["estimated_change_pct"])
                if rt.get("estimated_change_pct") is not None else "—", "dChange"),
        _bb_row("Retarget in",
                _clock(rt["estimated_ts"] - now) if rt.get("estimated_ts") else "—",
                "dRetarget"),
        _bb_row("Average block, this epoch",
                _n(rt["block_time_s"] / 60, 1) + " min" if rt.get("block_time_s")
                else "—", "dBlockTime", "the target is ten"),
        _bb_row("Paid to miners, last 24 hours",
                _usd(rw["reward_sats"] / SATS * price, 0)
                if rw.get("reward_sats") and price else "—"),
        _bb_row("Of which was fees",
                "%.2f%%" % fee_share if fee_share is not None else "—", None,
                "the rest is newly minted coin"),
    ], ('<div class="bbbar"><i id="dProg" style="width:%.1f%%"></i></div>'
        '<div class="bbbarl"><span id="dProgTxt">%.1f%% through this epoch</span>'
        '<span>2,016 blocks</span></div>'
        % (rt.get("progress_pct") or 0, rt.get("progress_pct") or 0))
        + _bb_chart(hr.get("series"))
        + '<p class="bbasof">A year of hash rate.</p>'))

    fee_chips = ""
    if fees:
        fee_chips = ('<div class="bbchips">'
                     + "".join('<span class="bbchip">%s <b id="%s">%s</b></span>'
                               % (lbl, vid, _n(fees.get(key)))
                               for lbl, key, vid in
                               (("Next block", "fastest", "fFast"),
                                ("Half hour", "half_hour", "fHalf"),
                                ("An hour", "hour", "fHour"),
                                ("Economy", "economy", "fEcon"),
                                ("Minimum", "minimum", "fMin")))
                     + '</div><p class="bbasof">Satoshis per virtual byte — what it '
                       'costs to be included that quickly.</p>')
    typical = (fees.get("half_hour", 0) * TYPICAL_TX_VBYTES / SATS * price
               if fees.get("half_hour") and price else None)
    cards.append(_bb_card("The mempool", [
        _bb_row("Transactions waiting", _n(mp.get("count")), "pCount"),
        _bb_row("Weight waiting",
                _n(mp["vsize"] / 1e6, 1) + " MvB" if mp.get("vsize") else "—",
                "pVsize", "a block holds about one"),
        _bb_row("Blocks to clear it",
                _n(-(-mp["vsize"] // 1000000)) + " blocks" if mp.get("vsize") else "—",
                "pBlocks"),
        _bb_row("Fees waiting to be collected",
                _usd(mp["total_fee_sats"] / SATS * price, 0)
                if mp.get("total_fee_sats") and price else "—", "pFees"),
        _bb_row("An ordinary payment, right now",
                _usd(typical, 2) if typical else "—", "pTypical",
                "one input, two outputs, confirmed within the half hour"),
    ], fee_chips))

    cards.append(_bb_card("The chain", [
        _bb_row("Block height", _n(height), "cHeight"),
        _bb_row("Size on disk", _bytes_fmt(ch.get("size_bytes")), None,
                "what a full node stores"),
        _bb_row("Transactions, all time", _n(ch.get("tx_total"))),
        _bb_row("Outputs, all time", _n(ch.get("outputs_total"))),
        _bb_row("Transactions a second",
                _n(ch["tx_24h"] / 86400, 1) if ch.get("tx_24h") else "—", None,
                "averaged over the last day"),
        _bb_row("In the last block",
                "%s txs" % _n(tip.get("tx_count")) if tip.get("tx_count") else "—",
                None, ("%s of data" % _bytes_fmt(tip["size"])) if tip.get("size")
                else None),
    ]))

    if ln:
        ln_cap = ln["capacity_sats"] / SATS
        cards.append(_bb_card("Lightning", [
            _bb_row("Public capacity", _n(ln_cap, 1) + " BTC"),
            _bb_row("That, in dollars",
                    money_cap(ln_cap * price) if price else "—"),
            _bb_row("Nodes", _n(ln.get("nodes"))),
            _bb_row("Channels", _n(ln.get("channels"))),
            _bb_row("Average channel",
                    _n(ln["avg_capacity_sats"] / SATS, 3) + " BTC"
                    if ln.get("avg_capacity_sats") else "—"),
            # NOT "only over Tor": mempool's tor_nodes counts every node with an
            # onion address, including the ones that also advertise a clearnet one.
            _bb_row("Reachable over Tor",
                    "%.0f%%" % (ln["tor_nodes"] / ln["nodes"] * 100)
                    if ln.get("tor_nodes") and ln.get("nodes") else "—", None,
                    "of the nodes that announce themselves"),
        ], '<p class="bbasof">Only the public network is countable, and a great '
           'deal of Lightning is deliberately private. This snapshot is dated '
           '%s — it is the one panel here that is not refreshed hourly.</p>'
           % esc(ln.get("as_of") or "unknown")))

    cards.append(_bb_card("Further out", [
        _bb_row("90% of all bitcoin issued", _bb_milestone(0.90)),
        _bb_row("95%", _bb_milestone(0.95)),
        _bb_row("99%", _bb_milestone(0.99)),
        _bb_row("99.9%", _bb_milestone(0.999)),
        _bb_row("The last whole coin",
                _bb_milestone((BTC_TRUE_MAX - 1) / BTC_TRUE_MAX)),
        _bb_row("The reward reaches zero",
                "≈%d" % _btc_era_date(BTC_ZERO_REWARD_BLOCK)[0].year, None,
                "after which miners are paid in fees alone"),
    ], '<p class="bbasof">Every date past the last halving is extrapolated at '
       'ten minutes a block, which is a target rather than a promise. Read them '
       'as years, not appointments.</p>'))

    # ── the methods panel ─────────────────────────────────────────────────
    methods = """
  <div class="panel">
    <h2>How these numbers are made</h2>
    <p>Three different kinds of number sit on this page, and they are not equally
    true. Rather than set them all in the same type and let you assume, here is
    which is which.</p>
    <ul>
      <li><b>Computed, and exact.</b> Everything about supply and halvings.
      Bitcoin's issuance is a published rule — 50 coins a block, halved every
      210,000 blocks — so the number of coins in existence is not an estimate
      anyone has to make. It is that schedule added up in whole satoshis from
      the block height above, and the working is
      <a href="how-many-bitcoins-are-there.html">set out here</a>.</li>
      <li><b>Polled, and live.</b> Price, block height, the mempool and the fee
      estimates are refreshed from <a href="https://mempool.space/">mempool.space</a>
      every minute while this page is open; difficulty and hash rate every five,
      because they cannot move faster than that. The chart's hour, day and week
      views are candles from <a href="https://www.coinbase.com/">Coinbase</a>,
      fetched only if you ask for them — baking minute resolution into this page
      would mean serving you a snapshot of an hour that ended before you
      arrived. If any of it fails the page keeps the last good reading and says
      so beside the dot at the top.</li>
      <li><b>Snapshots, taken through the day.</b> The all-time high, the chain's
      size and its all-time totals, the year of hash rate, and the price history
      behind the chart — weekly closes back to July 2010, daily for the last two
      years. The moving averages are worked out from those weekly closes in your
      own browser, which is why they are exactly 50, 100 and 200 weeks rather
      than an approximation of them. Lightning is the exception worth knowing
      about: its upstream statistics are rebuilt on someone else's schedule, so
      that panel carries its own date.</li>
    </ul>
    <p>The clocks — time since the last block, and the two countdowns — tick
    without asking anything, because they are arithmetic on a timestamp. The
    halving countdown assumes Bitcoin's ten-minute target, so it is an estimate
    that jumps a little each time a block actually lands.</p>
    <p>Sources: <a href="https://mempool.space/">mempool.space</a>,
    <a href="https://blockchair.com/">Blockchair</a> and
    <a href="https://www.coinbase.com/">Coinbase</a> — all public, none of them
    requiring an account. Nothing here is investment advice, and nothing here is
    for sale.</p>
  </div>
"""

    seed = json.dumps({
        "height": height,
        "tipTs": tip.get("timestamp"),
        "price": price,
        "maxSupply": BTC_TRUE_MAX,
        # The chart's own data. It rides in the page rather than being fetched,
        # because it is the same JSON this page was built from — fetching it
        # again at view time would download a second copy of what is already here.
        "weekly": stats.get("price_weekly") or [],
        "daily": stats.get("price_daily") or [],
        "halvingBlock": halving_block,
        "athUsd": ath_usd,
        "athTs": ath_ts,
        "goldPx": gold_px,
        "goldCap": gold_cap,
        "hashrate": _hashrate_fmt(hr.get("current")),
        "difficulty": hr.get("difficulty"),
        "mempool": {"count": mp.get("count"), "vsize": mp.get("vsize"),
                    "total_fee": mp.get("total_fee_sats")},
        "fees": {"fastestFee": fees.get("fastest"),
                 "halfHourFee": fees.get("half_hour"),
                 "hourFee": fees.get("hour"),
                 "economyFee": fees.get("economy"),
                 "minimumFee": fees.get("minimum")},
        "retarget": {"progressPercent": rt.get("progress_pct"),
                     "remainingBlocks": rt.get("remaining_blocks"),
                     "difficultyChange": rt.get("estimated_change_pct"),
                     "estimatedRetargetDate": (rt["estimated_ts"] * 1000
                                               if rt.get("estimated_ts") else None),
                     "timeAvg": (rt["block_time_s"] * 1000
                                 if rt.get("block_time_s") else None)},
    }, separators=(",", ":"))

    body = ('  <h1 class="btitle">%s'
            'The Bitcoin Board</h1>\n' % BB_COIN_SVG.replace("__ACCENT__", ACCENT) +
            '  <p class="bblede">Everything Bitcoin publishes about itself, on one '
            'page: how many coins exist, how hard they are to mine, what is waiting '
            'to be confirmed, and how long until the next halving. The network is '
            'the only source — nobody is asked to take a figure on faith.</p>\n'
            # The separator is inside the span it belongs to, so a narrow screen
            # cannot wrap the line and leave a dangling "·" at the end of it.
            '  <p class="bbstamp"><span class="bbdot" id="bbDot"></span>'
            '<span id="bbLive">live</span>'
            '<span><span class="bbsep">·</span> snapshot taken %s</span></p>\n'
            '  <div class="bbhero">\n%s\n  </div>\n'
            '  <div class="bbgrid">\n%s\n  </div>\n%s'
            % (esc(stats.get("generated", "—")), hero_html,
               "\n".join(cards), methods))

    return _shell(
        title="The Bitcoin Board — Bitcoin by the numbers, live",
        desc="Bitcoin's own numbers on one page: block height, coins issued, "
             "difficulty, hash rate, the mempool, fees and the next halving.",
        url="%sbitcoin.html" % BASE_URL, active="bitcoin", body=body,
        extra_css=BB_CSS, extra_js=BB_JS.replace("__SEED__", seed))


def build_sitemap(entries, tags):
    """A sitemap is not optional here — it IS the discovery plan.

    Nothing links to this publication from outside, so a crawler has no path in.
    robots.txt advertises this file. Tag pages appear only once they carry
    TAG_INDEX_MIN entries; submitting a page we have marked noindex would be
    asking Google to index something we told it not to.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, today), ("%sboard.html" % BASE_URL, today),
            ("%sbitcoin.html" % BASE_URL, today), ("%sask.html" % BASE_URL, today)]
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


def main():
    include_drafts = "--drafts" in sys.argv

    if not os.path.exists(SRC):
        sys.exit("no source/finance/asset_board.json — run tools/fetch_asset_board.py first")
    with open(SRC, encoding="utf-8") as fh:
        board = json.load(fh)
    if not (board.get("assets") or []):
        sys.exit("asset_board.json has no assets — refusing to build an empty board")

    # The Bitcoin board is optional by design. A missing or unreadable stats file
    # costs exactly one page and leaves the rest of the publication building —
    # the alternative, failing the whole build because mempool.space had a bad
    # night, would take the writing offline over a dashboard.
    stats = None
    if os.path.exists(BTC_SRC):
        try:
            with open(BTC_SRC, encoding="utf-8") as fh:
                stats = json.load(fh)
        except (ValueError, OSError) as exc:
            print("  ! bitcoin_stats.json unreadable (%s) — skipping the Bitcoin "
                  "board" % exc, file=sys.stderr)

    entries = load_entries(include_drafts=include_drafts)
    live = [e for e in entries if not e["draft"]]
    check_entries(entries)

    tags = tag_index(live)
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(live, board, stats))
    write("ask.html", build_ask())
    write("thanks.html", build_thanks())
    write("board.html", build_board(board))
    btc_page = build_bitcoin_board(stats, board) if stats else None
    if btc_page:
        write("bitcoin.html", btc_page)
    else:
        print("  ! no live block height — leaving the last Bitcoin board in place",
              file=sys.stderr)
    for e in entries:
        page = build_entry_page(e, board)
        if page is None:
            print("  ! %s: no live block height in this run — leaving the "
                  "last successful build in place" % e["file"], file=sys.stderr)
            continue
        write(e["file"], page)
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
    print("built /finance/ — %d assets, Bitcoin #%s, data %s"
          % (len(board["assets"]), board.get("btc_rank"), board.get("generated")))
    print("  %d entr%s (%d live), %d tag page%s (%d indexable, %d held back at <%d entries)"
          % (len(entries), "y" if len(entries) == 1 else "ies", len(live),
             len(tags), "" if len(tags) == 1 else "s", indexable,
             len(tags) - indexable, TAG_INDEX_MIN))
    for e in entries:
        print("  %s  %-38s %s" % (e["date"], e["file"], "[DRAFT]" if e["draft"] else ""))
    return 0


def _prune_stale_tag_pages(tags):
    """Delete tag pages whose tag no longer appears on any entry.

    Without this, renaming a tag leaves the old page on disk forever — still
    reachable, still in search, listing entries that have moved on. Scoped hard
    to finance/tag-*.html so it can never reach another publication's output.
    """
    keep = {"tag-%s.html" % blogkit.tag_slug(t) for t in tags}
    for fn in os.listdir(OUT):
        if fn.startswith("tag-") and fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(OUT, fn))
            print("  (removed stale tag page: %s)" % fn)


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

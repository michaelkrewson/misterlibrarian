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
        stroke = ' stroke="#5eb3d6" stroke-width="2.5"' if is_current else ""
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
                '<line x1="%.1f" y1="285" x2="%.1f" y2="%.2f" stroke="#5eb3d6" '
                'stroke-width="1.6"/>'
                '<text x="%.1f" y="255" text-anchor="middle" '
                'font-family="ui-sans-serif, system-ui, sans-serif" font-size="12.5" '
                'font-weight="bold" letter-spacing="0.08em" fill="#5eb3d6">WE ARE '
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
            '<a href="board.html"%s>The Board</a>'
            '<a href="ask.html"%s>Ask</a>'
            '<a href="feed.xml">RSS</a>'
            '<a class="sib" href="%s" title="%s">%s →</a>'
            '</nav>' % (cls("home"), cls("board"), cls("ask"), SIBLING_URL,
                        esc(SIBLING_BLURB), esc(SIBLING_NAME)))


def _chrome(active=""):
    """Header used by every page in the publication."""
    return ('<header class="hsm">'
            '<a class="brand" href="index.html">%s'
            '<span class="wm">The Librarian\'s <span class="em">Ledger</span></span></a>'
            '%s</header>' % (MARK_SVG.replace("__ACCENT__", ACCENT), _nav(active)))


def _foot():
    return ('<footer>%s · <a href="board.html">The Board</a> · '
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
<style>%(css)s</style>
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
       "site": esc(SITE_NAME), "ogt": og_type,
       "css": CSS.replace("__ACCENT__", ACCENT),
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


def build_front(entries, board):
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
      <span class="ec-t">The Biggest Assets in the World</span>
      <span class="ec-s">%s.</span>
    </a>""" % esc(board_line)

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


BOARD_BODY_TEMPLATE = """  <table class="board">
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

    body = """  <h1 class="btitle">The Biggest Assets in the World</h1>
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

    return _shell(title="The Biggest Assets in the World — %s" % SITE_NAME,
                  desc=desc, url="%sboard.html" % BASE_URL, active="board", body=body)


def build_sitemap(entries, tags):
    """A sitemap is not optional here — it IS the discovery plan.

    Nothing links to this publication from outside, so a crawler has no path in.
    robots.txt advertises this file. Tag pages appear only once they carry
    TAG_INDEX_MIN entries; submitting a page we have marked noindex would be
    asking Google to index something we told it not to.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(BASE_URL, today), ("%sboard.html" % BASE_URL, today),
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


def main():
    include_drafts = "--drafts" in sys.argv

    if not os.path.exists(SRC):
        sys.exit("no source/finance/asset_board.json — run tools/fetch_asset_board.py first")
    with open(SRC, encoding="utf-8") as fh:
        board = json.load(fh)
    if not (board.get("assets") or []):
        sys.exit("asset_board.json has no assets — refusing to build an empty board")

    entries = load_entries(include_drafts=include_drafts)
    live = [e for e in entries if not e["draft"]]
    check_entries(entries)

    tags = tag_index(live)
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    write("index.html", build_front(live, board))
    write("ask.html", build_ask())
    write("thanks.html", build_thanks())
    write("board.html", build_board(board))
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

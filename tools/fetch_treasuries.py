#!/usr/bin/env python3
"""Compute the Treasuries board into source/finance/treasuries.json.

    python3 tools/fetch_treasuries.py            # compute and write
    python3 tools/fetch_treasuries.py --dry-run  # print, write nothing

STANDARD LIBRARY ONLY, like fetch_bitcoin_stats.py — this board doesn't rank companies
by market cap the way the asset board does, it ranks every holder by BTC HELD, so the
only live number it actually needs is one BTC/USD price. That is read from the
already-fetched source/finance/asset_board.json (same CI run, zero extra network cost)
with a direct keyless fallback if that file is missing or unusable.

WHY HOLDINGS, NOT MARKET CAP
─────────────────────────────
bitbo.io/treasuries ranks by BTC held, across six kinds of holder: public companies,
mining companies, private companies, ETFs, countries, and DeFi protocols. Most of those
have no shares outstanding and no market cap at all (a country, a DeFi protocol) — so
unlike the asset board, this script does not price any equity. Every row's BTC count
comes from source/finance/treasuries_seed.json, a curated, dated, Claude-maintained
file (see its own "note" field) — the same posture the asset board takes with
GOLD_TONNES/SILVER_TONNES: a periodically-refreshed estimate, not a live feed.

FAIL-SAFE, LIKE ITS SIBLINGS
A missing or empty seed file, or no usable BTC price from any source, means this script
prints why and writes nothing — the build then keeps the previously-committed board
rather than publish a blank or broken page.

NOTHING HERE IS PERSONAL. Every input is either a public market quote or public
reporting about institutional holdings — no account, no key, nothing about anyone's
personal holdings — which is what makes it safe to run in a public repo on a schedule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "source", "finance", "treasuries_seed.json")
ASSET_BOARD = os.path.join(ROOT, "source", "finance", "asset_board.json")
OUT = os.path.join(ROOT, "source", "finance", "treasuries.json")

BTC_TRUE_MAX = 20_999_949.9769   # see fetch_asset_board.py's _btc_supply_sats()

CATEGORIES = ("public", "mining", "private", "etf", "country", "defi")

# Direct keyless fallback, only used when asset_board.json can't supply a price.
# Same operator (mempool.space) fetch_bitcoin_stats.py already relies on, so a
# down day for one is a down day for both — an acceptable shared dependency
# since this is a FALLBACK, not the primary path.
_PRICE_APIS = [
    "https://mempool.space/api/v1/prices",   # {"USD": ..., ...}
    "https://api.blockchair.com/bitcoin/stats",  # {"data": {"market_price_usd": ...}}
]

UA = "mistertranslation.com/finance (The Librarian's Ledger treasuries board)"


def _get_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — a down source is a skip, not a crash
        print("  ! %s — %s" % (url, exc), file=sys.stderr)
        return None


def _btc_price_from_asset_board():
    """The BTC row's live price out of the sibling board, or None."""
    if not os.path.exists(ASSET_BOARD):
        return None
    try:
        with open(ASSET_BOARD, encoding="utf-8") as fh:
            board = json.load(fh)
    except (ValueError, OSError):
        return None
    for a in board.get("assets", []):
        if a.get("symbol") == "BTC" and a.get("price"):
            return float(a["price"]), board.get("generated")
    return None, None


def _btc_price_fallback():
    """A direct keyless price read, only reached if the asset board has none."""
    d = _get_json(_PRICE_APIS[0])
    if isinstance(d, dict) and d.get("USD"):
        return float(d["USD"])
    d = _get_json(_PRICE_APIS[1])
    if isinstance(d, dict):
        v = (d.get("data") or {}).get("market_price_usd")
        if v:
            return float(v)
    return None


def compute():
    """The ranked treasuries board, or None if nothing usable. Never raises."""
    if not os.path.exists(SEED):
        print("  ! no source/finance/treasuries_seed.json — nothing to compute",
              file=sys.stderr)
        return None
    try:
        with open(SEED, encoding="utf-8") as fh:
            seed = json.load(fh)
    except (ValueError, OSError) as exc:
        print("  ! treasuries_seed.json unreadable — %s" % exc, file=sys.stderr)
        return None

    entities = seed.get("entities") or []
    if not entities:
        print("  ! treasuries_seed.json has no entities", file=sys.stderr)
        return None

    price, price_stamp = _btc_price_from_asset_board()
    price_source = "asset_board.json"
    if not price:
        price = _btc_price_fallback()
        price_source = "mempool.space/blockchair (fallback)"
        price_stamp = None
    if not price:
        print("  ! no BTC price from any source — keeping the previous board",
              file=sys.stderr)
        return None

    rows = []
    for e in entities:
        cat = e.get("category")
        btc = e.get("btc_holdings")
        name = e.get("name")
        if cat not in CATEGORIES or not name or not btc or btc <= 0:
            print("  ! skipping malformed entity: %r" % (e,), file=sys.stderr)
            continue
        rows.append({
            "name": name,
            "category": cat,
            "ticker": e.get("ticker"),
            "country": e.get("country"),
            "btc_holdings": float(btc),
            "value_usd": float(btc) * price,
            "pct_of_21m": float(btc) / BTC_TRUE_MAX * 100.0,
            "source_note": e.get("source_note"),
            # A row's OWN as_of means it was individually checked against a
            # real source (see source_note) — one that only inherits the
            # seed file's top-level date is a rougher, unverified estimate.
            "as_of": e.get("as_of") or seed.get("as_of"),
            "verified": bool(e.get("as_of")),
        })
    if not rows:
        return None

    # Rank overall, then within each category — same list, two different `rank`
    # keys, so the hub's global leaderboard and each category page's own table
    # can both sort without recomputing anything.
    rows.sort(key=lambda r: r["btc_holdings"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank_overall"] = i
    totals = {c: {"btc": 0.0, "value_usd": 0.0, "count": 0} for c in CATEGORIES}
    for cat in CATEGORIES:
        cat_rows = [r for r in rows if r["category"] == cat]
        cat_rows.sort(key=lambda r: r["btc_holdings"], reverse=True)
        for i, r in enumerate(cat_rows, 1):
            r["rank_category"] = i
        t = totals[cat]
        t["btc"] = sum(r["btc_holdings"] for r in cat_rows)
        t["value_usd"] = sum(r["value_usd"] for r in cat_rows)
        t["count"] = len(cat_rows)

    grand_btc = sum(t["btc"] for t in totals.values())
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "btc_price": price,
        "btc_price_source": price_source,
        "btc_price_as_of": price_stamp,
        "seed_as_of": seed.get("as_of"),
        "rows": rows,
        "totals": totals,
        "grand_total_btc": grand_btc,
        "grand_total_value_usd": grand_btc * price,
        "grand_total_pct_of_21m": grand_btc / BTC_TRUE_MAX * 100.0,
        "count": len(rows),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = ap.parse_args()

    board = compute()
    if board is None:
        # Not an error exit: a bad day should leave the committed board alone,
        # same posture as fetch_asset_board.py and fetch_bitcoin_stats.py.
        print("no treasuries board resolved — keeping the previous one", file=sys.stderr)
        return 0

    print("%d entities · %s BTC · $%.1fB · price $%s (%s) · %s"
          % (board["count"], "{:,.0f}".format(board["grand_total_btc"]),
             board["grand_total_value_usd"] / 1e9, "{:,.0f}".format(board["btc_price"]),
             board["btc_price_source"], board["generated"]))
    for cat in CATEGORIES:
        t = board["totals"][cat]
        print("  %-10s %3d entities  %12s BTC  $%9.2fB"
              % (cat, t["count"], "{:,.0f}".format(t["btc"]), t["value_usd"] / 1e9))

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(board, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, OUT)
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

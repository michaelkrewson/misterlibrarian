#!/usr/bin/env python3
"""Fetch the world's largest assets by market cap into source/finance/asset_board.json.

    python3 tools/fetch_asset_board.py            # fetch and write
    python3 tools/fetch_asset_board.py --dry-run  # print, write nothing

This is the ONLY part of /finance/ that touches the network, and it is deliberately
separate from build_finance.py so that the *builder* stays standard-library-only —
the same property build_travel.py has. The build reads a JSON file; this writes one.

WHY A FILE IN THE REPO IS THE INTERFACE
───────────────────────────────────────
Whoever writes asset_board.json is swappable. Today it is a scheduled GitHub Action
(.github/workflows/refresh-asset-board.yml) which needs no server and no secret. If
Yahoo ever blocks the runner's IP — datacenter ranges get rate-limited far more
aggressively than a home connection — the fix is to have some other machine commit
the same file on a schedule. The page and the builder do not change.

That indirection also buys the fail-safe for free: a fetch that resolves nothing
leaves the previous board committed, so the page shows slightly stale numbers rather
than going blank. `compute()` returns None in that case and main() writes nothing.

WHAT THE NUMBERS ARE
────────────────────
  stock   market cap straight from yfinance fast_info
  metal   spot price × a fixed above-ground-tonnage constant
  crypto  price × the EXACT circulating supply, computed from the current block
          height and Bitcoin's own halving schedule — not an estimate at all

Gold and silver's above-ground tonnage are genuine estimates that move slowly; they
are stamped into the payload as `constants` so the page can show its own working
rather than asking the reader to take a $30T number on faith. Bitcoin is different:
issuance is a public, deterministic rule (50 BTC/block, halved every 210,000 blocks),
so `_btc_supply_sats()` below derives the coin count directly from a live block
height instead of carrying its own slow-moving guess. See the entry
"How Many Bitcoins Are There, Exactly?" in source/finance/ for the full arithmetic.
The metal constants still only need refreshing about once a year.

NOTHING HERE IS PERSONAL. Every input is a public market quote. This script has no
credentials, reads no account, and knows nothing about anyone's holdings — which is
what makes it safe to run in a public repo.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    sys.exit("yfinance is required:  python3 -m pip install yfinance")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source", "finance", "asset_board.json")

OZ_PER_TONNE = 32150.7466

# Above-ground stocks. Genuine estimates, and the silver figure in particular
# varies a lot between sources — hence `constants` in the payload.
GOLD_TONNES = 216265          # World Gold Council, ~2024
SILVER_TONNES = 1750000       # common board assumption; estimates vary widely

# Bitcoin's supply is NOT an estimate — see _btc_supply_sats() below — but this
# is still the number that runs the board on a day every block-height API in
# _BLOCK_HEIGHT_APIS has failed. Bump it every so often so a persistently offline
# run degrades to "close" rather than "years stale"; it is never the normal path.
BTC_CIRCULATING = 19_870_000

# Metals, Bitcoin, and the mega-caps that sit around Bitcoin's rank, so Bitcoin is
# always shown in context. Over-inclusion is safe: the board ranks by live market cap
# and anything that fails to resolve is simply dropped.
ASSETS = [
    {"name": "Gold",               "symbol": "GOLD",    "kind": "metal",  "px": "GC=F",    "country": "🌐", "emoji": "🥇"},
    {"name": "Silver",             "symbol": "SILVER",  "kind": "metal",  "px": "SI=F",    "country": "🌐", "emoji": "🥈"},
    {"name": "Bitcoin",            "symbol": "BTC",     "kind": "crypto", "px": "BTC-USD", "country": "🌐", "emoji": "₿"},
    {"name": "Apple",              "symbol": "AAPL",    "kind": "stock",  "country": "🇺🇸", "domain": "apple.com"},
    {"name": "Microsoft",          "symbol": "MSFT",    "kind": "stock",  "country": "🇺🇸", "domain": "microsoft.com"},
    {"name": "NVIDIA",             "symbol": "NVDA",    "kind": "stock",  "country": "🇺🇸", "domain": "nvidia.com"},
    {"name": "Alphabet (Google)",  "symbol": "GOOGL",   "kind": "stock",  "country": "🇺🇸", "domain": "abc.xyz"},
    {"name": "Amazon",             "symbol": "AMZN",    "kind": "stock",  "country": "🇺🇸", "domain": "amazon.com"},
    {"name": "Saudi Aramco",       "symbol": "2222.SR", "kind": "stock",  "country": "🇸🇦", "domain": "aramco.com"},
    {"name": "Meta Platforms",     "symbol": "META",    "kind": "stock",  "country": "🇺🇸", "domain": "meta.com"},
    {"name": "Berkshire Hathaway", "symbol": "BRK-B",   "kind": "stock",  "country": "🇺🇸", "domain": "berkshirehathaway.com"},
    {"name": "Broadcom",           "symbol": "AVGO",    "kind": "stock",  "country": "🇺🇸", "domain": "broadcom.com"},
    {"name": "TSMC",               "symbol": "TSM",     "kind": "stock",  "country": "🇹🇼", "domain": "tsmc.com"},
    {"name": "Eli Lilly",          "symbol": "LLY",     "kind": "stock",  "country": "🇺🇸", "domain": "lilly.com"},
    {"name": "JPMorgan Chase",     "symbol": "JPM",     "kind": "stock",  "country": "🇺🇸", "domain": "jpmorganchase.com"},
    {"name": "Tesla",              "symbol": "TSLA",    "kind": "stock",  "country": "🇺🇸", "domain": "tesla.com"},
    {"name": "Walmart",            "symbol": "WMT",     "kind": "stock",  "country": "🇺🇸", "domain": "walmart.com"},
    {"name": "Visa",               "symbol": "V",       "kind": "stock",  "country": "🇺🇸", "domain": "visa.com"},
]


def _btc_supply_sats(height):
    """Total satoshis mined through and including block `height`.

    This is arithmetic, not an estimate. Bitcoin's issuance is a public,
    deterministic rule — 50 BTC per block, halved every 210,000 blocks — and
    this follows Bitcoin Core's own consensus subsidy formula exactly:
    subsidy(h) = (50 BTC) >> (h // 210_000), summed over h = 1..height, done in
    integer satoshis throughout to avoid float error.

    Block 0 (the genesis block) is deliberately excluded from that sum: its
    coinbase transaction was never added to the spendable UTXO set — a quirk
    from Bitcoin's original code, not a rule of the halving schedule — so no
    block explorer (blockchain.info, mempool.space) ever counts those 50 BTC
    as circulating. See https://en.bitcoin.it/wiki/Genesis_block. That is also
    why this is 50 BTC short of the "20,999,999.9769" figure quoted almost
    everywhere: that number is the raw subsidy-schedule sum INCLUDING genesis;
    this function returns the true spendable maximum, which is 50 BTC less.
    """
    HALVING_INTERVAL = 210_000
    INITIAL_SUBSIDY = 50 * 100_000_000  # satoshis
    total = 0
    for epoch in range((height // HALVING_INTERVAL) + 1):
        subsidy = INITIAL_SUBSIDY >> epoch
        if subsidy == 0:
            break
        epoch_lo = epoch * HALVING_INTERVAL
        epoch_hi = epoch_lo + HALVING_INTERVAL - 1
        lo = max(1, epoch_lo)          # skip genesis's block-0 subsidy
        hi = min(height, epoch_hi)
        if hi >= lo:
            total += (hi - lo + 1) * subsidy
    return total


# Public, keyless, no-auth block explorers, tried in order until one answers.
# Three independent operators so a single outage or a single blocked IP can't
# blind this script to the one number it actually needs from the chain itself.
_BLOCK_HEIGHT_APIS = [
    "https://mempool.space/api/blocks/tip/height",
    "https://blockchain.info/q/getblockcount",
    "https://blockstream.info/api/blocks/tip/height",
]


def _btc_block_height():
    """The current Bitcoin block height, or None if every source failed.

    None is the honest answer on a bad network day — the caller falls back to
    BTC_CIRCULATING, the same fail-safe posture every other number in this
    script already has (a bad Yahoo day keeps the previous board rather than
    going blank; a bad block-explorer day keeps the previous coin count).
    """
    import urllib.request

    for url in _BLOCK_HEIGHT_APIS:
        try:
            with urllib.request.urlopen(url, timeout=6) as r:
                return int(r.read().decode().strip())
        except Exception:
            continue
    return None


def _closes(df):
    """Daily closes out of a yfinance frame, NaNs dropped. [] if unusable."""
    if df is None or getattr(df, "empty", True) or "Close" not in df:
        return []
    col = df["Close"]
    if hasattr(col, "columns"):        # MultiIndex ('Close', sym) → first column
        col = col.iloc[:, 0]
    return [float(x) for x in col.dropna().tolist() if x == x]


def _bars(symbol):
    """Up to 30 daily closes for the sparkline, or None."""
    try:
        closes = _closes(yf.Ticker(symbol).history(period="2mo", interval="1d"))
        return closes[-30:] if len(closes) >= 2 else None
    except Exception:
        return None


def _fast(symbol):
    """(market_cap, last_price, previous_close) from fast_info; any may be None.

    fast_info is inconsistent about key names and raises on absent keys rather than
    returning None, so every read is guarded and tried under both spellings.
    """
    try:
        fi = yf.Ticker(symbol).fast_info
    except Exception:
        return None, None, None

    def g(*keys):
        for k in keys:
            try:
                v = fi[k]
            except Exception:
                v = getattr(fi, k, None)
            if v not in (None, 0):
                try:
                    return float(v)
                except (TypeError, ValueError):
                    pass
        return None

    return (g("market_cap", "marketCap"),
            g("last_price", "lastPrice"),
            g("previous_close", "previousClose"))


def one(asset, btc_circulating):
    """One board row, or None if it could not be priced."""
    sym = asset.get("px") or asset["symbol"]
    spark = _bars(sym)
    mcap, last, prev = _fast(sym)

    price = last if last is not None else (spark[-1] if spark else None)
    if price is None:
        return None

    change_pct = None
    if prev and prev > 0:
        change_pct = (price - prev) / prev * 100.0
    elif spark and len(spark) >= 2 and spark[-2] > 0:
        change_pct = (spark[-1] - spark[-2]) / spark[-2] * 100.0

    if asset["kind"] == "metal":
        tonnes = GOLD_TONNES if asset["symbol"] == "GOLD" else SILVER_TONNES
        mcap = price * tonnes * OZ_PER_TONNE
    elif asset["kind"] == "crypto":
        mcap = price * btc_circulating

    if not mcap or mcap <= 0:
        return None

    return {
        "name": asset["name"],
        "symbol": asset["symbol"],
        "kind": asset["kind"],
        "country": asset.get("country", ""),
        "emoji": asset.get("emoji"),
        "domain": asset.get("domain"),
        "market_cap": float(mcap),
        "price": float(price),
        "change_pct": round(change_pct, 2) if change_pct is not None else None,
        "spark": [round(x, 4) for x in (spark or [])],
    }


def compute():
    """The ranked board, or None if nothing resolved (caller keeps the old file)."""
    btc_height = _btc_block_height()
    if btc_height:
        btc_circulating = round(_btc_supply_sats(btc_height) / 1e8, 2)
    else:
        print("  ! every block-height source failed — falling back to the "
              "BTC_CIRCULATING constant", file=sys.stderr)
        btc_circulating = float(BTC_CIRCULATING)

    rows = []
    for a in ASSETS:
        try:
            r = one(a, btc_circulating)
        except Exception as exc:
            print(f"  ! {a['symbol']}: {exc}", file=sys.stderr)
            continue
        if r:
            rows.append(r)
        else:
            print(f"  ! {a['symbol']}: could not price, dropped", file=sys.stderr)

    if not rows:
        return None

    rows.sort(key=lambda r: r["market_cap"], reverse=True)
    btc_rank = None
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        if r["symbol"] == "BTC":
            btc_rank = i

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "assets": rows,
        "btc_rank": btc_rank,
        "count": len(rows),
        "constants": {
            "gold_tonnes": GOLD_TONNES,
            "silver_tonnes": SILVER_TONNES,
            "btc_circulating": btc_circulating,
            "btc_block_height": btc_height,   # None only if every source failed
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = ap.parse_args()

    board = compute()
    if board is None:
        # Deliberately not an error exit in CI: a bad Yahoo day should leave the
        # committed board alone and the page up, not fail the workflow red.
        print("no assets resolved — keeping the previous board", file=sys.stderr)
        return 0

    print(f"{board['count']} assets · Bitcoin is #{board['btc_rank']} · {board['generated']}")
    for r in board["assets"]:
        print(f"  {r['rank']:>2}. {r['name']:<22} ${r['market_cap']/1e12:>7.3f} T")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(board, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, OUT)
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

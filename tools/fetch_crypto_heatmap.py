#!/usr/bin/env python3
"""Compute the Crypto Heat Map into source/finance/crypto_heatmap.json.

    python3 tools/fetch_crypto_heatmap.py            # compute and write
    python3 tools/fetch_crypto_heatmap.py --dry-run  # print, write nothing

STANDARD LIBRARY ONLY (urllib) — no key, no yfinance. CoinGecko's public
`/coins/markets` endpoint returns the top 100 coins by market cap in ONE call,
with price, market cap, and native % change for 1H/1D/7D/1M/1Y baked in
(`price_change_percentage=1h,24h,7d,30d,1y`). That call is cheap and reliable
and is all this script needs for five of the eight buttons on the page.

THE OTHER THREE BUTTONS (3M/6M/YTD) — A SLOW BACKGROUND CRAWL, ON PURPOSE
──────────────────────────────────────────────────────────────────────────
CoinGecko has no bulk endpoint for 3M/6M/YTD at any price — those are not
among the periods its API recognises for ANY plan, free or paid. Getting a
real one means pulling a daily price series per coin
(`/coins/{id}/market_chart`) and reading the change off it directly. That is
fine for one coin; for a hundred it runs straight into the free, anonymous
tier's rate limit — measured directly against the live API while building
this (2026-09-07): three consecutive calls, each paced 2.5s apart, was enough
to draw a sustained 429 that a 15-45s cooldown did not clear.

So this follows the same shape as mstr-trader's `rh_backfill.py`: a small,
paced slice of the 100 coins gets its 3M/6M/YTD computed EACH RUN (see
MAX_SLOW_ATTEMPTS/SLOW_PACE_S below), persisted to a separate store
(SLOW_STORE) keyed by coin id so it survives across runs and across a coin
temporarily dropping out of the top 100. The full board fills in gradually
over several runs rather than all at once, and once complete, keeps
re-covering itself on a rolling basis (SLOW_REFRESH_DAYS) so the numbers
don't go stale forever. A coin that hasn't been reached yet just reads "—"
for those three columns until its turn comes — never a guess, never a
mislabeled substitute (a 200-day change is NOT six months, so it never
stands in for one here).

The FIRST 429 in a run stops the slow crawl for that run entirely — this
never hammers a limit that already said no, it just tries a few more coins
next time the workflow fires (roughly six times a day, see
.github/workflows/refresh-asset-board.yml).

FAIL-SAFE, LIKE ITS SIBLINGS
A failed `/coins/markets` call means this script prints why and writes
nothing — the build then keeps the previously-committed board rather than
publish a blank or broken page. The slow-crawl half failing costs nothing
but this run's small slice of 3M/6M/YTD progress; the fast five columns and
the board itself still update normally.

CATEGORIES — one deliberately-empty singleton, one curated positive list;
everything else is "Others"
The page groups every coin into one of three sections: Bitcoin (Bitcoin
itself and NOTHING else — see BITCOIN_DERIVATIVES below for why even its
own chain forks and wrapped/custodied representations moved out),
Infrastructure & Platform (base-layer chains, scaling layers, oracles,
interoperability — anything that IS a network rather than something built on
one), and Others (stablecoins, tokenized funds, DeFi apps, exchange tokens,
meme coins, Bitcoin's own forks/wraps/codebase-cousins — everything else).
Deliberately NOT an exhaustive taxonomy: the positive list covers what a
reader would actually look for grouped separately, and the "Others"
fallback means a brand-new coin entering the top 100 tomorrow renders
correctly (in Others) without this script needing an edit first.

NOTHING HERE IS PERSONAL. Every input is a public market quote — no account,
no key, nothing about anyone's holdings — which is what makes it safe to run
in a public repo on a schedule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source", "finance", "crypto_heatmap.json")
SLOW_STORE = os.path.join(ROOT, "source", "finance", "crypto_heatmap_slow.json")

UA = "mistertranslation.com/finance (The Librarian's Ledger Crypto Heat Map)"
MARKETS_URL = ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
               "&order=market_cap_desc&per_page=100&page=1&sparkline=false"
               "&price_change_percentage=1h,24h,7d,30d,1y")
CHART_URL = "https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=usd&days=%d"

CHART_DAYS = 364          # under CoinGecko's public 365-day historical ceiling
MAX_SLOW_ATTEMPTS = 12    # a safety ceiling; the first 429 stops the run well before this
SLOW_PACE_S = 3.5         # gap between per-coin historical calls, to be a polite anonymous caller
SLOW_REFRESH_DAYS = 5     # how long a coin's 3M/6M/YTD is trusted before it's due again

# ── categories — one deliberately-empty singleton, one curated list;
# everything unmapped is "Others" ──
#
# BITCOIN_DERIVATIVES holds exactly ONE id: "bitcoin". Two narrowings landed
# the same week (2026-09-08) and the direction kept pointing the same way,
# so this stopped halfway short of the honest endpoint: the FIRST pass split
# out Litecoin/Zcash/Dash (codebase-cousins with their own independent
# genesis block — never shared Bitcoin's ledger). That still left Bitcoin
# Cash/SV/Gold (literal chain forks, sharing every pre-fork transaction) and
# WBTC/cbBTC/tBTC/renBTC/Liquid BTC (the same asset, custodied and reissued
# elsewhere) in here on the reasoning that both groups are "Bitcoin in a
# real sense." Michael's direct follow-up rejected that reasoning outright:
# on THIS board, "Bitcoin" means the one thing everyone actually means by
# it — the coin itself — and every other one of those, real fork or real
# wrap, goes to Others with everything else. A name kept as a SET rather
# than inlined as a literal string so the intent ("this category is
# Bitcoin, and only Bitcoin, on purpose") stays visible at the call site
# rather than reading as an oversight. As a side effect this is also what
# actually fixed the treemap's degenerate-sliver problem two commits
# running: Bitcoin no longer shares a cell with ANYTHING, so there is
# nothing left to squeeze into a hairline.
BITCOIN_DERIVATIVES = {"bitcoin"}

INFRASTRUCTURE_PLATFORM = {
    "ethereum", "binancecoin", "ripple", "solana", "tron", "cardano",
    "avalanche-2", "polkadot", "near", "internet-computer", "cosmos",
    "algorand", "vechain", "filecoin", "the-open-network", "hedera-hashgraph",
    "stellar", "monero", "chainlink", "arbitrum", "optimism", "aptos", "sui",
    "polygon-ecosystem-token", "matic-network", "kaspa", "ethereum-classic",
    "injective-protocol", "sei-network", "celestia", "mantle",
    "render-token", "the-graph", "fantom", "eos", "tezos", "neo", "waves",
    "zilliqa", "harmony", "quant-network", "hyperliquid", "canton-network",
    "bittensor", "pi-network", "worldcoin-wld", "beldex", "xdce-crowd-sale",
    "rootstock-rsk", "stacks",
}

CATEGORY_BTC = "Bitcoin"
CATEGORY_INFRA = "Infrastructure & Platform"
CATEGORY_OTHER = "Others"


def category_for(coin_id):
    if coin_id in BITCOIN_DERIVATIVES:
        return CATEGORY_BTC
    if coin_id in INFRASTRUCTURE_PLATFORM:
        return CATEGORY_INFRA
    return CATEGORY_OTHER


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return default


def _nearest(series, target_ms, tolerance_days=6):
    """series: [(ts_ms, price), ...] ascending. The point closest to target_ms,
    or None if the nearest point is more than tolerance_days away (sparse/short
    history — e.g. a coin younger than the window asked for)."""
    if not series:
        return None
    best = min(series, key=lambda p: abs(p[0] - target_ms))
    if abs(best[0] - target_ms) > tolerance_days * 86400_000:
        return None
    return best[1]


def _pct(new, old):
    if old in (None, 0) or new is None:
        return None
    return (new / old - 1.0) * 100.0


def _compute_slow_changes(coin_id, current_price):
    """Real 3M/6M/YTD % change for one coin, from its own daily price series.
    None for any period whose reference point falls outside the coin's
    history (never fabricated, never approximated from a different window)."""
    try:
        data = _get_json(CHART_URL % (coin_id, CHART_DAYS))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ValueError) as exc:
        status = getattr(exc, "code", None)
        return None, status
    series = [(int(p[0]), float(p[1])) for p in data.get("prices", [])
              if p[1] is not None]
    if len(series) < 2:
        return None, None
    now = datetime.now(timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    jan1_ms = int(datetime(now.year, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    px_3m = _nearest(series, now_ms - 91 * 86400_000)
    px_6m = _nearest(series, now_ms - 182 * 86400_000)
    px_ytd = _nearest(series, jan1_ms)
    return {
        "chg_3m": _pct(current_price, px_3m),
        "chg_6m": _pct(current_price, px_6m),
        "chg_ytd": _pct(current_price, px_ytd),
    }, None


def _run_slow_crawl(rows, slow_store):
    """Advances the slow crawl by up to MAX_SLOW_ATTEMPTS coins, stopping the
    instant CoinGecko says no. Mutates slow_store in place; returns a small
    summary dict for the log line."""
    now_iso = datetime.now(timezone.utc).isoformat()
    cutoff = datetime.now(timezone.utc) - timedelta(days=SLOW_REFRESH_DAYS)

    def due_key(row):
        entry = slow_store.get(row["id"])
        if entry is None:
            return (0, "")  # never computed — most urgent
        computed_at = entry.get("computed_at", "")
        return (1, computed_at)  # stale-but-computed, oldest first

    candidates = sorted(rows, key=due_key)
    candidates = [r for r in candidates
                  if slow_store.get(r["id"]) is None
                  or datetime.fromisoformat(slow_store[r["id"]]["computed_at"]) < cutoff]

    attempted, succeeded = 0, 0
    for row in candidates[:MAX_SLOW_ATTEMPTS]:
        attempted += 1
        changes, http_status = _compute_slow_changes(row["id"], row["price"])
        if changes is None:
            if http_status == 429:
                print("  ! rate-limited after %d/%d attempts this run — stopping the "
                      "slow crawl until next time" % (succeeded, attempted),
                      file=sys.stderr)
                break
            print("  ! %s: no usable history this run" % row["id"], file=sys.stderr)
            time.sleep(SLOW_PACE_S)
            continue
        slow_store[row["id"]] = {**changes, "computed_at": now_iso}
        succeeded += 1
        time.sleep(SLOW_PACE_S)

    covered = sum(1 for r in rows if r["id"] in slow_store)
    return {"attempted": attempted, "succeeded": succeeded,
            "covered": covered, "total": len(rows)}


def compute(skip_slow_crawl=False):
    try:
        market = _get_json(MARKETS_URL)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ValueError) as exc:
        print("  ! %s — %s" % (MARKETS_URL, exc), file=sys.stderr)
        return None, None
    if not isinstance(market, list) or not market:
        print("  ! coins/markets returned no rows", file=sys.stderr)
        return None, None

    rows = []
    for rank, c in enumerate(market, 1):
        rows.append({
            "id": c["id"],
            "symbol": (c.get("symbol") or "").upper(),
            "name": c.get("name") or c["id"],
            "category": category_for(c["id"]),
            "rank": rank,
            "price": c.get("current_price"),
            "circulating_supply": c.get("circulating_supply"),
            "volume_24h": c.get("total_volume"),
            "market_cap": c.get("market_cap"),
            "chg_1h": c.get("price_change_percentage_1h_in_currency"),
            "chg_1d": c.get("price_change_percentage_24h_in_currency",
                             c.get("price_change_percentage_24h")),
            "chg_7d": c.get("price_change_percentage_7d_in_currency"),
            "chg_1m": c.get("price_change_percentage_30d_in_currency"),
            "chg_1y": c.get("price_change_percentage_1y_in_currency"),
        })

    slow_store = _load_json(SLOW_STORE, {})
    crawl = ({"attempted": 0, "succeeded": 0,
              "covered": sum(1 for r in rows if r["id"] in slow_store),
              "total": len(rows)}
             if skip_slow_crawl else _run_slow_crawl(rows, slow_store))

    for r in rows:
        entry = slow_store.get(r["id"])
        r["chg_3m"] = entry["chg_3m"] if entry else None
        r["chg_6m"] = entry["chg_6m"] if entry else None
        r["chg_ytd"] = entry["chg_ytd"] if entry else None
        r["slow_as_of"] = entry["computed_at"] if entry else None

    total_cap = sum(r["market_cap"] or 0 for r in rows)
    btc_cap = next((r["market_cap"] for r in rows if r["id"] == "bitcoin"), None)
    board = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total_market_cap": total_cap,
        "btc_dominance_pct": (btc_cap / total_cap * 100.0)
                              if btc_cap and total_cap else None,
        "rows": rows,
        "crawl": crawl,
    }
    return board, slow_store


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    ap.add_argument("--skip-slow-crawl", action="store_true",
                     help="fetch the fast columns only, advance no 3M/6M/YTD progress")
    args = ap.parse_args()

    board, slow_store = compute(skip_slow_crawl=args.skip_slow_crawl)
    if board is None:
        print("no crypto heat map resolved — keeping the previous one", file=sys.stderr)
        return 0

    c = board["crawl"]
    print("%d coins · dominance BTC %.1f%% · slow crawl: %d/%d attempted this run, "
          "%d/%d coins have 3M/6M/YTD so far · %s"
          % (len(board["rows"]), board["btc_dominance_pct"] or 0.0,
             c["succeeded"], c["attempted"], c["covered"], c["total"],
             board["generated"]))

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    for path, data in ((OUT, board), (SLOW_STORE, slow_store)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        print("wrote %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

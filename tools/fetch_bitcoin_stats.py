#!/usr/bin/env python3
"""Fetch the state of the Bitcoin network into source/finance/bitcoin_stats.json.

    python3 tools/fetch_bitcoin_stats.py            # fetch and write
    python3 tools/fetch_bitcoin_stats.py --dry-run  # print, write nothing

STANDARD LIBRARY ONLY. Unlike fetch_asset_board.py (which needs yfinance for equity
quotes) every number here comes from a plain public JSON endpoint, so this runs on any
Python anywhere with nothing installed. That is worth protecting: it means the board
survives a broken pip, a new runner image, or being moved to a different machine.

WHAT THIS IS FOR
build_finance.py renders The Bitcoin Board from this file. The split is the same one
the asset board already uses: the network lives here, the builder only reads JSON. A
Cloudflare hiccup at mempool.space can therefore never fail a build or blank a page.

FAIL-SAFE, SECTION BY SECTION
Every section is optional. A source that times out is simply absent from the payload
and the page drops that panel — it never renders a zero, and it never renders last
week's number as though it were current. The ONE thing that is not optional is the
block height: it is what every derived figure hangs off, so if that cannot be had the
script exits 0 having written nothing, the builder re-renders from the last committed
file, and the page keeps its honest "as of" stamp. A slightly old board beats a blank
one and beats a red inbox — the same posture fetch_asset_board.py takes with Yahoo.

WHY NOT A NODE
bitcoinexplorer.org-style dashboards show things only a full node with an address
index can know: UTXO set size, chain work, output-type breakdowns, coinjoin activity.
Public APIs cannot answer those, so this does not pretend to: the panels those would
fill are absent rather than estimated. Everything below is either a direct reading
from a public endpoint or arithmetic on Bitcoin's own consensus rules.

NOTHING HERE IS PERSONAL. No credentials, no account, no holdings — which is what
makes it safe to run in a public repo on a schedule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source", "finance", "bitcoin_stats.json")

MEMPOOL = "https://mempool.space/api"
BLOCKCHAIR = "https://api.blockchair.com/bitcoin/stats"

UA = "mistertranslation.com/finance (The Librarian's Ledger asset board)"
TIMEOUT = 30

# Used by the reporting and the self-test only. _btc_supply_sats() deliberately
# spells out 100_000_000 instead, so it stays a byte-for-byte copy of the
# function it is duplicated from — see the warning in its docstring.
SATS = 100_000_000

# How many points to keep for the two charts. The full price history is 25,000+
# points and the hash-rate year is 365; both are downsampled hard because this file
# is committed on every hourly run and a fat payload is a fat diff, forever.
CHART_POINTS = 120


# ─────────────────────────────────────────────────────────────────── fetching ──

def _get(url):
    """Parsed JSON, or None. Never raises: a source that is down is a missing
    panel, not a failed run."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — every failure mode is "skip this bit"
        print("  ! %s — %s" % (url, exc), file=sys.stderr)
        return None


def _tip():
    """The chain tip: height, its timestamp, and what was in it.

    /api/v1/blocks returns the most recent blocks in one call, so this is the
    cheapest way to get a height AND the timestamp the page's "time since last
    block" clock counts up from. Falls back to the bare height endpoint, because
    a height with no timestamp still builds a page; no height at all does not.
    """
    blocks = _get("%s/v1/blocks" % MEMPOOL)
    if isinstance(blocks, list) and blocks:
        b = blocks[0]
        if isinstance(b.get("height"), int):
            return {"height": b["height"], "timestamp": b.get("timestamp"),
                    "tx_count": b.get("tx_count"), "size": b.get("size"),
                    "weight": b.get("weight")}
    h = _get("%s/blocks/tip/height" % MEMPOOL)
    if isinstance(h, int):
        return {"height": h, "timestamp": None}
    return None


def _downsample(points, n=CHART_POINTS):
    """Evenly-spaced sample that always keeps the first and last point.

    Keeping both ends matters: the last point is today's value, which the page
    prints as a number beside the chart, and a chart whose line stops short of
    the figure printed next to it looks broken even when both are right.
    """
    if len(points) <= n:
        return points
    step = (len(points) - 1) / (n - 1)
    out = [points[int(round(i * step))] for i in range(n)]
    out[-1] = points[-1]
    return out


def _bucket_last(points, seconds):
    """One point per bucket of `seconds`, keeping the LAST in each — a close,
    not an average. Averaging would smooth away the highs and lows the chart
    exists to show, and would put the final point somewhere the price never
    actually traded."""
    out, seen = [], {}
    for ts, px in points:
        seen[ts // seconds] = [ts, px]
    for key in sorted(seen):
        out.append(seen[key])
    return out


def _price_history():
    """(spot, all-time high, weekly series, daily series) from mempool's own feed.

    ONE request answers all of it, because that endpoint's own resolution is
    already tiered — measured 2026-09-03 over 25,193 points: hourly for the last
    ~2.8 years, daily for a middle era, weekly back to 2010-07-19. So the whole
    history is there, and the only work here is thinning it to something worth
    committing every hour.

    WHAT THE TWO SERIES ARE FOR
      weekly  the entire history (~845 points). Drives the 3Y/10Y/ALL ranges AND
              every moving average — the 50/100/200-WEEK averages are a rolling
              mean over 50/100/200 of these points, computed in the browser so
              there is exactly one implementation of them.
      daily   the last two years (~730 points). Drives 1M through 1Y.
    Ranges shorter than a month are fetched live from Coinbase by the page, so
    intraday resolution costs this file nothing.

    The all-time high is the highest point in the feed. That is a close, so an
    intraday wick a few hundred dollars higher will not appear in it, and the
    page says so rather than implying this is the last word on the number.
    """
    d = _get("%s/v1/historical-price?currency=USD" % MEMPOOL)
    prices = (d or {}).get("prices")
    if not isinstance(prices, list) or not prices:
        return None, None, None, None
    clean = sorted(([p["time"], p["USD"]] for p in prices
                    if isinstance(p.get("time"), int)
                    and isinstance(p.get("USD"), (int, float)) and p["USD"] > 0),
                   key=lambda p: p[0])
    if not clean:
        return None, None, None, None
    top = max(clean, key=lambda p: p[1])
    now = clean[-1][0]
    weekly = _bucket_last(clean, 7 * 86400)
    daily = _bucket_last([p for p in clean if p[0] >= now - 730 * 86400], 86400)
    return clean[-1][1], {"usd": top[1], "ts": top[0]}, weekly, daily


def _hashrate():
    d = _get("%s/v1/mining/hashrate/1y" % MEMPOOL)
    if not isinstance(d, dict) or not d.get("currentHashrate"):
        return None
    series = [[h["timestamp"], h["avgHashrate"]]
              for h in d.get("hashrates") or []
              if isinstance(h, dict) and h.get("timestamp") and h.get("avgHashrate")]
    return {"current": d["currentHashrate"],
            "difficulty": d.get("currentDifficulty"),
            "series": _downsample(series)}


def _lightning():
    """Lightning's public snapshot, WITH the date it was taken.

    mempool.space rebuilds these statistics on its own cadence and "latest" has
    been observed weeks behind the present. The `as_of` date rides along so the
    page can label the panel honestly instead of implying it is as live as the
    block height beside it.
    """
    d = _get("%s/v1/lightning/statistics/latest" % MEMPOOL)
    latest = (d or {}).get("latest")
    if not isinstance(latest, dict) or not latest.get("total_capacity"):
        return None
    return {"capacity_sats": latest["total_capacity"],
            "nodes": latest.get("node_count"),
            "channels": latest.get("channel_count"),
            "tor_nodes": latest.get("tor_nodes"),
            "clearnet_nodes": latest.get("clearnet_nodes"),
            "avg_capacity_sats": latest.get("avg_capacity"),
            "med_capacity_sats": latest.get("med_capacity"),
            "as_of": (latest.get("added") or "")[:10] or None}


def _chain():
    """Whole-chain totals from Blockchair — the numbers no per-block endpoint has.

    Deliberately a second, independent provider. If it is down the page loses
    three rows and keeps everything else, which is a better trade than making
    the whole board depend on one company being up.
    """
    d = (_get(BLOCKCHAIR) or {}).get("data")
    if not isinstance(d, dict) or not d.get("blockchain_size"):
        return None
    return {"size_bytes": d.get("blockchain_size"),
            "tx_total": d.get("transactions"),
            "outputs_total": d.get("outputs"),
            "tx_24h": d.get("transactions_24h"),
            "blocks_24h": d.get("blocks_24h"),
            "avg_fee_24h_sats": d.get("average_transaction_fee_24h"),
            "median_fee_24h_sats": d.get("median_transaction_fee_24h")}


# ───────────────────────────────────────────────────────────────────── supply ──

def _btc_supply_sats(height):
    """Total satoshis mined through and including block `height`.

    Arithmetic, not an estimate — Bitcoin Core's own consensus subsidy formula,
    summed in integer satoshis: subsidy(h) = (50 BTC) >> (h // 210_000).

    ⚠️ This is a DELIBERATE second copy of tools/fetch_asset_board.py's function
    of the same name, and the two must stay identical. The alternative was to
    import it, which would drag yfinance (a module-scope import over there) into
    a script whose whole point is needing nothing installed. Eleven lines of
    consensus rules that have not changed since 2009 are the cheaper duplicate.
    Block 0 is excluded: the genesis coinbase was never spendable, which is why
    every explorer's supply is 50 BTC under the famous 20,999,999.9769.
    """
    HALVING_INTERVAL = 210_000
    INITIAL_SUBSIDY = 50 * 100_000_000
    total = 0
    for epoch in range((height // HALVING_INTERVAL) + 1):
        subsidy = INITIAL_SUBSIDY >> epoch
        if subsidy == 0:
            break
        lo = max(1, epoch * HALVING_INTERVAL)
        hi = min(height, epoch * HALVING_INTERVAL + HALVING_INTERVAL - 1)
        if hi >= lo:
            total += (hi - lo + 1) * subsidy
    return total


# ─────────────────────────────────────────────────────────────────────── main ──

def compute():
    tip = _tip()
    if not tip:
        return None

    height = tip["height"]
    spot, ath, weekly, daily = _price_history()
    supply_sats = _btc_supply_sats(height)

    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "generated_ts": int(datetime.now(timezone.utc).timestamp()),
        "tip": tip,
        "supply_sats": supply_sats,
        "sources": ["mempool.space", "api.blockchair.com"],
    }

    if spot:
        out["price_usd"] = spot
    if ath:
        out["ath"] = ath
    if weekly:
        out["price_weekly"] = weekly
    if daily:
        out["price_daily"] = daily

    adj = _get("%s/v1/difficulty-adjustment" % MEMPOOL)
    if isinstance(adj, dict) and adj.get("remainingBlocks") is not None:
        out["retarget"] = {
            "progress_pct": adj.get("progressPercent"),
            "remaining_blocks": adj.get("remainingBlocks"),
            "estimated_change_pct": adj.get("difficultyChange"),
            "previous_change_pct": adj.get("previousRetarget"),
            "estimated_ts": (int(adj["estimatedRetargetDate"] / 1000)
                             if adj.get("estimatedRetargetDate") else None),
            "next_height": adj.get("nextRetargetHeight"),
            "block_time_s": (adj.get("timeAvg") or 0) / 1000 or None,
        }

    hr = _hashrate()
    if hr:
        out["hashrate"] = hr

    mp = _get("%s/mempool" % MEMPOOL)
    if isinstance(mp, dict) and mp.get("count") is not None:
        out["mempool"] = {"count": mp["count"], "vsize": mp.get("vsize"),
                          "total_fee_sats": mp.get("total_fee")}

    fees = _get("%s/v1/fees/recommended" % MEMPOOL)
    if isinstance(fees, dict) and fees.get("minimumFee") is not None:
        out["fees"] = {"fastest": fees.get("fastestFee"),
                       "half_hour": fees.get("halfHourFee"),
                       "hour": fees.get("hourFee"),
                       "economy": fees.get("economyFee"),
                       "minimum": fees.get("minimumFee")}

    rw = _get("%s/v1/mining/reward-stats/144" % MEMPOOL)
    if isinstance(rw, dict) and rw.get("totalReward"):
        out["reward_144"] = {"reward_sats": int(rw["totalReward"]),
                             "fee_sats": int(rw.get("totalFee") or 0),
                             "tx": int(rw.get("totalTx") or 0)}

    ln = _lightning()
    if ln:
        out["lightning"] = ln

    ch = _chain()
    if ch:
        out["chain"] = ch

    return out


def selftest():
    """Check _btc_supply_sats against the halving boundaries, which are fixed
    facts about Bitcoin rather than anything this script decides.

    This exists because that function is a deliberate copy of the one in
    fetch_asset_board.py, and a copy with no test is a copy that will drift.
    Each checkpoint is the end of a reward era, where the total is a whole
    number anyone can do on paper: 209,999 blocks at 50 BTC, then 210,000 at
    25, and so on — the missing 50 being the genesis coinbase, which was never
    spendable and is excluded on purpose.
    """
    cases = [
        (209_999, 209_999 * 50),                                    # era 0 ends
        (419_999, 209_999 * 50 + 210_000 * 25),                     # era 1 ends
        (629_999, 209_999 * 50 + 210_000 * (25 + 12.5)),            # era 2 ends
        (839_999, 209_999 * 50 + 210_000 * (25 + 12.5 + 6.25)),     # era 3 ends
        (0, 0),                                                     # genesis: nothing
    ]
    bad = []
    for height, expect_btc in cases:
        got = _btc_supply_sats(height) / SATS
        if abs(got - expect_btc) > 1e-8:
            bad.append("height %d: expected %.8f BTC, got %.8f" % (height, expect_btc, got))

    # And the end of the schedule: the true spendable maximum, which is the
    # famous 20,999,999.9769 less the 50 unspendable genesis coins.
    final = _btc_supply_sats(33 * 210_000) / SATS
    if abs(final - 20_999_949.9769) > 1e-4:
        bad.append("final supply: expected 20,999,949.9769 BTC, got %.4f" % final)

    for line in bad:
        print("  FAIL %s" % line, file=sys.stderr)
    print("supply arithmetic: %s (%d checkpoints)"
          % ("FAILED" if bad else "ok", len(cases) + 1))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="print the payload, write nothing")
    ap.add_argument("--selftest", action="store_true",
                    help="check the supply arithmetic against the halvings, fetch nothing")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    stats = compute()
    if stats is None:
        # Exit 0 on purpose: keeping the last committed board and a green
        # workflow beats a red inbox over an upstream outage we cannot fix.
        print("no block height — keeping the previous bitcoin_stats.json",
              file=sys.stderr)
        return 0

    have = [k for k in ("price_usd", "retarget", "hashrate", "mempool", "fees",
                        "reward_144", "lightning", "chain") if k in stats]
    print("block %s · %s BTC issued · %d/8 sections"
          % ("{:,}".format(stats["tip"]["height"]),
             "{:,.0f}".format(stats["supply_sats"] / 1e8), len(have)))
    print("  have: %s" % ", ".join(have))
    missing = [k for k in ("price_usd", "retarget", "hashrate", "mempool", "fees",
                           "reward_144", "lightning", "chain") if k not in stats]
    if missing:
        print("  MISSING (those panels will not render): %s" % ", ".join(missing))

    if args.dry_run:
        print(json.dumps(stats, indent=1)[:2000])
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # Compact, not indented. The price history is ~1,600 points, and one line
    # per number would turn a 35KB file into a 250KB one that is rewritten
    # every time this runs. It is generated data, not something anyone edits —
    # `python3 -m json.tool` renders it for a human in one command.
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, separators=(",", ":"), ensure_ascii=False)
        fh.write("\n")
    print("wrote %s (%.1f KB)"
          % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Compute the Crypto Screener into source/finance/crypto_screener.json.

    python3 tools/fetch_crypto_screener.py            # compute and write
    python3 tools/fetch_crypto_screener.py --dry-run  # print, write nothing

STANDARD LIBRARY ONLY (urllib) — no key, no yfinance. An independent,
self-contained reimplementation of the 4-pillar scoring behind mstr-trader's
own (private) MiSTeRCryptoScreener — same four pillars, same 35/35/15/15
weights, same intent (rank a curated coin universe on trend/momentum/
volatility/relative-strength, cross-sectionally) — but built fresh against
CoinGecko's public API rather than reading that private tool's output, same
discipline as this repo's CEBE and Bitcoin-vs-Humanity ports: no reference
to that private repo anywhere on the page, no shared code, no shared data.

WHY A FRESH BUILD RATHER THAN A PORT OF THE OUTPUT (2026-09-16)
The private tool's own crypto data (Alpaca's spot feed) was found the same
day to carry years of fabricated/mismatched history under several tickers —
ARB/USD's 3-month return briefly read +19,746% off a stuck/wrong historical
price. Publishing that pipeline's output directly would have republished
whatever it gets wrong next. CoinGecko is this site's own already-proven
source (fetch_crypto_heatmap.py has run against it since 2026-09-07) and is
verified independently below (see COIN_IDS) — every id checked against its
returned `symbol`/`name` before being trusted, not merely guessed.

WHAT'S GENUINELY DIFFERENT FROM THE PRIVATE VERSION, AND WHY
Volatility (15% weight) cannot be a true ATR%, because CoinGecko's
`/coins/{id}/market_chart` returns one CLOSE-equivalent price per day, not
OHLC — there is no High/Low to take a true range from. This uses a
close-to-close realized-volatility proxy instead (the daily |log return|,
scored against its own trailing 20-day average with the identical
"Goldilocks — moderate is good, spiked or dormant is penalised" curve the
private tool uses for its ATR ratio). Same goal, same shape of scoring,
different raw ingredient — stated here and on the page itself.

Momentum's RSI/MACD/volume-expansion "confirm" term IS fully portable
(CoinGecko's market_chart also returns a parallel `total_volumes` series),
so that part is a faithful, not merely analogous, port.

NO VERDICTS. Every pillar and the composite score are shown; there is no
BUY/HOLD/TRIM/AVOID label anywhere in this output, on Michael's explicit
call (2026-09-16) — a label like that next to a specific coin reads as a
directive to a stranger, which is exactly what this whole publication's
`build_ask()`/`_legal()` footer already refuses to do ("what should I buy"
is the one question this site never answers). The private tool's own
verdict is an internal research heuristic; it stays internal.

THE SLOW CRAWL — full daily history is the expensive part, not the score
Every pillar here needs each coin's own ~year of daily closes (for SMA200,
the realized-vol trailing average, and the 1m/3m return legs) — a per-coin
`market_chart` call, the same endpoint whose free/anonymous rate limit
`fetch_crypto_heatmap.py` already measured directly (three calls, 2.5s
apart, was enough to draw a sustained 429). So this follows that script's
own paced-crawl shape exactly: a handful of coins get their full series
fetched/refreshed each run, persisted to SLOW_STORE keyed by coin id, and
the board is built from whatever's cached so far — a coin not yet reached
renders with its price and identity but no score, never a guessed one.
With a ~32-coin universe and the same pacing as the heat map, full coverage
takes several days to a week to first fill in, then refreshes on a rolling
basis (SLOW_REFRESH_DAYS) same as the heat map's 3M/6M/YTD crawl.

NOTHING HERE IS PERSONAL. Every input is a public market quote — no
account, no key, nothing about anyone's holdings — which is what makes it
safe to run in a public repo on a schedule.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source", "finance", "crypto_screener.json")
SLOW_STORE = os.path.join(ROOT, "source", "finance", "crypto_screener_series.json")

UA = "mistertranslation.com/finance (The Librarian's Ledger Crypto Screener)"
MARKETS_URL = ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
               "&ids=%s&per_page=250&sparkline=false")
CHART_URL = "https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=usd&days=%d"

CHART_DAYS = 364          # under CoinGecko's public 365-day historical ceiling
MAX_SLOW_ATTEMPTS = 10    # a safety ceiling; the first 429 stops the run well before this
SLOW_PACE_S = 3.5         # gap between per-coin historical calls — same pacing as the heat map
SLOW_REFRESH_DAYS = 5     # how long a coin's cached series is trusted before it's due again
MIN_BARS = 220            # need enough real history for a 200-day SMA plus room to spare

# Every id here was verified live against CoinGecko's own /coins/markets response
# (2026-09-16) — its returned `symbol` and `name` checked to actually match the
# intended coin, not merely assumed from the slug. Two are easy to get wrong by
# guessing: POL is "polygon-ecosystem-token" (the post-rebrand token; the old
# "matic-network" id is a different, legacy listing), and dogwifhat's id is
# "dogwifcoin", not the more obvious "dogwifhat".
COIN_IDS = {
    "AAVE": "aave", "ADA": "cardano", "ARB": "arbitrum", "AVAX": "avalanche-2",
    "BAT": "basic-attention-token", "BCH": "bitcoin-cash", "BONK": "bonk",
    "BTC": "bitcoin", "CRV": "curve-dao-token", "DOGE": "dogecoin",
    "DOT": "polkadot", "ETH": "ethereum", "FIL": "filecoin", "GRT": "the-graph",
    "HYPE": "hyperliquid", "LDO": "lido-dao", "LINK": "chainlink",
    "LTC": "litecoin", "ONDO": "ondo-finance", "PEPE": "pepe",
    "POL": "polygon-ecosystem-token", "RENDER": "render-token",
    "SHIB": "shiba-inu", "SKY": "sky", "SOL": "solana", "SUSHI": "sushi",
    "TRUMP": "official-trump", "UNI": "uniswap", "WIF": "dogwifcoin",
    "XRP": "ripple", "XTZ": "tezos", "YFI": "yearn-finance",
}


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


def _atomic_write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


# ── the slow crawl: one coin's full daily series, cached ────────────────────

def _fetch_series(coin_id):
    """[(ts_ms, close), ...] ascending, or (None, http_status) on failure."""
    try:
        data = _get_json(CHART_URL % (coin_id, CHART_DAYS))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ValueError) as exc:
        return None, getattr(exc, "code", None)
    prices = [(int(p[0]), float(p[1])) for p in data.get("prices", []) if p[1] is not None]
    volumes = [(int(p[0]), float(p[1])) for p in data.get("total_volumes", []) if p[1] is not None]
    if len(prices) < MIN_BARS:
        return None, None
    return {"prices": prices, "volumes": volumes}, None


def _run_slow_crawl(universe_ids, slow_store):
    now_iso = datetime.now(timezone.utc).isoformat()
    cutoff = datetime.now(timezone.utc) - timedelta(days=SLOW_REFRESH_DAYS)

    def due_key(cid):
        entry = slow_store.get(cid)
        if entry is None:
            return (0, "")
        return (1, entry.get("computed_at", ""))

    # BTC first, always — every coin's Rel-Strength pillar depends on it.
    candidates = sorted(universe_ids, key=due_key)
    if "bitcoin" in candidates:
        candidates.remove("bitcoin")
        candidates.insert(0, "bitcoin")
    candidates = [c for c in candidates
                  if slow_store.get(c) is None
                  or datetime.fromisoformat(slow_store[c]["computed_at"]) < cutoff]

    attempted, succeeded = 0, 0
    for cid in candidates[:MAX_SLOW_ATTEMPTS]:
        attempted += 1
        series, status = _fetch_series(cid)
        if series is None:
            if status == 429:
                print("  ! rate-limited after %d/%d attempts this run — stopping "
                      "the slow crawl until next time" % (succeeded, attempted),
                      file=sys.stderr)
                break
            print("  ! %s: no usable history this run" % cid, file=sys.stderr)
            time.sleep(SLOW_PACE_S)
            continue
        slow_store[cid] = {**series, "computed_at": now_iso}
        succeeded += 1
        time.sleep(SLOW_PACE_S)

    covered = sum(1 for c in universe_ids if c in slow_store)
    return {"attempted": attempted, "succeeded": succeeded,
            "covered": covered, "total": len(universe_ids)}


# ── pillar math — all computed from a close (+ volume) series only ─────────

def _sma(closes, n):
    if len(closes) < n:
        return None
    return sum(closes[-n:]) / n


def _rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(len(closes) - n, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_gain, avg_loss = sum(gains) / n, sum(losses) / n
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - 100 / (1 + rs), 2)


def _ema_series(closes, span):
    k = 2.0 / (span + 1)
    out = [closes[0]]
    for c in closes[1:]:
        out.append(c * k + out[-1] * (1 - k))
    return out


def _macd_state(closes):
    """3-state {-1,0,+1}: sign of the MACD histogram + whether it's turning,
    same reduced signal (magnitude discarded — it would double-count momentum
    and RSI) as the private tool's own _macd_state."""
    if len(closes) < 35:
        return 0
    ef, es = _ema_series(closes, 12), _ema_series(closes, 26)
    macd = [a - b for a, b in zip(ef, es)]
    sig = _ema_series(macd, 9)
    hist = [a - b for a, b in zip(macd, sig)]
    if len(hist) < 3:
        return 0
    h0, h1 = hist[-1], hist[-2]
    if h0 > 0 and h0 >= h1:
        return 1
    if h0 < 0 and h0 <= h1:
        return -1
    return 0


def _pct_return(closes, bars):
    if len(closes) < bars + 1:
        return None
    prev, cur = closes[-bars - 1], closes[-1]
    if prev == 0:
        return None
    return (cur / prev - 1.0) * 100.0


def _trend_score(closes):
    price = closes[-1]
    sma20, sma50, sma200 = _sma(closes, 20), _sma(closes, 50), _sma(closes, 200)
    sma50_5 = _sma(closes[:-5], 50) if len(closes) >= 55 else None
    score = 50.0
    if sma200 is not None:
        score += 20 if price > sma200 else -15
    if sma50 is not None:
        score += 15 if price > sma50 else -10
    if sma20 is not None:
        score += 10 if price > sma20 else -5
    if sma50 is not None and sma50_5 is not None:
        score += 5 if sma50 > sma50_5 else 0
    if sma50 is not None and sma200 is not None:
        score += 5 if sma50 > sma200 else 0
    return max(0.0, min(100.0, score))


def _realized_vol_ratio(closes, n_avg=20):
    """Close-to-close stand-in for the private tool's ATR%-vs-its-own-average
    (see the module docstring — no High/Low available here). `None` when
    there isn't a full trailing window of usable daily moves yet."""
    if len(closes) < n_avg + 2:
        return None
    moves = []
    for i in range(1, len(closes)):
        if closes[i - 1] > 0:
            moves.append(abs(math.log(closes[i] / closes[i - 1])) * 100.0)
    if len(moves) < n_avg + 1:
        return None
    avg = sum(moves[-(n_avg + 1):-1]) / n_avg
    if avg <= 0:
        return None
    return round(moves[-1] / avg, 3)


def _vol_score(vr):
    """Identical Goldilocks curve to the private tool's _vol_score."""
    if vr is None:
        return 50.0
    if vr <= 0:
        return 5.0
    if vr < 0.5:
        return max(5.0, 30.0 * vr / 0.5)
    if vr <= 1.5:
        return max(50.0, 100.0 - 50.0 * (vr - 1.0) ** 2 / 0.25)
    if vr <= 3.0:
        return max(5.0, 50.0 - 45.0 * (vr - 1.5) / 1.5)
    return 5.0


def _volume_expansion(volumes, n_recent=10, n_prior=20):
    vols = [v for _, v in volumes]
    need = n_recent + n_prior
    if len(vols) < need:
        return None
    recent = sum(vols[-n_recent:]) / n_recent
    prior = sum(vols[-(n_recent + n_prior):-n_recent]) / n_prior
    if prior <= 0:
        return None
    return round(recent / prior, 3)


def _percentile_rank(values, target):
    """% of the OTHER values a `target` beats — 50 with a one-item universe."""
    others = [v for v in values if v is not target]
    if not others:
        return 50.0
    beaten = sum(1 for v in others if target > v)
    tied = sum(1 for v in others if target == v)
    return 100.0 * (beaten + 0.5 * tied) / len(others)


def _compute_metrics(symbol, series, btc_series):
    prices = series["prices"]
    closes = [p for _, p in prices]
    if len(closes) < MIN_BARS:
        return None
    price = closes[-1]
    ret_1m = _pct_return(closes, 30)
    ret_3m = _pct_return(closes, 91)
    rsi = _rsi(closes)
    vol_ratio = _realized_vol_ratio(closes)
    vol_exp = _volume_expansion(series.get("volumes", []))
    macd = _macd_state(closes)

    btc_closes = [p for _, p in btc_series["prices"]] if btc_series else None
    btc_ret_1m = _pct_return(btc_closes, 30) if btc_closes else None
    btc_ret_3m = _pct_return(btc_closes, 91) if btc_closes else None
    excess_1m = (ret_1m - btc_ret_1m) if (ret_1m is not None and btc_ret_1m is not None) else None
    excess_3m = (ret_3m - btc_ret_3m) if (ret_3m is not None and btc_ret_3m is not None) else None

    # bounded ±10 confirm aggregate: RSI position + volume expansion + MACD —
    # same three inputs, same cap as the private tool's own confirm term.
    confirm = 0.0
    if rsi is not None:
        confirm += max(-3.0, min(3.0, (rsi - 50.0) / 5.0))
    if vol_exp is not None:
        confirm += max(-3.0, min(3.0, (vol_exp - 1.0) * 3.0))
    confirm += macd * 3.0
    confirm = max(-10.0, min(10.0, confirm))

    return {
        "symbol": symbol, "price": price, "ret_1m": ret_1m, "ret_3m": ret_3m,
        "rsi": rsi, "vol_ratio": vol_ratio, "vol_score": _vol_score(vol_ratio),
        "trend_score": _trend_score(closes), "confirm": round(confirm, 2),
        "excess_1m": excess_1m, "excess_3m": excess_3m,
        "as_of": series.get("computed_at"),
    }


def _score_all(rows):
    """Cross-sectional Momentum (return percentile + confirm) and Rel Strength
    (excess-return percentile), same 35/35/15/15 pillar weights as the private
    tool. Rows missing a leg (still mid-crawl) keep their other pillars and get
    a neutral 50 for the one they can't compute yet — never dropped outright,
    since price/identity is still worth showing while a score fills in."""
    blend = [(r["ret_1m"] or 0) * 0.5 + (r["ret_3m"] or 0) * 0.5 for r in rows]
    excess_blend = [(r["excess_1m"] or 0) * 0.5 + (r["excess_3m"] or 0) * 0.5 for r in rows]
    for i, r in enumerate(rows):
        mom_pct = _percentile_rank(blend, blend[i]) if r["ret_1m"] is not None else 50.0
        rs_pct = _percentile_rank(excess_blend, excess_blend[i]) if r["excess_1m"] is not None else 50.0
        momentum_score = max(0.0, min(100.0, mom_pct + r["confirm"]))
        r["momentum_score"] = round(momentum_score, 1)
        r["rel_strength_score"] = round(rs_pct, 1)
        r["trend_score"] = round(r["trend_score"], 1)
        r["vol_score"] = round(r["vol_score"], 1)
        r["composite"] = round(
            r["trend_score"] * 0.35 + r["momentum_score"] * 0.35
            + r["vol_score"] * 0.15 + r["rel_strength_score"] * 0.15, 1)
    rows.sort(key=lambda r: r["composite"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def compute(skip_slow_crawl=False):
    ids_csv = ",".join(COIN_IDS.values())
    try:
        market = _get_json(MARKETS_URL % ids_csv)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            ValueError) as exc:
        print("  ! %s — %s" % (MARKETS_URL % ids_csv, exc), file=sys.stderr)
        return None, None
    if not isinstance(market, list) or not market:
        print("  ! coins/markets returned no rows", file=sys.stderr)
        return None, None
    by_id = {c["id"]: c for c in market}

    universe_ids = list(COIN_IDS.values())
    slow_store = _load_json(SLOW_STORE, {})
    crawl = ({"attempted": 0, "succeeded": 0,
              "covered": sum(1 for c in universe_ids if c in slow_store),
              "total": len(universe_ids)}
             if skip_slow_crawl else _run_slow_crawl(universe_ids, slow_store))

    btc_series = slow_store.get("bitcoin")
    scored, unscored = [], []
    for symbol, coin_id in COIN_IDS.items():
        c = by_id.get(coin_id)
        base = {
            "symbol": symbol, "id": coin_id,
            "name": (c or {}).get("name", symbol),
            "image": (c or {}).get("image"),
            "price": (c or {}).get("current_price"),
            "market_cap": (c or {}).get("market_cap"),
        }
        series = slow_store.get(coin_id)
        if not series or not btc_series:
            unscored.append(base)
            continue
        m = _compute_metrics(symbol, series, btc_series)
        if m is None:
            unscored.append(base)
            continue
        scored.append({**base, **m})

    scored = _score_all(scored)

    board = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "rows": scored,
        "unscored": unscored,
        "crawl": crawl,
    }
    return board, slow_store


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    ap.add_argument("--skip-slow-crawl", action="store_true",
                     help="score whatever's already cached, advance no crawl progress")
    args = ap.parse_args()

    board, slow_store = compute(skip_slow_crawl=args.skip_slow_crawl)
    if board is None:
        print("no crypto screener resolved — keeping the previous one", file=sys.stderr)
        return 0

    c = board["crawl"]
    print("%d scored, %d still mid-crawl · slow crawl: %d/%d attempted this run, "
          "%d/%d coins have full history so far · %s"
          % (len(board["rows"]), len(board["unscored"]), c["succeeded"], c["attempted"],
             c["covered"], c["total"], board["generated"]))

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        for r in board["rows"][:10]:
            print("  #%-3d %-8s composite=%-6s trend=%-6s mom=%-6s vol=%-6s rs=%-6s"
                  % (r["rank"], r["symbol"], r["composite"], r["trend_score"],
                     r["momentum_score"], r["vol_score"], r["rel_strength_score"]))
        return 0

    _atomic_write(OUT, board)
    _atomic_write(SLOW_STORE, slow_store)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("wrote %s" % os.path.relpath(SLOW_STORE, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

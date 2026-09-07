#!/usr/bin/env python3
"""Compute the CEBE board into source/finance/cebe.json.

    python3 tools/fetch_cebe.py            # compute and write
    python3 tools/fetch_cebe.py --dry-run  # print, write nothing

CEBE (Common Equity Bitcoin Exposure) answers a sharper question than the plain
Treasuries board's "how much BTC does this company hold": *if every senior claim
on the balance sheet — debt AND any outstanding preferred stock's liquidation
preference, net of cash on hand — were paid in full right now, how much of that
BTC would actually still belong to a COMMON shareholder?* Unlike the Treasuries
board (one BTC price, ranks by coins held), this needs a live STOCK price per
company too, since the answer is expressed per share and compared against what
a share actually costs (see the Sats/$100 field).

WHY THIS IS A SEPARATE SCRIPT FROM fetch_treasuries.py
Same reasoning as every other board here: an outage in one must never cost the
others their refresh (see fetch_treasuries.py's own docstring). This one is also
the only board besides fetch_asset_board.py that touches yfinance, so a Yahoo
rate-limit affects at most two of the four fetchers, never all of them at once.

FORMULA — matches cebetracker.io's own published spec (verified 2026-09-06),
not an independently-derived one:
    Net Senior Claims  = Debt + Preferred liquidation preference − Cash
    CEBE (BTC)         = (BTC held × BTC price − Net Senior Claims) / BTC price
    CEBE sats/share     = CEBE (BTC) / shares outstanding × 100,000,000
    Sats/$100           = CEBE sats/share × 100 / stock price
    Claims %            = Net Senior Claims / (BTC held × BTC price) × 100
    Break-even BTC price = Net Senior Claims / BTC held

TWO MORE METRICS (added 2026-09-07), neither from cebetracker.io — a genuine
extension past matching their spec, prompted by the question "is netting cash
against a PERPETUAL preferred's principal even realistic, when a company
services that stock with dividends forever rather than retiring it?":

    Preferred-dividend COVERAGE (a GOING-CONCERN check, not a liquidation one —
    every metric above assumes claims are paid off TODAY; this asks whether the
    core business can actually afford the yearly dividend BILL):
        Annual dividend obligation = Preferred liq. pref. × blended dividend rate
        Coverage = Operating cash flow (core business, TTM) / annual obligation
    `preferred_div_rate_pct` and `operating_cf_usd` are curated, seed-file
    fields (like debt_usd/preferred_liq_usd) — populated only for companies
    that actually carry preferred stock (today: MSTR, MTPLF). `coverage_reason`
    distinguishes three different kinds of blank: `no_preferred` (nothing to
    cover), `ocf_undisclosed` (real preferred, but the company's own filings
    don't isolate core-business cash flow cleanly enough to compute this
    honestly — MTPLF today), `rate_unknown` (preferred exists, dividend rate
    not yet curated). Never force a number into a reason slot — a real "not
    disclosed" beats a fabricated ratio.

    BTC-price STRESS (a sensitivity test, explicitly NOT a forecast — same
    posture as this board declining to build cebetracker.io's 5-year
    projections): Sats/$100 recomputed at BTC −20% and −50% from today,
    holding the STOCK price and every claim fixed. Deliberately does not scale
    the stock price down too — doing so would make a BTC-pure-play's ratio
    look artificially stable (both sides of the fraction shrinking together),
    hiding the exact mechanism this exists to expose: fixed-dollar debt and
    preferred claims eating a growing share of a shrinking BTC pile. A −50%
    reading below zero is a real signal — common's claimed BTC backing would
    be gone at that price, even though the company still legally owns every
    coin.

ONLY TICKERS THAT PASS A REAL FRESHNESS CHECK ARE INCLUDED
A company is dropped from the OUTPUT (not from the seed file) if yfinance can't
price it at all, or if its most recent daily close is more than STALE_DAYS old —
the same "never act on a stale bar" discipline mstr-trader's own CEBE tracker
applies. This is exactly how Méliuz and OranjeBTC ended up excluded from the
curated seed file in the first place (see cebe_seed.json's own note): their US
OTC tickers either return nothing or return a quote too old to trust.

NOTHING HERE IS PERSONAL. Every input is a public market quote or the curated
seed file's own dated approximations — no account, no key, nothing about
anyone's personal holdings.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    sys.exit("yfinance is required:  python3 -m pip install yfinance")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "source", "finance", "cebe_seed.json")
ASSET_BOARD = os.path.join(ROOT, "source", "finance", "asset_board.json")
OUT = os.path.join(ROOT, "source", "finance", "cebe.json")

STALE_DAYS = 4   # daily bar — same threshold mstr-trader's market_data.is_stale uses

# Same fallback chain fetch_treasuries.py already uses for a BTC price when the
# asset board doesn't have one — kept identical so a shared outage behaves the
# same way in both places.
_PRICE_APIS = [
    "https://mempool.space/api/v1/prices",
    "https://api.blockchair.com/bitcoin/stats",
]

UA = "mistertranslation.com/finance (The Librarian's Ledger CEBE board)"


def _get_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — a down source is a skip, not a crash
        print("  ! %s — %s" % (url, exc), file=sys.stderr)
        return None


def _btc_price_from_asset_board():
    if not os.path.exists(ASSET_BOARD):
        return None, None
    try:
        with open(ASSET_BOARD, encoding="utf-8") as fh:
            board = json.load(fh)
    except (ValueError, OSError):
        return None, None
    for a in board.get("assets", []):
        if a.get("symbol") == "BTC" and a.get("price"):
            return float(a["price"]), board.get("generated")
    return None, None


def _btc_price_fallback():
    d = _get_json(_PRICE_APIS[0])
    if isinstance(d, dict) and d.get("USD"):
        return float(d["USD"])
    d = _get_json(_PRICE_APIS[1])
    if isinstance(d, dict):
        v = (d.get("data") or {}).get("market_price_usd")
        if v:
            return float(v)
    return None


def _closes_with_dates(df):
    """[(date_str, close), ...] out of a yfinance frame, newest last, NaNs
    dropped. [] if unusable. Dates matter here (unlike fetch_asset_board.py's
    `_closes`) because a stale OTC quote is exactly the failure mode this
    board has to catch — see the module docstring."""
    if df is None or getattr(df, "empty", True) or "Close" not in df:
        return []
    col = df["Close"]
    if hasattr(col, "columns"):        # MultiIndex ('Close', sym) → first column
        col = col.iloc[:, 0]
    col = col.dropna()
    out = []
    for idx, val in col.items():
        try:
            d = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
            out.append((d, float(val)))
        except Exception:
            continue
    return out


def _stock_price(ticker):
    """Latest close for `ticker`, or None if unpriceable OR the last bar is
    stale (>STALE_DAYS old). Tries fast_info first (cheap, one call), falls
    back to a short daily-bar history — mirrors fetch_asset_board.py's `_fast`/
    `_bars` split, but this one checks the bar's OWN date rather than trusting
    whatever fast_info hands back blind."""
    try:
        t = yf.Ticker(ticker)
        hist = _closes_with_dates(t.history(period="10d", interval="1d"))
    except Exception as exc:
        print("  ! %s: %s" % (ticker, exc), file=sys.stderr)
        return None, None
    if not hist:
        return None, None
    last_date, last_price = hist[-1]
    try:
        age_days = (datetime.now(timezone.utc).date()
                    - datetime.strptime(last_date, "%Y-%m-%d").date()).days
    except Exception:
        age_days = 0
    if age_days > STALE_DAYS:
        print("  ! %s: last bar %s is %dd old — stale, skipping"
              % (ticker, last_date, age_days), file=sys.stderr)
        return None, None
    return last_price, last_date


def compute():
    """The ranked CEBE board, or None if nothing usable. Never raises."""
    if not os.path.exists(SEED):
        print("  ! no source/finance/cebe_seed.json — nothing to compute", file=sys.stderr)
        return None
    try:
        with open(SEED, encoding="utf-8") as fh:
            seed = json.load(fh)
    except (ValueError, OSError) as exc:
        print("  ! cebe_seed.json unreadable — %s" % exc, file=sys.stderr)
        return None

    companies = seed.get("companies") or []
    if not companies:
        print("  ! cebe_seed.json has no companies", file=sys.stderr)
        return None

    btc_price, btc_stamp = _btc_price_from_asset_board()
    btc_source = "asset_board.json"
    if not btc_price:
        btc_price = _btc_price_fallback()
        btc_source = "mempool.space/blockchair (fallback)"
        btc_stamp = None
    if not btc_price:
        print("  ! no BTC price from any source — keeping the previous board",
              file=sys.stderr)
        return None

    rows = []
    for c in companies:
        ticker = c.get("ticker")
        btc = c.get("btc_holdings")
        shares = c.get("shares_out")
        if not ticker or not btc or btc <= 0 or not shares or shares <= 0:
            print("  ! skipping malformed entry: %r" % (c,), file=sys.stderr)
            continue

        price, price_date = _stock_price(ticker)
        if not price:
            continue   # unpriceable or stale — dropped from the OUTPUT, not the seed

        debt = float(c.get("debt_usd") or 0)
        preferred = float(c.get("preferred_liq_usd") or 0)
        cash = float(c.get("cash_usd") or 0)      # always 0 today — see seed's note
        cost = float(c.get("cost_basis") or 0)

        mcap = price * shares
        btc_nav = btc * btc_price
        claims = debt + preferred - cash

        cebe_usd = btc_nav - claims
        cebe_btc = cebe_usd / btc_price
        cebe_sats_per_share = cebe_btc / shares * 1e8
        sats_per_100 = cebe_sats_per_share * 100 / price
        breakeven = (claims / btc) if (btc and claims > 0) else None

        # Preferred-dividend COVERAGE — a going-concern companion to everything
        # above (which is all a liquidation snapshot). Three distinct "can't
        # answer this" reasons, kept separate rather than collapsed into one
        # blank — see the module docstring's formula section.
        div_rate = float(c.get("preferred_div_rate_pct") or 0)
        ocf_raw = c.get("operating_cf_usd")
        ocf = float(ocf_raw) if ocf_raw is not None else None
        annual_div_obligation = (preferred * div_rate / 100) if (preferred and div_rate) else None
        if not preferred:
            coverage_ratio, coverage_reason = None, "no_preferred"
        elif ocf is None:
            coverage_ratio, coverage_reason = None, "ocf_undisclosed"
        elif annual_div_obligation:
            coverage_ratio, coverage_reason = round(ocf / annual_div_obligation, 3), None
        else:
            coverage_ratio, coverage_reason = None, "rate_unknown"

        # BTC-price STRESS — Sats/$100 at BTC -20%/-50%, stock price and claims
        # held fixed. Not a forecast — see the module docstring.
        def _stress(factor):
            stressed_btc_price = btc_price * factor
            stressed_nav = btc * stressed_btc_price
            stressed_cebe_btc = (stressed_nav - claims) / stressed_btc_price
            stressed_sats_share = stressed_cebe_btc / shares * 1e8
            return round(stressed_sats_share * 100 / price)
        stress_20 = _stress(0.8)
        stress_50 = _stress(0.5)

        rows.append({
            "ticker": ticker,
            "name": c.get("name", ticker),
            "kind": c.get("kind", "treasury"),
            "country": c.get("country"),
            "domain": c.get("domain"),
            "primary_ticker": c.get("primary"),   # the foreign primary listing, if any
            "price": round(price, 4),
            "price_date": price_date,
            "market_cap": round(mcap),
            "btc_holdings": btc,
            "btc_nav": round(btc_nav),
            "mnav": round(mcap / btc_nav, 3) if btc_nav else None,
            "shares_out": shares,
            "cost_basis": round(cost) if cost else None,
            "debt_usd": round(debt),
            "preferred_usd": round(preferred),
            "cash_usd": round(cash) if cash else None,
            "claims_usd": round(claims),
            "claims_pct": round(claims / btc_nav * 100, 1) if btc_nav else None,
            "cebe_usd": round(cebe_usd),
            "cebe_btc": round(cebe_btc, 2),
            "cebe_sats_per_share": round(cebe_sats_per_share),
            "cebe_sats_per_100": round(sats_per_100),
            "breakeven_btc_price": round(breakeven, 2) if breakeven is not None else None,
            "preferred_div_rate_pct": div_rate or None,
            "operating_cf_usd": ocf,
            "annual_div_obligation": (round(annual_div_obligation)
                                      if annual_div_obligation else None),
            "coverage_ratio": coverage_ratio,
            "coverage_reason": coverage_reason,
            "stress_sats_per_100_20": stress_20,
            "stress_sats_per_100_50": stress_50,
            "as_of": c.get("as_of") or seed.get("as_of"),
        })

    if not rows:
        return None

    rows.sort(key=lambda r: (r["cebe_sats_per_100"] if r["cebe_sats_per_100"] is not None
                              else -1e18), reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "btc_price": btc_price,
        "btc_price_source": btc_source,
        "btc_price_as_of": btc_stamp,
        "seed_as_of": seed.get("as_of"),
        "rows": rows,
        "count": len(rows),
        "excluded_count": len(companies) - len(rows),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = ap.parse_args()

    board = compute()
    if board is None:
        print("no CEBE board resolved — keeping the previous one", file=sys.stderr)
        return 0

    print("%d priced (%d excluded: unpriceable/stale) · BTC $%s (%s) · %s"
          % (board["count"], board["excluded_count"],
             "{:,.0f}".format(board["btc_price"]), board["btc_price_source"],
             board["generated"]))
    if board["rows"]:
        top = board["rows"][0]
        print("  top: %s — %s sats/$100" % (top["ticker"], "{:,}".format(top["cebe_sats_per_100"])))

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(board, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, OUT)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Compute the Money Worldwide board into source/finance/money_worldwide.json.

    python3 tools/fetch_money_worldwide.py             # compute and write (if due)
    python3 tools/fetch_money_worldwide.py --force      # ignore the refresh cadence
    python3 tools/fetch_money_worldwide.py --dry-run    # print, write nothing

WHAT THIS BOARD COUNTS
Four things the other six boards don't: what a dollar buys in another currency
(exchange rates), how much money actually exists (M0/M1/M2-class money supply),
who holds the world's reserves — foreign exchange AND gold — and how big the
world's economy and government debt actually are. Bitcoin's market cap is
plotted against all four, the same "where does it rank" framing board.html
already applies to gold, silver and the mega-caps.

THE IMF RESEARCH THAT SHAPED THIS SCRIPT — READ BEFORE "FIXING" A SOURCE HERE
The obvious plan was "pull all of this straight from the IMF." Two of the IMF's
own systems turned out to be real, live, and keyless — and neither of them
serves actual observation data:
  - dataservices.imf.org (the old SDMX_JSON.svc everyone's blog post still
    links to) no longer resolves at all. DNS-dead.
  - sdmxcentral.imf.org/ws/public/sdmxapi/rest is alive and genuinely keyless
    — dataflow/datastructure/codelist queries all return real metadata (this
    is how EXR/MSG/GGD/NAG/ILV1/COF were confirmed to exist as IMF dataflows
    in the first place). But every /data/... query on it returns SDMX error
    501, "Data Queries are not implemented" — verified directly. It is a
    structure REGISTRY, not a data service; nothing at IMF exposes the actual
    observations behind those dataflows without a login (portal.api.imf.org).
  - The legacy human-facing exports (imf.org/external/np/fin/data/rms_five.aspx,
    the representative-exchange-rate TSV) return a hard Akamai 403 from a
    datacenter IP — the exact "Yahoo blocks datacenter ranges" problem this
    repo already lives with for yfinance, just from a different vendor's edge.

One IMF system DOES serve real observation data, keylessly, and is what this
script actually uses for growth/debt/GDP: the DataMapper API behind
imf.org/en/datamapper (the same JSON the public DataMapper site itself calls).
It is genuinely comprehensive — one call returns ~190-230 economies including
a WEOWORLD aggregate — but its catalogue is WEO/fiscal-surveillance indicators
(GDP, government debt-to-GDP, current account, …), not monetary aggregates,
not FX reserves, not spot exchange rates. Its one monetary-adjacent series,
Broad Money (% of GDP), turned out on inspection to cover only a curated set
of IMF-program African economies — not a single G7 country has a value in it.

So three of this board's four sections lean on other real, keyless, official
sources instead, each picked to be the closest available match to what the
IMF itself would publish if its own API served it:
  - Exchange rates: the European Central Bank's own daily reference rates,
    reached through Frankfurter (api.frankfurter.dev) — a keyless JSON proxy
    for the same ECB numbers, not a third-party estimate.
  - Money supply (M0/M1/M2-class) and non-gold reserves: the U.S. Federal
    Reserve (FRED's keyless CSV export, fredgraph.csv — no registration, no
    key, same trick already documented in mstr-trader's own CLAUDE.md) and,
    for the Euro area, the ECB's own SDMX 2.1 JSON API (data-api.ecb.europa.eu
    — also keyless). FRED separately mirrors IMF International Financial
    Statistics reserve series per country, which is how the non-gold-reserves
    table is sourced back to the IMF after all, just through a mirror that
    doesn't edge-block a CI runner.
  - Gold reserves: a curated, dated seed file (money_worldwide_seed.json),
    same posture as treasuries_seed.json's BTC holdings — central banks
    report this quarterly at best, so a live pull would cost a network call
    for a number that moves maybe once a quarter.

FAIL-SOFT, SECTION BY SECTION
Each of the four sections is fetched independently and wrapped so a bad
source costs only its own section, never the whole board — same contract as
every sibling fetcher. If literally nothing resolves, main() prints why and
writes nothing, leaving the previous board in place.

REFRESH CADENCE — NOT THE HOURLY CRON
Money supply, reserves and GDP/debt are monthly-to-quarterly real-world
series; they cannot move between two runs an hour apart, so running this on
the same hourly schedule as the market-quote boards would just be
144-commits-a-day of noise for zero informational gain (see the workflow's
own comment for the actual number). This script self-throttles: it checks its
own last "generated" timestamp and does nothing (exit 0) if less than
REFRESH_EVERY_HOURS have passed, rather than needing a second cron entry.
Exchange rates DO move daily, but a 6-hour floor is still far tighter than
this data actually needs and keeps the whole board on one predictable cadence
rather than mixing sub-boards with different staleness the reader has to
track separately.

NOTHING HERE IS PERSONAL. Every input is a public economic statistic from a
central bank, a supranational institution, or a public compilation of central
bank reports — no account, no key, nothing about anyone's personal holdings.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "source", "finance", "money_worldwide_seed.json")
ASSET_BOARD = os.path.join(ROOT, "source", "finance", "asset_board.json")
OUT = os.path.join(ROOT, "source", "finance", "money_worldwide.json")

UA = "mistertranslation.com/finance (The Librarian's Ledger - Money Worldwide board)"

REFRESH_EVERY_HOURS = 6   # see the module docstring's "REFRESH CADENCE" section

TROY_OZ_PER_TONNE = 32150.7466

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest?base=USD"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s"
ECB_BSI_URL = ("https://data-api.ecb.europa.eu/service/data/BSI/"
               "M.U2.N.V.%s.X.1.U2.2300.Z01.E"
               "?format=jsondata&lastNObservations=2&detail=full")
DATAMAPPER_URL = "https://www.imf.org/external/datamapper/api/v1/%s"

# The two Euro-area monetary aggregates ECB's BSI dataset publishes under
# these dimension codes — M10 is M1 (currency + overnight deposits), M20 is
# M2, M30 is M3 (the ECB's own headline "broad money" aggregate, since the
# Euro area does not publish a distinct M2 the way the US does — see the
# rendered page's own note on this).
ECB_ITEMS = {"m1": "M10", "m2": "M20", "m3": "M30"}

# IMF DataMapper indicator codes (see the module docstring — this is the one
# IMF system here that serves real observation data keylessly).
DM_GDP = "NGDPD"           # GDP, current prices, billions of U.S. dollars
DM_DEBT_PCT = "GGXWDG_NGDP"  # General government gross debt, % of GDP

# Region/aggregate codes DataMapper mixes into its per-economy dict — these
# are not countries and would otherwise pollute a "top N by GDP" ranking.
# MEASURED (2026-09-08): every WEO regional/income-group aggregate in the
# actual NGDPD response follows one of two shapes — either it's in this named
# set, or its 3-letter code ends in "Q" (AFQ, APQ, AZQ, CAQ, CBQ, CMQ, EAQ,
# EEQ, EUQ, MEQ, NAQ, OAE, PIQ, SAQ, SEQ, SMQ, SSQ, WEQ, WHQ, …) — no real
# ISO 3166-1 alpha-3 country code ends in Q, so that suffix rule is the
# actual filter (see `_is_country` below); this set exists only to catch the
# handful of aggregates that DON'T follow the Q convention (e.g. "OAE",
# Other Advanced Economies — three letters, no trailing Q, genuinely not a
# country; found only by eyeballing the actual 196-row output by hand).
DM_NON_COUNTRY = {
    "WEOWORLD", "ADVEC", "AS5", "DA", "OEMDC", "EURO", "EU", "WE", "MECA",
    "MAE", "EDE", "SSA", "LAC", "MENA", "APD", "AFR", "WHD", "EUR", "CEE",
    "CIS", "SSA_ALL", "NIP", "EDA", "PDA", "G20", "G7", "OAE",
}


def _is_country(area):
    return len(area) == 3 and area not in DM_NON_COUNTRY and not area.endswith("Q")

DEBT_GDP_TOP_N = 30

# ⚠️ MEASURED, NOT GUESSED (2026-09-08): FRED and IMF's own DataMapper API
# both silently reject a DESCRIPTIVE User-Agent header — FRED hangs the
# connection until it times out, DataMapper returns a flat 403 — yet BOTH
# happily serve the exact same request carrying no custom header at all
# (i.e. Python's own default "Python-urllib/x.y" string) or curl's default
# UA. Frankfurter is the mirror image: it 403s the bare "Python-urllib"
# default specifically, but accepts a descriptive UA fine. ECB tolerates
# both. So this fetcher sends a UA only to the two sources confirmed to want
# one (Frankfurter, ECB) and sends none at all to FRED and DataMapper —
# this is a real, verified-by-hand WAF quirk of those two services, not a
# bug to "clean up" by making every request look the same.
_UA_HEADER = {"User-Agent": UA}


def _get_json(url, timeout=25, send_ua=True):
    try:
        req = urllib.request.Request(url, headers=_UA_HEADER if send_ua else {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — a down source is a skip, not a crash
        print("  ! %s — %s" % (url, exc), file=sys.stderr)
        return None


def _get_text(url, timeout=25, send_ua=True):
    try:
        req = urllib.request.Request(url, headers=_UA_HEADER if send_ua else {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print("  ! %s — %s" % (url, exc), file=sys.stderr)
        return None


def _load_json_file(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError) as exc:
        print("  ! %s unreadable — %s" % (os.path.relpath(path, ROOT), exc), file=sys.stderr)
        return None


# ─────────────────────────────────────────────────────────────── section 1 ──
# Exchange rates — ECB reference rates via Frankfurter, base USD.

def fetch_fx():
    d = _get_json(FRANKFURTER_URL)
    if not isinstance(d, dict) or not d.get("rates"):
        print("  ! no exchange rates resolved", file=sys.stderr)
        return None
    return {"base": d.get("base", "USD"), "date": d.get("date"), "rates": d["rates"]}


# ─────────────────────────────────────────────────────────────── section 2 ──
# Money supply — U.S. via FRED (keyless CSV), Euro area via ECB SDMX.

def _fred_latest(series_id):
    """(date_str, float) for the most recent non-missing observation in a
    FRED series, or (None, None) if the series is unreachable or empty.
    FRED's CSV marks a missing observation as a bare '.' — skip those rather
    than crashing on float('.')."""
    text = _get_text(FRED_CSV_URL % series_id, send_ua=False)
    if not text:
        return None, None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in reversed(lines[1:]):   # skip the header row, walk newest-first
        parts = line.split(",")
        if len(parts) != 2:
            continue
        date_s, val_s = parts
        if val_s in ("", "."):
            continue
        try:
            return date_s, float(val_s)
        except ValueError:
            continue
    return None, None


def _ecb_bsi_latest(item_code):
    """(date_str "YYYY-MM", float millions-EUR) for the most recent Euro-area
    BSI observation of the given balance-sheet item, or (None, None)."""
    d = _get_json(ECB_BSI_URL % item_code)
    if not isinstance(d, dict):
        return None, None
    try:
        series = next(iter(d["dataSets"][0]["series"].values()))
        obs = series["observations"]
        obs_dims = d["structure"]["dimensions"]["observation"][0]["values"]
        last_idx = max(int(k) for k in obs.keys())
        value = obs[str(last_idx)][0]
        date_s = obs_dims[last_idx]["id"]
        return date_s, float(value)
    except (KeyError, IndexError, StopIteration, ValueError, TypeError) as exc:
        print("  ! ECB BSI %s parse failed — %s" % (item_code, exc), file=sys.stderr)
        return None, None


def fetch_money_supply(fx):
    """US (FRED, billions USD) + Euro area (ECB, millions EUR converted to
    USD via the live fx rate) rows. Two economies, not 190 — see the module
    docstring's IMF-research section for why a broader keyless pull of
    comparable, CURRENT money-supply levels isn't achievable today."""
    rows = []

    us_m0_date, us_m0 = _fred_latest("BOGMBASE")     # monetary base, billions USD
    us_m1_date, us_m1 = _fred_latest("M1SL")
    us_m2_date, us_m2 = _fred_latest("M2SL")
    if us_m2 is not None:
        rows.append({
            "area": "United States", "flag": "🇺🇸", "currency": "USD",
            "m0": us_m0, "m0_label": "Monetary base", "m0_date": us_m0_date,
            "m1": us_m1, "m1_date": us_m1_date,
            "m2": us_m2, "m2_date": us_m2_date,
            "m3": None,
            "usd_m0": us_m0, "usd_m1": us_m1, "usd_m2": us_m2, "usd_m3": None,
            "broad_usd": us_m2,   # this economy's own broadest published aggregate
            "source": "Federal Reserve H.6 (via FRED, billions of dollars)",
        })
    else:
        print("  ! US money supply unresolved (FRED)", file=sys.stderr)

    ea_m1_date, ea_m1 = _ecb_bsi_latest(ECB_ITEMS["m1"])
    ea_m2_date, ea_m2 = _ecb_bsi_latest(ECB_ITEMS["m2"])
    ea_m3_date, ea_m3 = _ecb_bsi_latest(ECB_ITEMS["m3"])
    eur_usd = (fx or {}).get("rates", {}).get("EUR")
    if ea_m3 is not None and eur_usd:
        # FRED/ECB give millions of national currency; this board's US row is
        # in BILLIONS — convert both onto the same "billions of dollars"
        # footing so the totals row and the scarcity chart can sum them.
        to_usd_b = lambda eur_m: (eur_m / 1000.0) / eur_usd if eur_m is not None else None
        rows.append({
            "area": "Euro area", "flag": "🇪🇺", "currency": "EUR",
            "m0": None, "m0_label": None, "m0_date": None,
            "m1": (ea_m1 / 1000.0) if ea_m1 is not None else None, "m1_date": ea_m1_date,
            "m2": (ea_m2 / 1000.0) if ea_m2 is not None else None, "m2_date": ea_m2_date,
            "m3": (ea_m3 / 1000.0), "m3_date": ea_m3_date,
            "usd_m0": None,
            "usd_m1": to_usd_b(ea_m1), "usd_m2": to_usd_b(ea_m2), "usd_m3": to_usd_b(ea_m3),
            "broad_usd": to_usd_b(ea_m3),   # M3 is the ECB's own headline "broad money"
            "source": "European Central Bank BSI dataset (billions of euro → USD "
                      "at today's rate)",
        })
    else:
        print("  ! Euro area money supply unresolved (ECB/fx)", file=sys.stderr)

    if not rows:
        return None
    total_broad_usd_b = sum(r["broad_usd"] for r in rows if r.get("broad_usd") is not None)
    return {"rows": rows, "total_broad_usd_b": total_broad_usd_b}


# ─────────────────────────────────────────────────────────────── section 3 ──
# Reserves — non-gold FX reserves per economy (FRED/IMF-IFS mirror) + gold
# (curated seed, priced off the asset board's own live gold quote).

def fetch_reserves_fx(seed):
    economies = (seed or {}).get("reserve_economies") or []
    rows = []
    for e in economies:
        date_s, val = _fred_latest(e["fred_series"])
        if val is None:
            print("  ! %s reserves unresolved (%s)" % (e["area"], e["fred_series"]),
                  file=sys.stderr)
            continue
        rows.append({"area": e["area"], "flag": e["flag"], "usd_m": val, "as_of": date_s})
    if not rows:
        return None
    rows.sort(key=lambda r: r["usd_m"], reverse=True)
    return {"rows": rows, "total_usd_m": sum(r["usd_m"] for r in rows)}


def _gold_price_from_asset_board(board):
    if not board:
        return None, None, None
    for a in board.get("assets", []):
        if a.get("symbol") == "GOLD" and a.get("price"):
            return float(a["price"]), a.get("market_cap"), board.get("generated")
    return None, None, None


def fetch_gold(seed, asset_board):
    gold = (seed or {}).get("gold_reserves") or {}
    seed_rows = gold.get("rows") or []
    price, world_market_cap, as_of = _gold_price_from_asset_board(asset_board)
    if price is None or not seed_rows:
        print("  ! gold reserves unresolved (no price or no seed rows)", file=sys.stderr)
        return None
    rows = []
    for r in seed_rows:
        usd = r["tonnes"] * TROY_OZ_PER_TONNE * price
        rows.append({"country": r["country"], "flag": r["flag"], "tonnes": r["tonnes"],
                      "usd": usd})
    return {
        "rows": rows,
        "total_tonnes": sum(r["tonnes"] for r in rows),
        "total_usd": sum(r["usd"] for r in rows),
        "world_official_tonnes_estimate": gold.get("world_official_tonnes_estimate"),
        "price_usd_oz": price,
        "price_as_of": as_of,
        "world_market_value_usd": world_market_cap,   # ALL above-ground gold, not just reserves
        "source_note": gold.get("source_note"),
    }


# ─────────────────────────────────────────────────────────────── section 4 ──
# Global debt & GDP — IMF DataMapper (WEO), genuinely broad country coverage.

def fetch_debt_gdp():
    gdp_data = _get_json(DATAMAPPER_URL % DM_GDP, send_ua=False)
    debt_data = _get_json(DATAMAPPER_URL % DM_DEBT_PCT, send_ua=False)
    if not gdp_data or not debt_data:
        return None
    gdp_by_area = (gdp_data.get("values") or {}).get(DM_GDP) or {}
    debt_by_area = (debt_data.get("values") or {}).get(DM_DEBT_PCT) or {}
    if not gdp_by_area:
        return None

    # WEO series run several years INTO THE FUTURE (a published forecast
    # horizon, out to ~5 years ahead) as well as into the past — so "the max
    # year present" is a 2031-ish forecast, not today's figure. Cap at the
    # current calendar year; IMF WEO itself labels the current year's own
    # value an estimate, which is the right "latest" figure to show, not a
    # forecast five years out (measured directly: the uncapped version of
    # this function was returning 2031 GDP figures on a 2026 build).
    this_year = datetime.now(timezone.utc).year

    def _latest_year(series):
        years = [y for y in series if y.isdigit() and int(y) <= this_year]
        return max(years) if years else None

    world_gdp_b, world_gdp_year = None, None
    if "WEOWORLD" in gdp_by_area:
        y = _latest_year(gdp_by_area["WEOWORLD"])
        if y:
            world_gdp_b, world_gdp_year = gdp_by_area["WEOWORLD"][y], y

    rows = []
    total_debt_usd_b = 0.0
    total_gdp_usd_b = 0.0
    for area, series in gdp_by_area.items():
        if not _is_country(area):
            continue
        y = _latest_year(series)
        if not y:
            continue
        gdp_b = series[y]
        debt_series = debt_by_area.get(area) or {}
        debt_pct = debt_series.get(y)
        debt_usd_b = (gdp_b * debt_pct / 100.0) if (gdp_b and debt_pct is not None) else None
        rows.append({"area": area, "gdp_usd_b": gdp_b, "year": y,
                      "debt_pct_gdp": debt_pct, "debt_usd_b": debt_usd_b})
        total_gdp_usd_b += gdp_b
        if debt_usd_b is not None:
            total_debt_usd_b += debt_usd_b

    if not rows:
        return None
    rows.sort(key=lambda r: r["gdp_usd_b"], reverse=True)
    top = rows[:DEBT_GDP_TOP_N]
    world_debt_pct = (total_debt_usd_b / total_gdp_usd_b * 100.0) if total_gdp_usd_b else None
    return {
        "rows": top,
        "n_countries_total": len(rows),
        "world_gdp_usd_b": world_gdp_b if world_gdp_b is not None else total_gdp_usd_b,
        "world_gdp_year": world_gdp_year or (top[0]["year"] if top else None),
        "world_debt_pct_gdp": world_debt_pct,
        "world_debt_usd_b": (world_gdp_b or total_gdp_usd_b) * (world_debt_pct or 0) / 100.0
                            if world_debt_pct else None,
    }


# ─────────────────────────────────────────────────────────────── section 5 ──
# Bitcoin's place in the mix — the "scarcity lineup."

_ISO3_TO_ISO2_FLAG_NAME = {
    # Only what's needed to label DataMapper's ISO3 codes with a flag/name in
    # the debt/GDP table — DataMapper itself gives no country names, only codes.
}


def compute_bitcoin_lineup(asset_board, money_supply, gold, debt_gdp):
    if not asset_board:
        return None
    btc = None
    for a in asset_board.get("assets", []):
        if a.get("symbol") == "BTC":
            btc = a
            break
    if not btc:
        return None

    lineup = []
    if money_supply and money_supply.get("total_broad_usd_b") is not None:
        lineup.append({
            "label": "Broad money — U.S. + Euro area (M2 + M3)",
            "usd": money_supply["total_broad_usd_b"] * 1e9,
            "note": "The two largest, most transparently published economies — a genuine "
                    "floor under the true global figure, not the whole world's money supply.",
        })
    if gold and gold.get("world_market_value_usd"):
        lineup.append({
            "label": "Gold — all above-ground supply",
            "usd": gold["world_market_value_usd"],
            "note": "Every ounce ever mined, at today's price — not just central-bank "
                    "reserves, and deliberately NOT added into the money-supply bar above it.",
        })
    lineup.append({
        "label": "Bitcoin — total market cap",
        "usd": btc["market_cap"],
        "note": "21 million coins, fixed by consensus rule — the fixed point this whole "
                "lineup is measured against.",
    })
    # Deliberately just these three — the scarcity contrast this chart exists
    # to show (printable fiat vs. slow-growing gold vs. fixed-supply Bitcoin)
    # is about STOCKS of money/value. World GDP is a FLOW (a year of output,
    # not a stock of anything) and is shown elsewhere on the page instead —
    # adding it as a fourth bar here would answer a different question than
    # the one this chart is asking, not just add more context to the same one.
    return {
        "price_usd": btc.get("price"), "market_cap_usd": btc.get("market_cap"),
        "btc_rank": asset_board.get("btc_rank"),
        "lineup": lineup,
    }


# ─────────────────────────────────────────────────────────────────────────────

def compute():
    """The full board, or None if nothing usable resolved at all."""
    seed = _load_json_file(SEED)
    asset_board = _load_json_file(ASSET_BOARD)

    fx = fetch_fx()
    money_supply = fetch_money_supply(fx)
    reserves_fx = fetch_reserves_fx(seed)
    gold = fetch_gold(seed, asset_board)
    debt_gdp = fetch_debt_gdp()
    bitcoin = compute_bitcoin_lineup(asset_board, money_supply, gold, debt_gdp)

    if not any([fx, money_supply, reserves_fx, gold, debt_gdp]):
        print("  ! every section failed — nothing to write", file=sys.stderr)
        return None

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "fx": fx,
        "money_supply": money_supply,
        "reserves_fx": reserves_fx,
        "gold": gold,
        "debt_gdp": debt_gdp,
        "bitcoin": bitcoin,
    }


def _due(force):
    """Self-throttle — see the module docstring's REFRESH CADENCE section.
    Anything unreadable/missing counts as due, so a corrupt state file can
    never permanently wedge the refresh."""
    if force:
        return True
    prev = _load_json_file(OUT)
    if not prev or not prev.get("generated"):
        return True
    try:
        prev_ts = datetime.strptime(prev["generated"], "%Y-%m-%d %H:%M UTC").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return True
    return datetime.now(timezone.utc) - prev_ts >= timedelta(hours=REFRESH_EVERY_HOURS)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    ap.add_argument("--force", action="store_true",
                     help="ignore the refresh cadence and run anyway")
    args = ap.parse_args()

    if not _due(args.force):
        print("not due yet (refreshes every %dh) — skipping" % REFRESH_EVERY_HOURS)
        return 0

    board = compute()
    if board is None:
        print("no money-worldwide board resolved — keeping the previous one",
              file=sys.stderr)
        return 0

    parts = []
    if board["fx"]:
        parts.append("%d currencies" % len(board["fx"]["rates"]))
    if board["money_supply"]:
        parts.append("%d money-supply economies" % len(board["money_supply"]["rows"]))
    if board["reserves_fx"]:
        parts.append("%d reserve economies" % len(board["reserves_fx"]["rows"]))
    if board["gold"]:
        parts.append("%d gold holders" % len(board["gold"]["rows"]))
    if board["debt_gdp"]:
        parts.append("%d/%d debt/GDP economies shown"
                      % (len(board["debt_gdp"]["rows"]), board["debt_gdp"]["n_countries_total"]))
    print(" · ".join(parts) + " · " + board["generated"])

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

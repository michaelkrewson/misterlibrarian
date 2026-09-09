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

MONEY SUPPLY EXPANSION — 2026-09-08 (read before adding/removing an economy)
Started as "as many economies as can be genuinely, honestly sourced," not a
fixed target — the board grew from 2 economies (US + Euro area) to 7 with
real, verified, CURRENT live data, plus 9 more shown with blank cells and an
honest source-note because they were seriously investigated but have no
working live source today (Michael's call: show the country, don't silently
drop it — a reader should see the board's coverage AMBITION, not just what
happened to resolve on a given day). Full per-economy detail lives in
money_worldwide_seed.json's `money_supply_economies`/`money_supply_unresolved`
notes; this is the shape of what was found.

THE OBVIOUS TEMPLATED-PATTERN HUNCH — REAL, BUT DEAD, VERIFIED DIRECTLY
The natural next move after the US/Euro-area build was "surely FRED mirrors
OECD's Main Economic Indicators money-supply tables the same templated way
it mirrors IMF reserve data" (`TRESEG<CC>M052N`, used above, IS templated
and IS current). It genuinely is templated — `MANMM101<CC>M657S` (narrow
money, growth rate) and `MABMM301<CC>M189S` / `MANMM101<CC>M189S` (broad/
narrow money, LEVEL, national currency) resolve for essentially every OECD
country by swapping in its 2-letter code (US/GB/JP/CA/AU/KR/MX/CH/CN all
confirmed to return real historical data). But EVERY series in this family
stopped updating years ago — most in 2023-11 (the US, UK, Japan, Australia,
South Africa), Canada in 2023-10, Korea in 2023-10, and Mexico/Switzerland
all the way back in 2018-12 — because OECD discontinued this MEI dataset.
The IMF-mirrored equivalent (`MYAGM2<CC>M189N`, used for China below) is
even staler (China's stopped in 2019-08). None of this is "roughly current"
by this board's standard — a series that cannot move for three years is not
a live source, so the whole family is unused here despite genuinely working
as an HTTP request. This is worth remembering distinctly from the reserve
series' FRED mirror, which IS current — "FRED mirrors this IMF/OECD dataset"
is not, by itself, evidence a mirror is still being fed.

FIVE REAL LIVE SOURCES FOUND INSTEAD, EACH VERIFIED BY A REAL REQUEST
  - Canada — Bank of Canada Valet API (bankofcanada.ca/valet), genuinely
    keyless, M1++/M2/M3 (gross, SA) as of 2026-06, updated within the API's
    normal 1-2 month lag. Accepts a bare default User-Agent.
  - Switzerland — the SNB Data Portal's cube API (data.snb.ch/api/cube/
    snbmonagg), genuinely keyless, M1/M2/M3 as of 2026-07. One HTTP call
    returns every aggregate in the cube (both the level AND the y/y-change
    series share dimension codes, so the fetch filters on "Level" — see
    `_snb_cube_values`). Accepts a bare default User-Agent.
  - Brazil — Banco Central do Brasil's SGS API (api.bcb.gov.br/dados/serie),
    genuinely keyless, M1/M2/M3 as of 2026-07 (codes 27841/27842/27813 —
    confirmed against each series' own dadosabertos.bcb.gov.br dataset page,
    not guessed; a same-shaped code, 27810, turned out to be a near-duplicate
    M2 vintage and was NOT used). Accepts a bare default User-Agent.
  - United Kingdom — the Bank of England's IADB (bankofengland.co.uk/
    boeapps/database), genuinely keyless but — confirmed directly — 403s
    Python's own bare default User-Agent (the opposite failure mode from
    FRED/DataMapper, which 403/hang on a DESCRIPTIVE one); `_boe_iadb_latest`
    sends this script's real UA. The UK discontinued M1/M2/M3-class
    reporting in 2006, so only M4 (LPMAUYN, SA, £m, as of 2026-07) exists —
    shown in the board's M3 column as this economy's own broadest published
    aggregate, the same convention the Euro area's M3 already uses.
  - Norway — Statistics Norway's StatBank PxWebAPI (data.ssb.no/api/v0),
    genuinely keyless, and the ONLY new economy with a complete M0-M3 row:
    table 10946 (base money M0) + table 10945 (M1/M2/M3), both as of
    2026-07. A POST with a JSON query body, not a query-string GET — see
    `_ssb_pxweb_latest`.

NINE ECONOMIES SERIOUSLY INVESTIGATED, SHOWN WITH BLANK CELLS
(full reasoning for each lives in the seed file's `money_supply_unresolved`
entries — this is the one-line summary of each dead end)
  - China, India, South Africa — the templated FRED/IMF mirror exists but is
    stale (see above); no confirmed alternative keyless API.
  - Japan — the Bank of Japan's OWN Time-Series Data Search API is real and
    keyless (its manual literally says "available for use by anyone"), but
    its series-code scheme is internal apostrophe-delimited mnemonics
    (e.g. "BS01'MABJMTA"), not a guessable template — a real candidate for a
    future dated follow-up, not a dead end like the others on this list.
  - South Korea (Bank of Korea ECOS), Mexico (Banxico SIE), Turkey (CBRT
    EVDS) — each has a real, documented API, and each confirmed BY A LIVE
    REQUEST to require a registered access key/token (Banxico returned a
    literal "Token inválido" error) — not keyless, so excluded on the same
    "keyless first" standard the rest of this board holds to.
  - Australia — the RBA's Table D3 is genuinely live, current (confirmed
    fresh within days) and keyless, but ONLY as an .xlsx download. This
    fetcher — like every sibling fetcher this repo's refresh workflow runs —
    is deliberately stdlib-only (no pip install step); parsing a binary
    spreadsheet would mean adding openpyxl/pandas for one economy's one
    column, so it's left out on purpose rather than breaking that convention.
  - Denmark — Danmarks Nationalbank's own StatBank instance publishes M1/M2/
    M3 (table DNMNOGL) but its PxWebAPI base path (distinct from Statistics
    Denmark's main dst.dk instance, which DOES work — see Norway/SSB above
    for the same API family working elsewhere) could not be confirmed
    working within reasonable research effort.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import re
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
# One extra call, USD-based, a year of daily ECB reference rates for every
# currency at once — verified directly (2026-09-08): a single request
# returns ~256 trading days × 28 currencies in ~100KB, so the volatility
# column below costs one live call, not a per-currency crawl.
FRANKFURTER_HISTORY_URL = "https://api.frankfurter.dev/v1/%s..%s?from=USD"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s"
ECB_BSI_URL = ("https://data-api.ecb.europa.eu/service/data/BSI/"
               "M.U2.N.V.%s.X.1.U2.2300.Z01.E"
               "?format=jsondata&lastNObservations=2&detail=full")
# Same series, more observations — used only for the money-supply YoY
# growth column (_ecb_bsi_series), kept separate from ECB_BSI_URL above so
# the already-verified latest-value path (_ecb_bsi_latest) is untouched.
ECB_BSI_URL_N = ("https://data-api.ecb.europa.eu/service/data/BSI/"
                  "M.U2.N.V.%s.X.1.U2.2300.Z01.E"
                  "?format=jsondata&lastNObservations=%d&detail=full")
DATAMAPPER_URL = "https://www.imf.org/external/datamapper/api/v1/%s"
# CoinGecko's public market_chart endpoint — genuinely keyless (verified
# 2026-09-08 with a bare urllib request, no custom header at all; already
# used elsewhere in this repo, see fetch_crypto_heatmap.py, which documents
# its rate-limit behavior on a multi-coin crawl — this is a single call for
# one coin, so that risk barely applies here).
COINGECKO_BTC_CHART_URL = ("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
                            "?vs_currency=usd&days=365&interval=daily")

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


def _post_json(url, payload, timeout=25, send_ua=False):
    """POST a JSON body, return the parsed JSON response (or None on any
    failure) — used only by Statistics Norway's PxWebAPI, which needs a
    query body rather than query-string params. Same fail-soft contract as
    _get_json/_get_text: a down source costs only its own row, never a crash."""
    try:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if send_ua:
            headers.update(_UA_HEADER)
        req = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
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


def _annualized_volatility_pct(prices):
    """Annualized volatility (%%) — the standard deviation of daily log
    returns, scaled by sqrt(252) (the usual trading-day convention; applied
    here to BOTH fiat FX rates and Bitcoin's own 24/7 price so the two
    numbers are computed the SAME way and stay comparable, even though
    Bitcoin actually trades every day of the year, not ~252). Needs at
    least 30 real points — an unusually short series shouldn't produce a
    wild two-point "volatility"."""
    vals = [p for p in prices if p and p > 0]
    if len(vals) < 30:
        return None
    returns = [math.log(vals[i] / vals[i - 1]) for i in range(1, len(vals))]
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    return (variance ** 0.5) * (252 ** 0.5) * 100.0


def fetch_fx_volatility():
    """{currency: annualized_volatility_pct} for every currency Frankfurter
    quotes against USD, from ONE year of its own daily ECB reference rates
    — one extra live call (FRANKFURTER_HISTORY_URL), not a per-currency
    crawl. USD itself never appears (Frankfurter's from=USD query has
    nothing to quote it against) — its row renders "—" on the Money
    Worldwide page rather than a meaningless "0%%" for the numeraire."""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=370)
    d = _get_json(FRANKFURTER_HISTORY_URL % (start.isoformat(), end.isoformat()))
    if not isinstance(d, dict) or not d.get("rates"):
        print("  ! FX volatility unresolved (Frankfurter history)", file=sys.stderr)
        return {}
    by_date = d["rates"]
    dates = sorted(by_date)
    currencies = set()
    for day in by_date.values():
        currencies.update(day.keys())
    out = {}
    for ccy in currencies:
        series = [by_date[dt][ccy] for dt in dates if ccy in by_date[dt]]
        vol = _annualized_volatility_pct(series)
        if vol is not None:
            out[ccy] = vol
    return out


def fetch_bitcoin_market_stats():
    """(volatility_pct, volume_usd) from ONE CoinGecko market_chart call —
    365 days of daily USD closes for volatility (the exact same statistic
    fetch_fx_volatility() computes for fiat) AND the latest day's own
    `total_volumes` figure for the trading-volume column, sharing a single
    request rather than fetching the same endpoint twice for two stats."""
    d = _get_json(COINGECKO_BTC_CHART_URL, send_ua=False)
    if not isinstance(d, dict) or not d.get("prices"):
        print("  ! Bitcoin market stats unresolved (CoinGecko)", file=sys.stderr)
        return None, None
    prices = [p[1] for p in d["prices"] if isinstance(p, list) and len(p) == 2]
    vol_pct = _annualized_volatility_pct(prices)
    volumes = d.get("total_volumes") or []
    volume_usd = volumes[-1][1] if volumes and isinstance(volumes[-1], list) else None
    return vol_pct, volume_usd


def fetch_fx_turnover(seed):
    """{currency: implied_daily_usd_volume} from the curated BIS Triennial
    Survey shares in money_worldwide_seed.json's `fx_turnover` block — a
    periodic SURVEY (once every three years), not a live feed, so this is
    curated and dated like the gold-reserve tonnages, not fetched (see the
    seed file's own source_note for the methodology: each share is ON ONE
    SIDE of a trade, summing to ~200%, so a currency's own implied volume
    is simply its share % × the survey's total daily turnover)."""
    fxt = (seed or {}).get("fx_turnover") or {}
    total = fxt.get("total_daily_usd")
    shares = fxt.get("shares_pct") or {}
    if not total or not shares:
        return {}
    return {ccy: (pct / 100.0) * total for ccy, pct in shares.items()}


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


## ── five more providers (2026-09-08) ──────────────────────────────────────
# Each of these is a REAL central bank / national statistics office API,
# individually verified by hand (see the module docstring's dated research
# log). Unlike the reserve series above, there is no single templated source
# that covers many countries' money supply at once — the obvious FRED/OECD-MEI
# templated pattern (MANMM101<CC>M657S / MABMM301<CC>M189S) is real but every
# country in that family stopped updating in 2018-2023 (verified directly,
# not assumed) — so this board leans on five separate national sources
# instead, dispatched generically from money_worldwide_seed.json's
# money_supply_economies list (`_fetch_generic_money_row`) rather than one
# hardcoded if-block per country. Adding another economy on one of these
# SAME five providers is a one-line seed-file entry; a new provider needs a
# new `_<name>_latest`/`_<name>_values` function below and a new dispatch
# branch in `_fetch_generic_money_row`.

BOC_VALET_URL = "https://www.bankofcanada.ca/valet/observations/%s/json?recent=1"
SNB_CUBE_URL = "https://data.snb.ch/api/cube/%s/data/json/en?fromDate=%s"
BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.%s/dados/ultimos/1?formato=json"
BOE_IADB_URL = ("https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"
                "?csv.x=yes&Datefrom=01/Jan/%d&Dateto=now&SeriesCodes=%s"
                "&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N")
SSB_PXWEB_URL = "https://data.ssb.no/api/v0/en/table/%s"
RBI_WSS_SECTION_URL = "https://rbi.org.in/Scripts/WSSViewDetail.aspx?TYPE=Section&PARAM1=%d"
RBI_WSS_VIEW_URL = "https://rbi.org.in/Scripts/WSSView.aspx?Id=%d"
BOJ_CSV_URL = "https://www.stat-search.boj.or.jp/ssi/mtshtml/csv/%s.csv"
RBA_D3_CSV_URL = "https://www.rba.gov.au/statistics/tables/csv/d3-data.csv"
DK_PXWEB_TABLEINFO_URL = "https://api.statbank.dk/v1/tableinfo/%s?lang=en"
DK_PXWEB_DATA_URL = "https://api.statbank.dk/v1/data/%s/JSONSTAT"


def _boc_valet_latest(series_name):
    """(date_str "YYYY-MM-DD", float millions-CAD) for the Bank of Canada
    Valet API's most recent observation of the given V-series, or
    (None, None). Genuinely keyless — no registration, no token."""
    d = _get_json(BOC_VALET_URL % series_name, send_ua=False)
    if not isinstance(d, dict):
        return None, None
    obs = d.get("observations") or []
    if not obs:
        return None, None
    row = obs[-1]
    try:
        val = (row.get(series_name) or {}).get("v")
        return row.get("d"), float(val)
    except (TypeError, ValueError):
        return None, None


def _snb_cube_values(cube_id, label_by_key, require_level=True):
    """{key: (date_str "YYYY-MM", float millions-CHF)} for every requested
    key in one SNB Data Portal "cube" — ONE http call regardless of how many
    series are requested, since the cube returns everything in it at once.
    `label_by_key` maps this board's own key ("m0"/"m1"/...) straight to the
    cube's own human-readable series label — the cube has no short codes of
    its own, only these labels, so the seed file names them directly rather
    than through an indirection layer here. `require_level` filters out a
    parallel "Change from the corresponding month of the previous year" set
    that a cube with a Level/change dimension (the monetary-aggregates cube)
    carries alongside the level under the same label — a single-dimension
    cube (the monetary-base one) has no such parallel set and needs no
    filter, else it (correctly) matches nothing and the key stays missing.
    `fromDate` is a real filter the cube API accepts; it's set a year back
    so the payload stays small without risking missing the latest
    observation on a slow-reporting month."""
    from_date = "%d-01-01" % (datetime.now(timezone.utc).year - 1)
    d = _get_json(SNB_CUBE_URL % (cube_id, from_date), send_ua=False)
    if not isinstance(d, dict):
        return {}
    out = {}
    for ts in d.get("timeseries") or []:
        header = ts.get("header") or []
        if require_level and not any(h.get("dimItem") == "Level" for h in header):
            continue
        dim_item = next((h.get("dimItem") for h in header if h.get("dim") != "Level/change"), None)
        vals = ts.get("values") or []
        if not vals:
            continue
        last = vals[-1]
        for key, label in label_by_key.items():
            if dim_item == label:
                try:
                    out[key] = (last.get("date"), float(last.get("value")))
                except (TypeError, ValueError):
                    pass
    return out


def _bcb_sgs_latest(series_code):
    """(date_str "YYYY-MM-DD", float thousands-BRL) for Banco Central do
    Brasil's SGS API's most recent observation of the given series code, or
    (None, None). Genuinely keyless."""
    d = _get_json(BCB_SGS_URL % series_code, send_ua=False)
    if not isinstance(d, list) or not d:
        return None, None
    row = d[-1]
    try:
        dd, mm, yyyy = row["data"].split("/")
        return "%s-%s-%s" % (yyyy, mm, dd), float(row["valor"])
    except (KeyError, ValueError):
        return None, None


def _boe_iadb_latest(series_code):
    """(date_str "YYYY-MM-DD", float millions-GBP) for the Bank of England
    IADB's most recent observation of the given series code, or (None,
    None). Keyless, but — confirmed by hand — 403s Python's own default
    User-Agent string the way FRED/DataMapper do the OPPOSITE (see
    `_UA_HEADER`'s note); this is the one new provider that needs a real UA."""
    this_year = datetime.now(timezone.utc).year
    text = _get_text(BOE_IADB_URL % (this_year - 1, series_code), send_ua=True)
    if not text:
        return None, None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        return None, None
    date_s, val_s = lines[-1].split(",")
    try:
        d = datetime.strptime(date_s, "%d %b %Y")
        return d.strftime("%Y-%m-%d"), float(val_s)
    except ValueError:
        return None, None


def _ssb_pxweb_latest(table_id, content_code):
    """(date_str "YYYY-MM", float millions-native) for Statistics Norway's
    PxWebAPI most recent observation of one content code in one table — two
    calls (metadata to find the latest period, then a scoped data query),
    since PxWebAPI has no simple "latest observation" shortcut the way
    FRED's CSV export does. Genuinely keyless."""
    meta = _get_json(SSB_PXWEB_URL % table_id, send_ua=False)
    if not isinstance(meta, dict):
        return None, None
    tid = next((v for v in meta.get("variables", []) if v.get("code") == "Tid"), None)
    if not tid or not tid.get("values"):
        return None, None
    latest_period = tid["values"][-1]
    payload = {
        "query": [
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [content_code]}},
            {"code": "Tid", "selection": {"filter": "item", "values": [latest_period]}},
        ],
        "response": {"format": "json-stat2"},
    }
    d = _post_json(SSB_PXWEB_URL % table_id, payload, send_ua=False)
    if not isinstance(d, dict):
        return None, None
    vals = d.get("value") or []
    if not vals:
        return None, None
    try:
        return latest_period, float(vals[0])
    except (TypeError, ValueError):
        return None, None


def _rbi_wss_latest_view_id(param1):
    """The highest (= most recent) WSSView.aspx `Id` linked from one of the
    Reserve Bank of India's Weekly Statistical Supplement permanent
    section-listing pages (PARAM1=8 is "Reserve Money: Components and
    Sources", PARAM1=7 is "Money Stock: Components and Sources") — these
    listing URLs never change, so finding the CURRENT release is a
    two-step crawl-then-fetch, the same shape ssb_pxweb already uses to
    find Norway's latest period. Confirmed by hand: unlike RBI's DBIE data
    portal (a JS single-page app with no keyless API found), these WSS
    pages are genuinely server-rendered plain HTML with a real data table
    — no browser needed, just a real User-Agent (RBI blocks Python's
    default one, the same `_boe_iadb_latest` quirk)."""
    text = _get_text(RBI_WSS_SECTION_URL % param1, send_ua=True)
    if not text:
        return None
    ids = [int(m) for m in re.findall(r"WSSView\.aspx\?Id=(\d+)", text)]
    return max(ids) if ids else None


def _rbi_wss_rows(html):
    """[[cell, cell, ...], ...] for every non-empty <tr> on one RBI WSS
    release page, tags stripped and blank/&nbsp;-only cells dropped."""
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, flags=re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)
        cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", "").strip() for c in cells]
        cells = [c for c in cells if c]
        if cells:
            rows.append(cells)
    return rows


_RBI_WSS_MONTH_DAY_RE = re.compile(r"^[A-Za-z]{3}\.\s*\d{1,2}$")


def _rbi_wss_asof_date(rows):
    """The table's own SECOND "Outstanding as on" column date (e.g.
    "Aug 15, 2026") — the actual data reference date, not the release's
    own "Date : Sep 04, 2026" header, which is when the release was
    PUBLISHED and lags the underlying fortnight by design (a weekly WSS
    release carrying fortnightly reserve-money/money-stock data). Reads
    the table's own two header rows: a lone 4-digit year, followed later
    by a "Mon. DD" pair whose SECOND value is the latest column — the
    first is always the start-of-fiscal-year reference point."""
    year = None
    for cells in rows:
        if re.match(r"^\d{4}$", cells[0]):
            year = cells[0]
        elif (year and len(cells) >= 2
              and _RBI_WSS_MONTH_DAY_RE.match(cells[0])
              and _RBI_WSS_MONTH_DAY_RE.match(cells[1])):
            return "%s, %s" % (cells[1].replace(".", ""), year)
    return None


def _rbi_wss_items(view_id, prefixes):
    """{prefix: (date_str, float crore)} for every requested item-row
    prefix in ONE RBI WSS release — one http call regardless of how many
    rows are requested. A row is matched by its "Item" cell STARTING WITH
    the given prefix (e.g. "Reserve Money", "M3", "1.1", "1.2", "1.4")
    rather than an exact string — some labels carry HTML-entity curly
    quotes ('Other') that would make an exact match fragile, while the
    row's own numeric sub-item code or a short unambiguous label prefix
    is stable. Reads the SECOND "Outstanding as on" column — see
    `_rbi_wss_asof_date` for why that's not the same as the release date."""
    html = _get_text(RBI_WSS_VIEW_URL % view_id, send_ua=True)
    if not html:
        return {}
    rows = _rbi_wss_rows(html)
    date_s = _rbi_wss_asof_date(rows)
    out = {}
    for cells in rows:
        if len(cells) < 3:
            continue
        label = cells[0]
        for prefix in prefixes:
            if prefix not in out and label.startswith(prefix):
                try:
                    out[prefix] = (date_s, float(cells[2].replace(",", "")))
                except ValueError:
                    pass
    return out


def _labeled_csv_values(text, header_label, date_re, codes_by_key):
    """{key: (date_str, float)} for every requested series code in ONE
    "labeled" central-bank CSV export — metadata rows up top (title,
    names, units, date range), one of which starts with `header_label`
    (e.g. the Bank of Japan's "Series code", the RBA's "Series ID") and
    otherwise names each column's own code, followed by dated data rows
    matching `date_re` in their first cell. Shared by any provider shaped
    this way — `csv.reader` handles the metadata rows' quoting; values
    are returned in the file's own native unit, the caller converts."""
    rows = list(csv.reader(io.StringIO(text)))
    code_row = next((r for r in rows if r and r[0] == header_label), None)
    if not code_row:
        return {}
    col_of = {code: i for i, code in enumerate(code_row)}
    data_rows = [r for r in rows if r and date_re.match(r[0])]
    if not data_rows:
        return {}
    last = data_rows[-1]
    date_s = last[0]
    out = {}
    for key, code in codes_by_key.items():
        idx = col_of.get(code)
        if idx is None or idx >= len(last) or not last[idx]:
            continue
        try:
            out[key] = (date_s, float(last[idx]))
        except ValueError:
            pass
    return out


_BOJ_CSV_DATE_RE = re.compile(r"^\d{4}/\d{2}$")
_RBA_CSV_DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def _boj_csv_values(table, codes_by_key):
    """{key: (date_str "YYYY/MM", float 100-million-yen)} for every
    requested FAME series code in one Bank of Japan "Main Time-series
    Statistics" CSV export (e.g. table "md02_m_1_en" carries Money
    Stock's M1/M2/M3 as separate columns of the SAME file) — one http
    call regardless of how many keys share a table. Genuinely keyless and
    a real CSV (not the REST API, whose exact M1/M2/M3/monetary-base FAME
    mnemonics could not be pinned down from its own docs — but this
    export names its OWN codes in a "Series code" header row, found by
    hand from the Money Stock/Monetary Base pages themselves)."""
    text = _get_text(BOJ_CSV_URL % table, send_ua=True)
    if not text:
        return {}
    return _labeled_csv_values(text, "Series code", _BOJ_CSV_DATE_RE, codes_by_key)


def _rba_csv_values(codes_by_key):
    """{key: (date_str "DD/MM/YYYY", float A$ billion)} for every
    requested Series ID in the RBA's own "D3 Monetary Aggregates" CSV
    (rba.gov.au/statistics/tables/csv/d3-data.csv) — genuinely keyless,
    already in A$ billion (no unit conversion needed, unlike every other
    provider here). Superseded the earlier xlsx-only finding: the RBA has
    since added a CSV export for this table (confirmed 2026-09-09)."""
    text = _get_text(RBA_D3_CSV_URL, send_ua=True)
    if not text:
        return {}
    return _labeled_csv_values(text, "Series ID", _RBA_CSV_DATE_RE, codes_by_key)


def _dk_pxweb_latest_period(table):
    """The most recent "Tid" (time) value for a table on the api.statbank.dk
    PxWebAPI instance Danmarks Nationalbank shares with Statistics Denmark
    — a DIFFERENT dialect from Norway's SSB PxWebAPI (its metadata lives
    at a "tableinfo" endpoint, not "table"; its data query is a plain GET
    with variable-name params, not a POST json-stat2 body — confirmed by
    hand, since the SSB-style POST returns nothing but a format error
    here no matter how it's phrased)."""
    meta = _get_json(DK_PXWEB_TABLEINFO_URL % table, send_ua=False)
    if not isinstance(meta, dict):
        return None
    tid = next((v for v in meta.get("variables", []) if v.get("id") == "Tid"), None)
    if not tid or not tid.get("values"):
        return None
    return tid["values"][-1]["id"]


def _dk_pxweb_values(table, dim, codes_by_key, extra_dims=None):
    """{key: (date_str "YYYYMmm", float native unit)} for the given
    content codes (a dimension like "AKTP") on one api.statbank.dk table,
    at its latest period — see `_dk_pxweb_latest_period`'s note on why
    this is its own provider rather than reusing `_ssb_pxweb_latest`.
    `extra_dims` fixes any other dimension the table requires (e.g. a
    sector selector) to its headline/total value; the response is a
    JSON-stat2 object whose value array is indexed by each dimension's
    own `category.index` — reading `dim`'s index map is enough since
    every other dimension here is pinned to exactly one value."""
    period = _dk_pxweb_latest_period(table)
    if not period:
        return {}
    params = {dim: ",".join(codes_by_key.values())}
    params.update(extra_dims or {})
    params["Tid"] = period
    qs = "&".join("%s=%s" % (k, v) for k, v in params.items())
    d = _get_json("%s?%s" % (DK_PXWEB_DATA_URL % table, qs), send_ua=False)
    if not isinstance(d, dict):
        return {}
    try:
        values = d["dataset"]["value"]
        index = d["dataset"]["dimension"][dim]["category"]["index"]
    except (KeyError, TypeError):
        return {}
    out = {}
    for key, code in codes_by_key.items():
        i = index.get(code)
        if i is not None and i < len(values) and values[i] is not None:
            try:
                out[key] = (period, float(values[i]))
            except (TypeError, ValueError):
                pass
    return out


## ── money-supply YoY growth ("debasement rate") — 2026-09-08 ──────────────
# A SEPARATE, additive layer on top of the already-verified latest-value
# code above, not a change to it: each provider gets its own small
# "_..._series"/"_..._yoy" function returning history instead of a single
# point, dispatched by _money_broad_yoy_pct(). Isolating this here means a
# bug in a YoY fetch can only blank one new cell, never the market-cap
# figure a reader already relies on.

def _parse_period_date(date_s):
    """A best-effort datetime for a period label in any of this board's
    shapes ('YYYY-MM-DD', 'YYYY-MM', 'YYYY/MM/DD', 'YYYY/MM', and the RBA's
    own day-first 'DD/MM/YYYY') — enough precision to find the point
    closest to a target day, not for display."""
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _yoy_pct(old_val, new_val):
    if old_val is None or new_val is None or old_val == 0:
        return None
    return (new_val / old_val - 1.0) * 100.0


def _yoy_from_pairs(rows, target_days=365, max_slack_days=45):
    """(old_val, new_val) — new_val is a series' own latest value, old_val
    is the value closest to `target_days` before it — from a
    [(date_str, float), ...] series in any order. (None, None) if the
    series is too short, or has no point within `max_slack_days` of the
    target (a monthly/quarterly series' normal reporting gap, not a
    mismatched pair of dates)."""
    parsed = sorted(
        ((_parse_period_date(d), v) for d, v in rows if v is not None and _parse_period_date(d)),
        key=lambda t: t[0])
    if len(parsed) < 2:
        return None, None
    latest_date, latest_val = parsed[-1]
    target = latest_date - timedelta(days=target_days)
    best_date, best_val = min(parsed[:-1], key=lambda t: abs((t[0] - target).days))
    if abs((best_date - target).days) > max_slack_days:
        return None, None
    return best_val, latest_val


def _fred_series(series_id):
    """[(date_str, float), ...] ascending, every non-missing observation in
    a FRED series — the same fredgraph.csv export _fred_latest() already
    reads, just kept in full rather than reduced to its last row."""
    text = _get_text(FRED_CSV_URL % series_id, send_ua=False)
    if not text:
        return []
    out = []
    for line in [ln.strip() for ln in text.splitlines() if ln.strip()][1:]:
        parts = line.split(",")
        if len(parts) != 2 or parts[1] in ("", "."):
            continue
        try:
            out.append((parts[0], float(parts[1])))
        except ValueError:
            continue
    return out


def _ecb_bsi_series(item_code, n=13):
    """[(period, float millions-EUR), ...] for the last `n` monthly BSI
    observations of one item — the same query _ecb_bsi_latest() makes,
    just with more history (n=13 comfortably spans a year of monthly
    data)."""
    d = _get_json(ECB_BSI_URL_N % (item_code, n))
    if not isinstance(d, dict):
        return []
    try:
        series = next(iter(d["dataSets"][0]["series"].values()))
        obs = series["observations"]
        obs_dims = d["structure"]["dimensions"]["observation"][0]["values"]
        return [(obs_dims[int(k)]["id"], float(v[0])) for k, v in obs.items()]
    except (KeyError, IndexError, StopIteration, ValueError, TypeError):
        return []


def _boc_valet_series(series_name, days_back=550):
    """[(date_str, float), ...] for a Bank of Canada Valet series over the
    last `days_back` days — confirmed 2026-09-08 that Valet's observations
    endpoint accepts start_date/end_date query params directly (the
    latest-value path uses its "?recent=1" shortcut instead). 550 days, not
    ~400: the M3 series itself reports with a real lag behind today (its
    latest observation can be ~3 months old), so a window sized only to
    "today minus a year" can fall short of a point 365 days before the
    series' own latest point — verified directly (2026-09-08), a 400-day
    window returned only 10 months of history and missed the year-ago
    target by ~90 days."""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days_back)
    url = ("https://www.bankofcanada.ca/valet/observations/%s/json"
           "?start_date=%s&end_date=%s" % (series_name, start.isoformat(), end.isoformat()))
    d = _get_json(url, send_ua=False)
    if not isinstance(d, dict):
        return []
    out = []
    for row in d.get("observations") or []:
        try:
            out.append((row["d"], float(row[series_name]["v"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _bcb_sgs_series(series_code, n=13):
    """[(date_str, float), ...] for the last `n` monthly observations of a
    Banco Central do Brasil SGS series — same endpoint _bcb_sgs_latest()
    uses, just "/ultimos/N" instead of "/ultimos/1"."""
    url = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.%s/dados/ultimos/%d?formato=json"
           % (series_code, n))
    d = _get_json(url, send_ua=False)
    if not isinstance(d, list):
        return []
    out = []
    for row in d:
        try:
            dd, mm, yyyy = row["data"].split("/")
            out.append(("%s-%s-%s" % (yyyy, mm, dd), float(row["valor"])))
        except (KeyError, ValueError):
            continue
    return out


def _boe_iadb_series(series_code):
    """[(date_str, float), ...] for a Bank of England IADB series — the
    latest-value path (_boe_iadb_latest) already requests a full year+ of
    history (Datefrom=01/Jan/<last year>) and reads only the last line;
    this reads every line instead."""
    this_year = datetime.now(timezone.utc).year
    text = _get_text(BOE_IADB_URL % (this_year - 1, series_code), send_ua=True)
    if not text:
        return []
    out = []
    for line in [ln.strip() for ln in text.splitlines() if ln.strip()][1:]:
        try:
            date_s, val_s = line.split(",")
            d = datetime.strptime(date_s, "%d %b %Y")
            out.append((d.strftime("%Y-%m-%d"), float(val_s)))
        except ValueError:
            continue
    return out


def _snb_cube_series(cube_id, label, require_level=True):
    """[(date_str "YYYY-MM", float millions-CHF), ...] for ONE label across
    the ~1yr window an SNB Data Portal cube query already covers (see
    _snb_cube_values, which reads the same window but keeps only each
    label's last point) — a second read of the same cube, not a threaded
    change to that already-verified function."""
    from_date = "%d-01-01" % (datetime.now(timezone.utc).year - 1)
    d = _get_json(SNB_CUBE_URL % (cube_id, from_date), send_ua=False)
    if not isinstance(d, dict):
        return []
    out = []
    for ts in d.get("timeseries") or []:
        header = ts.get("header") or []
        if require_level and not any(h.get("dimItem") == "Level" for h in header):
            continue
        dim_item = next((h.get("dimItem") for h in header if h.get("dim") != "Level/change"), None)
        if dim_item != label:
            continue
        for v in ts.get("values") or []:
            try:
                out.append((v.get("date"), float(v.get("value"))))
            except (TypeError, ValueError):
                continue
    return out


def _boj_csv_series(table, code):
    """[(date_str, float), ...] for ONE series code across an entire Bank
    of Japan CSV export — _boj_csv_values() reads the same file but keeps
    only the last row."""
    text = _get_text(BOJ_CSV_URL % table, send_ua=True)
    return _labeled_csv_series(text, "Series code", _BOJ_CSV_DATE_RE, code) if text else []


def _rba_csv_series(code):
    """[(date_str, float), ...] for ONE series code across the RBA's D3
    CSV export — _rba_csv_values() reads the same file but keeps only the
    last row."""
    text = _get_text(RBA_D3_CSV_URL, send_ua=True)
    return _labeled_csv_series(text, "Series ID", _RBA_CSV_DATE_RE, code) if text else []


def _labeled_csv_series(text, header_label, date_re, code):
    """[(date_str, float), ...] for ONE column of a "labeled" CSV export
    (see _labeled_csv_values, which reduces the same shape to its last
    row) — shared by the BoJ and RBA money-supply YoY lookups."""
    rows = list(csv.reader(io.StringIO(text)))
    code_row = next((r for r in rows if r and r[0] == header_label), None)
    if not code_row:
        return []
    idx = {c: i for i, c in enumerate(code_row)}.get(code)
    if idx is None:
        return []
    out = []
    for r in rows:
        if not r or not date_re.match(r[0]) or idx >= len(r) or not r[idx]:
            continue
        try:
            out.append((r[0], float(r[idx])))
        except ValueError:
            continue
    return out


def _ssb_pxweb_yoy(table_id, content_code):
    """(old_val, new_val) for one Statistics Norway content code, ~12
    months apart — reuses the metadata call _ssb_pxweb_latest() already
    makes to list every available period, then queries the period 13 slots
    back (confirmed 2026-09-08: table 10945's periods are monthly, so -13
    lands almost exactly a year before the latest one) instead of just the
    latest."""
    meta = _get_json(SSB_PXWEB_URL % table_id, send_ua=False)
    if not isinstance(meta, dict):
        return None, None
    tid = next((v for v in meta.get("variables", []) if v.get("code") == "Tid"), None)
    periods = (tid or {}).get("values") or []
    if len(periods) < 13:
        return None, None

    def _query(period):
        payload = {"query": [
            {"code": "ContentsCode", "selection": {"filter": "item", "values": [content_code]}},
            {"code": "Tid", "selection": {"filter": "item", "values": [period]}},
        ], "response": {"format": "json-stat2"}}
        d = _post_json(SSB_PXWEB_URL % table_id, payload, send_ua=False)
        vals = (d or {}).get("value") or []
        try:
            return float(vals[0])
        except (TypeError, ValueError, IndexError):
            return None

    return _query(periods[-13]), _query(periods[-1])


def _dk_pxweb_yoy(table, dim, code, extra_dims=None):
    """(old_val, new_val) for one Danmarks Nationalbank/Statistics Denmark
    content code, ~12 months apart — same "list every period, then query
    the one 13 slots back" pattern as _ssb_pxweb_yoy, adapted to this
    dialect's plain-GET query shape (see _dk_pxweb_values)."""
    meta = _get_json(DK_PXWEB_TABLEINFO_URL % table, send_ua=False)
    if not isinstance(meta, dict):
        return None, None
    tid = next((v for v in meta.get("variables", []) if v.get("id") == "Tid"), None)
    periods = (tid or {}).get("values") or []
    if len(periods) < 13:
        return None, None

    def _query(period_id):
        params = {dim: code}
        params.update(extra_dims or {})
        params["Tid"] = period_id
        qs = "&".join("%s=%s" % (k, v) for k, v in params.items())
        d = _get_json("%s?%s" % (DK_PXWEB_DATA_URL % table, qs), send_ua=False)
        try:
            values = d["dataset"]["value"]
            return float(values[0]) if values else None
        except (KeyError, TypeError, ValueError, IndexError):
            return None

    return _query(periods[-13]["id"]), _query(periods[-1]["id"])


def _money_broad_yoy_pct(econ, broad_key):
    """YoY %% growth of one economy's own broadest RESOLVED money-supply
    aggregate (whichever key `broad_key` names — the same broadest-first
    pick _fetch_generic_money_row() already makes for `broad_usd`), i.e.
    this board's per-currency "debasement rate." Returns None for a
    provider with no practical historical query (hand_curated — China's
    values are hand-typed from a press release, not a queryable series;
    rbi_wss — a fragile HTML scrape not worth extending here) or when the
    series itself doesn't resolve; never raises, so a bad source costs only
    this one cell."""
    provider = econ["provider"]
    try:
        if provider == "boc_valet":
            codes = econ.get("series", {}).get(broad_key)
            if not codes:
                return None
            codes = codes if isinstance(codes, list) else [codes]
            old_sum = new_sum = 0.0
            for code in codes:
                old_v, new_v = _yoy_from_pairs(_boc_valet_series(code))
                if old_v is None:
                    return None
                old_sum += old_v
                new_sum += new_v
            return _yoy_pct(old_sum, new_sum)
        if provider == "snb_cube":
            label = econ.get("dims", {}).get(broad_key)
            if not label:
                return None
            old_v, new_v = _yoy_from_pairs(_snb_cube_series(econ["cube"], label))
            return _yoy_pct(old_v, new_v)
        if provider == "bcb_sgs":
            code = econ.get("series", {}).get(broad_key)
            if not code:
                return None
            old_v, new_v = _yoy_from_pairs(_bcb_sgs_series(code))
            return _yoy_pct(old_v, new_v)
        if provider == "boe_iadb":
            codes = econ.get("series", {}).get(broad_key)
            if not codes:
                return None
            codes = codes if isinstance(codes, list) else [codes]
            old_sum = new_sum = 0.0
            for code in codes:
                old_v, new_v = _yoy_from_pairs(_boe_iadb_series(code))
                if old_v is None:
                    return None
                old_sum += old_v
                new_sum += new_v
            return _yoy_pct(old_sum, new_sum)
        if provider == "ssb_pxweb":
            code = econ.get("codes_m123", {}).get(broad_key)
            if not code:
                return None
            return _yoy_pct(*_ssb_pxweb_yoy(econ["table_m123"], code))
        if provider == "dk_pxweb":
            code = econ.get("codes", {}).get(broad_key)
            if not code:
                return None
            return _yoy_pct(*_dk_pxweb_yoy(econ["table"], econ["dim"], code, econ.get("extra_dims")))
        if provider == "boj_csv":
            spec = econ.get("tables", {}).get(broad_key)
            if not spec:
                return None
            old_v, new_v = _yoy_from_pairs(_boj_csv_series(spec["table"], spec["code"]))
            return _yoy_pct(old_v, new_v)
        if provider == "rba_csv":
            code = econ.get("codes", {}).get(broad_key)
            if not code:
                return None
            old_v, new_v = _yoy_from_pairs(_rba_csv_series(code))
            return _yoy_pct(old_v, new_v)
    except Exception as exc:  # noqa: BLE001 — a growth-rate miss costs one cell, never the row
        print("  ! %s broad-money YoY failed (%s) — %s" % (econ.get("area"), provider, exc),
              file=sys.stderr)
        return None
    return None   # hand_curated / rbi_wss / unrecognized — no practical history query


def _sum_series(fetch_one, codes):
    """(total, date_str) summing fetch_one(code) over every code in codes,
    or (None, None) if any single one fails to resolve — used where a
    provider's series value may be a LIST to add together rather than one
    series (Canada and the UK's m0 constructions, so far: a central bank
    that discontinued its own "M0" label and split it into separate
    published series with no ready-made sum of its own)."""
    total, date_s = 0.0, None
    for code in codes:
        d, v = fetch_one(code)
        if v is None:
            return None, None
        total += v
        date_s = date_s or d
    return total, date_s


def _fetch_generic_money_row(econ, fx):
    """Build one money_supply row from a money_worldwide_seed.json
    `money_supply_economies` entry, dispatching on its `provider`. Returns
    None if literally nothing resolved for this economy (costs only its own
    row — see the module's fail-soft-per-section contract)."""
    rate = (fx or {}).get("rates", {}).get(econ["currency"])
    if not rate:
        print("  ! %s money supply skipped — no %s/USD rate" % (econ["area"], econ["currency"]),
              file=sys.stderr)
        return None

    vals = {}   # "m0"/"m1"/"m2"/"m3" -> (native_billions, date_str)
    provider = econ["provider"]
    if provider == "boc_valet":
        for key, series in econ.get("series", {}).items():
            # a value may be one V-series, or a list of V-series to SUM —
            # Canada's m0 needs this (notes in circulation + settlement
            # balances, two separate balance-sheet line items with no
            # single published series for their sum), while every other
            # boc_valet key here stays a plain string.
            codes = series if isinstance(series, list) else [series]
            total, date_s = _sum_series(_boc_valet_latest, codes)
            if total is not None:
                vals[key] = (total / 1000.0, date_s)   # millions -> billions
    elif provider == "snb_cube":
        for key, (d, v) in _snb_cube_values(econ["cube"], econ.get("dims", {})).items():
            vals[key] = (v / 1000.0, d)   # millions -> billions
        # m0 (monetary base) is a genuinely SEPARATE SNB cube from M1/M2/M3
        # (its own single-dimension "Overview" shape, no Level/change split
        # to filter) — same table_m0/table_m123 split ssb_pxweb uses below.
        if econ.get("cube_m0") and econ.get("dims_m0"):
            for key, (d, v) in _snb_cube_values(econ["cube_m0"], econ["dims_m0"],
                                                 require_level=False).items():
                vals[key] = (v / 1000.0, d)   # millions -> billions
    elif provider == "bcb_sgs":
        for key, series in econ.get("series", {}).items():
            d, v = _bcb_sgs_latest(series)
            if v is not None:
                vals[key] = (v / 1e6, d)      # thousands -> billions
    elif provider == "boe_iadb":
        for key, series in econ.get("series", {}).items():
            # m0 needs this the same way Canada's boc_valet entry does —
            # the Bank of England discontinued its own "M0" in 2006 and
            # replaced it with two series meant to be read together
            # (Notes & Coin in circulation + Reserve Balances), no
            # single published series sums them.
            codes = series if isinstance(series, list) else [series]
            total, date_s = _sum_series(_boe_iadb_latest, codes)
            if total is not None:
                vals[key] = (total / 1000.0, date_s)   # millions -> billions
    elif provider == "ssb_pxweb":
        if econ.get("table_m0") and econ.get("code_m0"):
            d, v = _ssb_pxweb_latest(econ["table_m0"], econ["code_m0"])
            if v is not None:
                vals["m0"] = (v / 1000.0, d)  # millions -> billions
        for key, code in econ.get("codes_m123", {}).items():
            d, v = _ssb_pxweb_latest(econ["table_m123"], code)
            if v is not None:
                vals[key] = (v / 1000.0, d)   # millions -> billions
    elif provider == "hand_curated":
        # for an economy with genuinely no live keyless feed at all (China)
        # — the seed's own values are already in native-currency billions,
        # so no unit conversion here, unlike every fetched provider above.
        as_of = econ.get("as_of")
        for key, v in (econ.get("values") or {}).items():
            if v is not None:
                vals[key] = (v, as_of)
    elif provider == "rbi_wss":
        # M0 and M3 are direct single rows; M1 has no row of its own in
        # India's WSS release (unlike every other provider's M1) — it's
        # summed from that same table's own component rows (RBI's own
        # textbook M1 definition: currency with the public + demand
        # deposits with banks + 'other' deposits with the RBI). No M2 —
        # that needs post office savings data RBI doesn't publish here.
        m0_id = _rbi_wss_latest_view_id(econ["section_m0"])
        if m0_id:
            d, v = _rbi_wss_items(m0_id, [econ["item_m0"]]).get(econ["item_m0"], (None, None))
            if v is not None:
                vals["m0"] = (v / 100.0, d)   # crore -> billions
        m13_id = _rbi_wss_latest_view_id(econ["section_m13"])
        if m13_id:
            m1_prefixes = econ.get("items_m1", [])
            items = _rbi_wss_items(m13_id, [econ["item_m3"]] + m1_prefixes)
            d3, v3 = items.get(econ["item_m3"], (None, None))
            if v3 is not None:
                vals["m3"] = (v3 / 100.0, d3)
            if m1_prefixes and all(p in items for p in m1_prefixes):
                total = sum(items[p][1] for p in m1_prefixes)
                vals["m1"] = (total / 100.0, items[m1_prefixes[0]][0])
    elif provider == "boj_csv":
        # group requested keys by which CSV table they need, so a table
        # shared by more than one key (Japan's Money Stock file carries
        # m1/m2/m3 as three columns of ONE csv) is fetched exactly once.
        by_table = {}
        for key, spec in econ.get("tables", {}).items():
            by_table.setdefault(spec["table"], {})[key] = spec["code"]
        for table, codes_by_key in by_table.items():
            for key, (d, v) in _boj_csv_values(table, codes_by_key).items():
                vals[key] = (v / 10.0, d)   # 100-million-yen -> billions of yen
    elif provider == "rba_csv":
        for key, (d, v) in _rba_csv_values(econ.get("codes", {})).items():
            vals[key] = (v, d)   # already A$ billion, no conversion
    elif provider == "dk_pxweb":
        codes = econ.get("codes", {})
        for key, (d, v) in _dk_pxweb_values(econ["table"], econ["dim"], codes,
                                             econ.get("extra_dims")).items():
            vals[key] = (v / 1000.0, d)   # DKK million -> billions
    else:
        print("  ! %s money supply — unknown provider %r" % (econ["area"], provider),
              file=sys.stderr)
        return None

    if not vals:
        print("  ! %s money supply unresolved (%s)" % (econ["area"], provider), file=sys.stderr)
        return None

    row = {"area": econ["area"], "flag": econ["flag"], "currency": econ["currency"],
           "source": econ["source"]}
    for key in ("m0", "m1", "m2", "m3"):
        native_b, date_s = vals.get(key, (None, None))
        row[key] = native_b
        row["%s_date" % key] = date_s
        row["usd_%s" % key] = (native_b / rate) if native_b is not None else None
    # this economy's own broadest resolved aggregate, broadest-first —
    # same "whatever this economy itself calls its headline figure" idea
    # the US (M2) and Euro area (M3) rows already use.
    row["broad_usd"] = next(
        (row["usd_%s" % k] for k in ("m3", "m2", "m1", "m0") if row["usd_%s" % k] is not None),
        None)
    return row


def _unresolved_money_row(entry):
    """A blank-cells row for a genuinely-investigated economy with no
    working live source yet (Michael's call, 2026-09-08: show the country
    with dashes and an honest source-note rather than silently drop it —
    the board's own reader-facing coverage list should be honest about
    ambition vs. what actually resolved today)."""
    row = {"area": entry["area"], "flag": entry["flag"], "currency": entry["currency"],
           "source": entry["note"]}
    for key in ("m0", "m1", "m2", "m3"):
        row[key] = None
        row["%s_date" % key] = None
        row["usd_%s" % key] = None
    row["broad_usd"] = None
    return row


def fetch_money_supply(fx, seed, fx_volatility=None, fx_turnover=None):
    """US (FRED) + Euro area (ECB) + five more economies (Canada/Switzerland/
    Brazil/UK/Norway, each its own real keyless API — see the dated research
    log above `BOC_VALET_URL`) with resolved figures, PLUS a set of
    genuinely-investigated economies shown with blank cells and an honest
    source-note (`money_supply_unresolved` in the seed file) rather than
    silently dropped — see the module docstring's dated 2026-09-08 entry for
    the full research trail (what was tried for each, and why it either
    worked or didn't).

    The Euro area's M0 ("Base money") is the one figure in this whole board
    that is hand-curated rather than live-queried — not because the ECB
    doesn't publish it (it does, weekly, in plain English in its own
    Consolidated Financial Statement press release), but because that figure
    lives in a different ECB dataset (Internal Liquidity Management) than
    the one used for M1/M2/M3 here (Balance Sheet Items), and a real,
    substantial attempt at a live keyless query against it found no working
    combination — see money_worldwide_seed.json's own eu_base_money note for
    the full trail. Its DOLLAR value still recomputes from today's live
    EUR/USD rate on every build, same as M1/M2/M3 — only the underlying EUR
    figure itself is periodically hand-refreshed.

    `fx_volatility` (from fetch_fx_volatility(), computed once in compute()
    and threaded through here) supplies each row's `volatility_pct`, and
    `fx_turnover` (from fetch_fx_turnover(), the curated BIS survey shares)
    supplies `turnover_usd` — both kept as separate top-level fetches
    rather than reached for per-row so an outage in either never costs a
    money-supply row its own resolution."""
    rows = []
    fx_volatility = fx_volatility or {}
    fx_turnover = fx_turnover or {}

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
            "broad_yoy_pct": _yoy_pct(*_yoy_from_pairs(_fred_series("M2SL"))),
            "volatility_pct": fx_volatility.get("USD"),  # always None — USD is the numeraire
            "turnover_usd": fx_turnover.get("USD"),
            "source": "Federal Reserve H.6 (via FRED, billions of dollars)",
        })
    else:
        print("  ! US money supply unresolved (FRED)", file=sys.stderr)

    ea_m1_date, ea_m1 = _ecb_bsi_latest(ECB_ITEMS["m1"])
    ea_m2_date, ea_m2 = _ecb_bsi_latest(ECB_ITEMS["m2"])
    ea_m3_date, ea_m3 = _ecb_bsi_latest(ECB_ITEMS["m3"])
    eur_usd = (fx or {}).get("rates", {}).get("EUR")
    ea_base = (seed or {}).get("eu_base_money") or {}
    ea_m0 = ea_base.get("eur_b")          # hand-curated, already in billions EUR
    ea_m0_date = ea_base.get("as_of")
    if ea_m3 is not None and eur_usd:
        # FRED/ECB give millions of national currency; this board's US row is
        # in BILLIONS — convert both onto the same "billions of dollars"
        # footing so the totals row and the scarcity chart can sum them.
        to_usd_b = lambda eur_m: (eur_m / 1000.0) / eur_usd if eur_m is not None else None
        rows.append({
            "area": "Euro area", "flag": "🇪🇺", "currency": "EUR",
            "m0": ea_m0, "m0_label": "Base money (ECB weekly statement, hand-curated)",
            "m0_date": ea_m0_date,
            "m1": (ea_m1 / 1000.0) if ea_m1 is not None else None, "m1_date": ea_m1_date,
            "m2": (ea_m2 / 1000.0) if ea_m2 is not None else None, "m2_date": ea_m2_date,
            "m3": (ea_m3 / 1000.0), "m3_date": ea_m3_date,
            "usd_m0": (ea_m0 / eur_usd) if ea_m0 is not None else None,
            "usd_m1": to_usd_b(ea_m1), "usd_m2": to_usd_b(ea_m2), "usd_m3": to_usd_b(ea_m3),
            "broad_usd": to_usd_b(ea_m3),   # M3 is the ECB's own headline "broad money"
            "broad_yoy_pct": _yoy_pct(*_yoy_from_pairs(_ecb_bsi_series(ECB_ITEMS["m3"]))),
            "volatility_pct": fx_volatility.get("EUR"),
            "turnover_usd": fx_turnover.get("EUR"),
            "source": "European Central Bank BSI dataset (billions of euro → USD "
                      "at today's rate)",
        })
    else:
        print("  ! Euro area money supply unresolved (ECB/fx)", file=sys.stderr)

    for econ in (seed or {}).get("money_supply_economies") or []:
        row = _fetch_generic_money_row(econ, fx)
        if row is not None:
            broad_key = next((k for k in ("m3", "m2", "m1", "m0")
                               if row.get("usd_%s" % k) is not None), None)
            row["broad_yoy_pct"] = _money_broad_yoy_pct(econ, broad_key) if broad_key else None
            row["volatility_pct"] = fx_volatility.get(row["currency"])
            row["turnover_usd"] = fx_turnover.get(row["currency"])
            rows.append(row)

    if not rows:
        # nothing at all resolved (not even the US/Euro area bespoke rows) —
        # a genuine down-day. Keep the previous board rather than write a
        # board that's ALL blank-row placeholders (see _unresolved_money_row).
        return None
    resolved_count = len(rows)

    # Blank-cell rows for economies seriously investigated but with no
    # working live source yet — appended only once at least one real
    # economy resolved above, so a total outage never produces an
    # all-dashes board (see the module docstring's fail-soft contract).
    for entry in (seed or {}).get("money_supply_unresolved") or []:
        rows.append(_unresolved_money_row(entry))

    total_broad_usd_b = sum(r["broad_usd"] for r in rows if r.get("broad_usd") is not None)
    return {"rows": rows, "total_broad_usd_b": total_broad_usd_b,
            "n_resolved": resolved_count, "n_total": len(rows)}


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
    # ALL resolved economies are shown (2026-09-08, Michael's call — "expand it to
    # all 195 economies and tally them all") — no top-N truncation. The table's
    # own totals row is therefore a straight sum of every row shown here, which
    # is why it's kept SEPARATE from world_gdp_usd_b below: that field prefers
    # the IMF's own official WEOWORLD aggregate (a published figure, not a sum
    # of member countries) when available, so the two can differ slightly by
    # IMF methodology even though this list is now genuinely complete.
    world_debt_pct = (total_debt_usd_b / total_gdp_usd_b * 100.0) if total_gdp_usd_b else None
    return {
        "rows": rows,
        "n_countries_total": len(rows),
        "world_gdp_usd_b": world_gdp_b if world_gdp_b is not None else total_gdp_usd_b,
        "world_gdp_year": world_gdp_year or (rows[0]["year"] if rows else None),
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


# Bitcoin's own halving schedule — a public consensus rule, not an estimate,
# duplicated here (rather than imported) from build_finance.py's/
# fetch_asset_board.py's own copies of the same two constants, on purpose:
# this fetcher stays a fully independent script, the same separation every
# other tools/fetch_*.py keeps from the page builder.
_BTC_HALVING_INTERVAL = 210_000
_BTC_INITIAL_SUBSIDY_SATS = 50 * 100_000_000


def _btc_annual_issuance_pct(circulating_btc, block_height):
    """Bitcoin's own current annualized issuance rate (%%) — the money-
    supply "debasement rate" column's Bitcoin figure, computed exactly from
    the halving schedule rather than fetched: current per-block subsidy
    (50 BTC, halved every 210,000 blocks) × ~52,596 blocks/year (the
    10-minute target), over today's circulating supply. The one cell in
    this whole column derived from a fixed rule instead of a live query."""
    if not circulating_btc or block_height is None:
        return None
    epoch = block_height // _BTC_HALVING_INTERVAL
    subsidy_btc = (_BTC_INITIAL_SUBSIDY_SATS >> epoch) / 100_000_000.0
    blocks_per_year = 365.25 * 24 * 6   # 10-minute block target
    return (subsidy_btc * blocks_per_year / circulating_btc) * 100.0


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
    constants = asset_board.get("constants") or {}

    lineup = []
    if money_supply and money_supply.get("total_broad_usd_b") is not None:
        n_resolved = money_supply.get("n_resolved", len(money_supply.get("rows", [])))
        lineup.append({
            "label": "Broad money — %d economies with live data" % n_resolved,
            "usd": money_supply["total_broad_usd_b"] * 1e9,
            "note": "The %d economies on the Money Supply page with a real, current figure "
                    "today — a genuine floor under the true global figure, not the whole "
                    "world's money supply." % n_resolved,
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
    btc_vol_pct, btc_volume_usd = fetch_bitcoin_market_stats()
    return {
        "price_usd": btc.get("price"), "market_cap_usd": btc.get("market_cap"),
        "btc_rank": asset_board.get("btc_rank"),
        "volatility_pct": btc_vol_pct,
        "turnover_usd": btc_volume_usd,
        "broad_yoy_pct": _btc_annual_issuance_pct(
            constants.get("btc_circulating"), constants.get("btc_block_height")),
        "lineup": lineup,
    }


# ─────────────────────────────────────────────────────────────────────────────

def compute():
    """The full board, or None if nothing usable resolved at all."""
    seed = _load_json_file(SEED)
    asset_board = _load_json_file(ASSET_BOARD)

    fx = fetch_fx()
    fx_volatility = fetch_fx_volatility()
    fx_turnover = fetch_fx_turnover(seed)
    money_supply = fetch_money_supply(fx, seed, fx_volatility, fx_turnover)
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

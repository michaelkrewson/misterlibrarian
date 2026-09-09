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


def fetch_money_supply(fx, seed):
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
    figure itself is periodically hand-refreshed."""
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
            "source": "European Central Bank BSI dataset (billions of euro → USD "
                      "at today's rate)",
        })
    else:
        print("  ! Euro area money supply unresolved (ECB/fx)", file=sys.stderr)

    for econ in (seed or {}).get("money_supply_economies") or []:
        row = _fetch_generic_money_row(econ, fx)
        if row is not None:
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
    money_supply = fetch_money_supply(fx, seed)
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

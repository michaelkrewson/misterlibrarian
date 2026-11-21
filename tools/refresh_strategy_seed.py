#!/usr/bin/env python3
"""Keep Strategy's row in the Ledger's two seed files current from its own weekly 8-K on SEC EDGAR.

Why: Strategy's bitcoin count was typed into treasuries_seed.json / cebe_seed.json by hand and sat days behind
each Monday filing (2026-11-21: the page showed 845,050 while the company held 850,849). This runs in the board
refresh BEFORE the Treasuries and CEBE steps, updates only MSTR's `btc_holdings` (and, for CEBE, `cost_basis`),
and the normal "Commit if anything changed" step keeps it in git.

SEC fair-access asks for a descriptive User-Agent with a contact. The contact is the repo secret SEC_CONTACT; it
is never written to a file or printed. With no SEC_CONTACT the script does nothing (exit 0) — the seeds simply
keep their last value.

FAIL DIRECTION: no contact, no recent 8-K, a table layout that doesn't match, a move of more than 5% from the
seed value, an older as-of than the seed's, or an aggregate cost that disagrees with holdings x average — in every
case change NOTHING. (Same parse as the fleet's strategy_feed.py, pinned to the 2026-11-16 8-K: 850,849 BTC,
$64.20B aggregate, $75,452 average.)

  python3 tools/refresh_strategy_seed.py            # update the seeds
  python3 tools/refresh_strategy_seed.py --dry-run  # say what would change
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURIES = os.path.join(ROOT, "source", "finance", "treasuries_seed.json")
CEBE = os.path.join(ROOT, "source", "finance", "cebe_seed.json")
CIK = "0001050446"
EDGAR_DIR = "https://www.sec.gov/Archives/edgar/data/1050446"
MAX_MOVE_PCT = 5.0
MAX_AGE_DAYS = 21

_AS_OF = re.compile(r"As of ([A-Z][a-z]+ \d{1,2}, \d{4}) BTC Purchased")
_ROW = re.compile(r"(\d[\d,]*)\s+\$\s*([\d.]+)\s+\$\s*([\d,]+)\s+(\d{3},\d{3})\s+\$\s*([\d.]+)\s+\$\s*([\d,]+)\s+\(1\)\s+The bitcoin")


def parse_8k(html: str):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html).replace("&#160;", " ").replace("&nbsp;", " "))
    a, r = _AS_OF.search(t), _ROW.search(t)
    if not a or not r:
        return None
    try:
        return {"as_of": datetime.strptime(a.group(1), "%B %d, %Y").strftime("%Y-%m-%d"),
                "btc_holdings": int(r.group(4).replace(",", "")),
                "aggregate_cost_usd_b": float(r.group(5)), "avg_cost_usd": int(r.group(6).replace(",", ""))}
    except ValueError:
        return None


def plausible(new: dict, old_holdings: float, old_as_of: str):
    """(ok, reason) — the guards that keep a bad parse out of the seeds."""
    implied = new["aggregate_cost_usd_b"] * 1e9 / new["btc_holdings"]
    if not (0.97 <= implied / new["avg_cost_usd"] <= 1.03):
        return False, "aggregate/holdings disagrees with the stated average"
    if old_holdings and abs(new["btc_holdings"] - old_holdings) / old_holdings * 100 > MAX_MOVE_PCT:
        return False, f"implausible move from {old_holdings:,.0f} to {new['btc_holdings']:,}"
    if old_as_of and new["as_of"] < old_as_of:
        return False, "older than the seed's as-of"
    return True, "ok"


def _get(url: str, ua: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def latest(contact: str):
    ua = f"Ledger research ({contact})"
    rec = json.loads(_get(f"https://data.sec.gov/submissions/CIK{CIK}.json", ua))["filings"]["recent"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    for i, form in enumerate(rec["form"]):
        if form != "8-K":
            continue
        if datetime.strptime(rec["filingDate"][i], "%Y-%m-%d").replace(tzinfo=timezone.utc) < cutoff:
            break
        url = f"{EDGAR_DIR}/{rec['accessionNumber'][i].replace('-', '')}/{rec['primaryDocument'][i]}"
        got = parse_8k(_get(url, ua))
        if got:
            return got, rec["filingDate"][i]
    return None


def _edit(path: str, new_row, find, dry: bool) -> bool:
    """Rewrite just MSTR's row text in place (the seeds are hand-formatted one-row-per-line; keep that)."""
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    for n, line in enumerate(lines):
        if find(line):
            out = new_row(line)
            if out == line:
                return False
            if not dry:
                lines[n] = out
                open(path, "w", encoding="utf-8").write("\n".join(lines))
            return True
    return False


# ── Quarterly balance-sheet figures from the 10-Q/10-K XBRL (SEC companyfacts) ─────────────────────────────
# Only the three that map to ONE clean us-gaap tag (verified 2026-11-21 against Strategy's Q2 and Q3 2026 10-Qs;
# the Q2 preferred figure matched the seed's hand-sourced $15,462,056,000 exactly):
#   debt_usd            <- LongTermDebt                           (Q3: 6,715,414,000; strategy.com showed $6.714B)
#   preferred_liq_usd   <- TemporaryEquityLiquidationPreference   (Q3: 14,109,839,000)
#   operating_cf_usd    <- trailing twelve months of NetCashProvidedByUsedInOperatingActivities
# NOT automated (no clean tag, or a definition call): cash, diluted/basic shares, the blended preferred dividend
# rate. They stay curated.
FACTS_URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"


def _d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def _usd(facts, tag):
    return facts["facts"]["us-gaap"][tag]["units"]["USD"]


def _latest_instant(facts, tag):
    es = [e for e in _usd(facts, tag) if not e.get("start") and e.get("form") in ("10-Q", "10-K")]
    return max(es, key=lambda e: (e["end"], e["filed"])) if es else None


def _ytd(facts, tag, start, end):
    es = [e for e in _usd(facts, tag) if e.get("start") == start and e["end"] == end and e.get("form") in ("10-Q", "10-K")]
    return max(es, key=lambda e: e["filed"])["val"] if es else None


def _ttm_opcf(facts, end):
    """Trailing-twelve-month operating cash flow ending `end`, or None when any needed period is missing."""
    tag, e = "NetCashProvidedByUsedInOperatingActivities", _d(end)
    cur = _ytd(facts, tag, f"{e.year}-01-01", end)
    if cur is None:
        return None
    if (e.month, e.day) == (12, 31):
        return cur
    prior_ytd = _ytd(facts, tag, f"{e.year - 1}-01-01", f"{e.year - 1}-{e.month:02d}-{e.day:02d}")
    prior_fy = _ytd(facts, tag, f"{e.year - 1}-01-01", f"{e.year - 1}-12-31")
    if prior_ytd is None or prior_fy is None:
        return None
    return prior_fy + cur - prior_ytd


def extract_quarterly(facts):
    """PURE. {period_end, debt_usd, preferred_liq_usd, operating_cf_usd|None} from companyfacts, or None.
    Debt and preferred must come from the SAME period end (a half-updated pair is never used)."""
    try:
        debt = _latest_instant(facts, "LongTermDebt")
        pref = _latest_instant(facts, "TemporaryEquityLiquidationPreference")
        if not debt or not pref or debt["end"] != pref["end"]:
            return None
        if not (0 < debt["val"] < 5e10 and 0 < pref["val"] < 1e11):
            return None
        return {"period_end": debt["end"], "debt_usd": int(debt["val"]), "preferred_liq_usd": int(pref["val"]),
                "operating_cf_usd": _ttm_opcf(facts, debt["end"])}
    except (KeyError, ValueError, TypeError):
        return None


def quarterly_plausible(new: dict, row: dict):
    """(ok, reason): never go backwards in time, never accept a >2x / <0.5x jump in one quarter."""
    if row.get("quarterly_as_of") and new["period_end"] <= row["quarterly_as_of"]:
        return False, "not newer than the seed's quarter"
    for k in ("debt_usd", "preferred_liq_usd"):
        old = row.get(k) or 0
        if old and not (0.5 <= new[k] / old <= 2.0):
            return False, f"{k} moved from {old:,.0f} to {new[k]:,}"
    return True, "ok"


def _cebe_quarterly_row(new: dict):
    def edit(line):
        line = re.sub(r'"debt_usd": \d+', f'"debt_usd": {new["debt_usd"]}', line, count=1)
        line = re.sub(r'"preferred_liq_usd": \d+', f'"preferred_liq_usd": {new["preferred_liq_usd"]}', line, count=1)
        if new.get("operating_cf_usd") is not None:
            line = re.sub(r'"operating_cf_usd": -?\d+', f'"operating_cf_usd": {int(new["operating_cf_usd"])}', line, count=1)
        if '"quarterly_as_of"' in line:
            return re.sub(r'"quarterly_as_of": "[^"]*"', f'"quarterly_as_of": "{new["period_end"]}"', line, count=1)
        return line.replace(', "kind":', f', "quarterly_as_of": "{new["period_end"]}", "kind":', 1)
    return edit


def refresh_quarterly(contact: str, dry: bool) -> None:
    ua = f"Ledger research ({contact})"
    try:
        new = extract_quarterly(json.loads(_get(FACTS_URL, ua)))
    except Exception as exc:
        print(f"  ! Strategy quarterly fetch failed ({type(exc).__name__}) — quarterly figures left as they are", file=sys.stderr)
        return
    if not new:
        print("  ! no consistent quarterly XBRL figures — left as they are", file=sys.stderr)
        return
    row = next((c for c in json.load(open(CEBE, encoding="utf-8")).get("companies", []) if c.get("ticker") == "MSTR"), None)
    if not row:
        return
    ok, why = quarterly_plausible(new, row)
    if not ok:
        print(f"  quarterly figures unchanged ({why})")
        return
    changed = _edit(CEBE, _cebe_quarterly_row(new), lambda l: '"ticker": "MSTR"' in l, dry)
    print(f"Strategy quarterly {'would set' if dry else 'set'} from the {new['period_end']} filing "
          f"(debt ${new['debt_usd']:,}, preferred ${new['preferred_liq_usd']:,}, op cash flow TTM {new['operating_cf_usd']}): {changed}")


def main(argv) -> int:
    dry = "--dry-run" in argv
    contact = os.environ.get("SEC_CONTACT", "").strip()
    if not contact:
        print("no SEC_CONTACT — Strategy seeds left as they are")
        return 0
    refresh_quarterly(contact, dry)                # independent of the weekly 8-K: either may fail without the other
    try:
        got = latest(contact)
    except Exception as exc:                       # network/SEC trouble must never fail the board refresh
        print(f"  ! Strategy 8-K fetch failed ({type(exc).__name__}) — seeds left as they are", file=sys.stderr)
        return 0
    if not got:
        print("  ! no recent Strategy 8-K with the holdings table — seeds left as they are", file=sys.stderr)
        return 0
    new, fdate = got

    tre = json.load(open(TREASURIES, encoding="utf-8"))
    row = next((e for e in tre.get("entities", []) if e.get("ticker") == "MSTR"), None)
    if not row:
        return 0
    ok, why = plausible(new, row.get("btc_holdings") or 0, row.get("as_of") or "")
    if not ok:
        print(f"  ! Strategy reading rejected ({why}) — seeds left as they are", file=sys.stderr)
        return 0

    note = f"Strategy 8-K filed {fdate} (as of {new['as_of']}), read from SEC EDGAR by tools/refresh_strategy_seed.py"

    def tre_row(line):
        line = re.sub(r'"btc_holdings": \d+', f'"btc_holdings": {new["btc_holdings"]}', line, count=1)
        line = re.sub(r'"as_of": "[^"]*"', f'"as_of": "{new["as_of"]}"', line, count=1)
        return re.sub(r'"source_note": "[^"]*"', f'"source_note": "{note}"', line, count=1)

    def cebe_row(line):
        line = re.sub(r'"btc_holdings": \d+', f'"btc_holdings": {new["btc_holdings"]}', line, count=1)
        return re.sub(r'"cost_basis": \d+', f'"cost_basis": {new["avg_cost_usd"]}', line, count=1)

    a = _edit(TREASURIES, tre_row, lambda l: '"ticker": "MSTR"' in l and '"name": "Strategy (MicroStrategy)"' in l, dry)
    b = _edit(CEBE, cebe_row, lambda l: '"ticker": "MSTR"' in l, dry)
    verb = "would set" if dry else "set"
    print(f"Strategy {verb} to {new['btc_holdings']:,} BTC as of {new['as_of']} (treasuries: {a}, cebe: {b})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

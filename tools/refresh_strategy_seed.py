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


def main(argv) -> int:
    dry = "--dry-run" in argv
    contact = os.environ.get("SEC_CONTACT", "").strip()
    if not contact:
        print("no SEC_CONTACT — Strategy seeds left as they are")
        return 0
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

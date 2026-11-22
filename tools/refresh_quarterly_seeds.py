#!/usr/bin/env python3
"""Keep MARA's, Twenty One's, Riot's and CleanSpark's CEBE rows current from their own latest 10-Q/10-K on SEC EDGAR.

Neither company publishes a weekly holdings 8-K (checked 2026-11-21: their 8-Ks are results letters, notes pricing,
board changes), so unlike Strategy / Strive this is QUARTERLY — it moves when a 10-Q lands. Read per company:

  MARA  btc_holdings <- "Total bitcoin holdings N" in the 10-Q's digital-asset table (includes bitcoin lent out as
                        receivables: 34,012 at 2026-09-30 = 14,752 held + 19,260 receivable)
        debt_usd     <- us-gaap LongTermDebt (carrying amount, net of discount: 3,019,332,000 at 2026-09-30; the
                        10-Q's gross principal is 3,047,201,000 — 0.9% apart)
        cash_usd     <- us-gaap CashAndCashEquivalentsAtCarryingValue (946,545,000)
  XXI   btc_holdings <- us-gaap CryptoAssetNumberOfUnits (43,514; the unit label's case varies, so any non-USD unit)
        cash_usd     <- CashAndCashEquivalentsAtCarryingValue (102,846,000)
        debt_usd     NOT touched (its $486.5M convertible principal has no clean tag; it is stated in the 10-Q text)

Contract = refresh_strategy_seed.py: needs env SEC_CONTACT (no-op without), never raises, changes NOTHING on doubt
(no 10-Q, a pattern that doesn't match, an older period than the row's `quarterly_as_of`, holdings moving more than
40% or debt outside 0.5-2x in one quarter).

  python3 tools/refresh_quarterly_seeds.py [--dry-run]
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEBE = os.path.join(ROOT, "source", "finance", "cebe_seed.json")
MAX_HOLD_MOVE = 0.40

# holdings "text" -> regex over the filing text (groups are summed); "xbrl" -> us-gaap CryptoAssetNumberOfUnits.
COMPANIES = {
    "MARA": {"cik": "1507605", "holdings": "text", "debt": "LongTermDebt",
             "pattern": re.compile(r"Total bitcoin holdings ([\d,]+)")},
    "XXI": {"cik": "2070457", "holdings": "xbrl", "debt": None},
    # Riot sold 20,264 bitcoin in 2026 (10-Q: "reducing our bitcoin holdings to 2,418 bitcoin as of September 30, 2026");
    # the same 2,418 is tagged CryptoAssetNumberOfUnits (unit label "item").
    "RIOT": {"cik": "1167419", "holdings": "xbrl", "debt": "LongTermDebt"},
    # CleanSpark (fiscal year ends Sept 30, so its latest filing may be a 10-K): bitcoin held PLUS bitcoin posted as
    # collateral (still owned): "we held approximately 12,205 bitcoins and had a receivable for 1,719 bitcoin" (2026-06-30).
    "CLSK": {"cik": "827876", "holdings": "text", "debt": "LongTermDebt",
             "pattern": re.compile(r"we held approximately ([\d,]+) bitcoins(?: and had a receivable for ([\d,]+) bitcoin)?")},
    # HOLDINGS ONLY for the next two ("cash": False, no debt): their cash and debt are not bitcoin-strategy figures, and the
    # board's debt is deliberately 0 / curated for them. Hut 8's filing is consolidated with American Bitcoin (ABTC):
    # "we held approximately 16,787 Bitcoin, comprising approximately 8,360 Bitcoin held by Hut 8 and approximately 8,427
    # Bitcoin held by American Bitcoin" — take ONLY Hut 8's own, or ABTC's row would be counted twice.
    "HUT": {"cik": "1964789", "holdings": "text", "debt": None, "cash": False,
            "pattern": re.compile(r"comprising approximately ([\d,]+) Bitcoin held by Hut 8")},
    "XYZ": {"cik": "1512673", "holdings": "xbrl", "debt": None, "cash": False},     # Block: CryptoAssetNumberOfUnits (9,237)
}


def _get(url: str, ua: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def _text(raw: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("\xa0", " "))


def _instant(facts: dict, tag: str, end: str, units=("USD",)):
    """The value of an instant fact at exactly `end` (latest filing wins), any unit when units is None."""
    try:
        node = facts["facts"]["us-gaap"][tag]["units"]
    except KeyError:
        return None
    best = None
    for u, pts in node.items():
        if units is not None and u not in units:
            continue
        for p in pts:
            if p.get("end") == end and not p.get("start") and p.get("form") in ("10-Q", "10-K"):
                if best is None or p["filed"] > best["filed"]:
                    best = p
    return best["val"] if best else None


def text_holdings(tkr: str, text: str):
    m = COMPANIES[tkr]["pattern"].search(text)
    if not m:
        return None
    return sum(int(g.replace(",", "")) for g in m.groups() if g)


def extract(tkr: str, text: str, facts: dict, end: str):
    """Figures for one company at period `end`, only those that could be read; {} when the holdings can't be."""
    cfg = COMPANIES[tkr]
    hold = text_holdings(tkr, text) if cfg["holdings"] == "text" else _instant(facts, "CryptoAssetNumberOfUnits", end, None)
    if not hold or hold <= 0:
        return {}
    out = {"btc_holdings": int(hold)}
    cash = _instant(facts, "CashAndCashEquivalentsAtCarryingValue", end) if cfg.get("cash", True) else None
    if cash is not None and cash >= 0:
        out["cash_usd"] = int(cash)
    if cfg["debt"]:
        d = _instant(facts, cfg["debt"], end)
        if d and d > 0:
            out["debt_usd"] = int(d)
    return out


def plausible(new: dict, end: str, row: dict):
    if row.get("quarterly_as_of") and end < row["quarterly_as_of"]:
        return False, "older than the row's quarter"
    old = row.get("btc_holdings") or 0
    if old and abs(new["btc_holdings"] - old) / old > MAX_HOLD_MOVE:
        return False, f"holdings moved {old:,.0f} -> {new['btc_holdings']:,}"
    if new.get("debt_usd") and row.get("debt_usd") and not (0.5 <= new["debt_usd"] / row["debt_usd"] <= 2.0):
        return False, f"debt moved {row['debt_usd']:,.0f} -> {new['debt_usd']:,}"
    return True, "ok"


def _row_edit(tkr: str, new: dict, end: str):
    def edit(line):
        line = re.sub(r'"btc_holdings": [\d.]+', f'"btc_holdings": {new["btc_holdings"]}', line, count=1)
        if "debt_usd" in new:
            line = re.sub(r'"debt_usd": \d+', f'"debt_usd": {new["debt_usd"]}', line, count=1)
        if "cash_usd" in new:
            if '"cash_usd"' in line:
                line = re.sub(r'"cash_usd": \d+', f'"cash_usd": {new["cash_usd"]}', line, count=1)
            else:
                line = line.replace(', "kind":', f', "cash_usd": {new["cash_usd"]}, "kind":', 1)
        if '"quarterly_as_of"' in line:
            return re.sub(r'"quarterly_as_of": "[^"]*"', f'"quarterly_as_of": "{end}"', line, count=1)
        return line.replace(', "kind":', f', "quarterly_as_of": "{end}", "kind":', 1)
    return edit


def _edit(path: str, tkr: str, new_row, dry: bool) -> bool:
    lines = open(path, encoding="utf-8").read().split("\n")
    for n, line in enumerate(lines):
        if f'"ticker": "{tkr}"' in line:
            out = new_row(line)
            if out == line:
                return False
            if not dry:
                lines[n] = out
                open(path, "w", encoding="utf-8").write("\n".join(lines))
            return True
    return False


def refresh_one(tkr: str, contact: str, dry: bool) -> None:
    ua = f"Ledger research ({contact})"
    cfg = COMPANIES[tkr]
    cik10 = cfg["cik"].zfill(10)
    rec = json.loads(_get(f"https://data.sec.gov/submissions/CIK{cik10}.json", ua))["filings"]["recent"]
    i = next((n for n, f in enumerate(rec["form"]) if f in ("10-Q", "10-K")), None)
    if i is None:
        print(f"  ! {tkr}: no recent 10-Q/10-K — left as is", file=sys.stderr)
        return
    end = rec["reportDate"][i]
    url = f"https://www.sec.gov/Archives/edgar/data/{cfg['cik']}/{rec['accessionNumber'][i].replace('-', '')}/{rec['primaryDocument'][i]}"
    text = _text(_get(url, ua)) if cfg["holdings"] == "text" else ""
    facts = json.loads(_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json", ua))
    new = extract(tkr, text, facts, end)
    if not new:
        print(f"  ! {tkr}: couldn't read holdings from the {end} 10-Q — left as is", file=sys.stderr)
        return
    row = next((c for c in json.load(open(CEBE, encoding="utf-8")).get("companies", []) if c.get("ticker") == tkr), None)
    if not row:
        return
    ok, why = plausible(new, end, row)
    if not ok:
        print(f"  ! {tkr} reading rejected ({why}) — left as is", file=sys.stderr)
        return
    changed = _edit(CEBE, tkr, _row_edit(tkr, new, end), dry)
    print(f"{tkr} {'would set' if dry else 'set'} from the {end} 10-Q: {new}: {changed}")


def main(argv) -> int:
    dry = "--dry-run" in argv
    contact = os.environ.get("SEC_CONTACT", "").strip()
    if not contact:
        print("no SEC_CONTACT — MARA/XXI seeds left as they are")
        return 0
    for tkr in COMPANIES:
        try:
            refresh_one(tkr, contact, dry)
        except Exception as exc:                   # one company's trouble never blocks another or the board refresh
            print(f"  ! {tkr} failed ({type(exc).__name__}) — left as is", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

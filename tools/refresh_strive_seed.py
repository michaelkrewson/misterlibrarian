#!/usr/bin/env python3
"""Keep Strive (ASST)'s row in the Ledger's CEBE seed current from its own weekly 8-K on SEC EDGAR.

Why: Strive's row was typed in by hand and sat months behind (2026-11-21: seed said 24,531 BTC / 94.9M shares /
$1.0B preferred; the company's own Nov 16 8-K said 43,404 BTC / 127.3M shares / SATA+SATS ~ $2.1B).

Strive files a Monday 8-K with a two-column table (prior week, this week). From the THIS-week column we take:
  btc_holdings      <- "Bitcoin held"
  shares_out        <- "Effective Common Shares Outstanding" (Class A + Class B, 1:1 — the company's own definition)
  cash_usd          <- "Cash and cash equivalents (in thousands)"   (cash only; its STRC holding is not counted)
  preferred_liq_usd <- (SATA shares + SATS shares) x $100            (both stated amount $100/share, 10-Q 2026-09-30;
                                                                      SATA's accreting preference was $100.01 — ignored)
NOT touched: cost_basis (the 8-K gives only each week's purchase price, no aggregate) and debt_usd (0 — the Semler
convertible notes and the Coinbase loan were retired by May 2026; total liabilities were $37.5M at 2026-09-30).

Same contract as refresh_strategy_seed.py: needs env SEC_CONTACT (no-op without), never raises, changes NOTHING on
any doubt (no 8-K, layout mismatch, A+B != effective shares, an older as-of, or a move beyond the weekly bounds).

  python3 tools/refresh_strive_seed.py            # update the seed
  python3 tools/refresh_strive_seed.py --dry-run  # say what would change
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEBE = os.path.join(ROOT, "source", "finance", "cebe_seed.json")
CIK = "0001920406"
EDGAR_DIR = "https://www.sec.gov/Archives/edgar/data/1920406"
STATED = 100                    # $ per SATA / SATS share
MAX_AGE_DAYS = 21
MAX_MOVE = {"btc_holdings": 0.25, "shares_out": 0.10, "preferred_liq_usd": 0.25}   # one week; first run is seeded by hand

_N = r"(\d[\d,]*)"
_AS_OF = re.compile(r"As of [A-Z][a-z]+ \d{1,2}, \d{4} As of ([A-Z][a-z]+ \d{1,2}, \d{4}) Change")
_CASH = re.compile(r"Cash and cash equivalents \(in thousands\) \$ " + _N + r" \$ " + _N)
_BTC = re.compile(r"Bitcoin held " + _N + " " + _N)
_A = re.compile(r"Class A common stock " + _N + " " + _N)
_B = re.compile(r"Class B common stock " + _N + " " + _N)
_EFF = re.compile(r"Effective Common Shares Outstanding \(\d\) " + _N + " " + _N)
_SATS = re.compile(r"SATS Stock " + _N + " " + _N)
_SATA = re.compile(r"SATA Stock " + _N + " " + _N)


def _i(m):
    return int(m.group(2).replace(",", ""))


def parse_8k(raw: str):
    """The latest-week column of the holdings table, or None when the layout isn't recognised."""
    t = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("\xa0", " "))
    ms = [r.search(t) for r in (_AS_OF, _CASH, _BTC, _A, _B, _EFF, _SATS, _SATA)]
    if not all(ms):
        return None
    asof, cash, btc, a, b, eff, sats, sata = ms
    try:
        out = {"as_of": datetime.strptime(asof.group(1), "%B %d, %Y").strftime("%Y-%m-%d"),
               "cash_usd": _i(cash) * 1000, "btc_holdings": _i(btc), "shares_out": _i(eff),
               "sats_shares": _i(sats), "sata_shares": _i(sata)}
        if _i(a) + _i(b) != _i(eff):
            return None
    except ValueError:
        return None
    out["preferred_liq_usd"] = (out["sats_shares"] + out["sata_shares"]) * STATED
    return out


def plausible(new: dict, row: dict):
    """(ok, reason). `row` is the current seed row."""
    if row.get("as_of") and new["as_of"] < row["as_of"]:
        return False, "older than the seed's as-of"
    if not (new["btc_holdings"] > 0 and new["shares_out"] > 0 and new["cash_usd"] >= 0):
        return False, "non-positive figure"
    for k, lim in MAX_MOVE.items():
        old = row.get(k) or 0
        if old and abs(new[k] - old) / old > lim:
            return False, f"{k} moved from {old:,.0f} to {new[k]:,}"
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


def _row_edit(new: dict):
    def edit(line):
        for k in ("btc_holdings", "shares_out", "preferred_liq_usd"):
            line = re.sub(rf'"{k}": \d+', f'"{k}": {new[k]}', line, count=1)
        if '"cash_usd"' in line:
            line = re.sub(r'"cash_usd": \d+', f'"cash_usd": {new["cash_usd"]}', line, count=1)
        else:
            line = line.replace(', "kind":', f', "cash_usd": {new["cash_usd"]}, "kind":', 1)
        if '"holdings_as_of"' in line:
            return re.sub(r'"holdings_as_of": "[^"]*"', f'"holdings_as_of": "{new["as_of"]}"', line, count=1)
        return line.replace(', "kind":', f', "holdings_as_of": "{new["as_of"]}", "kind":', 1)
    return edit


def _edit(path: str, new_row, dry: bool) -> bool:
    lines = open(path, encoding="utf-8").read().split("\n")
    for n, line in enumerate(lines):
        if '"ticker": "ASST"' in line:
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
        print("no SEC_CONTACT — Strive seed left as it is")
        return 0
    try:
        got = latest(contact)
    except Exception as exc:                       # network/SEC trouble must never fail the board refresh
        print(f"  ! Strive 8-K fetch failed ({type(exc).__name__}) — seed left as it is", file=sys.stderr)
        return 0
    if not got:
        print("  ! no recent Strive 8-K with the holdings table — seed left as it is", file=sys.stderr)
        return 0
    new, fdate = got
    row = next((c for c in json.load(open(CEBE, encoding="utf-8")).get("companies", []) if c.get("ticker") == "ASST"), None)
    if not row:
        return 0
    ok, why = plausible(new, row)
    if not ok:
        print(f"  ! Strive reading rejected ({why}) — seed left as it is", file=sys.stderr)
        return 0
    changed = _edit(CEBE, _row_edit(new), dry)
    print(f"Strive {'would set' if dry else 'set'} from the 8-K filed {fdate} (as of {new['as_of']}): "
          f"{new['btc_holdings']:,} BTC, {new['shares_out']:,} shares, cash ${new['cash_usd']:,}, "
          f"preferred ${new['preferred_liq_usd']:,}: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

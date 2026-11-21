#!/usr/bin/env python3
"""Flag CEBE rows whose figures haven't been touched in too long — the stale-row check.

The CEBE seed's numbers (holdings, shares, cost basis, debt, preferred, cash) are curated, and a row can sit wrong for
months without anything noticing (2026-11-21: Strive's row was 19,000 BTC behind). This keeps a sidecar,
source/finance/cebe_freshness.json, of {ticker: {fingerprint, changed}}:

  changed    the date the row's figures last DIFFERED (fingerprint of those six fields). First sight of a ticker
             is dated from `git blame` of its seed line when history is available, else today.
  confirmed  the later of `changed` and the row's own as-of stamps (`holdings_as_of`, `quarterly_as_of`), which the
             SEC refreshers set when they re-read a filing and found nothing new — a verified-unchanged figure is not stale.
  stale      today - confirmed > limit: 60 days for a hand-curated row, 135 for one on a quarterly SEC refresh
             (a quarter plus the filing lag).

Run it BEFORE fetch_cebe.py (which copies `confirmed` / `age_days` / `stale` onto each board row; build_finance
shows a warning mark). It prints one `::warning::` line per stale row so the workflow run page lists them. Never fails:
any trouble leaves the sidecar as it was.

  python3 tools/figure_freshness.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "source", "finance", "cebe_seed.json")
SIDE = os.path.join(ROOT, "source", "finance", "cebe_freshness.json")
FIELDS = ("btc_holdings", "shares_out", "cost_basis", "debt_usd", "preferred_liq_usd", "cash_usd")
LIMIT_CURATED = 60
LIMIT_QUARTERLY = 135


def fingerprint(row: dict) -> str:
    return hashlib.sha1(json.dumps([row.get(k) for k in FIELDS]).encode()).hexdigest()[:12]


def _blame_date(ticker: str):
    """Date of the last commit that touched this ticker's seed line, or None (shallow clone / no git)."""
    try:
        lines = open(SEED, encoding="utf-8").read().split("\n")
        n = next(i for i, l in enumerate(lines, 1) if f'"ticker": "{ticker}"' in l)
        out = subprocess.run(["git", "blame", "-L", f"{n},{n}", "--date=short", "--", SEED], cwd=ROOT,
                             capture_output=True, text=True, timeout=30).stdout
        import re
        m = re.search(r"(\d{4}-\d{2}-\d{2})", out)
        return m.group(1) if m else None
    except Exception:
        return None


def limit_for(row: dict) -> int:
    return LIMIT_QUARTERLY if row.get("quarterly_as_of") else LIMIT_CURATED


def evaluate(row: dict, entry: dict, today: date):
    """PURE. -> (confirmed 'YYYY-MM-DD', age_days, stale)."""
    stamps = [entry["changed"], row.get("holdings_as_of") or "", row.get("quarterly_as_of") or ""]
    confirmed = max(s for s in stamps if s)
    age = (today - date.fromisoformat(confirmed)).days
    return confirmed, age, age > limit_for(row)


def main() -> int:
    try:
        today = date.today()
        rows = json.load(open(SEED, encoding="utf-8")).get("companies", [])
        try:
            side = json.load(open(SIDE, encoding="utf-8"))
        except (OSError, ValueError):
            side = {}
        out, stale = {}, []
        for r in rows:
            t = r.get("ticker")
            if not t:
                continue
            fp = fingerprint(r)
            old = side.get(t)
            if old and old.get("fingerprint") == fp:
                entry = {"fingerprint": fp, "changed": old["changed"]}
            else:                                   # new ticker or figures differ now
                entry = {"fingerprint": fp, "changed": (_blame_date(t) if not old else None) or today.isoformat()}
            confirmed, age, is_stale = evaluate(r, entry, today)
            out[t] = {**entry, "confirmed": confirmed, "age_days": age, "stale": is_stale}
            if is_stale:
                stale.append((t, age))
        with open(SIDE, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        for t, age in sorted(stale, key=lambda x: -x[1]):
            print(f"::warning title=CEBE figures stale::{t}: figures last confirmed {age} days ago — re-check its latest filing")
        print(f"freshness: {len(out)} rows, {len(stale)} stale")
    except Exception as exc:                        # must never cost the board its refresh
        print(f"  ! freshness check failed ({type(exc).__name__}) — sidecar left as is", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

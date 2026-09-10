#!/usr/bin/env python3
"""Analyse a Google Search Console Performance export around an impressions cliff.

Usage:
    gsc_cliff.py <export.zip|dir> [--split YYYY-MM-DD]          # one 3-month export
    gsc_cliff.py <before.zip|dir> <after.zip|dir>               # two window exports

Single-export mode splits the daily series at --split and asks the only question
that matters when impressions collapse: did POSITION move with them?
  - position collapsed too      -> a real re-rank into the tail
  - position held               -> the queries went away, not the rankings
  - position IMPROVED           -> a mix effect; the lost impressions were junk
Two-export mode additionally compares Queries.csv per query, holding the query
mix fixed -- the only honest re-rank test.

⚠ Two traps this tool exists to avoid, both paid for on mistertranslation.com
  (2026-09-10, diagnosing the 2026-08-15 cliff):

1. THE DAILY FILE IS NAMED Chart.csv, not Dates.csv, in the UI's CSV export.
   Looking for Dates.csv and finding nothing reads as "no data" when the data
   is right there.

2. GSC's headline "average position" is IMPRESSION-WEIGHTED, so a flood of
   junk deep-tail impressions DRAGS IT DOWN and hides the real number. The
   site's headline read 56.7 while its actual current position was ~7: 7,400
   of 7,785 impressions were page-6-to-9 noise on bare one-word lookups
   ("goshen", "shechem", "soteria") that earned 0 clicks. When that noise
   stopped, the headline barely moved (56.8 -> 54.5) and looked like nothing
   had changed -- but the daily median over the last 10 days was 7.6.
   ⭐ So: read the DAILY series and the per-day position, never the headline
   average, and never conclude "we were demoted" from a weighted mean that a
   vanished impression flood is still dominating.
"""
import csv, io, sys, zipfile
from pathlib import Path

def _rows(src, *names):
    """Yield dict rows from the first matching CSV in a zip or directory."""
    if isinstance(src, zipfile.ZipFile):
        avail = {Path(n).name.lower(): n for n in src.namelist()}
        for want in names:
            hit = avail.get(want.lower())
            if hit:
                raw = src.read(hit).decode("utf-8-sig", "replace")
                return list(csv.DictReader(io.StringIO(raw)))
    else:
        avail = {p.name.lower(): p for p in Path(src).glob("*.csv")}
        for want in names:
            hit = avail.get(want.lower())
            if hit:
                return list(csv.DictReader(
                    io.StringIO(hit.read_text("utf-8-sig", errors="replace"))))
    return []

def _open(p):
    p = Path(p)
    return zipfile.ZipFile(p) if p.suffix.lower() == ".zip" else p

def _num(s):
    s = (s or "").strip().replace("%", "").replace(",", "")
    try:    return float(s)
    except ValueError: return 0.0

def _get(row, *keys):
    """GSC column names vary by locale/report; match loosely."""
    for k in keys:
        for actual in row:
            if actual and actual.strip().lower() == k.lower():
                return row[actual]
    for k in keys:
        for actual in row:
            if actual and k.lower() in actual.strip().lower():
                return row[actual]
    return ""

def summarise(rows, label):
    clicks = sum(_num(_get(r, "Clicks")) for r in rows)
    imps   = sum(_num(_get(r, "Impressions")) for r in rows)
    # Position must be impression-weighted; a plain mean over days is wrong.
    wpos = sum(_num(_get(r, "Position")) * _num(_get(r, "Impressions")) for r in rows)
    pos  = (wpos / imps) if imps else 0.0
    ctr  = (clicks / imps * 100) if imps else 0.0
    print(f"  {label:<22} days={len(rows):<4} clicks={clicks:<7.0f} "
          f"impr={imps:<9.0f} CTR={ctr:.2f}%  avg position={pos:.1f}")
    return {"clicks": clicks, "imps": imps, "ctr": ctr, "pos": pos, "n": len(rows)}

def dates_report(src, split):
    rows = _rows(src, "Dates.csv", "Date.csv", "Chart.csv")
    if not rows:
        print("  !! no Dates.csv in this export "
              "(export the Performance report, not Indexing)")
        return
    for r in rows:
        r["_d"] = (_get(r, "Date") or "").strip()
    rows = [r for r in rows if r["_d"]]
    rows.sort(key=lambda r: r["_d"])
    if not any(_num(_get(r, "Position")) for r in rows):
        print("  !! WARNING: no Position data in this export. Tick 'Average position'")
        print("     in the Performance report before exporting, or every verdict below")
        print("     is meaningless. Re-export and re-run.")
    print(f"\n  range: {rows[0]['_d']} -> {rows[-1]['_d']}  ({len(rows)} days)")
    if split is None:                      # two-export mode: each file IS one window
        return summarise(rows, "window total")
    before = [r for r in rows if r["_d"] < split]
    after  = [r for r in rows if r["_d"] >= split]
    print(f"\n  SPLIT AT {split}\n")
    b = summarise(before, f"before {split}")
    a = summarise(after,  f"on/after {split}")
    if not (b and a and b["n"] and a["n"]):
        return
    print()
    bd = b["imps"] / b["n"]; ad = a["imps"] / a["n"]
    drop = ((ad - bd) / bd * 100) if bd else 0
    print(f"  impressions/day : {bd:.1f}  ->  {ad:.1f}   ({drop:+.1f}%)")
    print(f"  avg position    : {b['pos']:.1f}  ->  {a['pos']:.1f}   "
          f"({a['pos'] - b['pos']:+.1f})")
    print()
    print("  VERDICT:")
    moved = a["pos"] - b["pos"]
    fell = -drop  # percent decline, positive when impressions fell
    if fell > 60 and moved > 8:
        print("   -> RE-RANK. Position collapsed with the impressions. The site was")
        print("      pushed into the tail; zero impressions is the arithmetic result.")
    elif fell > 60 and abs(moved) <= 8:
        print("   -> NOT a re-rank. Position held while impressions died, so the")
        print("      QUERIES went away, not the rankings. Something stopped matching:")
        print("      a query cluster was reallocated, or demand itself vanished.")
        print("      Run the two-export mode to see which queries disappeared.")
    elif fell > 60:
        print("   -> Impressions collapsed while position IMPROVED. Almost always a")
        print("      mix effect: the wide-but-deep queries stopped, leaving a few")
        print("      narrow ones that happen to rank well. Check the query list.")
    else:
        print("   -> No cliff at this split date. Try a different --split.")

def queries_report(before_src, after_src):
    b = _rows(before_src, "Queries.csv", "Query.csv")
    a = _rows(after_src,  "Queries.csv", "Query.csv")
    if not (b and a):
        print("\n  !! need Queries.csv in both exports for the per-query comparison")
        return
    def index(rows):
        out = {}
        for r in rows:
            q = (_get(r, "Top queries", "Query") or "").strip()
            if q:
                out[q] = {"imp": _num(_get(r, "Impressions")),
                          "pos": _num(_get(r, "Position"))}
        return out
    B, A = index(b), index(a)
    both = set(B) & set(A)
    gone = sorted(set(B) - set(A), key=lambda q: -B[q]["imp"])
    print(f"\n  queries: before={len(B)}  after={len(A)}  "
          f"in both={len(both)}  disappeared={len(gone)}")
    if both:
        # The decisive number: for queries present in BOTH windows, did position move?
        wb = sum(B[q]["pos"] * B[q]["imp"] for q in both)
        wa = sum(A[q]["pos"] * A[q]["imp"] for q in both)
        ib = sum(B[q]["imp"] for q in both); ia = sum(A[q]["imp"] for q in both)
        if ib and ia:
            print(f"\n  SURVIVING queries, impression-weighted position: "
                  f"{wb/ib:.1f} -> {wa/ia:.1f}")
            print("   (this is the honest re-rank test -- it holds the query mix fixed)")
    lost = sum(B[q]["imp"] for q in gone)
    tot  = sum(v["imp"] for v in B.values())
    if tot:
        print(f"\n  impressions lost to queries that vanished entirely: "
              f"{lost:.0f} of {tot:.0f}  ({lost/tot*100:.0f}%)")
    if gone:
        print("\n  top queries that disappeared:")
        for q in gone[:15]:
            print(f"    {B[q]['imp']:>7.0f} impr  pos {B[q]['pos']:>5.1f}   {q}")

def main():
    argv = sys.argv[1:]
    split, args, skip = "2026-08-15", [], False
    for i, x in enumerate(argv):
        if skip:
            skip = False
            continue
        if x == "--split" and i + 1 < len(argv):
            split, skip = argv[i + 1], True
        elif x.startswith("--split="):
            split = x.split("=", 1)[1]
        elif not x.startswith("--"):
            args.append(x)
    if not args:
        print(__doc__); sys.exit(1)
    if len(args) == 1:
        print(f"\n=== {args[0]} ===")
        dates_report(_open(args[0]), split)
    else:
        print(f"\n=== BEFORE: {args[0]} ===")
        b = dates_report(_open(args[0]), None)
        print(f"\n=== AFTER: {args[1]} ===")
        a = dates_report(_open(args[1]), None)
        if b and a and b["n"] and a["n"]:
            bd, ad = b["imps"] / b["n"], a["imps"] / a["n"]
            print(f"\n  impressions/day : {bd:.1f}  ->  {ad:.1f}   "
                  f"({(ad - bd) / bd * 100 if bd else 0:+.1f}%)")
            print(f"  avg position    : {b['pos']:.1f}  ->  {a['pos']:.1f}   "
                  f"({a['pos'] - b['pos']:+.1f})")
        queries_report(_open(args[0]), _open(args[1]))
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Accent-insensitive concordance search across the archived Greek New Testament.

The Greek twin of `tools/heb_search.py`. The claims pass in CLAUDE.md says a
corpus claim ("occurs three times in the New Testament", "the only other place")
is guilty until the text is searched, and for the Old Testament that search has
been a command since heb_search.py. For the New Testament it was an ad-hoc
script every time. All 260 chapters of the SBLGNT are already in the archive
(`tools/archive_sources.py`), so the check runs against the text we translate.

Matching is on BARE letters: accents, breathings, iota subscripts, diaeresis
and the SBLGNT's own apparatus sigla (⸀ ⸂ ⸃ ⸁ ⸄ ⸅) are stripped from both the
text and the query, case is folded, and final sigma is folded into sigma — so
`θυρωρος`, `θυρωρός` and `ΘΥΡΩΡΟΣ` are one query.

    python3 tools/grk_search.py θυρωρ                # substring, with refs
    python3 tools/grk_search.py παραδιδ --count      # tally only
    python3 tools/grk_search.py ὄρος --word          # match at a word START only
    python3 tools/grk_search.py αλεκτωρ --book Mark

⚠ Like heb_search.py it matches LETTERS, not lemmas. A stem search catches the
inflected forms that keep the stem and misses the ones that do not (the aorist
of παραδίδωμι is παρέδωκεν/παραδοῖ — search `παραδ` AND `παρεδ`, or pass both
as `παραδ|παρεδ`), and a short stem will hit unrelated words. Read the hits
before quoting a count. The tally is of VERSES, not of occurrences.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_sources import SBLGNT_BOOKS  # noqa: E402
from source_text import fetch, verses  # noqa: E402

# SBLGNT apparatus sigla printed inline in the verse text.
_SIGLA = re.compile(r"[⸀-⸅⸆-⸏]")
_NONWORD = re.compile(r"[^\w\s]", re.UNICODE)


def bare(s: str) -> str:
    """Lowercase Greek letters only: no accents, breathings, sigla or punctuation."""
    s = _SIGLA.sub("", s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().replace("ς", "σ")
    s = s.replace("ʼ", " ").replace("’", " ").replace("'", " ")
    s = _NONWORD.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def chapter_verses(book: str, chapter: int) -> list[tuple[int, str]]:
    raw = fetch(book, chapter, quiet=True)
    out = []
    for line in verses(raw, "sblgnt").split("\n"):
        m = re.match(r"^(\d+)\s+(.*)$", line.strip())
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("query", help="Greek string; accents optional; a|b unions")
    ap.add_argument("--book", help="restrict to one book")
    ap.add_argument("--word", action="store_true",
                    help="match only at the start of a word")
    ap.add_argument("--count", action="store_true", help="tally only")
    args = ap.parse_args()

    needles = [bare(q) for q in args.query.split("|") if bare(q)]
    if not needles:
        print("[grk_search] empty query after stripping", file=sys.stderr)
        return 2

    books = [n_c for _bid, n_c in SBLGNT_BOOKS.items()]
    if args.book:
        want = re.sub(r"[^a-z0-9]", "", args.book.lower())
        books = [(n, c) for n, c in books
                 if re.sub(r"[^a-z0-9]", "", n.lower()) == want]
        if not books:
            print(f"[grk_search] unknown book {args.book!r}", file=sys.stderr)
            return 2

    hits = 0
    for name, n_ch in books:
        for ch in range(1, n_ch + 1):
            try:
                vv = chapter_verses(name, ch)
            except SystemExit:
                print(f"[grk_search] {name} {ch}: not in archive — run "
                      f"tools/archive_sources.py", file=sys.stderr)
                continue
            except Exception:
                continue
            for vno, text in vv:
                b = " " + bare(text)
                if any(((" " + n) if args.word else n) in b for n in needles):
                    hits += 1
                    if not args.count:
                        print(f"{name} {ch}:{vno}  {text}")
    print(f"\n[grk_search] {hits} verse(s) contain {args.query!r}"
          + (f" in {books[0][0]}" if args.book else " in the Greek New Testament"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

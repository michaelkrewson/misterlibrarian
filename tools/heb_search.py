#!/usr/bin/env python3
"""Consonantal concordance search across the archived Masoretic text.

The claims pass in CLAUDE.md says absolutes are guilty until proven — "first",
"only", "never", "the one place" — and that the counter-example must be grepped
before the word is allowed to stand. Until now that meant trusting a web search
or a memory of a lexicon. But `tools/archive_sources.py` already put all 929
chapters of Hebrew on local disk (and in S3), so the check can be run against
the actual text we translate from.

Searches the CONSONANTS: niqqud and cantillation are stripped from both the text
and the query, so a query typed without points still matches pointed text, and
maqaf (־) is treated as a word break like a space.

    python3 tools/heb_search.py חי-אני            # every occurrence, with refs
    python3 tools/heb_search.py זנות --count      # just the tally
    python3 tools/heb_search.py נפל --book Numbers

⚠ It matches letters, not lemmas: a root search will also hit unrelated words
that share the consonants, and a defective/plene spelling difference will miss.
Read the hits before quoting a count — this narrows the search, it is not a
substitute for looking.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_sources import MECHON_BOOKS  # noqa: E402
from source_text import ORIGINALS, fetch, resolve, verses  # noqa: E402

# Hebrew points + cantillation. U+05BE (maqaf) and U+05C0/05C3 (paseq/sof pasuq)
# are separators, not marks, so they are handled apart from this class.
_MARKS = re.compile(r"[֑-ֽֿׁׂׄ-ׇ]")
_SEPS = re.compile(r"[־׀׃\-]+")
_HEB_VERSE = re.compile(r"^([א-ת]{1,4})\s+(.*)$")


def bare(s: str) -> str:
    """Consonants only, separators normalised to single spaces."""
    s = unicodedata.normalize("NFD", s)
    s = _MARKS.sub("", s)
    s = _SEPS.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def chapter_verses(book: str, chapter: int) -> list[tuple[int, str]]:
    """-> [(verse_no, hebrew_text)] for one archived chapter."""
    raw = fetch(book, chapter, quiet=True)
    subdir, _fn, _url = resolve(book, chapter)
    out, n = [], 0
    for line in verses(raw, subdir).split("\n"):
        line = line.strip()
        # Mechon prints the Hebrew line (numbered with a Hebrew letter) then the
        # English (numbered with digits). We want the Hebrew ones.
        if _HEB_VERSE.match(line):
            n += 1
            out.append((n, _HEB_VERSE.match(line).group(2)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("query", help="Hebrew string; points optional")
    ap.add_argument("--book", help="restrict to one book")
    ap.add_argument("--count", action="store_true", help="tally only")
    args = ap.parse_args()

    needle = bare(args.query)
    if not needle:
        print("[heb_search] empty query after stripping points", file=sys.stderr)
        return 2

    books = [(n, c) for _code, (n, c) in MECHON_BOOKS.items()]
    if args.book:
        want = re.sub(r"[^a-z0-9]", "", args.book.lower())
        books = [(n, c) for n, c in books
                 if re.sub(r"[^a-z0-9]", "", n.lower()) == want]
        if not books:
            print(f"[heb_search] unknown book {args.book!r}", file=sys.stderr)
            return 2

    hits = 0
    for name, n_ch in books:
        for ch in range(1, n_ch + 1):
            try:
                vv = chapter_verses(name, ch)
            except SystemExit:
                print(f"[heb_search] {name} {ch}: not in archive — run "
                      f"tools/archive_sources.py", file=sys.stderr)
                continue
            except Exception:
                continue
            for vno, text in vv:
                if needle in bare(text):
                    hits += 1
                    if not args.count:
                        print(f"{name} {ch}:{vno}  {text}")
    print(f"\n[heb_search] {hits} verse(s) contain {args.query!r}"
          + (f" in {books[0][0]}" if args.book else " in the whole Hebrew Bible"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

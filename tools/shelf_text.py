#!/usr/bin/env python3
"""Fetch a shelf version's chapter text, so shelf quotes are READ, not remembered.

Why this exists (Michael, 2026-08-19): the doctrine says "FETCH every shelf
quote you print. Never write one from memory," and "a version's own revision is
a different witness" — but it never said WHERE the NWT comes from, and nothing
in this repo had ever fetched it. `wol.jw.org` returns an empty shell to
WebFetch (its JS chrome loads first), so the NWT was the one shelf version with
no fetch path at all: Numbers 14 shipped with no NWT comparison, and a
web-search snippet offered wording that was almost certainly the 2013 revision
wearing the 1984's name — the exact error the revision rule names.

The page is in fact plain server-rendered HTML. WebFetch was the problem, not
the supplier. A browser User-Agent and a straight GET return the whole chapter.

    python3 tools/shelf_text.py Numbers 14                    # NWT 1984
    python3 tools/shelf_text.py Numbers 14 --verses 8,20-24
    python3 tools/shelf_text.py Numbers 12 --version tnm2019
    python3 tools/shelf_text.py Numbers 12 --all --verses 8   # the whole shelf

THE EDITION GUARD IS THE POINT. Every WOL page names its own publication in the
<article> class ("pub-Rbi8"). We assert that against what was asked for and
refuse to print on a mismatch — so citing the 2013 revision as the 1984 cannot
happen silently, which is the failure this tool was built to end. Verified
against the doctrine's own discriminator: Rbi8 Numbers 12:8 reads "Mouth to
mouth," nwt reads "Face-to-face"; ES Rbi8 "Boca a boca," ES nwt "cara a cara".

WOL also serves the ASV and KJV, which the shelf uses and which have been
misquoted from memory before (the Numbers 10:36 audit). They are here too, so
one command covers most of the shelf.

Storage follows tools/archive_sources.py exactly, because WOL is a SINGLE point
of failure — it is the only fetchable NWT 1984 anywhere I could find, so the day
its markup changes or it goes away, the shelf loses a witness with no substitute:

    local  source/shelf/<loc>-<pub>-<bb>-<ccc>.html.gz   (gitignored)
    S3     blobs/bible_shelf/<same name>                 (private)
    live   wol.jw.org                                    (last resort)

One gzipped artifact serves as both cache and archive — deliberately not two
stores that drift. Gzip is ~7x here (~13 KB/chapter), so all six editions of all
1,189 chapters is ~86 MB.

    python3 tools/shelf_text.py --archive                 # fill the archive
    python3 tools/shelf_text.py --archive --only nwt1984  # one edition
    python3 tools/shelf_text.py --verify                  # re-hash vs manifest

PRIVATE ARCHIVE, like the Hebrew and Greek before it: source/shelf/ is
gitignored (this repo is public) and the bucket is private. The ASV and KJV are
public domain; the NWT/TNM are Watch Tower copyright, and this is a personal
archival copy of pages we already read on their site, quoted in short phrases
and never redistributed — the same posture already taken with Mechon-Mamre,
which also claims copyright on its edition.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MSTR_TRADER = Path.home() / "projects" / "mstr-trader"
S3_CATEGORY = "bible_shelf"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DELAY_S = 1.5

# Imported rather than re-typed: one chapter-count table, not two that drift.
sys.path.insert(0, str(ROOT / "tools"))
from archive_sources import MECHON_BOOKS, SBLGNT_BOOKS  # noqa: E402

# Editions WOL serves, each verified by fetching a discriminating verse.
# (locale, nav root, lang pub, publication symbol, human label, NT-only?)
EDITIONS: dict[str, tuple[str, str, str, str, str, bool]] = {
    "nwt1984":  ("en", "r1", "lp-e", "Rbi8",   "NWT 1984 (Reference Bible)", False),
    "nwt2013":  ("en", "r1", "lp-e", "nwt",    "NWT 2013 revision", False),
    "nwtsty":   ("en", "r1", "lp-e", "nwtsty", "NWT 2013 Study Edition", False),
    "asv":      ("en", "r1", "lp-e", "bi22",   "American Standard Version 1901", False),
    "kjv":      ("en", "r1", "lp-e", "bi10",   "King James Version", False),
    "byington": ("en", "r1", "lp-e", "by",     "Byington, The Bible in Living English", False),
    "int":      ("en", "r1", "lp-e", "int",    "Kingdom Interlinear (Greek NT)", True),
    "tnm1987":  ("es", "r4", "lp-s", "Rbi8",   "TNM 1987 (con referencias)", False),
    "tnm2019":  ("es", "r4", "lp-s", "nwt",    "TNM revision de 2019", False),
}
# What `--all` prints: the shelf versions this project actually cites, both
# languages, each edition alongside its own revision (the rule that a revision
# is a different witness is only checkable if you can see both).
SHELF = ["nwt1984", "nwt2013", "asv", "kjv", "tnm1987", "tnm2019"]

# WOL numbers books in the Christian order. The Hebrew canon order in
# MECHON_BOOKS is NOT that order (Isaiah is 12th there, Chronicles near the
# end), so this list has to exist; chapter counts still come from those tables.
WOL_ORDER = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John",
    "3 John", "Jude", "Revelation",
]


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


_ALIASES = {  # kept in step with tools/source_text.py
    "songofsongs": "songofsolomon", "canticles": "songofsolomon",
    "qoheleth": "ecclesiastes", "1kgs": "1kings", "2kgs": "2kings",
    "1sam": "1samuel", "2sam": "2samuel", "1chron": "1chronicles",
    "2chron": "2chronicles", "psalm": "psalms", "revelations": "revelation",
}
_CHAPTERS = {_norm(n): c for _, (n, c) in MECHON_BOOKS.items()}
_CHAPTERS.update({_norm(n): c for _, (n, c) in SBLGNT_BOOKS.items()})
_NUM = {_norm(n): i + 1 for i, n in enumerate(WOL_ORDER)}
_NT_FROM = _NUM[_norm("Matthew")]

# Fail at import, not mid-chapter, if the order list and the count tables drift.
_missing = [n for n in WOL_ORDER if _norm(n) not in _CHAPTERS]
if _missing:  # pragma: no cover - a wiring bug, not a runtime condition
    raise SystemExit(f"[shelf_text] no chapter count for: {_missing}")


def resolve(book: str, chapter: int) -> tuple[int, str]:
    """-> (WOL book number, canonical name). Raises ValueError on a bad ref."""
    key = _ALIASES.get(_norm(book), _norm(book))
    if key not in _NUM:
        raise ValueError(f"unknown book {book!r}")
    n_ch = _CHAPTERS[key]
    if not 1 <= chapter <= n_ch:
        raise ValueError(f"{book} has {n_ch} chapters; got {chapter}")
    return _NUM[key], WOL_ORDER[_NUM[key] - 1]


def url_for(version: str, book_no: int, chapter: int) -> str:
    loc, root, lp, pub, _label, _nt = EDITIONS[version]
    return f"https://wol.jw.org/{loc}/wol/b/{root}/{lp}/{pub}/{book_no}/{chapter}"


def _archive_root() -> Path:
    """The checkout that actually holds source/shelf/.

    It is gitignored, so it lives only in the MAIN checkout — a git worktree
    sees nothing. Without this every worktree would miss the local archive and
    re-pull from S3 into a directory that gets thrown away. (Same reasoning,
    and same fix, as tools/source_text.py.)
    """
    import subprocess
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        if common:
            main = Path(common).parent
            if (main / "source").is_dir():
                return main
    except Exception:
        pass
    return ROOT


ARCHIVE = _archive_root() / "source" / "shelf"
MANIFEST = ARCHIVE / "MANIFEST.json"


def blob_name(version: str, book_no: int, chapter: int) -> str:
    loc, _root, _lp, pub, _label, _nt = EDITIONS[version]
    return f"{loc}-{pub}-{book_no:02d}-{chapter:03d}.html.gz"


def _cache_path(version: str, book_no: int, chapter: int) -> Path:
    return ARCHIVE / blob_name(version, book_no, chapter)


def _manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _manifest_put(name: str, sha: str) -> None:
    m = _manifest()
    m[name] = sha
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=1, sort_keys=True), encoding="utf-8")


def _s3():
    try:
        sys.path.insert(0, str(MSTR_TRADER))
        import market_data_store as mds  # noqa: PLC0415
        return mds if mds.enabled() else None
    except Exception as exc:
        print(f"[shelf_text] S3 unavailable: {exc}", file=sys.stderr)
        return None


def live_fetch(version: str, book_no: int, chapter: int) -> str:
    """Straight GET with a browser UA. This is the whole trick — the page is
    plain server-rendered HTML; only WebFetch could not see it."""
    url = url_for(version, book_no, chapter)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def store(version: str, book_no: int, chapter: int, raw: str,
          *, push: bool = True) -> str:
    """Write one chapter to the local archive (+ S3). -> sha256 of the gzip."""
    name = blob_name(version, book_no, chapter)
    blob = gzip.compress(raw.encode("utf-8"), 9)
    sha = hashlib.sha256(blob).hexdigest()
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / name).write_bytes(blob)
    _manifest_put(name, sha)
    if push:
        mds = _s3()
        if mds:
            try:
                mds.put_blob(S3_CATEGORY, name, blob, "application/gzip")
            except Exception as exc:  # a dead S3 layer must never be fatal
                print(f"[shelf_text] S3 push failed for {name}: {exc}", file=sys.stderr)
    return sha


def fetch(version: str, book_no: int, chapter: int, *,
          refresh: bool = False, quiet: bool = False,
          allow_live: bool = True) -> str:
    """Archive-first HTML for one chapter: local -> S3 -> live."""
    name = blob_name(version, book_no, chapter)
    path = _cache_path(version, book_no, chapter)
    want = _manifest().get(name)

    if path.exists() and path.stat().st_size > 500 and not refresh:
        blob = path.read_bytes()
        if want and hashlib.sha256(blob).hexdigest() != want:
            print(f"[shelf_text] {name} FAILS its manifest hash — treating the "
                  f"local copy as damaged, restoring from S3", file=sys.stderr)
        else:
            if not quiet:
                print(f"[shelf_text] local archive: {name}", file=sys.stderr)
            return gzip.decompress(blob).decode("utf-8", "replace")

    if not refresh:
        mds = _s3()
        if mds:
            try:
                blob = mds.get_blob(S3_CATEGORY, name)
            except Exception:
                blob = None
            if blob:
                ARCHIVE.mkdir(parents=True, exist_ok=True)
                path.write_bytes(blob)
                if not quiet:
                    print(f"[shelf_text] restored from S3 -> {name}", file=sys.stderr)
                return gzip.decompress(blob).decode("utf-8", "replace")

    if not allow_live:
        raise SystemExit(f"[shelf_text] {name} is not in the archive and S3 could "
                         f"not supply it; re-run with --archive to fill it.")

    if not quiet:
        print(f"[shelf_text] fetch: {url_for(version, book_no, chapter)}", file=sys.stderr)
    raw = live_fetch(version, book_no, chapter)
    store(version, book_no, chapter, raw)
    time.sleep(DELAY_S)  # polite: one supplier, no hurry
    return raw


_VSTART = re.compile(r'<span id="v\d+-\d+-(\d+)-\d+" class="v">')


def parse(s: str) -> tuple[str, dict[int, str]]:
    """-> (publication symbol the PAGE claims, {verse: text}).

    The <article> element holds the verse body and nothing else — WOL's footnote
    and marginal-reference panels sit outside it, so slicing to the article is
    what keeps a footnote's "Lit. 'boca a boca'" from being read as the verse
    (it isn't; the 2019 body reads "cara a cara", and a careless grep says the
    opposite).
    """
    m = re.search(r'<article[^>]*class="([^"]*)"', s)
    pub = "?"
    if m:
        pm = re.search(r"pub-([A-Za-z0-9-]+)", m.group(1))
        if pm:
            pub = pm.group(1)
    start = s.find("<article")
    end = s.find("</article>", start)
    body = s[start:end] if start >= 0 and end > start else s

    marks = list(_VSTART.finditer(body))
    out: dict[int, str] = {}
    for i, mm in enumerate(marks):
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        frag = body[mm.end():stop]
        # Drop the verse-number link and the footnote (*) / cross-ref (+) marks.
        frag = re.sub(r'<a\b[^>]*\bclass="[^"]*\b(?:fn|b|vl)\b[^"]*"[^>]*>.*?</a>',
                      "", frag, flags=re.S)
        txt = html.unescape(re.sub(r"<[^>]+>", "", frag))
        txt = re.sub(r"\s+", " ", txt).strip()
        txt = re.sub(r"^\d+\s*", "", txt)  # a chapter's first verse prints its number
        v = int(mm.group(1))
        # A verse can be split across several spans (poetry, speaker changes).
        out[v] = (out[v] + " " + txt).strip() if v in out else txt
    return pub, out


def chapter(version: str, book: str, ch: int, *, refresh: bool = False,
            quiet: bool = False) -> dict[int, str]:
    """Verse text for one chapter, with the edition guard enforced."""
    book_no, name = resolve(book, ch)
    loc, _root, _lp, pub, label, nt_only = EDITIONS[version]
    if nt_only and book_no < _NT_FROM:
        raise SystemExit(f"[shelf_text] {label} covers the NT only; {name} is not in it")

    raw = fetch(version, book_no, ch, refresh=refresh, quiet=quiet)
    got, verses = parse(raw)
    if got != pub:
        # The whole reason this tool exists. Never print text we cannot name.
        raise SystemExit(
            f"[shelf_text] EDITION MISMATCH — asked for {version} (pub-{pub}, "
            f"{label}) but the page returned pub-{got}.\n"
            f"  Refusing to print: quoting one edition under another's name is "
            f"the error this guard exists to prevent.\n"
            f"  {url_for(version, book_no, ch)}"
        )
    if not verses:
        raise SystemExit(f"[shelf_text] no verses parsed from {url_for(version, book_no, ch)} "
                         f"— WOL's markup may have changed; fix parse() before quoting")
    return verses


def archive_all(versions: list[str], *, push: bool = True,
                books: list[int] | None = None) -> dict:
    """Fill the archive, one chapter at a time. Idempotent and resumable:
    a chapter already on disk is skipped, so an interrupted run just resumes."""
    stats = {"fetched": 0, "skipped": 0, "failed": 0}
    for ver in versions:
        _l, _r, _p, pub, label, nt_only = EDITIONS[ver]
        for book_no, name in enumerate(WOL_ORDER, start=1):
            if books and book_no not in books:
                continue
            if nt_only and book_no < _NT_FROM:
                continue
            for ch in range(1, _CHAPTERS[_norm(name)] + 1):
                path = _cache_path(ver, book_no, ch)
                if path.exists() and path.stat().st_size > 500:
                    stats["skipped"] += 1
                    continue
                try:
                    raw = live_fetch(ver, book_no, ch)
                    got, verses = parse(raw)
                    if got != pub:
                        print(f"[shelf_text] {ver} {name} {ch}: EDITION MISMATCH "
                              f"(wanted pub-{pub}, got pub-{got}) — not stored",
                              file=sys.stderr)
                        stats["failed"] += 1
                    elif not verses:
                        print(f"[shelf_text] {ver} {name} {ch}: no verses parsed "
                              f"— not stored", file=sys.stderr)
                        stats["failed"] += 1
                    else:
                        store(ver, book_no, ch, raw, push=push)
                        stats["fetched"] += 1
                        if stats["fetched"] % 25 == 0:
                            print(f"[shelf_text] {ver}: {name} {ch} "
                                  f"({stats['fetched']} fetched, "
                                  f"{stats['skipped']} already had)", file=sys.stderr)
                except Exception as exc:
                    print(f"[shelf_text] {ver} {name} {ch}: {exc}", file=sys.stderr)
                    stats["failed"] += 1
                time.sleep(DELAY_S)
        print(f"[shelf_text] {label}: {stats}", file=sys.stderr)
    return stats


def verify(*, spot_check_s3: bool = True) -> int:
    """Re-hash every local file against MANIFEST.json. -> count of bad files."""
    man = _manifest()
    bad = 0
    for name, want in sorted(man.items()):
        path = ARCHIVE / name
        if not path.exists():
            print(f"  MISSING  {name}")
            bad += 1
            continue
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            print(f"  DAMAGED  {name} (have {got[:12]}, want {want[:12]})")
            bad += 1
    print(f"[shelf_text] {len(man) - bad}/{len(man)} local files match the manifest")
    if spot_check_s3 and man:
        mds = _s3()
        if mds:
            name = sorted(man)[0]
            blob = mds.get_blob(S3_CATEGORY, name)
            ok = bool(blob) and hashlib.sha256(blob).hexdigest() == man[name]
            print(f"[shelf_text] S3 round-trip on {name}: {'OK' if ok else 'MISMATCH'}")
    return bad


def _want(spec: str | None, have: list[int]) -> list[int]:
    if not spec:
        return have
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("book", nargs="?")
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--version", default="nwt1984", choices=sorted(EDITIONS),
                    help="default: nwt1984, the shelf's NWT")
    ap.add_argument("--all", action="store_true",
                    help=f"print the whole shelf: {', '.join(SHELF)}")
    ap.add_argument("--verses", help="e.g. 8 or 8,20-24 (default: whole chapter)")
    ap.add_argument("--refresh", action="store_true", help="ignore the archive")
    ap.add_argument("--archive", action="store_true",
                    help="fill the local+S3 archive (idempotent, resumable)")
    ap.add_argument("--only", help="comma-separated versions for --archive")
    ap.add_argument("--no-push", action="store_true", help="--archive: skip S3")
    ap.add_argument("--verify", action="store_true",
                    help="re-hash the local archive against MANIFEST.json")
    args = ap.parse_args()

    if args.verify:
        raise SystemExit(1 if verify() else 0)
    if args.archive:
        vers = [v.strip() for v in args.only.split(",")] if args.only else SHELF
        unknown = [v for v in vers if v not in EDITIONS]
        if unknown:
            raise SystemExit(f"[shelf_text] unknown version(s): {unknown}")
        books = None
        if args.book:
            books = [resolve(args.book, 1)[0]]
        archive_all(vers, push=not args.no_push, books=books)
        return
    if not args.book or args.chapter is None:
        ap.error("book and chapter are required unless --archive/--verify")

    try:
        book_no, name = resolve(args.book, args.chapter)
    except ValueError as exc:
        raise SystemExit(f"[shelf_text] {exc}")

    versions = SHELF if args.all else [args.version]
    for i, ver in enumerate(versions):
        _l, _r, _p, pub, label, nt_only = EDITIONS[ver]
        if nt_only and book_no < _NT_FROM:
            continue
        verses = chapter(ver, args.book, args.chapter, refresh=args.refresh)
        if i:
            print()
        print(f"=== {label}  [{ver} / pub-{pub}] ===")
        print(f"# {url_for(ver, book_no, args.chapter)}")
        print(f"# {name} {args.chapter} — {len(verses)} verses parsed")
        for v in _want(args.verses, sorted(verses)):
            print(f"{v}: {verses.get(v, '(no such verse in this edition)')}")


if __name__ == "__main__":
    main()

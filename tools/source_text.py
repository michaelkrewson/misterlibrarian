#!/usr/bin/env python3
"""Serve a chapter's ORIGINAL-LANGUAGE source text from our own archive.

Why this exists (Michael, 2026-08-18): every chapter so far started by curl-ing
Mechon-Mamre live, one chapter at a time, even though `tools/archive_sources.py`
had already mirrored all 1,189 chapters of the Hebrew and Greek to local disk
AND to private S3 months earlier. Hitting a third-party supplier for a file we
already own is slower, ruder, and quietly fragile: the day Mechon-Mamre goes
down or changes its markup, the chapter stalls for no reason.

This module is the enforcement. It makes the archive the path of LEAST
resistance, so reaching for the live site takes deliberate effort:

    python3 tools/source_text.py Numbers 14          # clean verse text
    python3 tools/source_text.py Numbers 14 --raw    # the archived HTML/JSON
    python3 tools/source_text.py John 3              # Greek works the same way

Resolution order, and it never silently degrades:
  1. local  source/originals/<mechon|sblgnt>/<file>   (verified against MANIFEST)
  2. S3     blobs/bible_sources/<subdir>-<file>       (restores the local copy)
  3. live   upstream -- ONLY with --allow-live, and it says so on stderr

A local file whose sha256 disagrees with MANIFEST.json is treated as damaged:
we re-restore from S3 rather than translate from a corrupted scroll. That check
is the whole reason the manifest exists, and nothing was reading it before.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _archive_root() -> Path:
    """The checkout that actually holds source/originals/.

    That directory is gitignored, so it exists only in the MAIN checkout — a
    git worktree sees nothing. Without this, every worktree would miss the
    local archive, silently skip the manifest hash check, and re-pull all
    1,189 files from S3 into a directory that gets thrown away.
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


ARCHIVE_ROOT = _archive_root()
ORIGINALS = ARCHIVE_ROOT / "source" / "originals"
MANIFEST = ORIGINALS / "MANIFEST.json"
MSTR_TRADER = Path.home() / "projects" / "mstr-trader"
S3_CATEGORY = "bible_sources"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Imported rather than re-typed: one book table, not two that can drift.
sys.path.insert(0, str(ROOT / "tools"))
from archive_sources import MECHON_BOOKS, SBLGNT_BOOKS  # noqa: E402


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


_MECHON_BY_NAME = {_norm(n): (code, ch) for code, (n, ch) in MECHON_BOOKS.items()}
_SBLGNT_BY_NAME = {_norm(n): (bid, ch) for bid, (n, ch) in SBLGNT_BOOKS.items()}
# The few names a human actually types that don't match the table verbatim.
_ALIASES = {
    "songofsongs": "songofsolomon", "canticles": "songofsolomon",
    "qoheleth": "ecclesiastes", "1kgs": "1kings", "2kgs": "2kings",
    "1sam": "1samuel", "2sam": "2samuel", "1chron": "1chronicles",
    "2chron": "2chronicles", "psalm": "psalms", "revelations": "revelation",
}


def resolve(book: str, chapter: int) -> tuple[str, str, str]:
    """-> (subdir, filename, upstream_url). Raises ValueError on a bad ref."""
    key = _norm(book)
    key = _ALIASES.get(key, key)
    if key in _MECHON_BY_NAME:
        code, n_ch = _MECHON_BY_NAME[key]
        if not 1 <= chapter <= n_ch:
            raise ValueError(f"{book} has {n_ch} chapters; got {chapter}")
        fn = f"pt{code}{chapter:02d}.htm"
        return "mechon", fn, f"https://mechon-mamre.org/p/pt/{fn}"
    if key in _SBLGNT_BY_NAME:
        bid, n_ch = _SBLGNT_BY_NAME[key]
        if not 1 <= chapter <= n_ch:
            raise ValueError(f"{book} has {n_ch} chapters; got {chapter}")
        # NB: hyphenated — JHN-03.json, not JHN03.json. Checked against the
        # real archive, not assumed; the Hebrew side has no hyphen.
        fn = f"{bid}-{chapter:02d}.json"
        return "sblgnt", fn, f"https://bible.helloao.org/api/grc_sbl/{bid}/{chapter}.json"
    raise ValueError(f"unknown book {book!r}")


def _manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _expected_sha(subdir: str, fn: str) -> str | None:
    entry = _manifest().get(f"{subdir}/{fn}")
    if isinstance(entry, dict):
        return entry.get("sha256")
    return entry if isinstance(entry, str) else None


def _from_s3(subdir: str, fn: str) -> bytes | None:
    try:
        sys.path.insert(0, str(MSTR_TRADER))
        import market_data_store as mds  # noqa: PLC0415
        if not mds.enabled():
            return None
        return mds.get_blob(S3_CATEGORY, f"{subdir}-{fn}")
    except Exception as exc:  # a dead S3 layer must never be fatal
        print(f"[source_text] S3 unavailable: {exc}", file=sys.stderr)
        return None


def fetch(book: str, chapter: int, *, allow_live: bool = False,
          quiet: bool = False) -> bytes:
    """Archive-first bytes for one chapter. Live only on explicit opt-in."""
    subdir, fn, url = resolve(book, chapter)
    path = ORIGINALS / subdir / fn
    want = _expected_sha(subdir, fn)

    if path.exists() and path.stat().st_size > 100:
        raw = path.read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if want and got != want:
            print(f"[source_text] {subdir}/{fn} FAILS its manifest hash — "
                  f"treating the local copy as damaged, restoring from S3",
                  file=sys.stderr)
        else:
            if not quiet:
                print(f"[source_text] local archive: {subdir}/{fn}", file=sys.stderr)
            return raw

    blob = _from_s3(subdir, fn)
    if blob:
        got = hashlib.sha256(blob).hexdigest()
        if want and got != want:
            print(f"[source_text] WARNING: S3 copy of {subdir}/{fn} also "
                  f"disagrees with MANIFEST.json (have {got[:12]}, "
                  f"want {want[:12]})", file=sys.stderr)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        if not quiet:
            print(f"[source_text] restored from S3 -> {subdir}/{fn}", file=sys.stderr)
        return blob

    if not allow_live:
        raise SystemExit(
            f"[source_text] {subdir}/{fn} is not in the local archive and could "
            f"not be restored from S3.\n"
            f"  This is the point where earlier sessions quietly curl-ed the "
            f"supplier instead.\n"
            f"  Re-run `python3 tools/archive_sources.py` to repair the archive, "
            f"or pass --allow-live if you truly need {url} right now."
        )

    print(f"[source_text] LIVE FETCH (archive missed): {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    print(f"[source_text] wrote {subdir}/{fn} — run archive_sources.py to "
          f"re-manifest and push it to S3", file=sys.stderr)
    return raw


def verses(raw: bytes, subdir: str) -> str:
    """Readable verse text out of an archived page."""
    if subdir == "sblgnt":
        data = json.loads(raw.decode("utf-8"))
        out = []
        for c in data.get("chapter", {}).get("content", []):
            if c.get("type") != "verse":
                continue
            parts = [p for p in c.get("content", []) if isinstance(p, str)]
            out.append(f"{c.get('number')} {' '.join(parts)}")
        return "\n".join(out)

    t = raw.decode("utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>", "", t, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</p>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    # Drop Mechon-Mamre's own chrome, keep the Hebrew/English verse pairs.
    drop = ("requires Javascript", "דורש Javascript")
    return "\n".join(l for l in lines if not any(d in l for d in drop))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("book")
    ap.add_argument("chapter", type=int)
    ap.add_argument("--raw", action="store_true", help="print the archived file itself")
    ap.add_argument("--allow-live", action="store_true",
                    help="permit an upstream fetch if the archive misses")
    args = ap.parse_args()

    try:
        subdir, _fn, _url = resolve(args.book, args.chapter)
    except ValueError as exc:
        print(f"[source_text] {exc}", file=sys.stderr)
        return 2
    raw = fetch(args.book, args.chapter, allow_live=args.allow_live)
    sys.stdout.write(raw.decode("utf-8", errors="replace") if args.raw
                     else verses(raw, subdir) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Fetch the BibleGateway-only shelf versions for one chapter into the JSON
shape tools/shelf_check.py expects (<NAME>.json, keyed by verse number).

    python3 tools/fetch_shelf_bg.py Deuteronomy 14 source/shelf/d14
    python3 tools/shelf_check.py <fragment> --book Deuteronomy --chapter 14 \
            --shelf-dir source/shelf/d14

WHY THIS EXISTS. tools/shelf_text.py covers the six versions WOL serves (NWT
1984/2013, TNM 1987/2019, ASV, KJV) and is archive-first, so those are cheap and
durable. The other seven on the two shelves -- NIV, TLB, Geneva, Douay, RV 1909,
RV60, NVI -- had NO fetch path in this repo at all. shelf_check.py has always
accepted a --shelf-dir of their text, but nothing in the repo produced one, so in
practice they were either quoted from memory (the documented failure the whole
shelf rule exists to stop) or reported NO DATA, which shelf_check counts as a
defect precisely because it means the claim rests on memory.

It earned its place immediately: on Deuteronomy 14 the fetched text caught six
wrong shelf claims of mine before they shipped -- three in the Spanish notes
(including a Reina-Valera reading attributed to the wrong edition), an ASV
rendering of 'at the end of every three years' I had recorded as the KJV's bare
form, a 'hoopoe is unanimous' claim that two versions refute, and two quotes that
had picked up a definite article the versions do not print.

CACHING. The raw HTML is kept per version alongside the JSON, so a re-run of the
same chapter costs no network -- delete the _raw_*.html files to force a refetch.
Output goes under source/shelf/, which is gitignored: these are third-party
copyrighted translations, fetched on demand and quoted in short phrases only,
exactly as tools/shelf_text.py treats the WOL versions. Never commit them.

⚠ TWO PARSING TRAPS, both paid for. BibleGateway writes most verse spans as
<span id="en-NIV-5293" class="text Deut-14-2">, so the class is NOT the first
attribute -- requiring it to be matched 3 of one chapter's 29 verses and silently
dropped the rest. And BG tags its editorial section headings ("Clean and Unclean
Food") with the number of the verse they precede, so an unstripped <h3> lands
inside that verse as words no version actually prints there.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

VERSIONS = ["NIV", "TLB", "GNV", "DRA", "RVA", "RVR1960", "NVI"]

BOOK_ABBR = {"Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev",
             "Numbers": "Num", "Deuteronomy": "Deut", "Joshua": "Josh",
             "Judges": "Judg", "Ruth": "Ruth", "Psalms": "Ps"}


def _verse_spans(seg, abbr, chapter):
    """Collect every span for each verse, walking nesting by hand.

    A non-greedy regex truncates at the first </span>, which for any verse
    carrying inline markup (italics for supplied words -- endemic in the KJV
    line, and in Geneva especially) silently keeps only the opening fragment.
    """
    verses = {}
    # BG writes most verse spans as <span id="en-NIV-5293" class="text Deut-14-2">,
    # so the class cannot be assumed to be the first attribute -- requiring that
    # matched 3 of this chapter's 29 verses and silently dropped the rest.
    opener = re.compile(r'<span[^>]*class="text %s-%d-(\d+)"' % (re.escape(abbr), chapter))
    for mm in opener.finditer(seg):
        v = mm.group(1)
        start = seg.find(">", mm.end()) + 1
        depth, i = 1, start
        while i < len(seg) and depth > 0:
            nxt_open = seg.find("<span", i)
            nxt_close = seg.find("</span", i)
            if nxt_close == -1:
                break
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                i = nxt_open + 5
            else:
                depth -= 1
                i = nxt_close + 6
        verses.setdefault(v, []).append(seg[start:max(start, i - 6)])
    return verses


def _clean(t):
    # Drop cross-reference and footnote superscripts BEFORE stripping tags,
    # or their letters glue onto the adjacent word and a verbatim quote misses.
    t = re.sub(r'<sup[^>]*>.*?</sup>', " ", t, flags=re.S)
    t = re.sub(r'<[^>]+>', " ", t)
    t = html.unescape(t)
    return re.sub(r'\s+', " ", t).strip()


def fetch(book, chapter, version, outdir, refresh=False):
    raw_path = os.path.join(outdir, "_raw_%s_%d.html" % (version, chapter))
    if os.path.exists(raw_path) and not refresh:
        h = open(raw_path, encoding="utf-8", errors="replace").read()
    else:
        url = ("https://www.biblegateway.com/passage/?search=%s&version=%s"
               % (urllib.parse.quote("%s %d" % (book, chapter)), version))
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
        open(raw_path, "w", encoding="utf-8").write(h)
        time.sleep(2.0)  # be a polite guest

    m = re.search(r'class="passage-text"(.*?)<div class="footnotes"', h, re.S) \
        or re.search(r'class="passage-text"(.*)', h, re.S)
    seg = m.group(1) if m else h
    # BG tags its editorial section headings ("Clean and Unclean Food") with the
    # verse number they precede, so an unstripped <h3> lands inside that verse's
    # text as words no version actually prints there.
    seg = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', " ", seg, flags=re.S)

    abbr = BOOK_ABBR.get(book, book[:4])
    out = {}
    for v, chunks in _verse_spans(seg, abbr, chapter).items():
        t = _clean(" ".join(chunks))
        if t:
            out[v] = t

    # A merging version (The Living Bible) is tagged only on the FIRST verse of
    # each run, so the rest of the run sits in no span at all and would vanish
    # from the dump -- and shelf_check.py's whole-chapter fallback, which exists
    # for exactly this case, would then be searching a chapter with holes in it.
    # Keep the entire passage under a non-numeric key: shelf_pool() only reads
    # numeric verses, so per-verse precision is untouched, and the fallback
    # becomes honest.
    whole = _clean(seg)
    if whole:
        out["_whole"] = whole

    json.dump(out, open(os.path.join(outdir, "%s.json" % version), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    book, chapter, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    only = sys.argv[4].split(",") if len(sys.argv) > 4 else VERSIONS
    os.makedirs(outdir, exist_ok=True)
    for ver in only:
        try:
            d = fetch(book, chapter, ver, outdir)
            print("%-8s %2d verses | v1: %s" % (ver, len(d), (d.get("1", "") or "")[:78]))
        except Exception as e:
            print("%-8s FAILED: %s" % (ver, e))

# -*- coding: utf-8 -*-
"""Re-run a chapter's CORPUS-COUNT claims against the archived Hebrew.

    python3 tools/count_check.py source/shelf/d15_en.html

WHY THIS EXISTS. `shelf_check.py` verifies quoted PHRASES; `validate_chapter.py`
verifies LINKS; `twin_diff.py` verifies the two languages against each other.
None of them reads a number. So a sentence like "the word stands in five verses
of the Hebrew Bible and all five are in Deuteronomy" is invisible to every
automated check in this project, and that class has now shipped four times:

  * Deuteronomy 14  "sarat describes cutting flesh in only two verses" -- a third
    hit was in the search output on composition day and silently dropped.
  * Deuteronomy 14  Dishon's second occurrence undercounted the same way.
  * Deuteronomy 15  "'your eye shall not pity' is a formula of this book and of
    no other" -- five verses, all Deuteronomy, TRUE of the two-word string I
    searched; the head word alone stands in eleven, five of them Ezekiel saying
    the identical thing of God's eye. The count was right and the claim was not.

⭐ THE POINT IS THE FOURTH ONE, because it is the one a naive re-run would miss.
Re-running the author's own query reproduces the author's own number. So this
tool does TWO things: it re-runs the query, and -- when the query is more than
one word -- it ALSO runs the head word alone and reports the wider count. A
claim resting on a narrow string while the prose talks about "the word" or "the
formula" is the failure mode, and the two numbers side by side are what expose it.

HOW A CLAIM DECLARES ITSELF. The sentence must carry the Hebrew it counted, in a
`data-heb` attribute on any element inside it:

    the root <em data-heb="שמט">shamat</em> stands in <strong>eleven verses</strong>

The attribute is invisible to the reader and lives in the sentence that makes the
claim, so it cannot drift from it the way a sidecar file would. Recording the
string costs nothing at composition time -- the search has already been run.

FAILS SAFE. Anything the tool cannot resolve is reported UNVERIFIED, never as a
failure: an unparseable number, a missing archive chapter, a scope it does not
recognise. The only non-zero exit is a claim whose own declared query disagrees
with the archive.

⚠ WHAT IT DOES NOT DO, deliberately. It does not check a tally of shelf versions
against an enumeration ("Nine pluralise it (...eight named...)"). That was
measured and dropped: English enumerates versions in too many shapes -- a group
count governing a parenthetical, an out-of-group version named in the same
sentence, prose standing in for two more ("both later revisions") -- and a
sentence-scoped tag count produced two false positives and no true ones on a
chapter that HAD the defect. A checker that cannot separate its true positives
from its false ones is the cry-wolf failure this project already documents.
Counting an enumeration stays a human step on the checklist.
"""
from __future__ import annotations

import html
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heb_search as HS  # noqa: E402

WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "twenty-one": 21, "twenty-two": 22,
    "twenty-three": 23, "twenty-four": 24, "twenty-five": 25, "twenty-six": 26,
    # Spanish, for the twin
    "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
    "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
    "trece": 13, "catorce": 14, "quince": 15, "dieciséis": 16, "dieciseis": 16,
    "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20,
}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
        "seventy": 70, "eighty": 80, "ninety": 90,
        "veinti": 20, "treinta": 30, "cuarenta": 40}


def as_number(tok: str):
    """one / twenty-six / veintiséis / 26 -> int, else None.

    A hand-kept table is not a number parser: bumping a claim from twenty-six to
    twenty-seven fell straight out of the first version's dict and the claim
    silently degraded from CHECKED to UNVERIFIED. Compounds are composed here so
    the space is actually covered.
    """
    if tok is None:
        return None
    t = tok.strip().lower().replace("\u2011", "-")
    if t.isdigit():
        return int(t)
    if t in WORDS:
        return WORDS[t]
    if "-" in t:
        a, _, b = t.partition("-")
        if a in TENS and b in WORDS and WORDS[b] < 10:
            return TENS[a] + WORDS[b]
    if t in TENS:
        return TENS[t]
    flat = "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")
    if flat in WORDS:
        return WORDS[flat]
    for pre, base in (("veinti", 20), ("treinta y ", 30), ("cuarenta y ", 40)):
        if flat.startswith(pre):
            rest = flat[len(pre):]
            if rest in WORDS and WORDS[rest] < 10:
                return base + WORDS[rest]
    return None

TORAH = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

# Spanish book names, so the TWIN's claims are checked too. The Spanish page says
# "de Deuteronomio" where the English says "of Deuteronomy", and a checker that
# reads only English leaves half of every chapter unchecked.
ES_BOOKS = {
    "Genesis": "Genesis", "Exodo": "Exodus", "Levitico": "Leviticus",
    "Numeros": "Numbers", "Deuteronomio": "Deuteronomy", "Josue": "Joshua",
    "Jueces": "Judges", "1 Samuel": "1 Samuel", "2 Samuel": "2 Samuel",
    "1 Reyes": "1 Kings", "2 Reyes": "2 Kings", "Isaias": "Isaiah",
    "Jeremias": "Jeremiah", "Ezequiel": "Ezekiel", "Oseas": "Hosea",
    "Joel": "Joel", "Amos": "Amos", "Abdias": "Obadiah", "Jonas": "Jonah",
    "Miqueas": "Micah", "Nahum": "Nahum", "Habacuc": "Habakkuk",
    "Sofonias": "Zephaniah", "Hageo": "Haggai", "Zacarias": "Zechariah",
    "Malaquias": "Malachi", "1 Cronicas": "1 Chronicles",
    "2 Cronicas": "2 Chronicles", "Salmos": "Psalms", "Job": "Job",
    "Proverbios": "Proverbs", "Rut": "Ruth",
    "Cantar de los Cantares": "Song of Solomon", "Eclesiastes": "Ecclesiastes",
    "Lamentaciones": "Lamentations", "Ester": "Esther", "Daniel": "Daniel",
    "Esdras": "Ezra", "Nehemias": "Nehemiah",
}


def _deaccent(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def _book_alternation() -> str:
    """Every archived book name, English and Spanish, LONGEST FIRST.

    Longest-first is load-bearing: without it a future bare "Samuel" would
    shadow "1 Samuel", and "Cantar de los Cantares" would be cut at "Cantar".
    """
    names = [nm for _c, (nm, _ch) in HS.MECHON_BOOKS.items()] + list(ES_BOOKS)
    return "|".join(re.escape(x) for x in sorted(set(names), key=len, reverse=True))


BOOK_RE = _book_alternation()

# Normalised lookup: accent- and case-insensitive, either language -> the English
# name the archive indexes by. A .title() pass was tried first and mangled both
# "Song of Solomon" and "Cantar de los Cantares"; a dict cannot.
_BOOK_LOOKUP = {}
for _nm in [nm for _c, (nm, _ch) in HS.MECHON_BOOKS.items()]:
    _BOOK_LOOKUP[_deaccent(_nm).lower()] = _nm
for _es, _en in ES_BOOKS.items():
    _BOOK_LOOKUP[_deaccent(_es).lower()] = _en

# The trigger. A corpus-count claim names a SCOPE -- that is what makes it a
# claim about the whole text rather than about this chapter.
SCOPE_PATTERNS = [
    (r"of the Hebrew Bible|in the Hebrew Bible|in the whole Bible|in the Bible"
     r"|across the whole text|de la Biblia hebrea|en toda la Biblia", "bible"),
    (r"in the Torah|(?:across|in) the whole Torah|en (?:toda )?la Tor[aá]", "torah"),
    (r"in this book|en este libro", "book"),
    # A NAMED book: "stands in seventeen verses OF DEUTERONOMY". Deliberately
    # LAST -- a sentence reading "nine verses of the Hebrew Bible, all nine in
    # Deuteronomy" is a claim about the BIBLE, and the wider scope must win.
    # The negative lookahead is what makes this safe rather than noisy: "of
    # Deuteronomy," is a SCOPE, "at Deuteronomy 19:15" is a CITATION, and only a
    # following digit tells them apart.
    (r"(?:of|in|de|en)\s+(?:the\s+book\s+of\s+)?(?P<book>" + BOOK_RE
     + r")\b(?!\s*\d)", "named"),
]
COUNTING = (r"stands? in|occurs? in|appears? in|est[aá]n? en|aparecen? en"
            r"|nowhere else|ning[uú]n otro|the only|la [uú]nica|el [uú]nico")

NUM = r"(?:\d+|[^\W\d_]+(?:-[^\W\d_]+)?)"   # \w minus digits: keeps á é í ó ú ñ
# The number must be the one the CLAIM VERB governs. Taking the first "N verses"
# in the sentence read "the two verses that hold it" as the count for a claim
# that said six, and reported a mismatch that was the tool's and not the text's.
COUNT_NEAR = re.compile(
    r"(?:%s)\s+(?:\w+\s+){0,3}?(?:exactly\s+|only\s+|exactamente\s+|s[oó]lo\s+|solamente\s+)?(%s)\s+(?:\w+\s+){0,2}?"
    r"(?:verses?|vers[ií]culos?)\b" % (COUNTING, NUM), re.I)


def plain(chunk: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", chunk))


def strip_with_map(raw: str):
    """Plain text plus, for each plain character, its offset in the raw HTML.

    Sentence-splitting the RAW string was the first version and it was wrong
    twice in one run: a period followed by </strong> is not a boundary the split
    could see, so two sentences merged and the checker compared a claim's number
    against a different sentence's number. Working on plain text with an offset
    map back removes the whole class.
    """
    out, idx, i, n = [], [], 0, len(raw)
    while i < n:
        if raw[i] == "<":
            j = raw.find(">", i)
            if j == -1:
                break
            out.append(" ")
            idx.append(i)
            i = j + 1
            continue
        if raw[i] == "&":
            j = raw.find(";", i)
            if j != -1 and j - i <= 10:
                out.append(html.unescape(raw[i:j + 1]))
                idx.extend([i] * len(html.unescape(raw[i:j + 1])))
                i = j + 1
                continue
        out.append(raw[i])
        idx.append(i)
        i += 1
    return "".join(out), idx


def sentence_bounds(text: str, at: int):
    """Plain-text span of the sentence containing offset `at`."""
    start = max(text.rfind(". ", 0, at), text.rfind("; ", 0, at)) + 1
    nxt = min([p for p in (text.find(". ", at), text.find("; ", at)) if p != -1]
              or [len(text)])
    return max(start, 0), nxt + 1


def scope_of(text: str):
    """Which corpus the claim is about -- the scope phrase is the trigger.

    A named book comes back as "named:<English book>", so the caller needs no
    second return value and the scope prints itself in the report.
    """
    for pat, name in SCOPE_PATTERNS:
        m = re.search(pat, text, re.I)
        if not m:
            continue
        if name != "named":
            return name
        en = _BOOK_LOOKUP.get(_deaccent(m.group("book")).lower())
        if not en:
            return None
        return "named:" + en
    return None


_CORPUS: dict = {}


def _books_for(scope: str, book_hint: str | None):
    if scope.startswith("named:"):
        return [scope.split(":", 1)[1]]
    if scope == "torah":
        return TORAH
    if scope == "book":
        return [book_hint] if book_hint else []
    return [n for _c, (n, _ch) in HS.MECHON_BOOKS.items()]


def verse_count(needle: str, books) -> int | None:
    """Archived verses containing this consonantal string. None on any doubt.

    `a|b` is a UNION, counted once per verse: a word written both defectively and
    plene ("shephayim" as שפים and שפיים) is one claim and two searches, and
    summing them would double-count a verse carrying both.
    """
    alts = [HS.bare(x) for x in needle.split("|") if HS.bare(x)]
    if not alts:
        return None
    total = 0
    for name in books:
        n_ch = dict((n, c) for _code, (n, c) in HS.MECHON_BOOKS.items()).get(name)
        if not n_ch:
            return None
        for ch in range(1, n_ch + 1):
            key = (name, ch)
            if key not in _CORPUS:
                try:
                    _CORPUS[key] = [HS.bare(t) for _v, t in HS.chapter_verses(name, ch)]
                except BaseException:
                    return None
            total += sum(1 for t in _CORPUS[key] if any(a in t for a in alts))
    return total


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().split("\n\n")[1])
        return 2
    path = sys.argv[1]
    frag = open(path, encoding="utf-8").read()
    book_hint = None
    m = re.search(r'id="chapter-([a-z]+)\d+"', frag)
    if m:
        book_hint = {"deut": "Deuteronomy", "gen": "Genesis", "exod": "Exodus",
                     "lev": "Leviticus", "num": "Numbers"}.get(m.group(1))

    checked = unverified = failed = narrower = byhand = 0
    lines = []
    for para in re.findall(r"<p>(.*?)</p>", frag, re.S):
        text, idx = strip_with_map(para)
        seen = set()
        for m in re.finditer(COUNTING, text, re.I):
            lo, hi = sentence_bounds(text, m.start())
            if (lo, hi) in seen:
                continue
            sent = text[lo:hi]
            scope = scope_of(sent)
            if not scope:
                continue
            raw_sent = para[idx[lo]:(idx[hi - 1] if hi - 1 < len(idx) else len(para))]
            read = re.findall(r'data-heb-read="([^"]+)"', raw_sent)
            heb = re.findall(r'data-heb="([^"]+)"', raw_sent)
            snippet = re.sub(r"\s+", " ", sent).strip()[:110]
            if any(snippet in ln for ln in lines):
                continue
            if read and not heb:
                # Declared as counted by READING the hits, because the consonants
                # also spell unrelated words (shephi returns 55 verses; nine are
                # the word). Report the gap; never fail on it.
                # ⚠ This whole block used to sit one indent level out, so it ran
                # for EVERY claim and reached read[0] with `read` empty -- an
                # IndexError that killed the checker mid-file on 11 of 604
                # shipped pages, whose claims were therefore never checked.
                stated = None
                for cand in COUNT_NEAR.finditer(sent):
                    stated = as_number(cand.group(1))
                    if stated is not None:
                        break
                got = verse_count(read[0], _books_for(scope, book_hint))
                byhand += 1
                lines.append("  ~ BY HAND     claims %s; the bare string %r matches %s "
                             "verse(s) -- counted by reading, not by matching :: %s"
                             % (stated, read[0], got, snippet))
                continue
            if not heb:
                unverified += 1
                lines.append("  ? UNVERIFIED  no data-heb on this claim :: %s" % snippet)
                continue
            stated = None
            for cand in COUNT_NEAR.finditer(sent):
                stated = as_number(cand.group(1))
                if stated is not None:
                    break
            if stated is None:
                unverified += 1
                lines.append("  ? UNVERIFIED  no parseable verse count :: %s" % snippet)
                continue
            books = _books_for(scope, book_hint)
            got = verse_count(heb[0], books)
            if got is None:
                unverified += 1
                lines.append("  ? UNVERIFIED  archive could not answer %r :: %s"
                             % (heb[0], snippet))
                continue
            if got != stated:
                failed += 1
                lines.append("  x COUNT       claims %d, archive says %d for %r (%s) :: %s"
                             % (stated, got, heb[0], scope, snippet))
            else:
                checked += 1
            parts = HS.bare(heb[0]).split()
            if len(parts) > 1:
                wide = verse_count(parts[0], books)
                if wide is not None and wide > (got or 0):
                    narrower += 1
                    lines.append(
                        "  ? NARROWER    %r gives %d, head word %r gives %d -- is the "
                        "sentence about the phrase or the word? :: %s"
                        % (heb[0], got, parts[0], wide, snippet))
            seen.add((lo, hi))  # one claim per SENTENCE; keep scanning the paragraph

    print("%s  [count_check]" % path)
    print("  counts verified : %d" % checked)
    if failed:
        print("  COUNT MISMATCH  : %d" % failed)
    if narrower:
        print("  NARROWER QUERY  : %d -- claim rests on a phrase, prose may mean the word" % narrower)
    if byhand:
        print("  BY HAND         : %d claim(s) declared as counted by reading the hits "
              "-- the tool reports the gap, it cannot close it" % byhand)
    if unverified:
        print("  UNVERIFIED      : %d corpus-count claim(s) carrying no data-heb "
              "-- nothing checked these" % unverified)
    for ln in lines:
        print(ln)
    if failed:
        print("%d PROBLEM(S) -- a stated count disagrees with the archive." % failed)
        return 1
    print("clean." if not (unverified or narrower or byhand) else "no mismatches; read the flags above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

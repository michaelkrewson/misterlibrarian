# -*- coding: utf-8 -*-
"""What to translate next on Mister Translation, in priority order. Computed, never hand-kept.

    python3 tools/next_chapter.py              # next 10 English chapters + next 10 Spanish backfill
    python3 tools/next_chapter.py -n 25        # a longer look-ahead
    python3 tools/next_chapter.py --write      # regenerate TRANSLATION_QUEUE_EN.md and _ES.md
    python3 tools/next_chapter.py --gsc Queries.csv   # re-rank by what people already search the site for

The ORDER lives in tools/chapter_priority.py (it is a judgment and rarely changes). What is LEFT is
read from CHAPTERS in build.py and from source/es/, so shipping a chapter removes it from the queue
with no edit anywhere. CLAIMING: push a branch named for the chapter (psalms-22) and open a draft PR titled
"Psalms 22: ..."; open PRs show as IN PROGRESS here and on the cards (they need `gh`; without it the claims are just not shown). A new chapter ships in BOTH languages together (CLAUDE.md, per-chapter
checklist), so the English queue is also the queue for new Spanish chapters; the Spanish card is only
the BACKFILL: chapters that went live in English before their Spanish twin was written.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import chapter_priority as P  # noqa: E402

CANON = [("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36), ("Deuteronomy", 34),
         ("Joshua", 24), ("Judges", 21), ("Ruth", 4), ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22),
         ("2 Kings", 25), ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
         ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31), ("Ecclesiastes", 12),
         ("Song of Solomon", 8), ("Isaiah", 66), ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48),
         ("Daniel", 12), ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
         ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2), ("Zechariah", 14),
         ("Malachi", 4), ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
         ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6), ("Ephesians", 6),
         ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5), ("2 Thessalonians", 3),
         ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13), ("James", 5),
         ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1),
         ("Revelation", 22)]
BOOK_ORDER = {b: i for i, (b, _) in enumerate(CANON)}
ALIASES = {"psalm": "Psalms", "psalms": "Psalms", "song of songs": "Song of Solomon",
           "song of solomon": "Song of Solomon", "songs of solomon": "Song of Solomon",
           "proverb": "Proverbs", "revelations": "Revelation", "ecclesiastes": "Ecclesiastes"}


def done_english():
    src = open(os.path.join(ROOT, "build.py"), encoding="utf8").read()
    a = src.index("CHAPTERS = [")
    e = src.index("\n]\n", a)
    return {(bk, int(n)) for _slug, bk, n in re.findall(r'^\s*\("([a-z0-9]+)",\s*"([^"]+)",\s*(\d+),', src[a:e], re.M)}


def page_name(book, ch):
    return "%s-%d" % (book.lower().replace(" ", "-"), ch)


def done_spanish():
    d = os.path.join(ROOT, "source", "es")
    return {f[:-5] for f in os.listdir(d) if f.endswith(".html")}


def english_queue(done, gsc=None):
    remaining = {(b, c) for b, n in CANON for c in range(1, n + 1)} - done
    ranked = []
    reasons = {}
    for item in P.TOP:
        key = (item[0], item[1])
        if key in remaining:
            ranked.append(key)
            reasons[key] = item[2]
    rest = sorted(remaining - set(ranked),
                  key=lambda k: (-P.BOOK_WEIGHT.get(k[0], 1), BOOK_ORDER[k[0]], k[1]))
    out = ranked + rest
    if gsc:
        out.sort(key=lambda k: -gsc.get(k, 0))  # stable: ties keep the judged order
    return out, reasons


def spanish_backfill(done, es):
    back = [(b, c) for b, c in done if page_name(b, c) not in es]
    order = {k: i for i, k in enumerate(P.ES_BACKFILL_ORDER)}
    return sorted(back, key=lambda k: (order.get(k, 10 ** 6), BOOK_ORDER[k[0]], k[1]))


def read_gsc(path):
    """-> {(book, chapter): impressions} from a Search Console Queries.csv (Query, Impressions columns)."""
    hits = {}
    names = sorted({b.lower() for b, _ in CANON} | set(ALIASES), key=len, reverse=True)
    pat = re.compile(r"\b(%s)\s+(\d{1,3})\b" % "|".join(re.escape(n) for n in names))
    with open(path, encoding="utf8", newline="") as fh:
        for row in csv.DictReader(fh):
            q = (row.get("Top queries") or row.get("Query") or "").lower()
            try:
                imp = int((row.get("Impressions") or "0").replace(",", ""))
            except ValueError:
                continue
            m = pat.search(q)
            if not m:
                continue
            book = ALIASES.get(m.group(1)) or next(b for b, _ in CANON if b.lower() == m.group(1))
            key = (book, int(m.group(2)))
            hits[key] = hits.get(key, 0) + imp
    return hits


def label(k):
    return "%s %d" % k


def open_claims():
    """-> {(book, chapter): "PR #N"} for chapters somebody has an open PR on. Fails OPEN (empty) if gh is unavailable.

    A session CLAIMS a chapter by pushing a branch named for it (psalms-22) and opening a draft PR whose title
    names it ("Psalms 22: ..."). Nothing is written to the repo to claim, so a claim cannot go stale on main."""
    import json
    import subprocess
    try:
        out = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "100", "--json", "number,title,headRefName"],
                             capture_output=True, text=True, timeout=30, cwd=ROOT).stdout
        prs = json.loads(out or "[]")
    except Exception:
        return {}
    names = sorted((b for b, _ in CANON), key=len, reverse=True)
    pat = re.compile(r"\b(%s)\s+(\d{1,3})\b" % "|".join(re.escape(n) for n in names), re.I)
    claims = {}
    for pr in prs:
        hay = pr.get("title", "") + " " + pr.get("headRefName", "").replace("-", " ")
        for m in pat.finditer(hay):
            book = next((b for b, _ in CANON if b.lower() == m.group(1).lower()), None)
            if book:
                claims[(book, int(m.group(2)))] = "PR #%d" % pr["number"]
    return claims


def render_en(queue, reasons, done, claims=None):
    claims = claims or {}
    tot = sum(n for _, n in CANON)
    lines = [
        "# Mister Translation: chapters still to translate, in priority order",
        "",
        "**Generated by `python3 tools/next_chapter.py --write`. Do not hand-edit; the list shrinks by itself when a chapter",
        "is added to `CHAPTERS` in `build.py`.** The order is a judgment kept in `tools/chapter_priority.py`.",
        "",
        "- **%d of %d chapters are translated; %d remain**, all of them in the Old Testament (the New Testament is complete)." % (
            len(done), tot, len(queue)),
        "- A new chapter ships in **both languages together**, so this is also the order for new Spanish chapters. The Spanish",
        "  backfill (chapters live in English with no Spanish twin) is its own card: `TRANSLATION_QUEUE_ES.md`.",
        "- **Take the next chapter with `python3 tools/next_chapter.py`.** Same-chapter-twice is the one hazard: check open PRs first.",
        "",
        "## How the order was made",
        "",
        "No public dataset ranks Bible *chapters* by search demand; the public data is per verse and per year. It points one way:",
        "Bible Gateway's year-end lists are almost all Psalm 23 and Psalm 91, YouVersion's top verses of recent years include Isaiah 41:10",
        "and Philippians 4:6, Bible Gateway's all-time most-searched verses are John 3:16 and Jeremiah 29:11, and the Psalms are the most-read",
        "book. Those chapters, most of the New Testament and the other famous Psalms (1, 23, 27, 34, 37, 46, 51, 91, 100, 103, 119, 121, 139)",
        "are already live, so what is left is ranked by my judgment of how often people look a chapter up by name or quote a line from it,",
        "with that evidence as the tiebreaker. **It is an estimate, not a measurement.** To replace it with measurement, export Search Console's",
        "`Queries.csv` and run `python3 tools/next_chapter.py --gsc Queries.csv`.",
        "",
        "Within a book the chapters are not translated in order, but each chapter's closing notes name the earlier chapters it leans on, so",
        "the library stays connected whichever order we take.",
        "",
        "## The queue",
        "",
        "| # | Chapter | Why people look for it |",
        "|--:|---------|------------------------|",
    ]
    top_index = {(b, c): n for n, (b, c, _r) in enumerate(P.TOP)}

    def tier_of(k):
        n = top_index.get(k)
        if n is None:
            return "rest", "Everything else: ordered by how heavily the book is read, then chapter number"
        for start, end, title in P.TIERS:
            if start - 1 <= n and (end is None or n < end):
                return start, title
        return "rest", ""

    current = None
    for i, k in enumerate(queue, 1):
        t, title = tier_of(k)
        if t != current:
            lines.append("| | **%s** | |" % title)
            current = t
        why = reasons.get(k, "")
        if k in claims:
            why = "**IN PROGRESS (%s)** " % claims[k] + why
        lines.append("| %d | %s | %s |" % (i, label(k), why))
    lines.append("")
    return "\n".join(lines)


def render_es(back, done_count, claims=None):
    claims = claims or {}
    lines = [
        "# Mister Translation en espa&ntilde;ol: the Spanish backfill".replace("&ntilde;", "ñ"),
        "",
        "**Generated by `python3 tools/next_chapter.py --write`. Do not hand-edit.** These are chapters that are already live in English",
        "with **no Spanish twin yet** (%d of them). Every NEW chapter ships in both languages together, so new Spanish chapters follow the" % len(back),
        "English card, `TRANSLATION_QUEUE_EN.md`; this card is only the catch-up.",
        "",
        "- **Order = demand, except Genesis 15-33, which stays in book order**, because the Spanish pages of later Genesis chapters quote the earlier",
        "  ones (Spanish Genesis 15 has to supply 15:1 *magen*, 15:5 the stars, 15:6, 15:7 and 15:13 before 16-33 can cite them).",
        "- Compose the Spanish from the Hebrew or Greek, never from the English; collect what other Spanish pages already quote from the chapter",
        "  first (those quotes fix the verse). Details: `CLAUDE.md`, per-chapter checklist, and the Spanish shelf rules.",
        "",
        "| # | Chapter | Note |",
        "|--:|---------|------|",
    ]
    notes = {("Matthew", 10): "the twelve; 'sheep among wolves'; 10:34 'not peace but a sword'",
             ("Matthew", 9): "healings; 'the harvest is plentiful'",
             ("Daniel", 12): "'many who sleep in the dust of the earth shall awake'",
             ("Daniel", 11): "the long prophecy of the kings of the north and south",
             ("Daniel", 1): "the four in Babylon; the king's food"}
    for i, k in enumerate(back, 1):
        n = notes.get(k, "Genesis, in book order (in progress)" if k[0] == "Genesis" else "")
        if k in claims:
            n = "**IN PROGRESS (%s)** " % claims[k] + n
        lines.append("| %d | %s | %s |" % (i, label(k), n))
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--gsc", help="Search Console Queries.csv to re-rank by existing impressions")
    a = ap.parse_args()
    done = done_english()
    gsc = read_gsc(a.gsc) if a.gsc else None
    queue, reasons = english_queue(done, gsc)
    back = spanish_backfill(done, done_spanish())
    claims = open_claims()
    if a.write:
        open(os.path.join(ROOT, "TRANSLATION_QUEUE_EN.md"), "w", encoding="utf8").write(render_en(queue, reasons, done, claims))
        open(os.path.join(ROOT, "TRANSLATION_QUEUE_ES.md"), "w", encoding="utf8").write(render_es(back, len(done), claims))
        print("wrote TRANSLATION_QUEUE_EN.md (%d chapters) and TRANSLATION_QUEUE_ES.md (%d)" % (len(queue), len(back)))
        return 0
    print("English: %d chapters remain. Next %d (each ships in English AND Spanish):" % (len(queue), a.n))
    for i, k in enumerate(queue[: a.n], 1):
        print("  %2d. %-18s %s%s%s" % (i, label(k), reasons.get(k, ""),
                                       "   [GSC impressions: %d]" % gsc[k] if gsc and gsc.get(k) else "",
                                       "   <-- IN PROGRESS (%s), take the next one" % claims[k] if k in claims else ""))
    print("\nSpanish backfill: %d chapters have English and no Spanish. Next %d:" % (len(back), a.n))
    for i, k in enumerate(back[: a.n], 1):
        print("  %2d. %s%s" % (i, label(k), "   <-- IN PROGRESS (%s)" % claims[k] if k in claims else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

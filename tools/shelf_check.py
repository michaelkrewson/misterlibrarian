# -*- coding: utf-8 -*-
"""Compose-time SHELF-QUOTE validator: run BEFORE splicing a drafted chapter panel in.

    python3 tools/shelf_check.py /tmp/num27_en.html --book Numbers --chapter 27 \
            --shelf-dir /tmp/n27/out

Exists because the same defect class has now been caught in four consecutive
chapter reviews, each time AFTER the chapter shipped:

  Numbers 24  "the whole shelf keeps it plain... nothing to arbitrate" at v5 --
              false three ways (Douay swaps the two nouns, TLB drops the tents).
  Numbers 25  "the entire shelf reads a joining" at v3 -- false three ways
              (Geneva 'coupled', RV60 revised to «acudió», Douay 'was initiated').
  Numbers 27  the Douay named at v5 where its versification puts another sentence;
              the NVI quoted as «tienen razón» when it reads «lo que piden... es
              algo justo»; and the TNM cited twice without being fetched at all.

⭐ The Numbers 27 case is why this is a script and not another checklist line.
The shelf data was ALREADY FETCHED and sitting in the working directory. It was
not a failure to fetch; it was a failure to LOOK. And the reason was legible:
attention had gone to the newest checklist rule and come off an older one. A rule
that competes for attention with other rules loses; a script does not compete.

WHAT IT CHECKS. For every `<span class="tag t-XXX">` in a drafted panel that is
followed by a quoted phrase, it asks whether that phrase actually occurs in that
version's text, in the verses the enclosing note covers. Three outcomes:

    OK        the phrase is there
    MISS      the phrase is NOT in that version at those verses  <- a real defect
    NO DATA   that version was never fetched for this chapter    <- also a defect,
              because it means the claim rests on memory

WHAT IT DOES NOT CHECK, and says so rather than implying coverage: a tag with no
quoted phrase after it ("the ASV drops the quantifier") is a PARAPHRASE. Those are
counted and reported as unchecked. Paraphrases are where the remaining risk lives.

VERSE SCOPING comes from the panel itself -- each verse links to its own note, so
the note's verse range is read off the fragment rather than guessed.

PARTIAL is a WARNING, not a failure. When several versions share one quote ("the
NWT 1984 and TNM 1987 keep it indefinite ('<English phrase>')") the group passes if
ANY member has it, because the quote can only be one of their wordings. But the
members that do NOT contain it are listed, because that is exactly how a wrong name
hides behind a right one -- which is the Numbers 27 Douay defect. Read the PARTIAL
lines; most are legitimate and some are not.

MUTATION-TESTED against the three real defects that motivated it:
    NVI quoted as something it does not say ......... MISS      (fails the run)
    a version cited but never fetched ............... MISS      (fails the run)
    Douay named in a list where it does not belong .. PARTIAL   (warns)

KNOWN FALSE POSITIVE, seen in the wild: BibleGateway's DRA prints "whose eye ire
stopped up" at Numbers 24:3 -- a typo in that digital edition, not in the quote. When
a MISS looks like a one-letter difference, read the fetched text before rewriting a
correct quote to match a corrupt one.

KNOWN LIMITS, stated rather than implied:
  * a paraphrase with no quoted phrase is not checked at all -- these are counted
    and must still be read by a human;
  * an apostrophe written as &rsquo; inside a quoted phrase truncates the quote
    early, so the checked fragment may be shorter than what was written;
  * a very short quote can match by accident (--min-words guards the shortest);
  * it verifies that a phrase EXISTS in a version, never that the sentence built
    around it draws the right conclusion;
  * a tag with NO span markup is invisible to it -- which is itself worth catching,
    since untagged shelf citations went uncounted in both Numbers 23 and 27 and were
    found only because their quote then drifted onto the neighbouring versions.
"""
import argparse, html, json, os, re, subprocess, sys, unicodedata

# tag class -> (kind, source).  'wol' goes through tools/shelf_text.py (archive-first);
# 'bg' reads a JSON file of {verse: text} produced by the chapter's own fetch.
SOURCES = {
    "kjv":   ("wol", "kjv"),        "asv":  ("wol", "asv"),
    "nwt":   ("wol", "nwt1984"),    "tnm":  ("wol", "tnm1987"),
    "gnv":   ("bg", "GNV"),         "geneva": ("bg", "GNV"),
    "drb":   ("bg", "DRA"),         "douay": ("bg", "DRA"),  "dou": ("bg", "DRA"),
    "niv":   ("bg", "NIV"),         "tlb":  ("bg", "TLB"),
    "rv":    ("bg", "RVA"),         "rv60": ("bg", "RVR1960"), "nvi": ("bg", "NVI"),
}
NEAR = 40   # a quote further than this from its tag is someone else's
FAR  = 120  # ...and past this it is nobody's -- the tag is a paraphrase
SKIP = {"mine"}          # this translation -- nothing to check it against

QUOTE = re.compile(r'&lsquo;(.+?)&rsquo;|&laquo;(.+?)&raquo;|‘(.+?)’|«(.+?)»')

def norm(s):
    """Fold to a comparable form: entities, curly quotes, accents, case, spacing."""
    s = html.unescape(s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("ʼ", "'").replace("\u00ad", "")
    # WOL prints pronunciation marks inside names -- Mo'ab, Je-ho'vah. Delete them
    # rather than let the filter below turn them into spaces, which split "Moab" into
    # "mo ab" and failed a quote that was verbatim correct (Numbers 24:17).
    s = re.sub(r'[\u02b9\u02ba\u02bb\u02bd\u2032]', '', s)
    s = ''.join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    s = re.sub(r'[^0-9a-zA-Z\' ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip().casefold()

def wol_text(book, chapter, version):
    try:
        out = subprocess.run(["python3", "tools/shelf_text.py", book, str(chapter),
                              "--version", version], capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return None
    d = {}
    for line in out.split("\n"):
        m = re.match(r'^(\d+):\s(.*)$', line)
        if m:
            d[m.group(1)] = m.group(2)
    return d or None

def _expand_ranges(d):
    """The Living Bible merges verses, so its keys are ranges ('3-9', '15-19').

    Map every verse in the range to the merged text, so a per-verse lookup finds it.
    Without this, quoting anything from a merged block reported MISS on data that was
    sitting right there (Numbers 24:3).
    """
    out = {}
    for k, v in d.items():
        m = re.fullmatch(r'(\d+)\s*-\s*(\d+)', str(k).strip())
        if m:
            for n in range(int(m.group(1)), int(m.group(2)) + 1):
                out.setdefault(str(n), v)
        else:
            out.setdefault(str(k).strip(), v)
    return out

def bg_text(shelf_dir, name):
    """Load a fetched BibleGateway version, MERGING every file we have for it.

    A merged-verse version yields two files -- NAME.json with blank per-verse entries
    and NAME_ranges.json with the real text keyed "3-9". Returning the first file found
    handed back the blank one and reported MISS on text that was on disk (Numbers 24:3
    in The Living Bible). Non-empty always wins.
    """
    if not shelf_dir:
        return None
    out, seen = {}, False
    for fn in (name + ".json", name + "_ranges.json"):
        p = os.path.join(shelf_dir, fn)
        if not os.path.exists(p):
            continue
        seen = True
        for k, v in _expand_ranges(json.load(open(p, encoding="utf-8"))).items():
            if v and v.strip() or k not in out:
                out[k] = v
    return out if seen else None


def _quote_before(body, pos, used_end=0, window=30):
    """Quote immediately preceding a tag run: the «...» (RV, RV60) style.

    Returns (phrase, gap_len), and only when the gap between it and the tag is short and
    contains no sentence break and no other tag -- i.e. the quote and the version
    names are plainly one attribution, not two neighbouring sentences.
    """
    if pos is None:
        return None, None
    head = body[:pos]
    last = None
    for m in QUOTE.finditer(head):
        if m.start() < used_end:
            continue          # already spoken for by an earlier run in this note
        last = m
    if not last:
        return None, None
    gap = head[last.end():]
    if len(gap) > window or "." in gap or "class=\"tag" in gap:
        return None, None
    return next(g for g in last.groups() if g), len(gap)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fragment")
    ap.add_argument("--book", required=True)
    ap.add_argument("--chapter", required=True)
    ap.add_argument("--shelf-dir", default=None)
    ap.add_argument("--min-words", type=int, default=2,
                    help="quotes shorter than this are reported but not failed (too short to be evidence)")
    a = ap.parse_args()

    frag = open(a.fragment, encoding="utf-8").read()

    # verse -> note id, straight off the panel
    v2n = {}
    for m in re.finditer(r'id="v\d+-(\d+)".*?href="#(n[\d-]+)"', frag, re.S):
        v2n.setdefault(m.group(2), set()).add(m.group(1))

    notes = re.findall(r'<div class="note" id="(n[\d-]+)">(.*?)\n  </div>', frag, re.S)
    if not notes:
        print("no notes found in fragment -- is this a chapter panel?"); return 2

    cache, miss, nodata, ok, para, short, partial = {}, [], [], 0, 0, 0, []
    for nid, body in notes:
        verses = sorted(v2n.get(nid, set()), key=int)
        # Collect tags, then group any run of tags that SHARE one following quote:
        # "the NWT 1984 and TNM 1987 keep it indefinite ('...')" is one claim about two
        # versions, and the quote may be either one's wording. Attributing it to the last
        # tag alone produces false misses -- checked against Numbers 27, where it did.
        hits = [(m.start(), m.end(), m.group(1), body[m.end():m.end()+260])
                for m in re.finditer(r'class="tag t-([a-z0-9]+)"[^>]*>(.*?)</span>', body, re.S)]
        groups, cur, run_at, used_end = [], [], None, 0
        for pos, end, tag, after in hits:
            if tag in SKIP:
                continue
            if not cur:
                run_at = pos
            cur.append(tag)
            q = QUOTE.search(after)
            # a quote belongs to this run only if no further tag intervenes before it
            nxt = re.search(r'class="tag t-[a-z0-9]+"', after)
            fwd = q if (q and (not nxt or q.start() < nxt.start())) else None
            # A real attribution sits right NEXT to its tag, so the following quote wins
            # whenever it is close. Distance-comparison was tried instead and was much
            # worse: in "KJV 'joined himself', NWT 'attached itself'" every run has a
            # near quote on both sides, the near-ties broke the wrong way, and each run
            # stole the previous run's quote (Numbers 27 went from clean to 8 false
            # misses). Only when nothing is close does the preceding «...» (RV, RV60)
            # form get a look, which is what the n25-1 case needs.
            back_pk, _g = _quote_before(body, run_at, used_end)
            # Reaching further than FAR for a quote found my OWN rendering 180 chars
            # downstream and pinned it on the TLB, whose actual claim was a paraphrase.
            if fwd is not None and (fwd.start() <= NEAR or
                                    (back_pk is None and fwd.start() <= FAR)):
                groups.append((tuple(cur), next(g for g in fwd.groups() if g)))
                used_end = end + fwd.end()
                cur, run_at = [], None
            elif nxt is None:
                # Only once no further tag can join this run -- otherwise "KJV and ASV
                # 'one quote'" flushes KJV alone against some earlier phrase and every
                # later quote slides one version to the left.
                if back_pk is not None:
                    groups.append((tuple(cur), back_pk))
                    cur, run_at = [], None
        if cur:
            # Second attribution style: the quote comes FIRST and the versions follow in
            # parentheses -- «ahorcalos» (RV, RV60, NVI). Found by running this tool over
            # already-shipped Numbers 25, where the one-style rule skipped past the real
            # quote and grabbed an unrelated phrase from a 2 Samuel citation.
            # The window is deliberately tight (short gap, no sentence break, no other
            # tag) so a correct neighbouring quote cannot excuse an unrelated claim.
            back, _gap = _quote_before(body, run_at, used_end)
            if back:
                groups.append((tuple(cur), back))
            else:
                para += len(cur)
        for tags, phrase in groups:
            for part in [p for p in re.split(r'&hellip;|…', phrase) if p.strip()]:
                np = norm(part)
                if len(np.split()) < a.min_words:
                    short += 1
                    continue
                found, missing_data, matched, unmatched = False, [], [], []
                for tag in tags:
                    if tag not in SOURCES:
                        missing_data.append("%s: unknown tag" % tag); continue
                    kind, src = SOURCES[tag]
                    if src not in cache:
                        raw = wol_text(a.book, a.chapter, src) if kind == "wol" \
                              else bg_text(a.shelf_dir, src)
                        cache[src] = _expand_ranges(raw) if raw else raw
                    text = cache[src]
                    if not text:
                        missing_data.append("%s never fetched" % src); continue
                    # A verse present but EMPTY is missing data, not a failed match --
                    # The Living Bible merges verses into ranges, so single verses come
                    # back blank and were being reported as MISS (Numbers 24:3).
                    pool = " ".join(norm(text[v]) for v in verses
                                    if text.get(v, "").strip()) or \
                           " ".join(norm(t) for t in text.values() if t.strip())
                    if not pool:
                        missing_data.append("%s: no text for vv%s" %
                                            (src, ",".join(verses) or "?")); continue
                    if np in pool:
                        found = True; matched.append(tag)
                    else:
                        unmatched.append(tag)
                # A group of versions sharing one quote passes if ANY of them has it --
                # "the NWT and TNM keep it indefinite ('<English>')" is legitimate, since
                # the quote can only be one of their wordings. But a version listed in
                # such a group that does NOT contain the phrase is exactly how a wrong
                # name hides behind a right one (the Numbers 27 Douay case), so say so.
                if found and unmatched:
                    partial.append((nid, "+".join(matched), "+".join(unmatched), part, verses))
                if found:
                    ok += 1
                elif len(missing_data) == len(tags):
                    nodata.append((nid, "+".join(tags), part, "; ".join(missing_data)))
                else:
                    miss.append((nid, "+".join(tags), part, verses))

    print("%s  [%s %s]" % (a.fragment, a.book, a.chapter))
    print("  checked quotes : %d OK" % ok)
    if short: print("  too short      : %d (under --min-words, not failed)" % short)
    print("  PARAPHRASES    : %d tags with no quoted phrase -- NOT CHECKED, read these yourself" % para)
    if partial: print("  PARTIAL GROUPS : %d -- a listed version does not contain the shared quote" % len(partial))
    for nid, tag, part, why in nodata:
        print("  ⚠ NO DATA  %-8s %-6s %r  (%s)" % (nid, tag, part[:60], why))
    for nid, good, bad_, part, verses in partial:
        print("  ? PARTIAL  %-8s quote matches %s but NOT %s: %r" % (nid, good, bad_, part[:52]))
    for nid, tag, part, verses in miss:
        print("  ✗ MISS     %-8s %-6s %r  not found in vv%s" %
              (nid, tag, part[:60], ",".join(verses) if verses else "?"))
    bad = len(miss) + len(nodata)
    print("clean." if not bad else "%d PROBLEM(S) -- fix before splicing." % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""EN/ES twin diff: the chapter's two languages, compared note by note.

    python3 tools/twin_diff.py numbers-36                 # shape only
    python3 tools/twin_diff.py numbers-36 --prose         # + sentences, lengths, side-by-side
    python3 tools/twin_diff.py numbers-36 --prose --all   # side-by-side for EVERY note
    python3 tools/twin_diff.py /tmp/n36_en.html /tmp/n36_es.html --prose   # pre-splice

Exists because CLAUDE.md has told this project to diff the twins since Numbers 13,
told it again -- "AND DIFF THE NOTES, not just the verses" -- after Numbers 14, and
each time the diff was a throwaway script rewritten from scratch. A rule that gets
re-derived every chapter is a rule that gets re-derived slightly differently every
chapter, which is how Numbers 36 shipped a defect the twin-diff was supposed to own.
Same remedy as validate_chapter.py and shelf_check.py: stop restating the rule and
commit the script.

TWO MODES, because the two failures they catch are not the same failure.

SHAPE (default) is the documented check, finally mechanical: per note id, compare
paragraph count, the shelf-tag multiset, the digits, and the set of outbound links
(normalised across languages, so numbers-27.es.html and numbers-27.html are the same
citation). This is the mode that owns the Numbers 14 defect -- nine chapters cited as
live links in English and as dead prose in Spanish -- and it fails the run.

PROSE (--prose) is new, added 2026-08-27 after Numbers 36. The first note's opening
sentence read "the appellants open with the same word the verse it opens with" --
garbled, and wrong about its own chapter. The Spanish twin had it right ("la misma
palabra con que empieza el capitulo que apelan"), which is exactly the tell the twin
rule exists to exploit. Nothing caught it: the shape was identical on both sides, the
paragraph counts matched, the tags matched, the links matched. The prose was never
compared, because the diff never looked at prose.

WHAT PROSE MODE HONESTLY DOES, measured rather than asserted. It reports sentence
counts and lengths, and it prints the two sides side by side. It does NOT detect the
garble by arithmetic, and the numbers say so plainly:

    that sentence          EN 121 chars   ES 139   ratio 1.149
    its whole note         EN 5760        ES 5313  ratio 0.922
    corpus of 1,514 notes  para-ratio p05 0.73  median 1.01  p95 1.14

A ratio of 1.149 sits at the corpus p95 and its note sits at the p25 -- both
unremarkable. A garble that keeps its length is invisible to every length rule, and
a threshold tight enough to flag it would flag hundreds of clean sentences. So the
arithmetic is TRIAGE and the side-by-side is the CHECK: shape divergence anywhere in
a note prints that note's two sides aligned, and a human reads across. On the real
Numbers 36 note this works -- the note diverges (one paragraph runs 6 sentences in
English against 5 in Spanish, another at ratio 0.63), so the note prints, and the
garbled sentence is the first line of the printout.

WHICH ALSO MEANS: a garbled sentence in a note that is otherwise perfectly matched
will not print unless you ask. That is what --all is for, and on a chapter you are
about to ship it is the mode to use. Reading four notes side by side is a minute.

ALIGNMENT is per PARAGRAPH, not per note, and that was a measurement too. Aligning
sentences across a whole note by index drifts the moment either side merges or splits
one. On the Numbers 36 note, note-scoped alignment flags 8 sentence pairs, with
ratios like 4.31 and 0.06 for pairs that are simply off by one; paragraph-scoped
alignment flags 2, and both of those are real (the Spanish genuinely abridges them).
So six of the eight were drift. Paragraph counts match in 92.8% of the corpus's 1,514
notes, so paragraphs re-anchor the alignment and any drift stays inside one paragraph.
When a paragraph's own sentence counts disagree, its sentences are reported as counts
only, never as pairs.

BANDS come from the corpus, not from taste (see --calibrate to re-derive them):
paragraph ratio p05 0.73 / p95 1.14, so anything outside [0.72, 1.30] is flagged;
sentence ratio is much noisier (p05 0.60 / p95 1.22) and uses [0.55, 1.60].

KNOWN LIMITS, stated rather than implied:
  * a length-preserving garble is not detected -- only displayed (see above);
  * the sentence splitter is a regex; an abbreviation or a mid-sentence numeral can
    split one sentence into two, which is why a sentence-count mismatch is a WARNING
    and only shape mismatches fail the run;
  * it compares the two sides to each other, never either side to the Hebrew -- two
    twins can agree perfectly and both be wrong;
  * a note present on one side and absent on the other is reported and failed, but
    this tool cannot say which side is right.
"""
import argparse, glob, html, os, re, sys

NOTE = re.compile(r'<div class="note" id="(n[\d-]+)">(.*?)\n  </div>', re.S)
PARA = re.compile(r'<p>(.*?)</p>', re.S)
TAG = re.compile(r'class="tag (t-[a-z0-9]+)"')
HREF = re.compile(r'href="([^"]+)"')
DIGIT = re.compile(r'\d+')
TAGSPAN = re.compile(r'<span class="tag t-[a-z0-9]+"[^>]*>.*?</span>', re.S)
# Version years and the bare "60" of RV60 -- these are version NAMES, not claims.
YEARISH = re.compile(r'^(1[5-9]\d\d|20\d\d|60)$')


def _num(s):
    return (len(s), int(s))
# A sentence ends at . ! ? and the next one opens with a capital or an opening mark.
# Spanish opens with the inverted marks as often as with a letter, so those count.
SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡&“"‘«])')

PARA_LO, PARA_HI = 0.72, 1.30     # corpus p05 0.73 / p95 1.14
SENT_LO, SENT_HI = 0.55, 1.60     # corpus p05 0.60 / p95 1.22 -- deliberately looser

# Spanish page names for the library surfaces, so a link to the dictionary in one
# language is recognised as the same citation as its twin in the other.
ES_PAGES = {"diccionario": "dictionary", "enciclopedia": "encyclopedia",
            "concordancia": "concordance", "biblioteca": "library"}
# The library surfaces hold every term on one page, so their links carry a meaningful
# anchor; a chapter link's anchor is just which note, and is compared separately.
LIBRARY_PAGES = {"dictionary.html", "encyclopedia.html"}


def prose(h):
    """Visible text of an HTML fragment."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def sentences(t):
    return [s for s in SPLIT.split(t) if s.strip()]


def norm_link(href):
    """Fold an href to a language-neutral form: numbers-27.es.html -> numbers-27.html."""
    href = href.split("#")[0]
    if not href or href.startswith("http"):
        return href
    d, _, f = href.rpartition("/")
    if f.endswith(".es.html"):
        f = f[:-8] + ".html"
    base = f[:-5] if f.endswith(".html") else f
    f = ES_PAGES.get(base, base) + ".html"
    return (d + "/" + f) if d else f


def links(body):
    """Language-neutral (page, anchor) pairs. The anchor matters for the library
    surfaces, where one page holds every term -- dictionary.html#sabab and
    dictionary.html#davaq are two different citations, not one."""
    out = set()
    for h in HREF.findall(body):
        if h.startswith("#"):
            continue
        page, _, anchor = h.partition("#")
        page = norm_link(page)
        out.add(page + "#" + anchor if page in LIBRARY_PAGES and anchor else page)
    return out


_ES_POOLS = None


def es_pools():
    """ES dictionary/encyclopedia slugs, or None if library_data cannot be imported.

    Lazy and fail-soft: this tool is useful without it (validate_chapter.py owns the
    real anchor validation), so a run from outside the repo root degrades to a stated
    limitation rather than an import error.
    """
    global _ES_POOLS
    if _ES_POOLS is None:
        try:
            sys.path.insert(0, ".")
            import library_data as L
            _ES_POOLS = {"dictionary.html": set(L.DICTIONARY_ES),
                         "encyclopedia.html": set(L.ENCYCLOPEDIA_ES)}
        except Exception:
            _ES_POOLS = False
    return _ES_POOLS or None


def resolve(args):
    """Accept a chapter slug ('numbers-36') or two explicit file paths."""
    if len(args) == 2:
        return args[0], args[1]
    a = args[0]
    if a.endswith(".html"):
        a = a[:-8] if a.endswith(".es.html") else a[:-5]
    return a + ".html", a + ".es.html"


def read_notes(path):
    if not os.path.exists(path):
        sys.exit("no such file: %s" % path)
    return dict(NOTE.findall(open(path, encoding="utf-8").read()))


# --------------------------------------------------------------------------- shape

def twin_exists(target, src_path):
    """Does the other language have a page for this link target?

    Answers the one question that separates the Numbers 14 defect from its
    documented legitimate exception: 'Nehemiah 9:17' live in English and dead prose
    in Spanish is a defect ONLY IF nehemiah-1.es.html exists. If it does not, the
    Spanish note is obeying the rule (cite it as prose, "todavia no en espanol").
    Getting this right in both directions matters: of the corpus's 1,475 one-sided
    links, 804 are the legitimate exception and 671 are real. An answer of "no twin"
    is an excuse, and handing out excuses too freely is how a check goes quiet.

    ⚠ Resolved against the REPO ROOT (cwd), not against the input file's directory.
    The compose-time workflow drafts fragments in /tmp, and looking beside the
    fragment finds no chapter pages at all -- which silently excused EVERY one-sided
    link and turned the tool's one real failure mode off. Caught by running it on a
    /tmp fragment; the fragment's own directory is only a fallback.
    """
    if target.startswith("http"):
        return True
    # ⚠ Split the anchor off BEFORE the .html test. Library links arrive here as
    # "dictionary.html#nefesh", which does not end in ".html", so an endswith() test
    # placed first returned early and made the whole anchor check below dead code --
    # every library link was then treated as a real defect and the 477 legitimately
    # unlinkable ones came back as failures. Caught by re-reading the function when
    # the corpus failure rate went UP (67% -> 68%) on a change meant to lower it;
    # with the ordering fixed it is 64%.
    page, _, anchor = target.partition("#")
    if not page.endswith(".html"):
        return True                      # not a chapter/atlas/library page
    # The library surfaces are named, not suffixed: dictionary.html's Spanish twin is
    # diccionario.html, so looking for dictionary.es.html finds nothing and would
    # excuse a one-sided dictionary link forever. But the PAGE existing is not the
    # question -- the TERM is. Measured over the corpus: of 704 one-sided library
    # links, 477 name a slug with no ES entry at all, so the Spanish note could not
    # have linked it if it wanted to; only the other 227 are real defects. Excusing
    # by page alone turned those 477 legitimate notes into failures.
    if page[:-5] in ES_PAGES.values():
        pools = es_pools()
        if pools is None:
            return True          # cannot tell; see the note printed by main()
        return not anchor or anchor in pools.get(page, set())
    es = page[:-5] + ".es.html"
    for d in (".", os.path.dirname(src_path) or "."):
        if os.path.exists(os.path.join(d, es)):
            return True
    return False


def shape_diff(en, es, en_path="."):
    """Compare the two sides structurally.

    Returns (fails, warns). The split is measured, not chosen: run over all 261 twin
    pairs (1,514 notes), the first cut failed 245 of 261 files, which is the cry-wolf
    tool nobody reads. Each check was then diagnosed and tiered by whether a hit is
    reliably a defect.

    FAILS -- a hit here is a defect nearly every time:
      * a note present on one side only
      * paragraph count mismatch                                (7.2% of notes)
      * a link live in one language whose TWIN EXISTS in the other (the page for a
        chapter, the ES term for a library slug) and is not linked there -- the
        Numbers 14 defect exactly. 671 real instances in the corpus, sampled and
        confirmed: 1 Thessalonians 1 n2 links 1-corinthians-1 in English and says
        "1 Corintios 13:13" as bare prose in Spanish.

    WARNS -- legitimate often enough that failing on them would train you to ignore
    the tool:
      * a one-sided link whose twin does NOT exist. 804 of the corpus's 1,475
        one-sided links are this, and CLAUDE.md documents it as the correct handling.
        Still worth a line, because the rule is to FLAG it in prose, not drop it.
      * digits differing (179 notes, 11.8%, even after version years are excluded --
        and only when the SETS differ, not merely the counts, which is another 89)
      * one side citing the shelf while the other cites nothing (159 notes, 10.5%)

    NOT CHECKED AT ALL, and this was the biggest surprise: the shelf-tag MULTISET.
    CLAUDE.md says to diff shelf tags, but the two languages cite two different
    shelves -- English notes lead with KJV 803 / ASV 585 / NIV 574, Spanish with
    RV60 551 / NVI 433 / RV 220. The sets genuinely differ in 781 of the 800 notes
    where they differ at all, so a cross-language multiset compare fails almost every
    clean chapter and measures nothing. What survives of that rule is the asymmetry
    check above: one side cites the shelf, the other is silent.
    """
    bad, warn = [], []
    pe, ps = PARA.findall(en), PARA.findall(es)
    if len(pe) != len(ps):
        bad.append("paragraphs  EN %d  ES %d" % (len(pe), len(ps)))

    ne, ns = len(TAG.findall(en)), len(TAG.findall(es))
    if (ne == 0) != (ns == 0):
        warn.append("shelf       cited in %s (%d tags), silent in %s"
                    % (("EN", ne, "ES") if ne else ("ES", ns, "EN")))

    # Digits: strip the tag spans first (they carry version years -- "RV 1909",
    # "NWT 1984", "RV60"), then drop any remaining year-shaped number. Without this
    # the check is dominated by version names: '60' alone accounted for 469 of the
    # one-sided values, and the noise hid the verse numbers and counts worth reading.
    de = [d for d in DIGIT.findall(prose(TAGSPAN.sub(" ", en))) if not YEARISH.match(d)]
    ds = [d for d in DIGIT.findall(prose(TAGSPAN.sub(" ", es))) if not YEARISH.match(d)]
    if sorted(de) != sorted(ds):
        oe, os_ = sorted(set(de) - set(ds), key=_num), sorted(set(ds) - set(de), key=_num)
        if oe or os_:
            warn.append("digits      EN only %s  ES only %s"
                        % (",".join(oe) or "-", ",".join(os_) or "-"))

    le, ls = links(en), links(es)
    for side, missing in (("EN", le - ls), ("ES", ls - le)):
        other = ("ES" if side == "EN" else "EN")
        real = sorted(x for x in missing if twin_exists(x, en_path))
        excused = sorted(x for x in missing if not twin_exists(x, en_path))
        if real:
            bad.append("links       live in %s, prose in %s (the %s page EXISTS): %s"
                       % (side, other, other, ", ".join(real)))
        if excused:
            warn.append("links       live in %s, no %s page yet: %s  "
                        "(correct -- but the %s note must still FLAG it in prose)"
                        % (side, other, ", ".join(excused), other))
    return bad, warn


# --------------------------------------------------------------------------- prose

def prose_diff(en, es):
    """Soft signals: sentence counts and length ratios. Warnings, never failures."""
    warn = []
    pe, ps = PARA.findall(en), PARA.findall(es)
    te, ts_ = prose(en), prose(es)
    ne, ns = len(sentences(te)), len(sentences(ts_))
    if ne != ns:
        warn.append("sentences   EN %d  ES %d" % (ne, ns))
    if te and ts_:
        r = len(ts_) / len(te)
        if not (PARA_LO <= r <= PARA_HI):
            warn.append("note length EN %d  ES %d  ratio %.2f" % (len(te), len(ts_), r))

    if len(pe) != len(ps):
        return warn          # paragraph alignment is gone; per-paragraph is meaningless

    for i, (a, b) in enumerate(zip(pe, ps)):
        ta, tb = prose(a), prose(b)
        if len(ta) < 120 or len(tb) < 40:
            continue
        r = len(tb) / len(ta)
        if not (PARA_LO <= r <= PARA_HI):
            warn.append("para %-2d     EN %d  ES %d  ratio %.2f" % (i, len(ta), len(tb), r))
        sa, sb = sentences(ta), sentences(tb)
        if len(sa) != len(sb):
            warn.append("para %-2d     sentences EN %d  ES %d" % (i, len(sa), len(sb)))
            continue         # index alignment inside this paragraph is unreliable
        for j, (x, y) in enumerate(zip(sa, sb)):
            if len(x) < 60:
                continue
            r = len(y) / len(x)
            if not (SENT_LO <= r <= SENT_HI):
                warn.append("para %-2d s%-2d EN %d  ES %d  ratio %.2f"
                            % (i, j, len(x), len(y), r))
    return warn


def wrap(t, w):
    out, line = [], ""
    for word in t.split():
        if len(line) + len(word) + 1 > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word) if line else word
    if line:
        out.append(line)
    return out or [""]


def side_by_side(nid, en, es, width):
    """Print the two sides aligned, paragraph by paragraph and sentence by sentence.

    This is the part that actually catches a garble, so it is laid out to be READ:
    matched sentences sit on the same row, and a row whose two halves say different
    things is visible without counting anything.
    """
    print("\n" + "=" * (width * 2 + 3))
    print("  %s   ENGLISH%sSPANISH" % (nid, " " * max(1, width - len(nid) - 12)))
    print("=" * (width * 2 + 3))
    pe, ps = PARA.findall(en), PARA.findall(es)
    for i in range(max(len(pe), len(ps))):
        ta = prose(pe[i]) if i < len(pe) else ""
        tb = prose(ps[i]) if i < len(ps) else ""
        print("-" * (width * 2 + 3))
        sa, sb = sentences(ta), sentences(tb)
        if len(sa) != len(sb):
            # counts disagree -- show the whole paragraph rather than mis-pair it
            sa, sb = [ta], [tb]
        for x, y in zip(sa, sb):
            la, lb = wrap(x, width), wrap(y, width)
            for k in range(max(len(la), len(lb))):
                print("%-*s | %s" % (width, la[k] if k < len(la) else "",
                                     lb[k] if k < len(lb) else ""))
            print("%-*s |" % (width, ""))


# ----------------------------------------------------------------------- calibrate

def calibrate():
    """Re-derive the bands from every twin pair in the repo. Prints, changes nothing."""
    pairs = [(b[:-8] + ".html", b) for b in sorted(glob.glob("*.es.html"))]
    pairs = [(e, s) for e, s in pairs if os.path.exists(e)]
    pr, sr, eq, tot = [], [], 0, 0
    for en, es in pairs:
        E, S = read_notes(en), read_notes(es)
        for nid in E.keys() & S.keys():
            pe, ps = PARA.findall(E[nid]), PARA.findall(S[nid])
            if not pe or not ps:
                continue
            tot += 1
            if len(pe) != len(ps):
                continue
            eq += 1
            for a, b in zip(pe, ps):
                ta, tb = prose(a), prose(b)
                if len(ta) < 120:
                    continue
                pr.append(len(tb) / len(ta))
                sa, sb = sentences(ta), sentences(tb)
                if len(sa) == len(sb):
                    sr += [len(y) / len(x) for x, y in zip(sa, sb) if len(x) >= 60]
    if not tot:
        print("no twin pairs found -- run from the repo root"); return
    print("twin pairs %d   notes %d   equal paragraph counts %d (%.1f%%)"
          % (len(pairs), tot, eq, 100.0 * eq / tot))
    for name, v, band in (("paragraph", pr, (PARA_LO, PARA_HI)),
                          ("sentence", sr, (SENT_LO, SENT_HI))):
        v.sort()
        q = lambda p: v[int(p * (len(v) - 1))]
        out = sum(1 for x in v if not (band[0] <= x <= band[1]))
        print("%-9s n=%-5d p01 %.2f  p05 %.2f  med %.2f  p95 %.2f  p99 %.2f   "
              "band [%.2f, %.2f] flags %d (%.1f%%)"
              % (name, len(v), q(.01), q(.05), q(.50), q(.95), q(.99),
                 band[0], band[1], out, 100.0 * out / len(v)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="*",
                    help="chapter slug (numbers-36) or two file paths (EN then ES)")
    ap.add_argument("--prose", action="store_true",
                    help="sentence counts, length ratios, and a side-by-side of diverging notes")
    ap.add_argument("--all", action="store_true",
                    help="with --prose, print the side-by-side for EVERY note")
    ap.add_argument("--width", type=int, default=62, help="column width for the side-by-side")
    ap.add_argument("--calibrate", action="store_true",
                    help="re-derive the ratio bands from every twin pair in the repo, then exit")
    a = ap.parse_args()

    if a.calibrate:
        calibrate()
        return 0
    if not a.target:
        ap.error("give a chapter slug or two file paths (or --calibrate)")

    en_path, es_path = resolve(a.target)
    E, S = read_notes(en_path), read_notes(es_path)
    if not E or not S:
        print("no notes found in %s -- are these chapter panels?"
              % (en_path if not E else es_path))
        return 2

    print("%s  vs  %s" % (en_path, es_path))
    if es_pools() is None:
        print("  (library_data not importable -- run from the repo root, or one-sided "
              "dictionary/encyclopedia links go UNREPORTED)")
    problems, warnings, shown = 0, 0, 0

    only_en, only_es = sorted(E.keys() - S.keys()), sorted(S.keys() - E.keys())
    for side, ids in (("EN", only_en), ("ES", only_es)):
        if ids:
            problems += len(ids)
            print("  x NOTES only in %s: %s" % (side, ", ".join(ids)))

    def key(s):
        return [int(x) for x in re.findall(r"\d+", s)]

    for nid in sorted(E.keys() & S.keys(), key=key):
        bad, warn = shape_diff(E[nid], S[nid], en_path)
        if a.prose:
            warn = warn + prose_diff(E[nid], S[nid])
        problems += len(bad)
        warnings += len(warn)
        if bad or warn:
            print("\n  %s" % nid)
            for b in bad:
                print("    x %s" % b)
            for w in warn:
                print("    ? %s" % w)
        if a.prose and (a.all or bad or warn):
            side_by_side(nid, E[nid], S[nid], a.width)
            shown += 1

    print("\n%d note(s) compared" % len(E.keys() & S.keys()))
    print("%d problem(s), %d warning(s)%s"
          % (problems, warnings,
             ", %d note(s) printed side by side" % shown if a.prose else ""))
    if a.prose and not a.all:
        print("NOTE: a garbled sentence that keeps its length shows in NO count above. "
              "Before shipping, run --all and READ the columns.")
    print("clean." if not problems else "%d PROBLEM(S) -- fix before shipping." % problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""How often does a Deuteronomy chapter switch between singular and plural
address? One crude detector, applied uniformly, so chapters are comparable.

WHY THIS EXISTS. Deuteronomy 11 shipped (2026-09-01) asserting "No previous
chapter on these pages has come close to that rate." That was written from
impression and never checked, and it is FALSE. CLAUDE.md's claims pass says an
absolute is guilty until grepped, and tools/heb_search.py had been used
diligently all session for WORD-level absolutes -- while this CORPUS-level one
went out unchecked. Exactly the failure the checklist itself names: patching
the category last criticised while the same laxity reappears one category over.
Two minutes of measurement would have caught it. So it is a script now.

RESULT (2026-09-01, all shipped Deuteronomy chapters):

    chapter           vv  blocks  mid-verse  switches/verse
    Deuteronomy 1     46      17          6            0.35
    Deuteronomy 4     49      25         10            0.49
    Deuteronomy 5     29      15          5            0.48
    Deuteronomy 6     25      16          6            0.60   <-- densest
    Deuteronomy 7     26      15          8            0.54
    Deuteronomy 8     20       4          2            0.15
    Deuteronomy 9     29      15          6            0.48
    Deuteronomy 10    22       7          3            0.27
    Deuteronomy 11    32      20          6            0.59   <-- second

Deuteronomy 11 is SECOND, effectively tied with Deuteronomy 6 -- which is the
chapter Deuteronomy 11 turns out to be quoting, so the near-tie is a better
note than the false record was. Deuteronomy 4 leads on mid-verse switches (10).

⚠ LIMITS, so nobody over-reads this. The detector counts consonantal endings
(-khem / -tem / -un / attem for plural; final kaf and attah for singular) with a
hand-kept exclusion list for words merely ENDING in kaf (derekh, melekh, betokh,
tidrokh...). It cannot see imperatives, so Deuteronomy 11:26's singular re'eh is
invisible to it. It does NOT collapse a single out-of-step form into the block
around it, so its "blocks" run higher than a careful hand count (Deut 11: 20 here
vs 12 by hand). It is built for COMPARISON between chapters under one consistent
rule, not for the authoritative structure of any one chapter.
"""
import re, subprocess, unicodedata

FALSE_KAF = {"בתוך", "מלך", "דרך", "הדרך", "תדרך", "כדרך", "ודרך", "ארך",
             "בדרך", "לדרך", "מדרך", "ערך", "תמך", "סמך", "אמך", "הלך",
             "ילך", "תלך", "ולך", "מלכך"}


def forms(verse):
    s = unicodedata.normalize("NFD", verse)
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("־", "-")
    out = []
    for w in re.split(r"[\s,;:.\-]+", s):
        if not w:
            continue
        if w.endswith("כם"):
            out.append("PL")
        elif re.match(r"^ו?[א-ת]{2,}תם$", w) or re.match(r"^ת[א-ת]{2,}ון$", w) or w == "אתם":
            out.append("PL")
        elif w == "אתה":
            out.append("SG")
        elif w.endswith("ך") and w not in FALSE_KAF:
            out.append("SG")
    return out


def rate(book, ch):
    t = subprocess.run(["python3", "tools/source_text.py", book, str(ch)],
                       capture_output=True, text=True).stdout
    heb = [m.group(2) for m in
           (re.match(r"^([א-ת]{1,3})\s\s+(.*)$", l) for l in t.splitlines()) if m]
    seq, mid = [], 0
    for v in heb:
        f = forms(v)
        if len({x for x in f}) > 1:
            mid += 1
        for x in f:
            if not seq or seq[-1] != x:
                seq.append(x)
    n = len(heb)
    return n, len(seq), mid, (len(seq) - 1) / n if n else 0


print(f"{'chapter':<16}{'vv':>4}{'blocks':>8}{'mid-verse':>11}{'switches/verse':>16}")
for ch in [1, 4, 5, 6, 7, 8, 9, 10, 11]:
    n, b, mid, r = rate("Deuteronomy", ch)
    star = "  <-- this chapter" if ch == 11 else ""
    print(f"Deuteronomy {ch:<4}{n:>4}{b:>8}{mid:>11}{r:>16.2f}{star}")

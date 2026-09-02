# -*- coding: utf-8 -*-
"""AUDIT the shipped absolute: 'No previous chapter on these pages has come
close to that rate' of singular/plural switching.

Same crude detector for every shipped Deuteronomy chapter, so the comparison is
at least like-for-like. Crude on purpose: it only needs to answer 'is Deut 11
clearly the densest, or not?'
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

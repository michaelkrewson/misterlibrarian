# -*- coding: utf-8 -*-
"""POST-SHIP AUDIT of the shipped claim:
   'the first of twelve such switches ... thirteen alternating blocks ...
    five of the switches happen INSIDE a single verse (v8,v10,v14,v19,v26)'

Rebuild the block map from the verified per-verse forms and count it two ways.
"""

# verified by hand from the archived Hebrew (false positives from words merely
# ENDING in kaf -- betokh, melekh, derekh, tidrokh -- already removed)
V = {
    1:  ["SG"],
    2:  ["PL"],
    3:  [],
    4:  ["PL"],
    5:  ["PL"],
    6:  [],
    7:  ["PL"],
    8:  ["PL", "SG", "PL"],      # metzavvekha embedded in a plural verse
    9:  ["PL"],
    10: ["SG", "PL", "SG"],      # yetsatem embedded in a singular verse
    11: ["PL"],
    12: ["SG"],
    13: ["PL"],
    14: ["PL", "SG"],            # genuine boundary, mid-verse
    15: ["SG"],
    16: ["PL"], 17: ["PL"], 18: ["PL"],
    19: ["PL", "SG"],            # genuine boundary, mid-verse
    20: ["SG"],
    21: ["PL"], 22: ["PL"], 23: ["PL"], 24: ["PL"], 25: ["PL"],
    26: ["SG", "PL"],            # re'eh (sg imperative) + lifneikhem (pl)
    27: ["PL"], 28: ["PL"],
    29: ["SG"],
    30: [],
    31: ["PL"], 32: ["PL"],
}

EMBEDDED = {8, 10, 26}   # a single form out of step, the block resuming after it


def blocks(collapse_embedded):
    seq = []
    for v in range(1, 33):
        forms = V[v]
        if collapse_embedded and v in EMBEDDED:
            # the block's own number is the one that opens AND closes the verse
            forms = [forms[0]] if len(forms) < 3 else [forms[0]]
            if v == 8:      # verse is plural; the singular is the excursion
                forms = ["PL"]
            elif v == 10:   # verse is singular; the plural is the excursion
                forms = ["SG"]
            elif v == 26:   # verse is plural-addressed; re'eh is the excursion
                forms = ["PL"]
        for f in forms:
            if not seq or seq[-1] != f:
                seq.append(f)
    return seq


for label, collapse in (("A. embedded singles treated as EXCURSIONS", True),
                        ("B. every change of form counted", False)):
    b = blocks(collapse)
    print(f"{label}\n   blocks = {len(b)}   transitions = {len(b)-1}   {' '.join(b)}\n")

print("SHIPPED CLAIM: 13 blocks / 12 switches / 5 of them inside one verse")

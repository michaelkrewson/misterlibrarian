# -*- coding: utf-8 -*-
"""One-off audit for the ES atlas-link retarget: classify every hand-authored
enciclopedia.html#slug link in source/es/ into rewrite / leave buckets.

RESULT (2026-08-21, at the commit that added _es_atlas_retarget):
  rewrite (place + ES entry): 56 links / 29 slugs
  leave (place, NO ES entry): {}          <- every linked place already had an ES entry
  leave (non-place):          46 links / 24 slugs (amalek, balaam, caleb, chemosh, ...)
  not in ENCYCLOPEDIA at all: ['tiro']    <- a real dangling link in source/es/matthew-15.html
                                             (the slug is `tyre`); fixed in the same commit.
"""
import re, os, sys
sys.path.insert(0, '.')
import library_data as L

kind = {e["slug"]: e["kind"] for e in L.ENCYCLOPEDIA}
es = set(L.ENCYCLOPEDIA_ES)
slugs = {}
for fn in os.listdir('source/es'):
    if not fn.endswith('.html'):
        continue
    txt = open(os.path.join('source/es', fn), encoding='utf-8').read()
    for s in re.findall(r'href="enciclopedia\.html#([a-z0-9\-]+)"', txt):
        slugs[s] = slugs.get(s, 0) + 1

place_es = {s: n for s, n in slugs.items() if kind.get(s) == "place" and s in es}
place_noes = {s: n for s, n in slugs.items() if kind.get(s) == "place" and s not in es}
nonplace = {s: n for s, n in slugs.items() if s in kind and kind[s] != "place"}
print("rewrite (place + ES entry):", sum(place_es.values()), "links /", len(place_es), "slugs")
print("leave (place, NO ES entry):", place_noes)
print("leave (non-place):", sum(nonplace.values()), "links /", len(nonplace), "slugs:", sorted(nonplace)[:12])
print("slugs not in ENCYCLOPEDIA at all:", [s for s in slugs if s not in kind])

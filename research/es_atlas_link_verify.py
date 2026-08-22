# -*- coding: utf-8 -*-
"""Post-build verification for the ES atlas-link retarget:
  1. every atlas/<slug>.es.html referenced from a built page exists on disk
  2. the built .es.html chapters carry the expected atlas links; EN pages still
     carry theirs
  3. the Spanish toggle lines inside ENGLISH chapter pages inherited the
     retarget too (the _es_panels choke point serving both consumers)

Reusable after any build that touches Spanish place links.

RESULT (2026-08-21, first build with _es_atlas_retarget):
  ES atlas targets referenced: 71 | missing on disk: none
  built ES chapter pages carrying atlas links: 11   (was 0 corpus-wide)
  numbers-21.html esp toggle lines with atlas links: 10
  EN root pages with atlas links: 185 -> 191 (the +6 is those toggle lines, no EN change)
"""
import glob, os, re

refs = set()
es_pages_with = []
for fn in glob.glob("*.html"):
    txt = open(fn, encoding="utf-8").read()
    hits = re.findall(r'href="(atlas/[a-z0-9\-]+\.es\.html)"', txt)
    refs.update(hits)
    if hits and fn.endswith(".es.html"):
        es_pages_with.append(fn)

missing = sorted(r for r in refs if not os.path.isfile(r))
print("ES atlas targets referenced:", len(refs), "| missing on disk:", missing or "none")
print("built ES chapter pages carrying atlas links:", len(es_pages_with))

en21 = open("numbers-21.html", encoding="utf-8").read()
esp_lines = re.findall(r'<div class="esp">.*?</div>', en21)
toggled = [l for l in esp_lines if 'href="atlas/' in l]
print("numbers-21.html esp toggle lines with atlas links:", len(toggled))
print("  sample:", re.findall(r'href="(atlas/[a-z0-9\-]+\.es\.html)"', " ".join(toggled))[:4])

en_atlas = sum(1 for fn in glob.glob("*.html") if not fn.endswith(".es.html")
               and 'href="atlas/' in open(fn, encoding="utf-8").read())
print("EN root pages with atlas links (was 185):", en_atlas)

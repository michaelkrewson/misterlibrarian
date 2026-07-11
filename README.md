# The MisterLibrarian Bible Project

A fresh translation of the Bible into modern English, made from the original Hebrew
(the Masoretic Text) **one chapter at a time**, with the pointed Hebrew reproduced
verse-by-verse and translator's notes comparing every choice against seven landmark
versions: NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the ASV,
and the NWT (1984).

**Live site:** https://michaelkrewson.github.io/misterlibrarian/

## How this repo works

The site is plain static HTML — no framework, no build service. `build.py`
regenerates every page from the project's single content source (the
`mister_translation.html` working file, maintained elsewhere):

```
python3 build.py            # regenerate all pages
git add -A && git commit && git push   # publish
```

To add a new chapter: add it to the source file, register one line in the
`CHAPTERS` list at the top of `build.py` (and bump `NEXT_UP`), rebuild, push.
The chapter page, prev/next navigation chain, Table of Contents progress bar,
and home-page cards all update together.

Translated with Claude; kept by Mr. Librarian.

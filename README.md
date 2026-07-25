# The MisterLibrarian Bible Project

A fresh translation of the Bible into modern English, made from the original Hebrew
(the Masoretic Text) **one chapter at a time**, with the pointed Hebrew reproduced
verse-by-verse and translator's notes comparing every choice against seven landmark
versions: NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the ASV,
and the NWT (1984).

**Live site:** https://michaelkrewson.github.io/misterlibrarian/

## How this repo works

The site is plain static HTML — no framework, no build service. `build.py`
regenerates every page from the project's single content source, kept right
here in this repo at `source/mister_translation.html`. (It used to live in a
separate trading-dashboard repo as a second "working copy" — that caused real
staleness/caching confusion when the two fell out of sync, so as of
2026-07-11 everything lives in one place.)

```
python3 build.py            # regenerate all pages
git add -A && git commit && git push   # publish
```

To add a new chapter: add it to the source file, register one line in the
`CHAPTERS` list at the top of `build.py` (and bump `NEXT_UP`), rebuild, push.
The chapter page, prev/next navigation chain, Table of Contents progress bar,
and home-page cards all update together.

Translated with Claude; kept by Mr. Librarian.

---

## The other site in this repo: `/travel/`

This repo also publishes **The Librarian Abroad**, a travel & food blog, at
`mistertranslation.com/travel/`. It shares the domain and nothing else.

**The two sites are deliberately not linked.** There is no nav entry, no footer
link and no home-page card pointing at `/travel/`, and nothing inside `/travel/`
points back. That separation is the whole point of the arrangement — please don't
"helpfully" add a link between them.

```
python3 build_travel.py            # rebuild the blog
python3 build_travel.py --drafts   # local preview incl. draft: true posts
```

- **A new entry** is one file: `source/travel/YYYY-MM-DD-slug.html`, with front
  matter at the top (copy `source/travel/_template.html`). The index, tag filters,
  archive, prev/next chain, RSS feed and sitemap all regenerate from it.
- **Photos go through the resizer first** — `python3 tools/travel_photos.py <files>`
  writes web-sized copies into `travel/img/` and **strips EXIF, including GPS**.
  Git history is forever, so an oversized or geotagged original committed once can't
  really be taken back out. `--check` audits what's already there.
- **The build refuses to run** on a front-matter typo, a missing summary, or a date
  that disagrees with the filename. That's on purpose.
- **Originals go to S3, not git** — `python3 tools/travel_archive.py add <slug> <files…>`
  puts the full-size photos and any video in the durable blob store, so the Desktop
  copies can be deleted. `list` / `check` / `restore` do what they say. Only the
  web-sized derivatives belong in this repo.
- **`build.py` and `build_travel.py` never touch each other's output** — the Bible
  builder writes only to the repo root and never globs or deletes elsewhere. Keep it
  that way: don't import one from the other.

### How anyone finds it

Being unlinked means no crawler has a path to it, so `travel/sitemap.xml` (regenerated
each build) is the discovery mechanism — it's advertised in the root `robots.txt` and
should be submitted once in Google Search Console. Delete the `Sitemap:` line from
`robots.txt` if you'd rather the blog stayed link-only.

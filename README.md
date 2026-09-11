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
- **The build refuses to run** on a front-matter typo, a missing summary, a date
  that disagrees with the filename, or a `stars:` value that isn't on the scale.
  That's on purpose.
- **A `draft: true` entry gets a real preview link on the live site**, not just a
  local build — every plain `python3 build_travel.py` (no flag needed) publishes it
  to `mistertranslation.com/travel/draft-<slug>.html`, with everything currently in
  draft listed at `/travel/drafts.html`. Same unlinked posture as the rest of this
  blog: `noindex`, no nav link, absent from the sitemap and RSS feed — reachable only
  by that direct URL, which is enough to review on a phone before flipping the front
  matter to `draft: false` and rebuilding. Publishing or deleting a draft prunes its
  stale preview page automatically on the next build.
- **Librarian's Stars** — an optional `stars:` (1–5, halves allowed) turns an entry
  into a review: a rating block under the title, stars on the index card and archive
  row, and schema.org `Review` markup so search results can show the score. Leave the
  line out for a notes entry. ⚠ **The scale only works if it discriminates** — the
  published meaning of each level lives on the About page and *three stars is a good
  meal*; if everything you enjoyed gets five, the rating stops saying anything.
- **General contact is a form** (`write.html`, in the nav) — deliberate: a comment system
  on a static site means adopting Disqus's tracking, a GitHub login, or a server to run,
  and a permanent spam-moderation chore. See the note on `FORM_ENDPOINT`.
- **Per-post comments are X, not a form** (2026-09-09) — the nudge at the foot of every
  published entry is now two links, `blogkit.x_comment_url`/`x_search_url`: one opens a
  pre-filled X post ("Commenting on \<title\>: \<url\> @Mr__Librarian") so a reply posts
  publicly and pings the account directly, the other searches X for every existing post
  mentioning that entry's URL, so a reader can see what others already said. X hosts,
  ranks, and moderates it — this domain runs no comment backend. A **draft** preview keeps
  the old form-based nudge instead (its URL is unlisted, not meant to be posted publicly).
- **Originals go to S3, not git** — `python3 tools/travel_archive.py add <slug> <files…>`
  puts the full-size photos and any video in the durable blob store, so the Desktop
  copies can be deleted. `list` / `check` / `restore` do what they say. Only the
  web-sized derivatives belong in this repo.
- **Voice memos become tasting notes** — `python3 tools/travel_transcribe.py <memo>
  --archive <slug>` transcribes a memo recorded at the table and files the audio plus
  a transcript next to that meal's photos. It runs Apple's **on-device** speech model:
  no API key, no upload, nothing leaves the Mac — which is the point, since a memo is
  Michael's voice in a public place. The texture and the one surprising thing about a
  dish are exactly what's gone by the time the entry gets written, so thirty seconds
  spoken at the table beats any amount of remembering later. ⚠ **Don't take the entry
  from the filename** — Voice Memos names a recording after whatever venue its location
  lookup resolves to, which on a street of restaurants is regularly a neighbour (the
  St Honoré panini memo arrived called "Domaine Serene Wine Lounge"). ⚠ **The transcript
  is a draft, not a quote** — the model mishears menu French ("brie" → "debris"), so the
  archived `.txt` keeps the raw output as evidence and has a CORRECTIONS block to fill
  in beside it. Never publish the audio itself.
- **`build.py` and `build_travel.py` never touch each other's output** — the Bible
  builder writes only to the repo root and never globs or deletes elsewhere. Keep it
  that way: don't import one from the other.

### How anyone finds it

Being unlinked means no crawler has a path to it, so `travel/sitemap.xml` (regenerated
each build) is the discovery mechanism — it's advertised in the root `robots.txt` and
should be submitted once in Google Search Console. Delete the `Sitemap:` line from
`robots.txt` if you'd rather the blog stayed link-only.

---

## The fourth site in this repo: `/health/`

**The Librarian's Regimen** — health, nutrition and medicine, one question at a time, read
from the primary literature — at `mistertranslation.com/health/`. Built by `build_health.py`
(standard library only), the same shape as the Ledger's writing half: dated entries in
`source/health/`, a tile/list front page with tag filters and search, per-tag pages, RSS and a
sitemap. It is linked from the home-page hub and from the other two blogs' nav/footer.

```
python3 build_health.py            # rebuild the blog
python3 build_health.py --drafts   # LOCAL preview incl. draft: true entries — never commit one
```

- **A new entry** is one file: `source/health/YYYY-MM-DD-slug.html` (copy
  `source/health/_template.html`; its header comment is the checklist).
- **There is no published drafts page** — unlike `/travel/`, an entry here ships straight
  live. `draft: true` simply keeps it out of the build.
- **Every entry must end with a `<ol class="sources">`** — the build refuses one without it.
- **Nothing on it is medical advice**, and the site says so on every page; keep it that way.
- **Spanish edition:** an entry's twin is the same file with `.es.html`
  (`source/health/YYYY-MM-DD-slug.es.html`); the Spanish front page is `health/es.html`, and
  About / Ask / Disclaimer have `.es.html` twins. Both editions build from the one command.

---

## The fifth site in this repo: `/notebook/`

**The Librarian's Notebook** — a commonplace book: science and technology, the world, arts
and culture, and whatever else didn't fit the other four — at
`mistertranslation.com/notebook/`. Built by `build_notebook.py` (standard library only), the
same shape as the Regimen's writing half: dated entries in `source/notebook/`, a tile/list
front page with tag filters and search, per-tag pages, RSS and a sitemap — **plus a fixed
`section:` on every entry** (`technology` / `world` / `culture` / `notes`), each with its own
nav link and page. It is linked from the home-page hub and from the other three blogs'
nav/footer.

```
python3 build_notebook.py          # rebuild the blog — that's the whole CLI
```

- **A new entry** is one file: `source/notebook/YYYY-MM-DD-slug.html` (copy
  `source/notebook/_template.html`; its header comment is the checklist). `section:` is
  required and must be one of the four above; the build refuses anything else.
- **There are no drafts at all** — no `draft:` key, no `--drafts` flag, no preview page.
  Every file in `source/notebook/` builds and ships.
- **Sources are optional** (an opinion piece may have none), but an `<ol class="sources">`
  renders the same as on the Regimen when an entry has one.
- **What goes here vs. the Ledger:** if the spine of a piece is a price, a balance sheet, or
  an institution that moves money, it's the Ledger; otherwise it's here.

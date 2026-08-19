# MisterLibrarian — Claude instructions

This repo publishes **three separate things at mistertranslation.com**:

1. **The Bible project** (site root, `build.py`) — a fresh translation of the Bible into
   modern English, made from the original Hebrew/Greek one chapter at a time, with the
   source text reproduced verse-by-verse and notes comparing every rendering choice
   against a fixed shelf of landmark versions.
2. **The Librarian Abroad** (`/travel/`, `build_travel.py`) — Michael's travel & food blog.
3. **A finance board** (`/finance/`, `build_finance.py`) — a standing "world's largest
   assets by market cap" board, built offline from a JSON snapshot.

**Read `README.md` first** for the mechanical how-to (build commands, how to add a chapter
or a travel entry, publishing). It's well-maintained and this file doesn't repeat it. This
file is the layer README doesn't cover: translation doctrine, editorial judgment calls,
paid-for gotchas, and the conventions that only show up once you've been burned by them.

## The one relationship rule that must hold

**The Bible project links to neither of the other two publications, and is linked from
neither.** No nav entry, no footer link, no home-page card, nothing pointing back. This is
deliberate, not an oversight — don't "helpfully" add a cross-link.

**The Librarian Abroad and the finance board DO link to each other** (Michael's call,
2026-08-07) — nav, footer, entry-to-entry references are fine between those two.

Each of the three builders (`build.py`, `build_travel.py`, `build_finance.py`) writes only
inside its own output area and never globs or deletes elsewhere — that discipline is what
lets all three coexist safely in one repo. Keep it that way; don't import one builder from
another.

## Before touching anything — verify, don't assume

- **Check the actual repo/live site, not `ls`/`grep` guesses.** Chapter build slugs are not
  always consistent (John's are `john1`/`john2` but `jhn3+`), and template shape can drift
  *within* a book, not just between books — always re-read a sibling chapter's raw HTML
  before assuming a pattern holds. `curl` the live pages directly when checking what's
  actually shipped; don't trust a stale claim in a memory note.
- **Chapter progress lives in the `CHAPTERS` list at the top of `build.py`** (and the live
  site) — that's the source of truth for what's translated, not a status paragraph in this
  file. Don't add a "current progress" snapshot here; it will be wrong within days and
  nobody will remember to update it. (See "Deep history" at the bottom for where the
  book-by-book log actually lives.)
- NT chapters use a different template family than OT chapters (`.grk` + red-letter
  `<span class="rl">` + `.info-block` vs `.heb` + `.chnote`).
- Read the **previous chapter's closing info-block** before starting a new one — "Patterns
  worth carrying forward" is the open-threads ledger (echoes promised, teasers planted).

---

## Translation doctrine (settled — don't re-litigate)

- **Source, OT:** Masoretic Text only, as printed at Mechon-Mamre (`mechon-mamre.org/p/pt/pt01NN.htm`
  — needs a browser UA or Cloudflare 403s it). Variants (LXX/Samaritan/DSS) are **noted, never
  adopted** — e.g. a gap in the Hebrew is bracketed, not silently patched from another witness.
- **Source, NT:** the critical Greek text (Nestle/Alexandrian eclectic tradition), with a named
  apparatus — Nestle 18th ed. 1948, Bover, Merk; Codex Vaticanus (B/03) and Sinaiticus (א/01);
  early papyri P52/P66/P75/P46. ⚠️ The papyri and Nestle/Bover/Merk are **NT-only** — for Genesis,
  Vaticanus starts at 46:28 and Sinaiticus's Genesis survives only in fragments, so neither is a
  usable OT witness there; the printed critical LXX fills that role instead.
- **Register: essentially literal, natural modern English.** Keep cognate wordplay ("swarm with
  swarms"), keep Hebrew narrative's repetition (trimming it is editing), keep article patterns,
  keep root echoes in English where possible.
- **Every rendering must pass a READER check, not a lexicon check.** The question is *what will
  an English reader take this to mean* — not *can the word mean this*. No calques ("standing-under"
  for hypostasis), no translationese, no hedging between two senses via a hyphenated literalism
  (that just moves the difficulty onto the reader instead of resolving it — pick the best real
  rendering and put the range in the note). Strangeness is fine, even good, but only when it's
  strange enough to send the reader to the note — smooth-but-wrong is the worst outcome because it
  fails silently. Check the English and Spanish twins against each other; a divergence between them
  is a signal one is off.
- **NT fixed rendering — `ekklēsia` → "congregation"**, never "church" (a different Greek word,
  *kyriakon*, is where "church" descends from; Tyndale's rendering, forbidden by King James's Rule
  3). Applies to every NT chapter. "House-church" (the archaeological *domus-ecclesiae* term)
  stays as its own thing.
- **Other fixed renderings, established — search the source file's existing notes before inventing
  a new one for a recurring word; consistency is the product:** "vault" (raqia, not firmament),
  "side" not "rib" (tsela — the flagship departure), "humankind/the human" (generic adam),
  "a helper corresponding to him" (ezer kenegdo), "appointed times" (mo'adim), "the LORD" small-caps
  (YHVH), "Look —" (hineh), "my bow" not "rainbow" (qeshet), "great sea-beasts" (taninim).
- **Neutrality rule:** where traditions genuinely split (protoevangelium, sons-of-God, "like
  God/gods"), present the readings with their pedigrees and don't vote. A doctrinal rendering in a
  shelf version (e.g. NWT's "active force") gets flagged as doctrinal, factually, not dismissively.
  Historical abuses of a verse (curse-of-Ham/slavery, witch-trial readings) get named plainly, then
  explained as a misreading — state the documented misuse as fact first, then correct it.
- **Honesty habits:** hapax/uncertain words are said to be uncertain; anachronisms are acknowledged
  in the text itself; source-critical seams are shown, not sanded — described as "readings differ,"
  not resolved by fiat.
- **The seven-version shelf (fixed):** NIV 2011, KJV, Douay-Rheims (translates the Vulgate — its
  divergences usually trace to Latin, not Hebrew/Greek), The Living Bible, Geneva 1599, ASV, NWT
  1984. Quote the copyrighted ones (NIV/TLB/NWT) only in short phrases.
- **⚠ Always compare the NWT's exactness — don't default to the familiar rendering.** The NWT 1984
  and the ASV are usually the two *most literal* witnesses on the shelf, despite the NWT's doctrinal
  reputation. For every verse, check what they do; where either is tighter to the source than the
  familiar (KJV/NIV) rendering *and* carries no doctrinal axe, follow it on the merits. Never frame
  agreement with the KJV as a virtue in itself — that's popularity over precision, the opposite of
  this project's reason to exist.
- **The Spanish shelf** gets the identical treatment: `TNM` (the Spanish New World Translation) is
  the Spanish analog of the NWT — apply the same exactness rule, flag the same class of doctrinal
  renderings (e.g. *ruach*/*pneuma* → "fuerza activa"). Reina-Valera spans a register the English
  shelf has no single equivalent for — use RV antigua (1909, archaic) and RV60/NVI (modern) as a
  *spectrum* for a register check, separate from the TNM exactness check. **Order of operations:**
  do the Hebrew/Greek work first, compose the Spanish verse independently from that source work
  (never translated from the English), *then* pull the Spanish shelf into the notes as a tiebreaker
  — shelf phrasing belongs in notes only, never in the verse text's own cadence.
- **Give near-synonyms their own dictionary entries — don't lump a word-family together.** Hebrew
  keeps related words distinct (a wisdom vocabulary of six near-synonyms is six entries, not one),
  and the translation + dictionary should too.
- **Historically-weaponized verses** (a text used to justify slavery, witch trials, antisemitism)
  get named-and-explained treatment: state the documented misuse as fact, then explain why it's a
  misreading — don't soften or skip past it.

## Note-writing doctrine

- Per-verse notes are grouped where verses share one issue; genealogies get fewer, grouped notes
  (the repetitive formula *is* the point).
- **The signature move is the echo system:** flag a word/root the first time it appears, promise
  its return, pay it off when it recurs. Every chapter's closing info-block lists which echoes were
  paid and planted, plus a one-line teaser for the next chapter.
- Name-puns are always surfaced (transliteration in em-dash, the Hebrew/Greek phrase in the note).
- **Shelf density is enforced by the build**, not just editorial intent — `build.py`'s
  `check_shelf_density()` fails the build if a chapter's notes carry fewer than 3 shelf-comparison
  tags. Write the comparisons as you translate, not retroactively; a genuinely low-shelf chapter
  needs an explicit exemption, not a default pass. When quoting the shelf, never print "the LORD"
  even inside a version's verbatim quote — paraphrase or pick a quote that avoids it (ASV prints
  "Jehovah" natively, which is handy here).

## Per-chapter checklist

1. **Get the source chapter FROM OUR OWN ARCHIVE — never curl the supplier.**
   `python3 tools/source_text.py <Book> <Chapter>` (add `--raw` for the archived
   file itself). All 1,189 chapters of Hebrew and Greek were mirrored to
   `source/originals/` and to private S3 months ago; hitting Mechon-Mamre or
   helloao live for a file we already own is slower, ruder, and breaks the day
   they do. Resolution is local → S3 → (only with `--allow-live`) upstream, and
   the local copy is checked against `MANIFEST.json`'s sha256 so a corrupted
   scroll is caught instead of translated. ⚠️ `source/originals/` is gitignored,
   so it exists **only in the main checkout** — the tool resolves the archive
   root via `git rev-parse --git-common-dir` for exactly that reason; don't
   "fix" it to a repo-relative path or every worktree silently re-pulls from S3.
   Then verify the verse count.
2. Add the chapter to `source/mister_translation.html` (the project's single content
   source, in *this* repo — not a second working copy anywhere else).
3. Validate: div balance, anchor resolution, verse counts, shelf density (the build enforces
   this last one). `build.py` also runs `check_forward_claims()` (every "not yet on these
   pages" / "already translated" / "next in sequence" claim gets checked against the real
   registries, both languages) and `check_local_anchors()` (every in-chapter href must
   actually resolve) — read a build failure from either as real, not noise.
4. **Grow the library** for this chapter, all five parts — a missing one fails silently, no
   build error:
   - `DICTIONARY` (English) — new/extended terms this chapter's notes lean on
   - `DICTIONARY_ES` — the **same slugs**, no exceptions; the Spanish site is a first-class
     page, not a courtesy translation
   - `ENCYCLOPEDIA` — do this chapter's people/places exist *at all* yet?
   - `ENCYCLOPEDIA_ES` — Spanish for every entry the chapter touches
   - Atlas coords for every new `kind: "place"` entry (mark a guess `approx: True`)
   `build.py`'s `check_library_parity()` prints the running English/Spanish gap on every
   build — watch that the number doesn't grow on a chapter you just shipped.
5. **Write the note headings SEO-first.** The meta description and JSON-LD are automatic
   from the chapter's teaser (`check_seo()` guards them) — the one manual step per chapter is
   writing `<h3>` note headings that *lead* with the term someone would actually search for,
   then the literary line ("Hypostasis — substance, assurance, or a title-deed? Two words,
   and one of them decided a century of councils," not the literary half alone). The site
   will never outrank BibleGateway/BibleHub on head terms ("Hebrews 11") — its winnable
   ground is the long tail its notes uniquely answer.
6. **Check `VIDEO_QUEUE` in `library_data.py`** at the moment you write a new `ENCYCLOPEDIA`
   entry for a person/place — that's exactly when a queued archaeology video (from Michael's
   trusted Expedition Bible channel) is usually waiting to be placed into it. This is a
   per-entry check, not a per-book intention — skipping it for a whole book has happened and
   left a queued video unplaced past the chapter it was meant for.
7. Register the chapter: one line in `CHAPTERS` in `build.py`, bump `NEXT_UP`.
8. **Run a CLAIMS PASS — separate from, and after, every check above.** ⚠ Paid for twice in
   one night (Numbers 7 and Numbers 8, 2026-08-18): every structural check passed, the build
   was green, and both chapters still shipped false statements — because the build validates
   *structure*, never *assertions*. `check_local_anchors()` proves a link resolves;
   `check_forward_claims()` proves a chapter exists. **Neither one reads what you said about
   it.** Numbers 8's headline claim ("the first time the lampstand is lit") was refuted by
   Exodus 40:25 — already shipped, and linked from a note *in that same chapter* — and it
   had propagated to six places including a brand-new dictionary entry. Re-read every
   asserting sentence and check:
   - **Absolutes are guilty until proven** — "first / only / never / every / the one place."
     Grep the shipped source for the counter-example *before* keeping the word. ⚠️ For a claim
     about the HEBREW ("occurs once", "the first time in the Bible"), grep the actual text, not
     a memory or a web search: `python3 tools/heb_search.py <hebrew>` searches all 929 archived
     OT chapters consonantally (`--book X`, `--count`). It matches **letters, not lemmas**, so
     read the hits rather than quoting the tally — the calibration case is Nephilim, where the
     defective spelling returns 20 verses of which only 2 are the word. Numbers 14's four best
     notes were all found this way, and the same pass killed a false "first time Israel proposes
     killing its own leaders" that Exodus 17:4 — already on these pages — refutes. Both of
     Numbers 8's worst errors were absolutes ("first time it is lit"; "every other *tenufah*
     waves a piece of an animal" — Leviticus 23:20, already on these pages, waves two LIVE
     lambs).
   - **Recompute every number.** If a sentence says "two breaks" and then lists three, that
     is a shipped contradiction (it was). If it states a ratio, do the division (Numbers 7
     claimed 5× where the real figure was ~4.25×).
   - **Open every chapter you cite** — its actual shipped text, not just proof the file
     exists. Cross-reference *existence* and cross-reference *substance* are different checks
     and only the first one is automated.
   - **FETCH every shelf quote you print. Never write one from memory.** ⚠ Added after
     Numbers 10 (2026-08-18) printed four renderings of 10:36 unfetched: ASV came out
     misquoted ("the ten thousand thousands" for its actual "the ten thousands of the
     thousands"), and worse, the sentence claimed the shelf split along the *eleph*
     thousand/clan seam when **not one of the five versions reads "clan" there** — a false
     causal claim resting on quotes that were never checked. The tell is that the three
     preceding chapters got this right *by habit*, which is precisely why it failed the
     moment attention was elsewhere: an unwritten rule is not a rule. Fetch the parallel
     page, paste the wording, and only then say what the shelf is doing.
   - **Run the shelf rule on BOTH shelves, and re-run it on every version's own
     REVISION.** ⚠ Added after Numbers 12 (2026-08-18), where the rule directly above
     was obeyed for the English shelf and skipped entirely for the Spanish one — six wrong
     claims in one chapter, all written from memory. The worst inverted the chapter's central
     note: it told a Spanish reader the RV60 "conserva «boca a boca»" when the RV60 reads
     "Cara a cara." Two specific traps this class keeps setting. (a) **The Reina-Valera is not
     one version.** The doctrine above calls RV antigua (1909) and RV60/NVI a *spectrum*; both
     Spanish errors that mattered came from attributing the antigua's archaic reading to the
     RV60, which had revised it away. Fetch the edition you are naming. (b) **A version's own
     revision is a different witness.** NWT 1984 "Mouth to mouth" → 2013 "Face-to-face";
     RV antigua "Boca á boca" → RV60 "Cara a cara"; TNM 2019 "cara a cara". Naming the wrong
     edition is the same error as naming the wrong version — and checking both editions is
     usually where the better note is hiding, since a shelf that moves across four centuries
     says more than a shelf frozen at one date.
   - **Check what you assert ABOUT a list, not just the list.** The members and the count can
     all be right while the predicate binding them is wrong — Numbers 9 called four cases
     "a law made in response to a complaint" when two were prosecutions, and Numbers 10
     titled a note "the same blast for war and for festival" when the Hebrew uses *heria*
     in one verse and *taqa* in the other, inverting the chapter's own point.
   - **DIFF THE TWINS, mechanically, verse by verse.** The doctrine section above already
     says a divergence between the English and Spanish is a signal one of them is off &mdash;
     but saying it is not doing it, and Numbers 13 (2026-08-18) shipped with three, none of
     which any other check could see. v21 had the English printing the place-name
     `Lebo-hamath` while the Spanish translated the phrase (`a la entrada de Hamat`), so the
     two twins were taking opposite sides of a live scholarly question; v20's `fat or lean`
     became `f&eacute;rtil o magra`, breaking the very pair the note points at; and vv22/28
     kept the Hebrew's definite article in English (`the offspring of THE Anak`) and dropped
     it in Spanish. Print the two verse texts side by side and read them &mdash; it takes one
     throwaway script and finds what nothing else does. Two useful corollaries it surfaced:
     a divergence usually means **neither** side has a note (v21's strange English word
     appeared twice with nowhere to send the reader), and the fix is often to make both sides
     strange and explain it once, not to smooth one of them.
   - **AND DIFF THE NOTES, not just the verses.** ⚠ Added after Numbers 14 (2026-08-18), where
     the verse twin-diff was run exactly as written above, came back clean, and missed
     everything — because the rule said *verse by verse* and the notes are where the claims
     actually live. A post-ship read found **nine chapters cited as live links in English and
     as dead prose in Spanish** (Nehemiah, Exodus 14/17/32/34, Genesis 15/37, Numbers 1,
     Deuteronomy 1): the Spanish reader was being told *ya en estas páginas* with no way to get
     there. Diff per note id — paragraph count, shelf tags, digits, and the set of outbound
     links — and treat a link present on one side only as a defect until proven otherwise.
     Two legitimate exceptions exist and should be *flagged rather than linked*: a chapter with
     no Spanish edition takes `numbers-13.es.html`'s wording, "ya en estas páginas, todavía no
     en español". ⚠ And check that a citation's link actually points at the chapter it names —
     "Nehemiah 9:17" linked to `nehemiah-1.html` survived this chapter's own composition-time
     fix of the identical bug on Galatians 3:11, because the fix was applied to the instance
     that was noticed and not swept for its parallels.
   - **A fix written during the review is not exempt from the review.** ⚠ The Lebo-hamath
     note added while FIXING the above put the NWT 1984 on the wrong side of the shelf split
     (it reads &lsquo;to the entering in of Ha&rsquo;math&rsquo;, the phrase reading, not the
     name). New prose written in an audit feels like a correction and therefore trustworthy;
     it is just prose, and needs the same fetch-and-check as the prose it replaces.
   - **Diff the bookkeeping.** A chnote saying "X and Y extended, N new entries" must match
     `git diff library_data.py`. Numbers 8 claimed two entries extended when only one was.
   - When a claim fails, prefer the one that survives — it is usually the better note anyway
     (Moses handing the lamps to Aaron beat the false "first lit"; the
     object → piece → live-animal → living-people escalation beat the false "every other").
9. `python3 build.py` → commit → push. GitHub Pages rebuilds in ~30–90s; poll the live URL
   to confirm.

## Library architecture

- **Concordance is generated**, not curated — indexes this translation's actual English
  ("vault," not "firmament") at build time. Never hand-edit it.
- **Dictionary / Encyclopedia / XREFS are curated** in `library_data.py`, grown per chapter
  per the checklist above.
- **Routes and Regions are hand-drawn inline SVG maps** (`ROUTES` / `REGIONS` in
  `library_data.py`), deliberately no external map library — real lat/lon math, a
  cos-lat-equirectangular projection, numbered stops or boundary polygons over a basemap of
  fixed geographic features. **Honesty is load-bearing:** a route's caption states which legs
  are reconstructed vs. located; a region's outline is drawn **dashed** so it never looks
  surveyed, and carries its own caveat naming which edges are real geography vs. which fade
  into desert. A genuinely unknown place (Eden, Havilah) gets no polygon at all — a region
  too vague to bound honestly just isn't drawn, rather than drawn wrong.
- **Any hand-drawn schematic map needs a distinct land color, not just accurate geometry.**
  A geometrically-correct SVG map with no land/water contrast still reads as "all ocean" —
  proven the hard way on a route map that was pixel-verified correct and still failed the
  "does this look like a real place" test. Pair every schematic with a real embedded
  OpenStreetMap iframe alongside it (`osm_embed` for a point, a bbox variant for a route/
  region) — the schematic carries the narrative (numbered stops, notes, verse refs) a real
  map can't show; the real map carries actual terrain and place names the schematic can't.
  Do both, not one or the other. Before calling any map work done, look at the actual
  rendered screenshot and ask whether it reads as a real place — not just whether the
  geometry checks out.

## The Librarian Abroad (`/travel/`)

- **A new entry is one file:** `source/travel/YYYY-MM-DD-slug.html`, front matter then plain
  HTML (copy `source/travel/_template.html`). The build fails loudly on a typo'd key, a
  missing required field, or a filename date that disagrees with the front matter.
- **Photos are the source, not optional context.** If Michael says photos exist but they
  aren't attached, go get them — Photos.app AppleScript automation is already granted on his
  Mac (`tell application "Photos"`, walk `media item -(i+1)` in a loop since date-filter
  `whose` clauses and index ranges both throw; read `location` for real GPS *before*
  exporting, since export-with-originals strips it from the file). **Every photo must go
  through `python3 tools/travel_photos.py <files>`** before it can be used — it resizes to
  web size and strips EXIF including GPS. Git history is forever; an oversized or geotagged
  original committed once can't really be taken back out. HEIC sources need `sips -s format
  jpeg -Z 1600 in.HEIC --out out.jpg` first (this machine's Pillow has no HEIC plugin).
- **Ask for a voice memo before writing a food entry.** Michael records ~30-second memos at
  the table; the sensory detail he actually noticed is exactly the part a photo or menu can't
  reconstruct, and it's the part worth reading an entry for. `python3
  tools/travel_transcribe.py <memo> --archive <slug>` runs Apple's on-device speech model —
  no upload, nothing leaves the Mac, deliberately, since a memo is his voice in a public
  place. ⚠️ **The memo's filename names the wrong venue** (Voice Memos names a recording
  after whatever its location lookup resolves to, which on a restaurant street is often a
  neighbor) — never infer the entry from the filename, ask. ⚠️ **The transcript is a draft,
  not a quote** — the model mishears menu terms; correct it in the archived transcript's
  CORRECTIONS block, don't overwrite the raw output.
- **Writing in Michael's first-person voice is normal and welcome** — that's the job, not a
  risk to hedge on. What matters is a *place*, not a permission: it goes into the drafts
  pipeline (`draft: true` → build → push → he reads it at
  `mistertranslation.com/travel/drafts.html`) before it's public, because he's the
  proofreader and that page exists for him to read on his phone. Don't skip straight to `main`.
- **Never invent a specific he didn't give you** — a dollar figure, a time, a founder detail,
  or (twice now, the standing failure mode to actually watch for) *his own experience of a
  dish*. Describing food from a photo is fine; saying he tasted it and liked it is not, unless
  it's in the photo, the memo, or something he actually told you. Per-sentence test while
  drafting: is this in a photo, or did he say it? If neither, cut it.
- **Librarian's Stars** (`stars: 1–5`, halves allowed) turns an entry into a review — only
  worth printing because the scale can say no. Three stars is a good meal, five is meant to
  stay rare; the published meaning lives on the About page. A post with no `stars:` renders
  no rating.
- **Readers write in via a form** (`write.html`), not comments — deliberate, to avoid
  trading the site's no-tracking posture for Disqus or a moderation chore on a notebook
  written irregularly by design.
- **Originals + video go to S3** via `python3 tools/travel_archive.py add <slug> <files...>`
  — content-addressed by sha256, so `add` is idempotent. ⚠️ The slug is the tool's **first
  positional argument** — a bare glob with no explicit slug silently makes the first matched
  photo the slug instead. Always write the slug explicitly and read the tool's own last line
  (`archived … under '<slug>'`) to confirm what it actually used.

## The finance board (`/finance/`)

Standard-library-only build (`build_finance.py`), deliberately no network dependency in the
build itself — a separate fetcher (`tools/fetch_asset_board.py`) writes the data snapshot;
the builder only reads it. Newer addition than the other two publications and not yet
deeply documented here beyond the relationship rule above (links with `/travel/`, not with
the Bible project) — check the builder's own docstring and `tools/fetch_asset_board.py`
before assuming its conventions match the other two sites.

## Source archive

**Read from it. That is the whole point of it.** ⚠️ Paid for 2026-08-18: the
archive had existed since July and *every* chapter since was still started with a
live `curl` to Mechon-Mamre, because the checklist said "fetch the source chapter"
and nothing pointed at the copy we already had. `tools/source_text.py` now exists
so the archive is the path of least resistance (see checklist step 1) — use it,
and if it ever misses, repair the archive rather than reaching past it.

The translation's upstream suppliers (Mechon-Mamre Hebrew, the SBLGNT Greek via
bible.helloao.org) could vanish; shipped chapters embed their own source text, but
untranslated chapters exist only upstream. `python3 tools/archive_sources.py` downloads
**whole books** (not just translated chapters), sha256-manifests them, and mirrors to the
fleet's private S3 (`blobs/bible_sources/...`; restore via `market_data_store.get_blob`).
**Private by design** — `source/originals/` is gitignored; the repo is public via GitHub
Pages and this archive exists to insure the workflow, not to redistribute copyrighted source
editions. Add a new book by adding one line to `MECHON_BOOKS` or `SBLGNT_BOOKS` and re-running
the script (idempotent — only fetches what's missing).

## SEO / discovery

- Two sitemaps (`/sitemap.xml` for the Bible project, `/travel/sitemap.xml` for the blog),
  both listed in `robots.txt`. The travel sitemap is that blog's *only* discovery path since
  it's deliberately unlinked from everything.
- `lastmod` in the sitemap comes from git history, not file mtime (every build rewrites every
  file, so mtime would stamp "today" on everything, always).
- The ~3,800 `/v/` per-verse stub pages are deliberately **excluded** from the sitemap — they
  exist to give a shared verse its own link-preview card, not to be indexed; listing a
  `noindex` URL in a sitemap is a reported Search Console error, not a bonus.
- `page(...)`'s `url=` argument controls **both** the canonical tag and `og:type` at once
  (`og_type = og_type or ("article" if url else "website")`). Passing `url=` to fix a missing
  canonical on a hub/index page (home, table of contents, dictionary index) will silently
  flip its `og:type` to "article" unless you also pass an explicit `og_type="website"`.
- hreflang lives in the **sitemap**, as reciprocal `<xhtml:link>` entries per `.es.html`/
  `.html` pair — not as `<link>` tags in the page `<head>`.
- Search Console ownership is verified via `google3b2c8b57143d235a.html` at the repo root
  (a single verification line). **Never delete it** — Google re-checks it periodically.

## Known gaps — not yet documented here

`gen_audio.py`, `audio-reader.js`, `player-clips.js`, `reader-notes.js`, `reading.js`, and
`share.js` all exist in this repo but haven't been reverse-engineered into this file yet —
read them directly before touching that surface rather than assuming this doc covers it.

## Deep history

Two memory files carry the full book-by-book chapter log and the complete extended methods
doctrine — they're large (thousands of lines each, grown as an append-only running log) and
this file deliberately does **not** try to compress them wholesale, since a live status
snapshot goes stale the moment it's written. Read the **dated tail** (newest entries at EOF)
of `project_misterlibrarian_site` and `project_misterlibrarian_methods` in the memory system
before starting a new book, or when this file's doctrine and the actual code disagree — trust
the code and the live site over any memory note, this file included.

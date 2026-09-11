# MisterLibrarian — Claude instructions

This repo publishes **four separate things at mistertranslation.com**, reached through a
hand-written 4-card hub at the bare domain root (`index.html`, no builder of its own —
added 2026-09-09 with three cards; the fourth 2026-09-10):

1. **The Bible project** (`/bible.html`, `build.py`; moved off the bare root 2026-09-09 when
   the hub took over `/` — see below) — a fresh translation of the Bible into modern English,
   made from the original Hebrew/Greek one chapter at a time, with the source text reproduced
   verse-by-verse and notes comparing every rendering choice against a fixed shelf of landmark
   versions.
2. **The Librarian Abroad** (`/travel/`, `build_travel.py`) — Michael's travel & food blog.
3. **A finance board** (`/finance/`, `build_finance.py`) — a standing "world's largest
   assets by market cap" board, built offline from a JSON snapshot.
4. **The Librarian's Regimen** (`/health/`, `build_health.py`) — a blog on health,
   nutrition and medicine, one question at a time, read from the primary literature.
   Added 2026-09-10; see its own section below.

**Read `README.md` first** for the mechanical how-to (build commands, how to add a chapter
or a travel entry, publishing). It's well-maintained and this file doesn't repeat it. This
file is the layer README doesn't cover: translation doctrine, editorial judgment calls,
paid-for gotchas, and the conventions that only show up once you've been burned by them.

## The relationship rule — RETIRED 2026-09-09, all three now cross-link via the hub

**This used to say the Bible project links to neither of the other two publications and is
linked from neither.** That isolation was deliberate (see git history / RETIRED.md-style
context below), but Michael dropped the concern that motivated it and asked for a top-level
hub at `/` with one card per publication — Bitcoin & Finance, Food & Travel, and Religion
(the Bible project) — so all three are now mutually reachable through it. **Don't reintroduce
the isolation** — the current, correct state is: hub → all three; Bible project → back to the
hub only via its own nav's brand-name conventions (it doesn't carry a hub link of its own
today, and none was asked for); Librarian Abroad ↔ finance board still link directly to each
other too (Michael's call, 2026-08-07), unaffected by the hub's addition.

**Why the Bible project's own pages didn't move:** `build.py` still emits ~2,772 pages at the
SAME root-level URLs they've always had (`genesis-1.html`, `toc.html`, etc.) — moving them
under a subpath would have broken every indexed URL for zero benefit. Only the ONE page that
used to occupy the bare root — the project's own homepage — moved, to `bible.html`
(`build.py`'s `HOME_URL` constant; every page's nav/brand link was repointed there in one
pass). The bare root itself is now the hub's file, not a `build.py` output at all.

Each of the four builders (`build.py`, `build_travel.py`, `build_finance.py`,
`build_health.py`) writes only inside its own output area and never globs or deletes elsewhere — that discipline is what
lets all three coexist safely in one repo. Keep it that way; don't import one builder from
another. The hub's `index.html` follows the same discipline by construction — it's a single
static file with no generator, so there's nothing for a builder to accidentally clobber it
with, and nothing it can accidentally glob into any of the three builders' own outputs.

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
- **Where the shelf text comes from — `tools/shelf_text.py`, not memory and not a search snippet.**
  ⚠ Added 2026-08-19 after Numbers 14 shipped with **no NWT comparison at all**: `wol.jw.org`
  returns an empty shell to WebFetch, so the NWT was the one shelf version with no fetch path, and
  the search snippet that surfaced instead was almost certainly the 2013 revision wearing the
  1984's name. The page is in fact plain server-rendered HTML — **WebFetch was the problem, not the
  supplier** — and a browser User-Agent gets the whole chapter. WOL serves the **NWT 1984**
  (`Rbi8`), the **NWT 2013**, the **TNM 1987** and **TNM 2019**, and also the **ASV** and **KJV**,
  so one command covers most of both shelves:

      python3 tools/shelf_text.py Numbers 14                  # NWT 1984 (the default)
      python3 tools/shelf_text.py Numbers 12 --all --verses 8 # the whole shelf, both languages
      python3 tools/shelf_text.py Numbers 12 --version tnm2019

  It is **archive-first** like [[tools/source_text.py]] — local `source/shelf/` → private S3
  (`blobs/bible_shelf/`) → live — so a chapter is pulled from the supplier at most once, and WOL
  going away or changing its markup can no longer cost us a witness. **The edition guard is the
  point:** every WOL page names its own publication in the `<article>` class, and the tool asserts
  that against what you asked for and *refuses to print* on a mismatch — so quoting the 2013
  revision as the 1984 cannot happen silently, which is exactly the error the revision rule below
  names. The DRB / Geneva / NIV / TLB are not on WOL and still need their own fetch.
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
- **No sentence in a published page may be about OUR OWN drafting/building process — every
  sentence is about the text, for the reader, or it doesn't ship.** (Michael's call, 2026-09-09,
  after Numbers 36's "A correction the new chapter found in the old ones" paragraph — a whole
  note about a site-internal encyclopedia-linker bug just fixed — read to him like the build log
  talking to Claude instead of notes helping a reader understand a word or phrase.) This kills, on
  sight: "an earlier draft of this page said…", "this site's own automatic linking had a bug…",
  "a new entry was written and then deleted…", "the note was drafted saying X; fetching Y inverted
  it…", "composing a chapter is a good time to audit the machinery…" — all real, all shipped
  (Numbers 36; three more in Psalm 139/Job and Hebrews 11). The published page is the finished
  product; readers should never be able to tell it was revised along the way, only that it's
  right. **"Patterns worth carrying forward" is the one place this discipline slips most often**
  — its own doctrine (below) is a reader-facing translation-philosophy summary + next-chapter
  teaser (see Genesis 1's, the original), but on many later chapters (Numbers 34–36 among them) it
  quietly turned into a QA/audit journal — "the claim was written here, tested, and found false",
  "the search needed to be done on the causative form" — addressed to the next Claude session, not
  to the reader. If a paragraph's subject is the chapter's own composition rather than the Hebrew/
  Greek/English/Spanish text, cut it; don't launder it into "Patterns" just because that heading
  exists. **If something genuinely needs to persist for the next chapter's Claude session and
  isn't reader content, it does not go in the public page at all** — there is no private channel
  for it today, so either it's reader-worthy prose or it doesn't get written down; don't invent a
  workaround that lands it on the page anyway. A full sweep of the other 257 "Patterns worth
  carrying forward" paragraphs for this same drift has NOT been done — only Numbers 36 has been
  fixed; ask before doing the rest, it's a large review.
- Name-puns are always surfaced (transliteration in em-dash, the Hebrew/Greek phrase in the note).
- **Shelf density is enforced by the build**, not just editorial intent — `build.py`'s
  `check_shelf_density()` fails the build if a chapter's notes carry fewer than 3 shelf-comparison
  tags. Write the comparisons as you translate, not retroactively; a genuinely low-shelf chapter
  needs an explicit exemption, not a default pass. When quoting the shelf, never print "the LORD"
  even inside a version's verbatim quote — paraphrase or pick a quote that avoids it (ASV prints
  "Jehovah" natively, which is handy here).

## Public notes (X) — chapter / dictionary / encyclopedia / atlas / route pages

**Added 2026-09-09 (Michael's call), simplified and repositioned the same day.** Every chapter
page, dictionary/encyclopedia/atlas entry page, and route page carries a bare two-button row
(`build.py`'s `_note_nudge()`, class `.notebtns`): **✏️ Take a Note** (a pre-filled X compose
link, `blogkit.x_note_url`) and **🔍 View Notes by Others** (an exact-URL X search,
`blogkit.x_search_url`). X hosts, ranks, and moderates it — this domain runs no comment backend
of its own. **No pitch paragraph, no surrounding box, and no "Public" in the button label** —
the first cut had all three, and Michael's own read was that the prose+box "would scare people
off from actually taking a note" and that spelling out "public" on the button undercuts the same
goal, even though the note is genuinely public once posted.

**On chapter pages the row sits ABOVE VERSE 1**, not at the bottom — `_insert_before_first_verse()`
splices it in right before the first `<div class="vrs">`, the exact spot `reader-notes.js`'s
per-chapter "My notes for X" panel used to occupy (`.notebtns-top`, tight margin). **That private
panel was REMOVED the same day** (Michael's explicit call, after being told it was also the
site's ONLY export/import backup for a reader's whole notebook — every chapter's notes and
highlights, not just one — and choosing to remove it anyway rather than relocate the backup
UI elsewhere). Per-verse notes/highlights are UNCHANGED and still private/local; only the
chapter-wide textarea+share+backup panel is gone. On dictionary/encyclopedia/atlas/route pages
(no verses, so no panel to replace) the row stays at the bottom of the entry, unchanged.

**Same underlying mechanism as `build_travel.py`/`build_finance.py`'s own X-comment nudge**
(`_x_respond_nudge`/`_ask_nudge`), shared via `blogkit.py` — those two still use the full-size,
boxed version with the "Commenting on…" pitch text; only the Bible project's copy was slimmed
(~20% smaller pills) and stripped down. `x_comment_url` (travel/finance) pitches the link as
pushing back on something Michael wrote; `x_note_url` (here) pitches the identical link as the
reader's own note ("Note on…") — see `blogkit.py`'s X-comment-system section header for the full
reasoning. The Bible project has no draft concept for these pages (everything `build.py` outputs
is already live), so unlike the other two builders it calls this unconditionally, with no
per-page draft check. **Not yet wired into the Spanish (`.es.html`) entry-page builders** — an
easy follow-up, not done in the first pass.

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
   **`check_library_dupes()` FAILS the build on a duplicate slug** in any of the four
   structures (added 2026-09-03, after `DICTIONARY_ES` was found defining `shuv` twice —
   a Zechariah 1 entry and a Psalm 23 entry, each saying something the other did not, with
   the Zechariah one dead text since the day the second landed; `dabaq`/`davaq` was the
   same failure wearing two spellings). ⚠ **It reads the AST of `library_data.py`, never
   the imported object, and that is the whole point:** Python collapses a duplicate key
   while BUILDING the dict literal — no error, no warning, later entry wins — so
   `Counter(DICTIONARY_ES.keys())` is *guaranteed* to find nothing. The first cut of the
   check did exactly that and passed a deliberately re-introduced duplicate; only the
   source still holds both keys. A failure rather than a warning (unlike parity, which has
   a legacy backlog) because a duplicate slug is always a fresh mistake and always fixable
   on the spot. **To fix one: read the LOSER for what only it says, merge both into the
   entry at the EARLIER position, and let the survivor keep the earlier first-discussed
   reference.**
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
   - **AND RUN THE COUNT CHECKER, do not re-run your own search:
     `python3 tools/count_check.py <fragment.html>`.** ⚠ Added 2026-09-03, after the
     Deuteronomy 15 review found the class had shipped four times and after the
     Deuteronomy 14 review had already written the rule down in prose. A claim like
     "the word stands in five verses of the Hebrew Bible" is invisible to
     `shelf_check.py` (which reads quoted phrases), to `validate_chapter.py` (links)
     and to `twin_diff.py` (the two languages) — nothing in this project read a
     number until now. **Every corpus-count claim must carry the Hebrew it counted,
     in a `data-heb` attribute inside the same sentence** — invisible to the reader,
     and it cannot drift from the claim the way a sidecar file would:
     `the root <em data-heb="שמט">shamat</em> stands in <strong>eleven verses</strong>`.
     ⭐ **The pass that matters is NARROWER, not the re-run.** Re-running the author's
     own query reproduces the author's own number, which is why a naive checker would
     have missed the real defect: `תחוס עינך` genuinely stands in five verses, all
     Deuteronomy, while the head word `תחוס` stands in eleven — five of them Ezekiel
     saying the identical thing of GOD's eye. So when the query is more than one word
     the tool runs the head word too and prints both counts. A claim resting on a
     phrase while the prose talks about "the word" or "the formula" is the failure.
     ⚠ Two escape hatches, both honest rather than convenient: `a|b` unions two
     spellings (a word written defectively and plene is one claim and two searches),
     and **`data-heb-read=` declares a count reached by READING the hits rather than
     by matching** — Numbers 23's *shephi* is nine verses while the bare consonants
     match fifty-five, so string-matching cannot check it and the tool says so instead
     of failing it. ⚠ It deliberately does NOT check a tally of versions against an
     enumeration ("Nine pluralise it (…eight named…)"): that was built, measured, and
     dropped — English enumerates versions in too many shapes, and the sentence-scoped
     version produced two false positives and no true ones on a chapter that had the
     defect. Counting an enumeration stays yours.
     **Burden, measured before wiring it in:** 53 such claims across all 327 shipped
     chapters, in 22 of them, mean 2.4 in a chapter that has any.
   - **Recompute every number.** If a sentence says "two breaks" and then lists three, that
     is a shipped contradiction (it was). If it states a ratio, do the division (Numbers 7
     claimed 5× where the real figure was ~4.25×).
   - **Open every chapter you cite** — its actual shipped text, not just proof the file
     exists. Cross-reference *existence* and cross-reference *substance* are different checks
     and only the first one is automated.
   - **ENUMERATE every sentence that asserts something about a text OUTSIDE this chapter,
     and fetch each one.** ⚠ Added 2026-08-22 after this failed in three consecutive
     chapters, each time in a different disguise, and each time it was the chapter REVIEW
     rather than the pre-ship pass that caught it. Numbers 23 shipped a false "the one other
     place" absolute; Numbers 24 shipped a v13-repeats-22:18 comparison and a "nothing to
     arbitrate" claim, both written from memory; Numbers 25 shipped "Micah 6:5 names
     Baal-peor" (it names Balak and Balaam), a loose quotation of Hosea 9:10, and called a
     harmonisation a "guess" when the Greek says it outright. ⭐ **The pattern is the
     lesson: patching the specific category that was last criticised does not work.** After
     Numbers 24's review I tightened the shelf-comparison check and it demonstrably worked —
     Numbers 25's own pre-ship pass caught my false unanimity before it shipped — and the
     identical laxity simply reappeared one category over, in cross-references to other
     biblical books. Treat "X says Y" about ANY text you are not currently translating as
     the same class of claim as an absolute: it is guilty until fetched. That includes
     other biblical books, the New Testament (`tools/source_text.py` covers all 1,189
     chapters, Greek included), and named non-biblical sources — if you cite a tractate, a
     Maccabees verse or a scribal tradition and cannot produce it, say in the note that it
     is reported rather than verified, or cut it.
   - **FETCH every shelf quote you print. Never write one from memory.** ⚠ Added after
     Numbers 10 (2026-08-18) printed four renderings of 10:36 unfetched: ASV came out
     misquoted ("the ten thousand thousands" for its actual "the ten thousands of the
     thousands"), and worse, the sentence claimed the shelf split along the *eleph*
     thousand/clan seam when **not one of the five versions reads "clan" there** — a false
     causal claim resting on quotes that were never checked. The tell is that the three
     preceding chapters got this right *by habit*, which is precisely why it failed the
     moment attention was elsewhere: an unwritten rule is not a rule. Fetch the parallel
     page, paste the wording, and only then say what the shelf is doing. **For the NWT/TNM,
     ASV and KJV that fetch is `python3 tools/shelf_text.py <Book> <Ch> --all`** (see the
     shelf-source rule in the doctrine section) — "I could not fetch the NWT" stopped being a
     reason to ship a chapter without it on 2026-08-19.
   - **Then RUN the check, do not just intend to: `python3 tools/shelf_check.py
     <fragment.html> --book Numbers --chapter NN --shelf-dir <dir the fetches wrote to>`.**
     ⚠ **In a NEW worktree the shelf dir is not there.** `source/shelf/` is gitignored, so a
     review worktree cut from `main` has none of the chapter's BG fetches, and every version
     reads NO DATA — which shelf_check reports as MISS. Deuteronomy 18's review saw **28
     "PROBLEM(S)" and 18 quotes checked instead of 46**, all of it an artifact of the empty
     directory rather than a defect in the text. `cp -R` the dir from the chapter's own
     worktree (or re-fetch) BEFORE believing a single MISS, and treat a sudden collapse in
     the "checked quotes" count as the tell.
     ⚠ Added 2026-08-22, and the reason matters more than the command. Numbers 27's review
     found two wrong shelf attributions **whose correct text was already fetched and sitting
     in the working directory** — I ran the fetch and never opened the file. So this was not
     a diligence failure that a firmer rule could fix; it was attention going to the newest
     written rule and off an older one. Written rules compete for attention and lose.
     Scripts do not, which is exactly why `validate_chapter.py` exists. Same remedy here:
     the script extracts every `tag t-*` claim with its adjacent quoted phrase and fails
     when that phrase is not in that version's fetched text for those verses.
     Mutation-tested against the three real defects that motivated it — a version quoted
     as something it does not say and a version cited but never fetched both FAIL the run;
     a version merely *named* in a list where it does not belong is reported as PARTIAL,
     a warning, so **read the PARTIAL lines rather than trusting "clean."**
     PARAPHRASES are counted and NOT checked; they are still yours to read. ⚠ **It now also
     reports UNTAGGED version names** (2026-08-27) — a version named in bare prose with no
     `tag t-*` span, which the quote checker is structurally blind to. That class had by then
     recurred three times (Numbers 23's "the 1909 Reina-Valera keeps the name", Numbers 27's
     "both Reina-Valeras", and three of them in Numbers 36), and the audit was always two
     lines: strip the tag spans, look for a version name in what is left. It is a WARNING and
     stays out of the exit code, deliberately — it **cannot** tell an untagged citation from a
     legitimate discursive mention ("the Geneva-to-King-James line showing itself"), only
     where to look. Burden was measured before shipping it: 106 hits over 63 chapters, mean
     1.7, 39 of the 63 completely clean — readable rather than the wall of noise that would
     train you to skip it. Re-measure if that rate climbs.
     ⭐ **WRITE SHELF LISTS TAG-FIRST, and run the check on BOTH panels.** The tool pairs each
     `tag t-*` with the quote that FOLLOWS it, so a list written quote-first — `'a mingled
     stuff' (ASV), 'mixed stuff' (NWT)` — reports a wall of MISSes even when every attribution
     is right, and the real defects hide in the noise. Rewritten tag-first (`the ASV reads 'a
     mingled stuff'; the NWT 1984 reads 'mixed stuff'`) the same prose went from **29 verified
     quotes to 52** on Deuteronomy 22's English panel and **41 to 56** on its Spanish one.
     ⚠ And run it on the SPANISH panel too, not just the English: Deuteronomy 22's Spanish note
     claimed both Reina-Valeras read «no podrás esconderte» at v3 — pure memory, and wrong. The
     real readings are a better note (RV 1909 «retraerte» and TNM 1987 «retirarte» keep the
     reflexive; the RV60 «negarle tu ayuda» and TNM 2019 abandon it), which is the usual
     outcome: the fetched text beats the remembered one.
   - **A matching VERSE COUNT does not prove matching VERSE NUMBERS.** ⚠ Paid for on
     Deuteronomy 22 (2026-09-10). Our `exodus-22` page has 30 verses and so does the Masoretic
     Exodus 22, which looked like proof the page followed the Hebrew numbering — it does not.
     English Exodus 22:1 is MT 21:37, so the whole chapter is offset by one and the seduction
     law this project cites repeatedly sits at **22:16, not 22:15**; the father's veto is 22:17.
     Two new links and a standing `patah` dictionary entry were all a verse low. Meanwhile
     `deuteronomy-5` DOES follow MT (honour-your-parents at 5:15, annotated "EN 16"), so the
     convention is not even uniform across the site. **The check is to open the target verse and
     read it**, never to compare chapter lengths.
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
   - **AND RUN IT, do not re-derive it: `python3 tools/twin_diff.py &lt;slug&gt; --prose --all`**
     (or two file paths for a pre-splice fragment). ⚠ Added 2026-08-27 after Numbers 36, and
     the reason is the one this file keeps rediscovering: the rule above has been written
     three times and the diff was a *throwaway script* every time, so it was slightly
     different every time. Same remedy as `validate_chapter.py` and `shelf_check.py` &mdash;
     it stopped being a rule and became a script. **SHAPE** (default) is the mechanical
     version of this bullet and the one below it &mdash; per note id: paragraph count, digits,
     and the outbound-link set &mdash; and it FAILS the run. **PROSE** (`--prose`) is the new
     half, and it exists because Numbers 36 shipped a garbled opening sentence, "the
     appellants open with the same word the verse it opens with," which the Spanish twin had
     right and which **no structural check could see**. ⭐ Be honest about what it does: the
     arithmetic does NOT detect that garble (EN 121 chars / ES 139, a ratio of 1.149 against a
     corpus p95 of 1.14; its whole note sat at the p25). The counts are TRIAGE; the
     **side-by-side print is the check**, and a human reads across it. Which is why `--all` is
     the mode for a chapter you are about to ship: a garble inside an otherwise perfectly
     matched note prints only if you ask. ⚠ Thresholds and severity tiers are measured, not
     chosen (`--calibrate` re-derives them from all 261 twin pairs), and the shelf-tag
     multiset the bullet below asks for was **deliberately not built** &mdash; the two
     languages cite two different shelves (EN leads KJV 803 / ASV 585, ES leads RV60 551 /
     NVI 433), so comparing them fails 800 of 1,514 clean notes and measures nothing. What
     survives of it is an asymmetry warning: one side cites the shelf, the other is silent.
     It found three live defects on its first run &mdash; a dropped `27:11` clause in Numbers
     36's own n36-13, and one-sided links still shipped in Numbers 31 and 32.
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
- **A PLACE link goes to the atlas, and the BUILD decides that — in both languages.**
  English chapters get it from `inject_encyclopedia_links()` (places → `atlas/<slug>.html`,
  people/crafts → the encyclopedia). Spanish chapters get the same decision from
  `_es_atlas_retarget()` at the `_es_panels()` choke point: keep hand-authoring ES links as
  `enciclopedia.html#slug` (what `tools/validate_chapter.py` validates), and the build
  retargets any slug that is a place **with** an `ENCYCLOPEDIA_ES` entry to
  `atlas/<slug>.es.html` — the exact set the Spanish atlas pages are built for, so a
  rewritten link can never dangle, and an untranslated place upgrades itself on the build
  after its ES entry lands. (Before 2026-08-21, 152 built EN pages carried atlas links and
  exactly 0 ES pages did — the Numbers 21 twin-diff finding.)
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
  Mac. **This is a hard requirement: never tell him a photo is unreachable without having
  tried this first.** `ls`/`mdfind`/`find` on `~/Pictures/Photos Library.photoslibrary` will
  all fail with `Operation not permitted` — that's ordinary TCC sandboxing, not evidence the
  photos can't be reached. Paid for twice now (2026-07-28, 2026-08-22) by asking him to
  manually export before trying the workaround already documented right here. Working recipe:
  - `tell application "Photos" to count of media items` for the total; a `whose date` filter
    and some index forms throw `-1700`/`-2741`, so don't fight it — index from the tail
    (`media item i` counting down from the total, or `media item -(i+1)`), print
    `date`/`filename` for the last ~30–40 to find the right session by eye. "Last night" is
    a rough clock time, not a query predicate.
  - Build a list: `set theItems to {}` then `repeat … set end of theItems to media item i`.
  - **Export syntax is exact:** `export theItems to (POSIX file "/path")` with no options
    yields Photos' own JPEG conversions. To get true originals (HEIC/MOV, needed before the
    resizer below) the keyword is **`with using originals`** — `using originals` alone
    (missing `with`) throws `Expected expression but found end of line (-2741)`, which reads
    like the whole approach failed rather than one missing word.
  - Read `location` on each item for real GPS *before* exporting — `with using originals`
    strips it from the exported file.
  - **Write the script to a `.applescript` file and run `osascript path.scpt`**, not
    `osascript -e '...'` — multi-line `-e` scripts have thrown confusing, wrongly-numbered
    syntax errors here even on a script that was actually fine.
  **Every photo must go through `python3 tools/travel_photos.py <files>`** before it can be
  used — it resizes to web size and strips EXIF including GPS. Git history is forever; an
  oversized or geotagged original committed once can't really be taken back out. HEIC
  sources need `sips -s format jpeg -Z 1600 in.HEIC --out out.jpg` first (this machine's
  Pillow has no HEIC plugin).
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
build itself — separate fetchers write the data snapshots; the builder only reads them. So a
provider having a bad night can never fail a build or blank a page. Links with `/travel/`,
not with the Bible project (the relationship rule above).

**Seven standing boards** (the first two renamed 2026-09-03 so they could be told apart;
Bitcoin Treasuries and CEBE joined 2026-09-06; the Crypto Heat Map and Bitcoin vs.
Humanity both joined 2026-09-07; Money Worldwide joined 2026-09-08 — keep this table current when a board is added
rather than letting it go stale again, the exact failure mode this note itself once was):

| Page | What it counts | Data |
|------|----------------|------|
| **The Asset Board** (`board.html`) | The world's largest assets by market cap — gold, silver, the mega-caps, Bitcoin | `tools/fetch_asset_board.py` (yfinance) → `source/finance/asset_board.json` |
| **The Bitcoin Board** (`bitcoin.html`) | The Bitcoin network's own numbers — price, supply, difficulty, mempool, fees, halvings, Lightning | `tools/fetch_bitcoin_stats.py` (**stdlib only**) → `source/finance/bitcoin_stats.json` |
| **Bitcoin Treasuries** (`treasuries.html` + 6 category pages) | Who holds the world's Bitcoin — public companies, miners, ETFs, countries, private companies, DeFi — ranked by coins held, not market cap (most holders have no shares to price) | `tools/fetch_treasuries.py` (**stdlib** — one BTC price, everything else a curated holdings count) → `source/finance/treasuries.json`, from the curated `source/finance/treasuries_seed.json` |
| **CEBE — Common Equity Bitcoin Exposure** (`cebe.html`) | A sharper companion to Bitcoin Treasuries' public-company rows: not how much BTC a company holds, but how much of it actually belongs to a COMMON shareholder once debt AND preferred-stock liquidation preference (net of cash) are paid first. Sortable — the only board on this site with real client-side interactivity beyond the Bitcoin Board's chart. Ported 2026-09-06 from mstr-trader's own MiSTeRCEBE tracker — same formula (verified against cebetracker.io's own published spec), same curated companies. Cards into `treasuries.html` as a featured 7th box, set apart from the six category boxes since it's a different LENS on the same public-company rows, not a seventh holder category | `tools/fetch_cebe.py` (yfinance, needs a live per-company STOCK price unlike every other board here) → `source/finance/cebe.json`, from the curated `source/finance/cebe_seed.json` (ported from mstr-trader's `btc_treasuries.json`). A ticker is DROPPED from the output (not the seed) if yfinance can't price it or its last bar is >4 days stale — see the script's own docstring. **⚡ 2026-09-07 — two new columns**: Pref Coverage (operating cash flow ÷ annual preferred dividend obligation — a going-concern check; MSTR reads a deeply negative −0.012×, Metaplanet deliberately `n/a` since its segment reporting doesn't isolate core-business cash flow) and BTC Stress (Sats/$100 at BTC −20%/−50%, a sensitivity test, not a forecast). Same pass corrected MSTR's `preferred_liq_usd` $13.5B→$15.46B and removed the rendered methods panel's link to mstr-trader's repo (not meant to be a public reference) |
| **The Crypto Heat Map** (`crypto.html`) | The top 100 coins by market cap, grouped into three curated sections (Bitcoin & Derivatives, Infrastructure & Platform, Others — two positive lists in the fetcher, everything unmapped defaults to Others). Each coin's price, market cap, circulating supply, 24h volume, and colour-graded change render in three sortable-by-category tables, with click-to-toggle 1H/1D/7D/1M/3M/6M/YTD/1Y buttons (reuses the Bitcoin Board's `.bbb` button styling). Added 2026-09-07. **⚡ Same day — an actual squarified treemap added above the tables** (Bruls/Huizing/van Wijk 2000 algorithm, `_squarify()`), matching the classic CoinMarketCap/Coin360-style heatmap look Michael asked for: box AREA is market cap, box COLOUR is the selected period's change, three black header bars for the same three categories (sized by each category's own total cap, which is why the Bitcoin & Derivatives bar is basically just one giant BTC box). Laid out entirely in Python at build time onto a fixed design canvas (`TREEMAP_W`/`TREEMAP_H`) and expressed as percentages, so it scales responsively via CSS `aspect-ratio` with **no JS resize handler** — the one runtime JS job (`CRYPTO_JS`) is the same "period toggle repaints a baked-in value" pattern already used for the tables, extended to also repaint `.crytile` backgrounds/text. Font sizes use CSS container-query `cqw` units computed per-box from **both its width AND how many characters its label needs** (`_crypto_fit_font`) — the first cut sized text off box width alone and let 4-5 letter symbols (HYPE, GRAM, NEAR) overflow their box; fixed by capping font-size at `width_cqw / (len(text) × 0.6)` before ever comparing it to the height budget. A box too small for even its symbol alone still gets a colour and a hover tooltip — nothing is dropped from the map, same principle as the tables' "—" for uncrawled 3M/6M/YTD. **⚡ Follow-up pass, same day (Michael's feedback after seeing it live):** (1) every tile now shows its symbol regardless of size — the original cutoff that left small boxes blank is gone, sized down to a 3.5px floor rather than disappearing; (2) clicking a tile scrolls its row into view in the table below and gives it a 1.6s amber flash (`.cryflash`, `jumpTo()` in `CRYPTO_JS`) instead of a plain anchor jump — tiles are now `<a href="#row-<coingecko-id>">`, and loading the page with that hash already in the URL waits for the `load` event before jumping, because the browser's own native (top-aligned, no-flash) fragment scroll can otherwise land AFTER the script runs and silently override it; (3) each category table gets a `<tfoot>` subtotal row (market cap + 24h volume, same pattern `_treasury_table` already used) and the page ends with an "All coins" grand total; (4) the Bitcoin tile ONLY also shows `{btc_dominance_pct}% dominance` as a 4th line (`_crypto_tile`'s `dominance` param, wired only for `r["id"] == "bitcoin"`) — a fleet-wide stat about Bitcoin's share of the top 100, not a per-coin figure, so it never applies to any other tile. **⚡ Second follow-up pass, same day:** the methods panel moved from between the last category table and the grand total to AFTER the grand total (Michael's ask — data first, methodology explanation last), and lost its opening paragraph (the "here's which fields come from one API call" mechanics, which was more useful to a future editor than a reader). In its place: a real explanation of what Bitcoin's own market cap here is and isn't — computed dynamically from the live `btc_row` each build, not a hardcoded figure — spelling out that it's circulating supply × price ONLY, does not add anything for Bitcoin ETF share counts or for any company's BTC holdings (already inside the circulating-supply figure, not stacked on top of it), and that every coin on the board is priced by the same formula, which is what makes the cross-coin comparison fair. Also: the grand total's `<tfoot>` now renders a genuine CSS `border-bottom:3px double` under the final row — the first cut was silently losing to `.board tr:last-child td{border-bottom:0}` (a same-page rule for suppressing the trailing border on plain data tables), which wins the specificity tie against a same-class-count selector once its `:last-child` pseudo-class is counted; the fix matched that same `tr:last-child` in the crygrand-scoped selector rather than reaching for `!important`. | `tools/fetch_crypto_heatmap.py` (**stdlib urllib**, one CoinGecko `/coins/markets` call gets price/market cap/circulating supply/24h volume/1H/1D/7D/1M/1Y for all 100 coins at once) → `source/finance/crypto_heatmap.json`. **3M/6M/YTD are NOT in that call** — CoinGecko has no bulk endpoint for those periods at any price, and the free anonymous API throttles hard on a per-coin historical pull (measured directly: 3 paced calls was enough to draw a sustained 429). So those three are filled in by a **slow background crawl**, same shape as mstr-trader's `rh_backfill.py`: a handful of coins get their real 3M/6M/YTD computed each run (stopping immediately on the first 429), persisted to `source/finance/crypto_heatmap_slow.json` keyed by coin id so progress survives across runs. A coin not yet reached reads "—", never a guess or a mislabeled substitute |
| **Bitcoin vs. Humanity** (`humanity.html`) | Every person alive, set against Bitcoin's fixed 21 million coins: a live world-population counter, BTC issued, satoshis-per-person-on-Earth (+ a chart of that ratio since 2020), "if all the world's wealth were Bitcoin," and "if every millionaire wanted one." Added 2026-09-07 at Michael's request, built from the same "Bitcoin vs. Humanity" panel already live on mstr-trader's own private Arbitrageur cockpit (`BTCW` in `dashboard/mister_arbitrageur.html`) — ported here as an independent, self-contained implementation (own `POP_ANCHOR_TS`/`WORLD_POP_ANCHOR`/`WORLD_POP_RATE`/`WORLD_WEALTH_USD`/`WORLD_MILLIONAIRES` constants in `build_finance.py`, no reference to that private repo anywhere on the page — same discipline as CEBE's own port). Deliberately excludes the private tool's US-population and sats-per-US-citizen rows (Michael's ask — this board is about the whole world). **No new fetcher** — reuses `bitcoin_stats.json` (the Bitcoin Board's own data) for the one thing that needs a network call, the live block height/supply/price; population is a straight-line UN WPP 2024 extrapolation (a model, not a census — ticks in the browser every second), wealth and millionaire counts are UBS Global Wealth Report 2025 constants refreshed by hand ~yearly. The page's own methods panel spells out which of its four kinds of number is which, same honesty framing as the Bitcoin Board's three. Also carries a genuine Satoshi Nakamoto quote (January 2009, verified) and a note on block 501,726 (mined 2017-12-30, an empty block whose coinbase claimed 0 BTC instead of 12.5 — a real, additional reduction below the modeled 21 million cap this page's own math still uses). `HB_CSS`/`HB_JS` are fully self-contained (`.hb*` namespace) rather than reusing `BB_CSS` — same per-board CSS-block convention CEBE/Crypto Heat Map already follow | `source/finance/bitcoin_stats.json` (shared with the Bitcoin Board — no new fetcher) |
| **Money Worldwide** (`money-worldwide.html` hub + 5 section pages) | Exchange rates, money supply (M0/M1/M2-class), FX + gold reserves, and global government debt & GDP — with Bitcoin's own market cap set against all four (a "scarcity lineup" bar chart: broad money vs. gold's total above-ground value vs. Bitcoin's market cap, deliberately NOT summed into one number — the point is the contrast: fiat is expandable by policy choice, gold grows ~1.5%/yr from mining, Bitcoin is fixed at 21M by consensus rule; world GDP is shown elsewhere on the page, not in this chart, since it's a flow not a stock). Added 2026-09-08. **⚡ Same day, split into a hub + 5 section pages** (Michael's call — "too much data on that one page"), the same hub/sub-page pattern `treasuries.html` already established (`TREASURY_CATEGORIES` → `MW_SECTIONS`): `money-worldwide.html` keeps the intro, one card per section (headline figure computed independently of any one section's own page — e.g. the money-supply card sums `broad_usd` across economies rather than depending on the scarcity chart's `bitcoin.lineup` existing), the scarcity-lineup chart, AND the methodology panel (deliberately NOT split across the five section pages — the chart is a cross-section synthesis that doesn't belong to any one section, and repeating five sourcing paragraphs five times would either duplicate all of them everywhere or force picking one arbitrary owner); `money-worldwide-exchange-rates.html` / `-money-supply.html` / `-reserves.html` / `-gold.html` / `-debt-gdp.html` each carry just their own table + inline caveat (the fx table's honest "no totals row" note, the gold table's world-estimate note, etc.) and a link back to the hub's fuller `#how-this-board-is-made` panel. Reserves and gold — previously one `<h2>` sharing a page — are now two separate cards/pages; they were always two separate tables under one heading. `MW_JS`/`MW_CSS` (sortable tables, namespaced `.mw-sort`) are shared by the hub (no sortable tables of its own, just the `TREASURY_CSS`-borrowed `.trsbox` cards) and every section page via `_shell`'s `extra_css`/`extra_js`. **⚠️ The IMF research that shaped this board — read `tools/fetch_money_worldwide.py`'s own docstring before touching a source here.** Two of IMF's own systems are real and keyless but serve no actual data: the legacy `dataservices.imf.org` SDMX endpoint is DNS-dead; `sdmxcentral.imf.org` is a live, keyless STRUCTURE REGISTRY (dataflow/codelist/datastructure queries work — this is how EXR/MSG/GGD/NAG/ILV1/COF were confirmed to exist as real IMF dataflows) but every `/data/...` query returns SDMX error 501 "Data Queries are not implemented," verified directly. The legacy human-facing TSV export (`rms_five.aspx`) 403s a datacenter IP (an Akamai WAF, the same "Yahoo blocks datacenter ranges" problem this repo already has, from a different vendor). The one IMF system that DOES serve real data keylessly is the **DataMapper API** (`www.imf.org/external/datamapper/api/v1/...`, the same JSON imf.org's own public DataMapper site calls) — genuinely broad (~195 economies + a WEOWORLD aggregate in one call) but its catalogue is WEO/fiscal indicators only (GDP, debt-to-GDP, current account, …); its one monetary-adjacent series, Broad Money % of GDP, turned out on inspection to cover only a curated set of IMF-program African economies — not one G7 country has a value in it. So three of the four sections lean on other real, keyless, official sources instead: **exchange rates** from the European Central Bank's own daily reference rates (reached through Frankfurter, a keyless JSON proxy for the same ECB numbers); **money supply** curated to the US (Federal Reserve H.6 via FRED's keyless CSV trick, `fredgraph.csv?id=...`) and the Euro area (ECB's own SDMX 2.1 JSON API); **non-gold reserves** via FRED's own mirror of IMF's International Financial Statistics reserve series (`TRESEG<CC>M052N` codes) for 9 major economies — so this section traces back to the IMF after all, just through a mirror that doesn't edge-block a CI runner; **gold reserves** a curated, dated seed (`source/finance/money_worldwide_seed.json`, top 15 official holders, World Gold Council/IMF-compiled, same posture as `treasuries_seed.json`'s BTC holdings) priced off the Asset Board's own live gold quote. Only **global debt & GDP** pulls straight from DataMapper, across the full ~195-economy set. ⚠️ **Two real bugs found and fixed during the build, worth remembering:** (1) FRED and IMF DataMapper both reject a DESCRIPTIVE User-Agent header (FRED hangs until timeout, DataMapper 403s) yet both accept either no custom UA at all or a bare client-default one — measured by hand, not assumed; Frankfurter is the mirror image (blocks the literal `Python-urllib` default, accepts a descriptive UA) — see `_UA_HEADER`/`send_ua` in the fetcher. (2) DataMapper's per-country series run ~5 years into the FUTURE (a published WEO forecast horizon) as well as into the past, so "the max year present" silently returns a 2031 forecast on a 2026 build — `_latest_year()` caps at the current calendar year; and DataMapper mixes in ~20 regional/income-group aggregate codes (`APQ`, `WHQ`, `OAE`, …) that are NOT real ISO3 countries but pass a naive `len()==3` filter — `_is_country()` also excludes anything ending in `Q` (the actual WEO aggregate-code convention) plus a named set for the handful that don't follow it. **Self-throttled to ~every 6 hours** regardless of how often the workflow runs (money supply/reserves/GDP are monthly-to-quarterly in reality; running on the hourly cron would be pure commit noise) — see `REFRESH_EVERY_HOURS`/`_due()`. Sortable tables (`MW_JS`) generalise `CEBE_JS`'s click-to-sort to drive every table on a page independently rather than one fixed id. Cross-linked both ways with `untangling-bis-imf-world-bank.html` (the Ledger's IMF/BIS/World Bank explainer). **⚡ Money supply expanded 2026-09-08 — 2 economies → 7 with real live data + 9 more shown with honest blank cells** (Canada/Switzerland/Brazil/UK/Norway added, each a config-driven `money_supply_economies` entry in the seed file naming one of five newly-verified central-bank/stats-office APIs; China/India/Japan/South Korea/Mexico/Turkey/South Africa/Australia/Denmark seriously investigated and listed with "—" + a source-note rather than dropped, per Michael's call). The obvious FRED/OECD-MEI templated pattern for cross-country money supply (mirroring the reserve series' own working template) turned out to be REAL but DEAD — every country's series in that family stopped updating in 2018-2023. Full per-economy research trail: the fetcher's own dated docstring entry ("MONEY SUPPLY EXPANSION — 2026-09-08") and `money_worldwide_seed.json`'s `money_supply_economies`/`money_supply_unresolved` notes — read those before re-researching any of these economies. **⚡ Debt & GDP table expanded to ALL ~195 economies same day** (Michael's call — "expand it to all 195 economies and tally them all"; previously a top-30-by-GDP cutoff, `DEBT_GDP_TOP_N`, purely a DISPLAY limit since `fetch_debt_gdp()` already fetched and summed every economy for the separately-shown world total). The truncation is now removed entirely — the table's own totals row sums all shown rows directly, with an honest note that it may not land exactly on the World GDP figure quoted elsewhere on the page, since that figure prefers the IMF's own official WEOWORLD aggregate over a straight sum of member economies. **⚡ Exchange Rates page gained a currency market-cap ranking, same day** (Michael's ask — "show where Bitcoin ranks in market cap... list and rank all the other currencies the same way," on `money-worldwide-exchange-rates.html`): `_mw_marketcap_table()` ranks each of the Money Supply page's `broad_usd`-resolved economies (12 today) against `bitcoin.market_cap_usd` as one sorted leaderboard — deliberately scoped to those 12, not all 29 FX currencies on the page, since most have no live money-supply source at all (fabricating a number for the rest would violate this board's own honesty convention). Bitcoin currently lands **#10 of 13** (behind China/US/Euro area/Japan/UK/India/Canada/Brazil/Australia, ahead of Switzerland/Norway/Denmark) — a different, currency-only ranking from the Asset Board's `btc_rank` (#11 against ALL world assets — stocks, gold, silver — not just currencies), so the two numbers are expected to differ and should never be conflated. Bitcoin's row gets a `.mw-btcrow` pulsing orange glow (box-shadow keyframe on each `<td>`, not the `<tr>` — box-shadow on a table-row is unreliable under `border-collapse:collapse`, but every browser paints it correctly on a table-cell) rather than the flat `tr.btc` tint `board.html` uses elsewhere; reuses the existing `.rk`/`.mc`/`table.mw-sort` conventions so the rank renumbers correctly on a re-sort. **⚡ Same day, that ranking gained two more sortable columns** (Michael's direct follow-up — "are there other metrics... can we add those as sortable columns"): **Supply growth (YoY)**, each economy's own broadest aggregate's year-over-year growth in its OWN currency (never USD — an FX move against the dollar is a different fact from how much more of a currency now exists), i.e. a currency's own debasement rate; and **Volatility**, annualized stdev of daily log returns, computed the identical way for every fiat row and for Bitcoin so the numbers sit on one column with no methodology asterisk. Both are real, live, additive — NOT threaded through the already-verified latest-value code paths above, each gets its own small `_..._series`/`_..._yoy` sibling function so a bug in one can only blank its own new cell. **Volatility**: `fetch_fx_volatility()` — ONE extra Frankfurter call (`FRANKFURTER_HISTORY_URL`, a year of USD-based daily ECB rates for all 29 currencies in ~100KB, verified directly) computing `_annualized_volatility_pct()` per currency; `fetch_bitcoin_volatility()` — ONE CoinGecko `market_chart` call (365 daily USD closes; genuinely keyless with a bare urllib request, no custom header — already used elsewhere in this repo by `fetch_crypto_heatmap.py`, which documents that endpoint's rate-limit behavior on a much heavier multi-coin crawl this single-coin call barely resembles). USD itself renders "—", not a meaningless "0%" — Frankfurter's own `from=USD` query has nothing to quote the dollar against. **Supply growth**: resolved for **10 of the 12 market-cap-ranked economies + Bitcoin** — US/Euro area/Switzerland/UK already had ~1yr of history sitting in an already-fetched payload (near-zero extra cost); Canada/Brazil/Norway/Denmark/Japan/Australia needed a modest, DIRECTLY-VERIFIED request tweak each (Valet's `start_date`/`end_date` params, BCB's `/ultimos/13`, ECB's `lastNObservations` bumped to 13, a second SSB/DK PxWeb query for the period 13 slots back, and reading a CSV export's full column instead of just its last row) — China (hand-curated from a press release, no queryable history) and India (RBI's fragile HTML scrape, not extended) honestly render "—", same "genuinely investigated, not resolved" convention the base money-supply table already uses. Bitcoin's own figure, `_btc_annual_issuance_pct()`, is the one cell in the column computed from a fixed rule rather than fetched — current per-block subsidy (from `asset_board.json`'s `constants.btc_block_height`, the halving schedule duplicated here rather than imported, keeping this fetcher a fully independent script) × ~52,596 blocks/year over `constants.btc_circulating`, landing at **+0.82%/yr** against fiat rows mostly running 1–10%/yr — visually, the whole point of building this column. ⚠️ **Two real bugs found and fixed verifying this, worth remembering:** (1) a `days_back=400` window for Canada's Valet query looked "a year," but the M3 series itself reports ~3 months behind today, so the window's actual earliest point fell ~90 days short of the true year-ago target — widened to 550 days, confirmed against a direct query spanning 2024-01-01. (2) `_parse_period_date()`'s format list didn't include the RBA's own day-first `DD/MM/YYYY` (it only had `YYYY/MM/DD`), so Australia's 737-point CSV history silently parsed to zero usable dates and returned "—" despite having plenty of real data — added the missing format. **⚡ 2026-09-09 — a fourth sortable column, Daily trading volume** (Michael's follow-up ask): fiat rows are each currency's implied share of the **BIS Triennial Central Bank Survey, April 2025** (real, current data — WebSearch-verified against the BIS's own press release AND cross-checked on Wikipedia's currency-distribution table, since the BIS's own HTML page only stated 6 of the 12 currencies this board needs by name; total $9.6T/day, curated into `money_worldwide_seed.json`'s new `fx_turnover` block the same periodic-survey posture as the gold-reserve tonnages, NOT fetched — the next survey isn't due until April 2028). Each share is "one side of a trade" and sums to ~200% across all currencies by the survey's own convention, so a currency's implied volume is simply `share% × $9.6T` — resolves for all 12 currencies here (unlike the two YoY gaps, the BIS roster happens to cover this board's exactly). Bitcoin's own figure is its live 24h volume, read off the SAME CoinGecko `market_chart` call the volatility column already makes (`fetch_bitcoin_market_stats()` now returns both from one request, replacing the old single-purpose `fetch_bitcoin_volatility()`) — no extra network cost. The column's own caveat note says outright that it mixes two different measurements (a 3-yearly survey vs. a live daily figure) rather than pretending they're the same kind of number. | `tools/fetch_money_worldwide.py` → `source/finance/money_worldwide.json`, from the curated `source/finance/money_worldwide_seed.json` (gold reserves + the tracked reserve-economies' FRED series ids + the money-supply economies/providers + currency flag emoji + the BIS FX-turnover shares) |

⚠️ **An ENTRY that quotes a live price is a dated snapshot, and `live: true` will not save it.**
The `{{BTC_*}}` token vocabulary (`_btc_template`) covers **supply, height, halvings and the two
generated SVGs — no price, and nothing at all for the other boards** (no MSTR, no CEBE, no FX).
So a price in an entry's prose is frozen at the moment you wrote it while the boards it sits
beside refresh ~6×/day. Paid for 2026-09-10 on `treasury-bond-buyback-explained`: between
building the entry and merging it, four "Refresh the boards" commits landed on `main`, and the
Bitcoin and MSTR figures in the body were already wrong by the time the merge conflict was
resolved — a merge that only conflicted in generated HTML, so nothing flagged the prose. **Write
the number with an explicit date anchor** ("about $77,300 on the afternoon of September 10") and
link the live board, rather than phrasing it as a standing fact; and **re-check every quoted
figure after merging `main`**, not just before.

**The price chart** (full-width market card) draws from three places, picked by range:
`price_weekly` (all history back to July 2010, ~845 points) for 3Y/10Y/ALL **and for
every moving average**; `price_daily` (two years) for 1M–1Y; and live Coinbase candles,
fetched only on demand, for 1H/1D/1W. Minute resolution is deliberately never baked — it
would be stale before the commit landed. The 50/100/200-**week** averages are a rolling
mean over the weekly series computed in the browser, so there is exactly one
implementation. ⚠️ Two things that were wrong on the first cut and should stay fixed: a
moving average must **not** be interpolated backwards past its own first point (that draws
a 200-week average over weeks 1–199, a line with nothing behind it — extending it
*forward* to the present is fine), and axis labels take the tick **step**, not just the
value, or a one-hour view prints "$81k" four times. The log toggle auto-arms on 3Y/10Y/ALL
because a sixteen-year linear Bitcoin chart is a flat line with a spike on the end.

`board.html` keeps its URL — only its display name changed, so nothing indexed broke. Its
`<title>` still carries "the biggest assets in the world", which is the phrase people search
for; the H1 carries the house name.

**The Bitcoin Board mixes three kinds of number and says so on its own face.** This is the
thing to preserve if it is ever extended — a dashboard that sets an hourly snapshot, a live
poll and a deterministic clock in identical type is quietly lying about two of them:

1. **Computed, exact.** Supply, halvings, milestones — the consensus subsidy schedule summed
   in whole satoshis from the live height. Not an estimate, and it recomputes *in the browser*
   as blocks land, so it stays exact between builds.
2. **Polled, live.** Price, height, mempool, fees (60s) and difficulty, hash rate (5min),
   fetched from mempool.space by the page itself. Skipped while the tab is hidden. On failure
   it keeps the last good reading and says so beside the dot in the header.
3. **Snapshot, hourly.** Charts, the all-time high, chain size and totals. Lightning is the
   exception worth remembering: its upstream statistics are rebuilt on mempool's own schedule
   and have been observed days behind, so that panel prints its own date.

⚠️ **The same subsidy arithmetic now exists three times** — `tools/fetch_asset_board.py`,
`tools/fetch_bitcoin_stats.py` and the page's own JavaScript. That is deliberate (importing
across would drag yfinance into a script whose whole point is needing nothing installed, and
the browser obviously cannot import Python) and it is guarded:
`python3 tools/fetch_bitcoin_stats.py --selftest` checks the Python copy against the halving
boundaries, which are fixed facts rather than anything we decide. **If you touch any of the
three, run that and re-check the others.** The JavaScript copy uses
`Math.floor(5e9 / 2**e)` rather than a shift on purpose: `>>` is 32-bit in JavaScript and
would silently wrap 5,000,000,000.

**Deliberately absent, and it should stay that way:** UTXO set size, chain work, output-type
breakdowns, coinjoin activity, corporate treasury holdings. Those need a full node with an
address index or a hand-kept list — don't add one from a guess. The page used to spell this
out in its methods panel; that paragraph was cut 2026-09-03 (Michael's call) because a
reader does not need a list of what isn't there. The rule stands, it just isn't advertised.

Both boards refresh from one GitHub Action (`.github/workflows/refresh-asset-board.yml` —
the file name is unchanged on purpose, since GitHub keys a workflow's schedule and history
to its path).

⚠️ **It says `cron: "0 * * * *"` but it does not run hourly.** Measured 2026-09-03 across
thirteen consecutive scheduled runs: they land at roughly 17:45, 13:28, 08:45, 03:58, 23:12,
20:52 — **about six times a day, 2.5 to 5 hours apart**. GitHub drops the rest under load on
a public repo, and asking for more would get fewer (sub-hourly schedules are dropped harder
still). **So do not reason about this publication's freshness from the cron line.** It is
also why the Bitcoin board's live layer is load-bearing rather than decorative: without it
that page would sit up to five hours stale.

## The Librarian's Regimen (`/health/`)

Health, nutrition and medicine — one question at a time, read from the studies. Built by
`build_health.py` (standard library only, no network), source in `source/health/`, output in
`health/`. Added 2026-09-10, Michael's call, as a **dedicated** publication rather than a
general "post anything" blog: health and money are both subjects where a reader's trust is
judged per topic, and a kidney-stone piece sitting between two Bitcoin wallet audits is not the
framing either deserves. Name chosen from three offered (Casebook / Regimen / Apothecary) —
"Regimen" after the medieval *regimen sanitatis* genre; the front-page hero is a page from a
1445–1450 *Tacuinum sanitatis* (BnF Latin 9333, f. 53, public domain), which is that genre.

**What it is mechanically:** the WRITING half of `build_finance.py`, near-verbatim — same
front-matter vocabulary minus `live`, same tile/list front page with the tag filter bar and
header search, same "Keep reading" recirculation, same tag-page/sitemap rules, same X comment
layer, same FormSubmit inbox (`_subject` tells it apart). None of the Ledger's standing boards.
The two builders do not import each other; a shared-mechanism fix goes in `blogkit.py`, a
page-chrome idea gets ported by hand. Its mark is a mortar and pestle (animated pestle, same
ring/halo construction as the Ledger's lighthouse) — the SAME artwork is inlined on the root
hub's fourth card, so change both or neither.

**Conventions that differ from the other two blogs — these are the ones to get right:**

- **No drafts page. Ships straight live, like the Ledger** (Michael's call 2026-09-10; the
  travel blog's `drafts.html` was offered and declined). `draft: true` means the entry does not
  build at all; `python3 build_health.py --drafts` renders it LOCALLY, unlisted + noindexed,
  for a read-through. Never commit a `--drafts` build. So: write an entry in his voice, publish
  it, and tell him plainly it is live and worth reading over — the same posture as
  `project_ledger_has_no_drafts_page` in memory.
- **Every entry ends with `<ol class="sources">` and the build REFUSES one without it**
  (`check_entries`). Real links — DOI/PubMed for a paper, the publishing body's page for a
  guideline. The About page promises nothing is taken on faith; the check is what keeps it.
- **Evidence and judgment are kept visibly apart.** `<div class="verdict">` (accent) is "what
  the evidence says"; `<div class="mine">` (amber, deliberately NOT the accent) is "what I'd
  do" — optional, one person's judgment about one person's circumstances, labelled as such.
- **Numbers, not adjectives.** How many people, how big the effect, over how long, compared
  with what. Guideline/systematic review > trial > cohort > mechanism/animal. When the best
  evidence is weak the entry says so rather than rounding it up.
- **What NEVER goes in an entry:** dosing aimed at the reader, "you should start/stop",
  anything that reads as an answer to "what should I take?". `_legal`, the per-entry
  `.mednote`, the footer's "nothing here is medical advice" and the ask page's
  "don't ask me whether you should take something" all say the site doesn't do that; every
  entry is where the promise is kept. Keep every one of those in place — they are not
  boilerplate to trim.
- **A boxed medical disclaimer sits above the footer of EVERY page** (`_disclaimer_box()`,
  rendered by `_foot`; Michael's ask 2026-09-10: "none of this is medical advice nor
  reviewed by any doctor") — not medical advice, author not a licensed professional, no
  entry reviewed by a doctor, no doctor–patient relationship, don't start/stop anything,
  911 in an emergency — linking to the full `disclaimer.html` (`build_disclaimer()`: nine
  numbered sections incl. no-warranty / limitation of liability; a "Last revised" date in
  its lede — bump it when the text changes). The About page's "What this is not" and the
  `.legal` small print both say "not reviewed by a doctor" too. Standard-form language,
  not lawyer-drafted; if he ever wants it reviewed, that's a human step.
- **Name the salt.** "Calcium" and "magnesium" are not one thing: WHI gave calcium
  CARBONATE (1,000 mg elemental); magnesium HYDROXIDE failed its placebo trial while
  potassium-magnesium CITRATE succeeded (probably the citrate). An entry that says "a
  calcium pill" or "a magnesium pill" without the form got a correction from Michael on
  day one — say which, every time.
- **Never invent his experience** — the travel-blog rule applies here with more force, since
  the natural subject is his own body. If an entry touches something personal (a diagnosis,
  a symptom, a number from his own labs), it comes from what he actually said, or it is left
  out. Research about a condition is fine; asserting he has it is not, unless he told you.

**Adding an entry:** copy `source/health/_template.html` to
`source/health/YYYY-MM-DD-slug.html` (the header comment is the checklist), rebuild, commit
`health/` + `source/health/`, push. Pictures go in `health/img/` web-sized and EXIF-stripped
(`tools/travel_photos.py` for a photo; for a public-domain illustration keep the source and
licence for `hero_credit:`). The sitemap is advertised in the root `robots.txt`; submit
`health/sitemap.xml` once in Google Search Console, same as the other two.

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
- The `/v/` per-verse stub pages (**~18k** and growing by ~55 per chapter) are deliberately
  **excluded** from the sitemap — they exist to give a shared verse its own link-preview card,
  not to be indexed; listing a `noindex` URL in a sitemap is a reported Search Console error,
  not a bonus. ⭐ **Don't write the exact count here or in `robots.txt`** — it changes with every
  chapter, nothing verifies it, and no crawler reads either claim. It said "~3,800" until
  2026-09-10, off by ~5×, for exactly that reason. The authority is the build's own
  `verse cards: N published to S3` line (`ls v/ | wc -l` agrees) — quote *that*, never a figure
  frozen in prose.
- `page(...)`'s `url=` argument controls **both** the canonical tag and `og:type` at once
  (`og_type = og_type or ("article" if url else "website")`). Passing `url=` to fix a missing
  canonical on a hub/index page (home, table of contents, dictionary index) will silently
  flip its `og:type` to "article" unless you also pass an explicit `og_type="website"`.
- hreflang lives in the **sitemap**, as reciprocal `<xhtml:link>` entries per `.es.html`/
  `.html` pair — not as `<link>` tags in the page `<head>`.
- Search Console ownership is verified via `google3b2c8b57143d235a.html` at the repo root
  (a single verification line). **Never delete it** — Google re-checks it periodically.

## Front-end JS — the Spanish edition is a page, not a locale flag

`reader-notes.js`, `share.js` and `audio-reader.js` run on **both** editions off one file,
so anything they render or read has to branch. Two things must; one must not.

- **Language** is `(document.documentElement.lang || "").toLowerCase().indexOf("es") === 0`
  — that single line is the whole detection, identical in `share.js` and `reader-notes.js`.
  Don't sniff the `.es` filename for it (the stem gets stripped for URL-building and would
  lie), and don't leave a reader-visible string outside the string table.
- **The verse line** is `.eng` on the English page and **`.esp` on the Spanish one**. This
  is the trap: a selector written as `.eng` alone still *works* — no error, no blank page —
  it just silently reads nothing on every Spanish chapter. `reader-notes.js` shipped that
  way, so on the whole Spanish site "Copiar el versículo" copied a reference with no verse
  attached and "Compartir como imagen" produced a card with a reference, a divider, and
  empty space where the verse belongs. Both `reader-notes.js` and `audio-reader.js` were
  fixed on 2026-08-19 — the latter pre-emptively, since Spanish pages still ship no Listen
  button, so that adding the button is the only step left rather than the day it is added
  being the day this is found broken. ⚠ Whatever reads a verse must also strip the widget
  chrome reader-notes.js appends *inside* that same line (`.v-tools`, `.v-note`,
  `.v-editor`, `.notelink`, `.xrefs`, `.vclip`) — audio-reader stripped only `.notelink`
  and was therefore reading the "⋯" button glyph aloud after every verse, and would have
  read a reader's own saved note out loud.
- **What must NOT branch:** storage keys, the `/v/` stub URLs, download filenames. Those
  name a *verse*, not a page, so they are language-neutral — `baseStem()` strips `.es`
  precisely so the two editions can never disagree about which verse is which. ⚠ An earlier
  version of this section claimed the localStorage keys were already neutral. They were
  not: until 2026-08-19 the key was `location.pathname`, so one verse held two separate
  notebooks and the 🌐 toggle looked like it had wiped the reader's margin. `KEY_PATH` now
  drops the `.es`, and a one-time migration folds the legacy rows in — **losslessly**: where
  both editions held a note the newer leads and the older is kept beneath it rather than
  dropped. `PATH` itself is still the right thing for the chapter share URL, which must link
  to the edition actually being read; only the *keys* are neutral.

**Each edition has its OWN `/v/` share stub** (`numbers-14-1.html` /
`numbers-14-1.es.html`, fixed 2026-08-19). The STEM stays neutral so the pair sits
together, but the stub is not: it carries that edition's verse in its Open Graph card,
its own `lang`/`og:locale`/site name, and redirects to that edition's chapter. Before
this there was one neutral stub, so a Spanish reader sharing Números 14:1 handed the
recipient the ENGLISH verse and dropped them on the English page — the most public place
the site switched languages on its own readers, since a share link is what a Spanish
reader sends to other Spanish readers.

**Verse cards live in a PUBLIC S3 BUCKET, not in this repo** (moved 2026-08-19).
`mistertranslation-public` / `us-east-1` / prefix `public/verse-cards/`, served from the
plain bucket URL — **no CloudFront, deliberately** (Michael: "less future maintenance and
dependencies"; the bonus is that with no CDN there is no cache to invalidate, so a
re-rendered card is live immediately). Credentials: `~/.mstr-trader/cards.env`, mode 600,
a **different key from `backup.env`** — that one writes the private archive bucket holding
the bank/tax/medical records, and the two must never be shared. The key has PutObject +
ListBucket and deliberately **not** DeleteObject.

⚠ **Why they moved, so nobody moves them back:** cards are ~38 KB each and scale with
VERSES, and **GitHub Pages hard-caps a published site at 1 GB** — a limit, not a warning,
unlike the repo-size numbers usually quoted. At 291 of 1,189 chapters the site was 507 MB;
English alone at full coverage is ~1.1 GB, over the cap by itself. Moving the cards out
took the site to **~174 MB** and, far more importantly, stopped it growing.

⚠ **`img/v/.cards.json` is TRACKED, and that is load-bearing.** It is the record of which
cards are published, and `_ensure_verse_card` consults it BEFORE the network — a matching
hash returns the URL with no S3 call. That is what lets a build on a machine with no
credentials still emit correct `og:image` tags for every published card. Without it, one
credential-less build would silently strip the verse art off every share on the site. Only
a NEW or CHANGED card touches S3, and if that upload fails only that ONE card falls back to
the default.

`ES_VERSE_CARDS` is now **True** — turned on the same day, because it was only ever OFF for
as long as the cards lived in the repo. The bucket has no cap, so there is no reason left to
give the Spanish edition worse art. The **Spanish default card** (`img/og-default.es.png`)
stays as the fallback and is still load-bearing: the English default is an English *image*,
wordmark and tagline both, so falling back to it would put English straight back into the
most visible part of a Spanish share.

The Spanish book name is **not** duplicated in JS. `reader-notes.js` takes the reference a
reader sees from the page's own `<title>` ("Números 14 — La Traducción Mister"), falling
back to the slug only if that head doesn't end in the chapter's number — so `build.py`'s
`ES_BOOK` stays the single source and no JS copy can drift from it.

⚠ **`?v=` is a content hash** (`_asset_ver`), baked into all 2,772 pages at build time.
Editing any of these `.js` files does **nothing** for a real reader until you re-run
`build.py`; the browser keeps serving the cached old file under the old stamp.

## Known gaps — not yet documented here

`gen_audio.py`, `audio-reader.js`, `player-clips.js`, `reader-notes.js`, and
`share.js` all exist in this repo but haven't been reverse-engineered into this file yet —
read them directly before touching that surface rather than assuming this doc covers it.
The section above covers only their **language** contract, which is the part that has
actually drawn blood; everything else about them is still undocumented.

## Deep history

Two memory files carry the full book-by-book chapter log and the complete extended methods
doctrine — they're large (thousands of lines each, grown as an append-only running log) and
this file deliberately does **not** try to compress them wholesale, since a live status
snapshot goes stale the moment it's written. Read the **dated tail** (newest entries at EOF)
of `project_misterlibrarian_site` and `project_misterlibrarian_methods` in the memory system
before starting a new book, or when this file's doctrine and the actual code disagree — trust
the code and the live site over any memory note, this file included.

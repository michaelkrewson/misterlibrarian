# Per-chapter checklist — full original text, with the history behind every step

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.

> This is the checklist exactly as it stood in `CLAUDE.md` before the 2026-09-25 split. `CLAUDE.md` now carries a condensed version of the same steps; the dated incidents and worked examples below are the WHY behind each sub-rule. If the two ever disagree on a rule, the newer `CLAUDE.md` wording wins, and this file should be updated to say so.


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
     ⚠ **The archive reader dropped the second half of every multi-line verse until
     2026-09-11.** In the poetic books Mechon prints a long verse across two lines, and
     `heb_search.chapter_verses` kept only the numbered first line — **605 continuation
     lines** (488 in Psalms, 56 in Job, 32 in Proverbs) were invisible to every count
     `heb_search.py` or `count_check.py` ever ran. Found because Psalm 119:176's second
     half, *for I have not forgotten your commandments*, did not exist to the tool. A
     sweep of all 622 built pages after the fix turned up **three shipped claims that were
     low** — Deuteronomy 24's *ani ve-evyon* "eleven verses" (fifteen: four psalm/Job
     hits sat on second lines) and Deuteronomy 17's *pele* "eighty-one" (eighty-six) —
     corrected in the same change. **Two scope traps in `count_check.py`, both fixed the
     same day:** "N verses **of** this book" was not a scope (only "in this book" was) and
     such a claim was silently SKIPPED — no UNVERIFIED line, nothing — so three
     Deuteronomy 26 claims went unchecked until the wording was noticed; and a claim
     joined to another by a semicolon shares its sentence, and only the FIRST count in a
     sentence is read. One claim per sentence.
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
     ⚠ **An OFFSET chapter needs the PREVIOUS chapter's BibleGateway text too, under
     `<NAME>_prev.json`.** `--verse-offset 1` sends our v1 to the shelf's last verse of the
     chapter before, and for the seven BG versions the checker reads that from
     `<shelf-dir>/<NAME>_prev.json` — so fetch the previous chapter into its own dir and copy
     each `NIV.json`… across under the `_prev` name (Deuteronomy 23, 2026-09-10, whose v1 is
     every English Bible's 22:30: `fetch_shelf_bg.py Deuteronomy 22 source/shelf/d22` then
     `cp d22/NIV.json d23/NIV_prev.json` for all seven). Without it every quote from that
     verse reads NO DATA. ⚠ `fetch_shelf_bg.py` also writes a non-numeric `_whole` key, and
     the `_prev` path crashed on it the first time it was fed a real fetch — fixed in
     `shelf_check.py`, but it means the path had only ever been exercised on hand-made files.
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
     ⚠ **It reads straight double quotes too, since 2026-09-11.** The chapters written
     before the tool existed (Genesis 1 through the early thirties) quote the shelf as
     `"without form, and void"` in plain ASCII quotes, and the `QUOTE` regex only knew
     ‘…’/«…»/`&lsquo;` — so Genesis 1 reported **0 checked quotes and 128 "paraphrases"**
     while carrying ~40 wrong attributions the tool would have caught. A review of Genesis
     1–33 that day found the same class in nearly every early chapter (NWT "land of
     Fugitiveness" for Nod, DRB "my iniquity", ASV "as God" not "as gods", GNV "die the
     death", NIV "streams" for *ed*, the NWT 1984 still reading "ladder" at 28:12 — and one
     adopted LXX variant in the verse text, Gen 4:15 "Not so" for the Masoretic "Therefore").
     Attribute values are excluded (`href="#v21-8"` was the one false positive), and
     Deuteronomy 15/21 report identical results with and without it.
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

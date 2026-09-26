# MisterLibrarian — Claude instructions

This repo publishes **six separate things at mistertranslation.com**, reached through a
hand-written 6-card hub at the bare domain root (`index.html` — added 2026-09-09 with three
cards; the fourth 2026-09-10; the fifth and sixth 2026-09-11). **Since 2026-09-18 the hub has
one small builder, `build_hub.py`**, which does NOT write the page: it refills the one
`<div class="latest" data-pub="…">` line inside each card from that publication's sources
(newest non-draft entry; the Bible's from bible.html's own "Newest:" button) and renders the
hub's own share image `img/og-hub.png`. Every builder below calls `build_hub.refresh()` at the
end of its `__main__`, so publishing anywhere refreshes the hub — never hand-edit a latest
line, and keep the six `data-pub` slots when editing the cards. The copy, cards and styling
stay hand-written in `index.html`. Card convention (2026-09-18 review): the big `<h2>` is the
PUBLICATION's name (the brand), the small eyebrow is its category; the persona is
"Mr. Librarian" everywhere on the hub.

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
5. **The Librarian's Notebook** (`/notebook/`, `build_notebook.py`) — a commonplace book:
   science & technology, the world, arts & culture, and whatever else fits none of the
   other four. The one ORDINARY blog on the domain. Added 2026-09-11; see its own section
   below.
6. **Eight Miles West** (`/west/`, `build_west.py`) — a family history published a
   chapter at a time; a BOOK (numbered chapters in five fixed parts, read in order), not a
   blog. Added 2026-09-11; see its own section below.

**Read `README.md` first** for the mechanical how-to (build commands, how to add a chapter
or a travel entry, publishing). It's well-maintained and this file doesn't repeat it. This
file is the layer README doesn't cover: translation doctrine, editorial judgment calls,
paid-for gotchas, and the conventions that only show up once you've been burned by them.

## Keeping this file small (2026-09-25)

This file is loaded in full into every Claude session in this repo, so its size is a direct
per-session cost. **Budget: 70,000 bytes** (`wc -c CLAUDE.md`). It holds current rules plus
pointers; surface-specific detail and dated history live in `claude-docs/*.md` (moved there
verbatim on 2026-09-25 — nothing was dropped or reworded). **New dated history, incident
write-ups and "paid for on …" narratives go into the relevant `claude-docs/*.md` file, not
here** — add at most a one-line rule here when a lesson changes what every session must do.
When a section below points at a `claude-docs/` file, read that file before working on that
surface. (The mstr-trader repo enforces the same pattern with a size-budget commit hook; a copy
may be added here.) `claude-docs/` is served publicly by GitHub Pages exactly as this file is,
so the same rule applies: nothing private goes in either.

## Voice — a touch of wit, across every publication (Michael's ask, 2026-09-16)

Michael reads Morning Brew and Robinhood Snacks for their morning newsletters and wants more
of that in his own writing here — not a tone swap, an addition. **The wit rides on top of a
real fact; it never replaces one, and it never softens or hides an uncertain claim, a risk, or
a hedge.** A joke that makes a shaky number sound more certain than it is fails this site's own
honesty doctrine before it fails as a joke. Concretely: look for **one or two moments per
entry** — usually the opening hook, a section transition, or a closing line — where a wry,
plain-spoken observation can do double duty as both true and funny, the way Morning Brew turns
a real earnings miss into a one-line punch rather than burying the joke in a separate aside.
Compare a flat sentence to a witty one carrying the identical fact: "Municipal Credit's tokenized
value is $8.34" (flat) vs. "Municipal Credit clocks in at $8.34 — not billion, not million,
*eight dollars and thirty-four cents*, which is either the newest category on the board or
someone's lunch money" (same fact, now it has a pulse).

**Calibrate per publication — this is not a uniform volume knob:**
- **The Ledger** (`/finance/`) and **The Librarian's Notebook** (`/notebook/`) have the most
  room — first-person, conversational registers already, so a wry aside fits naturally between
  the citations.
- **The Librarian Abroad** (`/travel/`) and **The Librarian's Regimen** (`/health/`) take it
  more lightly — travel already has personality built in; health writing needs the humor to
  never read as flippant about someone's actual medical situation.
- **The Bible project** (`/bible.html`) and **Eight Miles West** (`/west/`) take the least —
  the translation doctrine above already forbids first-person meta-commentary on the page, and
  a family history has real people's real lives in it. Any wit there lives in a genuinely
  interesting turn of phrase about the text or the history itself (a name-pun payoff, an
  ironic historical detail), never a jokey aside from the writer.
- **Never at the expense of the per-publication rules above or below this one** — the Ledger's
  "Where I Could Be Wrong" honesty, the Bible project's reader-check translation standard, and
  every other doctrine in this file all outrank being funny.

**How to remember this without being told again:** it's saved as a standing feedback memory
(`feedback_add_wit_to_blog_voice` in Claude's own memory store) in addition to living here, so
it should surface on its own in a future session — but if a run of entries reads dry again,
that's the sign to re-read this section rather than wait to be asked twice.

## Every entry gets a hero image, and a drafted (not posted) tweet (Michael's ask, 2026-09-23)

Caught the first time on a `/health/` entry that shipped with neither. Two separate misses,
one root cause — publishing was treated as done once the page built and the sources checked
out, when two more steps are actually part of "done" for every blog on this domain (Regimen,
Ledger, Notebook, Travel — not just the one this was caught on):

- **A hero image, by default.** Every existing `/health/` entry has one; Ledger and Notebook
  are close behind (27/33 and 31/39 as of 2026-09-23 — the exceptions are the rule Michael
  hasn't pushed on, not evidence a hero is optional). `REQUIRED_KEYS` in each builder doesn't
  enforce this — the build will happily ship without one — so it has to be a checklist habit,
  not something a missing `hero:` line gets caught by. Source a real, on-topic, properly
  licensed image (Wikimedia Commons public-domain/CC search is the usual path — a period
  anatomical plate, a historical photo, a relevant CC-licensed photo; see any existing
  `source/<pub>/*.html`'s `hero_credit:` line for the citation format), web-size it
  (~1400–1600px wide is the existing range) and strip metadata before it goes in
  `<pub>/img/`, which is the tracked, canonical location (not gitignored, not a separate
  `source/<pub>/img/`). Skipping the hero is a real option only when there genuinely isn't a
  fitting image to find — not the default when one wasn't looked for.
- **A tweet, after publishing — drafted, never posted. Settled 2026-09-23, Michael's call.**
  A posting mechanism exists (`tools/post_to_x.py`, built the same day: standard library
  only, hand-rolled OAuth 1.0a/HMAC-SHA1 signing verified against X's own published worked
  example and independently against `openssl dgst -sha1 -hmac`; `--dry-run` signs and prints
  a request without spending anything). **It stays unused by default.** X moved to
  pay-per-use pricing 2026-02-06 — no free tier, roughly $0.20 per post since an announcement
  tweet always carries a URL — and once Michael saw that, his call was that it's a sensible
  way for X to charge, and that he'd rather post these by hand than pay per tweet. So: no X
  developer app, no credentials, no `~/.misterlibrarian/x_credentials.json` — none of that
  should be requested or chased. **The standing workflow is: after publishing, draft the
  tweet text (under 280 chars including the link — a plain manual count is fine; the script's
  `_tco_length` helper in `tools/post_to_x.py` does the t.co-adjusted version if it's worth
  double-checking) and hand it over in chat for Michael to post himself.** The script is kept
  — not deleted — because the underlying decision was about the API's price, not about the
  code being wrong or the idea being bad; if that ever changes (a price drop, a free tier
  returning, or Michael simply changing his mind), it's ready to go with no further work.
  Don't independently decide to set up credentials or spend money on this without him raising
  it again.

## Monetization — Google AdSense publisher policy binds EVERY publication (2026-09-17)

Michael applied for Google AdSense on 2026-09-17 (privacy.html / librarian.html were built
for it — see the hub section above). From that day the whole domain is a Google publisher
property, and **AdSense can demonetize a page, or drop the whole site, for content that
breaks its publisher policies — retroactively, on any page, on any of the six publications.**
This is a standing editorial constraint, not a one-off. The note Michael asked for on
application day, seeing the AdSense home-page banner:

- **Ukraine / Russia.** Google's standing notice: *"Due to the war in Ukraine, we will pause
  monetization of content that exploits, dismisses, or condones the war."* Read it exactly —
  it does NOT forbid writing about the war. It forbids three postures: **exploiting** it
  (clickbait, using the war as a hook for something else), **dismissing** it (denying or
  minimizing it — "nothing is really happening," "it's all staged"), or **condoning** it
  (justifying or cheering the invasion, repeating Kremlin framing as fact). Sourced, sober
  explainers about the war, its economics, its refugees, its history — the Notebook's and the
  Ledger's ordinary mode — are fine. The failure mode to avoid is a wry line that reads as
  minimizing, or a "both sides" framing that reads as condoning. When in doubt, cite the
  documented fact and drop the joke — the wit doctrine above already says wit never softens a
  real thing, and this is the sharpest case of it.
- **The broader Google Publisher Policies** apply equally and are the ones more likely to bite
  by accident on this site: no **dangerous or derogatory** content (attacking a group on
  religion/ethnicity/nationality — relevant on the Bible project's comparative-tradition notes,
  which present disagreements between traditions rather than settling them, which is exactly
  the safe posture); no **misrepresentation** (claims presented as fact that are demonstrably
  false — the site's own sourcing doctrine already exceeds this, keep it); no **unreliable and
  harmful claims** in health (the Regimen's "not medical advice" + primary-literature standard
  is the protection — never a cure claim, never "stop your medication"); nothing sexually
  explicit, no shocking content, no promotion of dangerous products. Financial content is
  allowed; **financial advice** and "get rich" framing is where the Ledger's own "measurement,
  never a recommendation" rule does the work.
- **Mechanics to remember:** don't click your own ads (an instant ban); don't place ads on
  the 404/thanks/contact pages or pop them into the middle of a form; if ads ever go on the
  Bible chapters, keep them out of the Hebrew/Greek source panels. `privacy.html` §6 already
  carries the required cookie/opt-out language and says "no ads running as of the date at
  the top" — **flip that sentence and its date the day ads go live.** The verification
  `<script>` goes in every page shell (`build.py`'s `page()`, the five blog `_shell`s, and the
  hand-written `index.html` / `privacy.html` / `librarian.html`), never pasted per page.

**Amazon Associates (2026-09-17) — text links only, tagged at build time.** One tracking ID per
blog in `blogkit.AMAZON_TAGS` (`librarianledger-20` / `librarianregimen-20` / `librarianabroad-20`;
the Notebook has none on purpose — nothing there mentions products; the account's old catch-all
`thwoneme-20` is retired here). **Write a plain product URL in the source
(`https://www.amazon.com/dp/B0XXXXXXXX`) and nothing else** — each blog's loader runs
`blogkit.tag_amazon_links`, which appends that blog's `tag=` and sets
`rel="sponsored nofollow noopener"`; never paste an `amzn.to` short link (its tag is baked into
the redirect and can't be rewritten — the Coldcard entry's was one, pointing at a store page
under the old ID, and was replaced with the `/dp/` URL). Two disclosures, both automatic: (1)
Amazon's required sentence (`blogkit.AMAZON_DISCLOSURE`, EN + ES) lands in a blog's footer the
moment ANY of its entries links to Amazon (`AFFILIATE_LIVE` in each builder) and not before —
today that is the Ledger only; (2) the travel blog's opening entry promised a paid link would
"say so plainly where it happened," so every builder REFUSES an entry that links to Amazon
without the word "affiliate" in its own text (`blogkit.affiliate_note_missing`; the Coldcard
entry's `.half-note` is the model). **No banners, no Native Shopping Ads widgets** (Michael asked;
declined — they convert worse than an in-sentence link and compete with AdSense for the same
slots). Expectation set honestly: 45 clicks → 1 order → $0.10 for all of 2026 across the account;
this is plumbing so a link written anyway gets credited, not a revenue plan.

## Hub, cross-links and site-wide legal pages

The old "the Bible project links to nothing and is linked from nothing" isolation rule was
**RETIRED 2026-09-09 — don't reintroduce it.** Current state: the hub (`index.html`) links all
six publications; since 2026-09-18 every blog's footer (each builder's `SIBLINGS`, and
`build_travel.py`'s hand-rolled header/footer links) also links straight to `bible.html`, while
`build.py`'s own ~2,772 pages were deliberately left untouched. Librarian Abroad ↔ finance
board link directly too. Bible pages keep their root-level URLs; only the old homepage moved,
to `bible.html` (`HOME_URL`). **Each builder writes only inside its own output area, never
globs or deletes elsewhere, and never imports another builder.** ⚠ `build.py`'s
`check_built_descriptions()` also scans the hand-written root pages and FAILS the Bible build
when any `<meta name="description">` runs past 160 characters — count it when editing the hub.
`privacy.html` (one policy for all six publications) and `librarian.html` (site-wide About &
Contact) are hand-written in the hub's style; every footer links the policy — change it by
editing `privacy.html` and moving its dated line, never by forking per-publication copies.

Full detail (the retirement history, the Spanish-footer imprecision, the AdSense wording the
policy must keep): `claude-docs/hub_and_crosslinks.md` — read it before editing the hub,
footers, sibling links or the legal pages.

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
- **Spanish verse text addresses a plural "you" as *ustedes*, never *vosotros*** (Michael's call,
  2026-09-25): *les digo*, *saben*, *Dejen*, *Vayan*, *Tengan*, *su Padre* — never *os digo*,
  *sabéis*, *Dejad*, *Id*, *Tened*, *vuestro Padre*. Mark is converted; Matthew, John, Acts and
  most of the OT are legacy *vosotros* — convert a whole book at a time, and change a note's
  quote of a verse with the verse. Shelf quotations (RV 1909/RV60 print *vosotros*) stay exact.
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

Every chapter page and dictionary/encyclopedia/atlas/route entry page carries a bare
two-button row (`build.py`'s `_note_nudge()`, class `.notebtns`: **✏️ Take a Note** /
**🔍 View Notes by Others**, built on `blogkit.py`'s X links). **No pitch paragraph, no box, no
"Public" in the button label** (Michael's call). On chapter pages it sits ABOVE VERSE 1; the old
private per-chapter notes panel (and its notebook backup UI) was deliberately removed —
per-verse notes/highlights are unchanged. Not yet wired into the Spanish (`.es.html`)
entry-page builders. Full detail: `claude-docs/bible_public_notes.md` — read it before
touching that row or `reader-notes.js`'s panels.

## Per-chapter checklist

The steps below are the current rules. **The full original text of this checklist — every
dated incident and worked example that explains WHY each sub-rule exists (the Numbers 7–36,
Deuteronomy 14–26 and Genesis 1–33 reviews, the tool-calibration numbers, the known tool
traps) — is preserved verbatim in `claude-docs/chapter_checklist_history.md`.** Read it before
your first chapter in a session, and whenever a check below fails in a way you don't
understand.

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
   actually resolve) — read a build failure from either as real, not noise. It reads bare
   same-book citations ("(14:22, not yet…)") and lists inside their own parenthesis, but NOT a list
   written before its parenthesis or an unparenthesised "…, neither yet on these pages." — when a
   chapter ships, grep older pages for its book and chapter number by hand.
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
   structures. ⚠ It reads the AST of `library_data.py`, never the imported object — Python
   silently collapses a duplicate key while building a dict literal, so
   `Counter(DICTIONARY_ES.keys())` is *guaranteed* to find nothing. **To fix one: read the
   LOSER for what only it says, merge both into the entry at the EARLIER position, and let the
   survivor keep the earlier first-discussed reference.** (why: `claude-docs/chapter_checklist_history.md`, step 4)
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
8. **Run a CLAIMS PASS — separate from, and after, every check above.** The build validates
   *structure*, never *assertions*. `check_local_anchors()` proves a link resolves;
   `check_forward_claims()` proves a chapter exists. **Neither one reads what you said about
   it.** Re-read every asserting sentence and check (why, with every incident:
   `claude-docs/chapter_checklist_history.md`, step 8):
   - **Absolutes are guilty until proven** — "first / only / never / every / the one place."
     Grep the shipped source for the counter-example *before* keeping the word. For a claim
     about the HEBREW, grep the actual text, not a memory or a web search:
     `python3 tools/heb_search.py <hebrew>` searches all 929 archived OT chapters
     consonantally (`--book X`, `--count`). It matches **letters, not lemmas**, so read the
     hits rather than quoting the tally.
   - **AND RUN THE COUNT CHECKER, do not re-run your own search:
     `python3 tools/count_check.py <fragment.html>`.** **Every corpus-count claim must carry
     the Hebrew it counted, in a `data-heb` attribute inside the same sentence**
     (`the root <em data-heb="שמט">shamat</em> stands in <strong>eleven verses</strong>`).
     ⭐ **The pass that matters is NARROWER, not the re-run:** for a multi-word query the tool
     also counts the head word and prints both — a claim resting on a phrase while the prose
     talks about "the word" or "the formula" is the failure. `a|b` unions two spellings;
     `data-heb-read=` declares a count reached by READING the hits. It does NOT check a tally
     of versions against an enumeration — counting an enumeration stays yours. **One claim per
     sentence** (only the first count in a sentence is read).
   - **Recompute every number.** A count must match the list it introduces; a stated ratio
     gets the division done.
   - **Open every chapter you cite** — its actual shipped text, not just proof the file
     exists. Cross-reference *existence* and cross-reference *substance* are different checks
     and only the first one is automated.
   - **ENUMERATE every sentence that asserts something about a text OUTSIDE this chapter,
     and fetch each one.** ⭐ Patching the specific category that was last criticised does not
     work — the laxity reappears one category over. "X says Y" about ANY text you are not
     currently translating is guilty until fetched: other biblical books, the New Testament
     (`tools/source_text.py` covers all 1,189 chapters, Greek included), and named
     non-biblical sources — if you cannot produce it, say in the note that it is reported
     rather than verified, or cut it.
   - **FETCH every shelf quote you print. Never write one from memory.** For the NWT/TNM, ASV
     and KJV that fetch is `python3 tools/shelf_text.py <Book> <Ch> --all`.
   - **Then RUN the check, do not just intend to: `python3 tools/shelf_check.py
     <fragment.html> --book Numbers --chapter NN --shelf-dir <dir the fetches wrote to>`.**
     Written rules compete for attention and lose; scripts do not. Traps: ⚠ **an OFFSET
     chapter needs the PREVIOUS chapter's BibleGateway text too, under `<NAME>_prev.json`**;
     ⚠ **in a NEW worktree the shelf dir is not there** (`source/shelf/` is gitignored) —
     `cp -R` it from the chapter's own worktree (or re-fetch) BEFORE believing a single MISS,
     and treat a sudden collapse in the "checked quotes" count as the tell. **Read the
     PARTIAL lines rather than trusting "clean"**; PARAPHRASES are counted and NOT checked;
     UNTAGGED version-name warnings are yours to read. ⭐ **WRITE SHELF LISTS TAG-FIRST, and
     run the check on BOTH panels** (English and Spanish).
   - **A matching VERSE COUNT does not prove matching VERSE NUMBERS.** English Exodus 22 is
     offset by one against the Masoretic text, while `deuteronomy-5` follows MT — the
     convention is not uniform across the site. **The check is to open the target verse and
     read it**, never to compare chapter lengths.
   - **Run the shelf rule on BOTH shelves, and re-run it on every version's own
     REVISION.** (a) **The Reina-Valera is not one version** — fetch the edition you are
     naming (RV antigua 1909 vs RV60). (b) **A version's own revision is a different
     witness** (NWT 1984 vs 2013; TNM 1987 vs 2019) — naming the wrong edition is the same
     error as naming the wrong version.
   - **Check what you assert ABOUT a list, not just the list.** The members and the count can
     all be right while the predicate binding them is wrong.
   - **DIFF THE TWINS, mechanically, verse by verse — AND RUN IT, do not re-derive it:
     `python3 tools/twin_diff.py <slug> --prose --all`** (or two file paths for a pre-splice
     fragment). **SHAPE** (default: per note id, paragraph count, digits, outbound-link set)
     FAILS the run; **PROSE** is triage — the **side-by-side print is the check**, and a human
     reads across it, which is why `--all` is the mode for a chapter about to ship. A
     divergence usually means **neither** side has a note; the fix is often to make both
     sides strange and explain it once, not to smooth one of them.
   - **AND DIFF THE NOTES, not just the verses.** Per note id — paragraph count, shelf tags,
     digits, and the set of outbound links — and treat a link present on one side only as a
     defect until proven otherwise (a cited chapter with no Spanish edition is flagged, not
     linked: "ya en estas páginas, todavía no en español"). ⚠ Check that a citation's link
     actually points at the chapter it names, and sweep a fix for its parallels.
   - **A fix written during the review is not exempt from the review.** New prose written in
     an audit needs the same fetch-and-check as the prose it replaces.
   - **Diff the bookkeeping.** A chnote saying "X and Y extended, N new entries" must match
     `git diff library_data.py`.
   - When a claim fails, prefer the one that survives — it is usually the better note anyway.
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

Must-knows: a new entry is one file, `source/travel/YYYY-MM-DD-slug.html` (copy
`source/travel/_template.html`). **Never tell Michael a photo is unreachable without first
trying the Photos.app AppleScript recipe** in the full doc — `ls`/`mdfind`/`find` failing on
the Photos library is ordinary TCC sandboxing, not evidence. **Every photo must go through
`python3 tools/travel_photos.py <files>`** (web size, EXIF/GPS stripped) before it is used —
git history is forever. Ask for a voice memo before a food entry (the memo's filename names
the wrong venue; the transcript is a draft, not a quote). Writing in his first-person voice is
the job, but it goes through the drafts pipeline (`draft: true` → `travel/drafts.html`) before
it's public. **Never invent a specific he didn't give you** — above all his own experience of
a dish. Originals/video → `python3 tools/travel_archive.py add <slug> <files...>`, slug
written explicitly.

Full detail (the exact AppleScript/export syntax, transcription, Librarian's Stars, the reader
form): `claude-docs/travel.md` — read it before working on /travel/.

## The finance board (`/finance/`)

"The Ledger" — a standard-library build (`build_finance.py`) that only reads data snapshots
written by separate fetchers, so a provider's bad night can never fail a build or blank a page.
Eight standing boards (Asset Board, Bitcoin Board, Bitcoin Treasuries, CEBE, Crypto Heat Map,
Bitcoin vs. Humanity, Money Worldwide, Crypto Screener) beside the Ledger's written entries.
Must-knows: **a live price quoted in an entry is a dated snapshot** — write it with an explicit
date anchor, link the live board, and re-check every quoted figure after merging `main`
(`live: true` and the `{{BTC_*}}` tokens do not cover prices); **the Bitcoin subsidy
arithmetic exists three times** — touch any copy and run
`python3 tools/fetch_bitcoin_stats.py --selftest`; the refresh workflow's hourly cron really
runs ~6×/day, so never reason about freshness from the cron line; no BUY/HOLD/TRIM/AVOID-style
verdict next to a specific coin; keep the board table in the full doc current when a board is
added.

Full detail (every board's data sources, fetcher quirks and paid-for bugs, the price chart,
the three kinds of number, what is deliberately absent): `claude-docs/finance.md` — read it
before working on any /finance/ board, fetcher or entry that quotes a figure.

## The Librarian's Regimen (`/health/`)

`build_health.py` (standard library, no network) — the writing half of `build_finance.py`,
near-verbatim; the two do not import each other (shared fixes go in `blogkit.py`). **No drafts
page — ships live**; `--drafts` is a local noindexed preview, never committed. Must-knows:
**every entry ends with `<ol class="sources">` or the build refuses it**; evidence
(`<div class="verdict">`) and his judgment (`<div class="mine">`) stay visibly apart; numbers,
not adjectives; **never dosing aimed at the reader, never "you should start/stop"**, and keep
every disclaimer (`_disclaimer_box()`, `.mednote`, footer, `disclaimer.html`) in place; **name
the salt** (calcium carbonate vs citrate, magnesium hydroxide vs citrate); **never invent his
experience** of his own body. A Spanish twin is a `.es.html` beside the original and must cite
the same source numbers the same number of times.

Full detail: `claude-docs/health_regimen.md` — read it before working on /health/.

## The Librarian's Notebook (`/notebook/`)

`build_notebook.py` (standard library, no network) — the one ordinary blog on the domain; the
writing half of `build_health.py`. Editorial line: **if the spine of a piece is a price, a
balance sheet, or an institution that moves money, it's the Ledger; otherwise it's the
Notebook.** Must-knows: **`section:` is REQUIRED** and must be `technology` / `world` /
`culture` / `notes` (the `SECTIONS` table); **no drafts at all** — every file in
`source/notebook/` builds and ships, so publish and tell him it is live; sources optional; no
Spanish edition by default; keep geopolitics analytical; never invent his experience or his
opinion.

Full detail: `claude-docs/notebook.md` — read it before working on /notebook/.

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
- **The `dict/`, `ency/` and `atlas/` per-entry pages are `noindex,follow` and out of the
  sitemap (2026-09-17, Michael's call — reversing the 09-10 wait-and-see).** `NOINDEX_PREFIXES`
  in `build.py`, applied inside `page()` off the `url=` prefix, so no call site opts in or out
  by hand; the sitemap's existing noindex sniff drops them (3,814 → 738 URLs). Measured the
  same day: dict median 140 body words, ency 172, atlas 201, vs 4,114 for a chapter — 3,077
  thin pages beside 347 substantial ones — and GSC's per-reason exports showed the cost: the
  stubs got crawled in July and made up most of the 1,718 indexed pages while ~220 of 347
  English chapters sat un-indexed and impressions ran ~0–3/day. Readers see no change; the
  landing pages (`dictionary.html` / `encyclopedia.html` / `atlas.html` + Spanish twins) and
  `routes/` stay indexable. ⚠️ **GSC's Indexed count WILL fall** toward ~400–500 over the
  following weeks — that is the fix working, not a regression; the number to watch is English
  chapters indexed (~127 of 347 at the time) and daily impressions. To reverse: remove a
  prefix from the tuple and rebuild. Full trace in Claude's memory
  (`project_mistertranslation_indexing_cliff`).
- `page(...)`'s `url=` argument controls **both** the canonical tag and `og:type` at once
  (`og_type = og_type or ("article" if url else "website")`). Passing `url=` to fix a missing
  canonical on a hub/index page (home, table of contents, dictionary index) will silently
  flip its `og:type` to "article" unless you also pass an explicit `og_type="website"`.
- hreflang lives in the **sitemap**, as reciprocal `<xhtml:link>` entries per `.es.html`/
  `.html` pair — not as `<link>` tags in the page `<head>`.
- Search Console ownership is verified via `google3b2c8b57143d235a.html` at the repo root
  (a single verification line). **Never delete it** — Google re-checks it periodically.

## Front-end JS — the Spanish edition is a page, not a locale flag

`reader-notes.js`, `share.js` and `audio-reader.js` run on **both** editions off one file.
Must-knows: language is `(document.documentElement.lang || "").toLowerCase().indexOf("es") === 0`
— never sniff the `.es` filename; **the verse line is `.eng` in English and `.esp` in Spanish**
— a `.eng`-only selector silently reads nothing on every Spanish chapter; anything reading a
verse must strip the widget chrome inside it. **Storage keys, `/v/` stub URLs and download
filenames must NOT branch** (`baseStem()`/`KEY_PATH` strip `.es`). Each edition has its OWN
`/v/` share stub. **Verse cards live in the public S3 bucket, not this repo — don't move them
back** (GitHub Pages hard-caps a site at 1 GB); `img/v/.cards.json` is tracked and
load-bearing. `?v=` is a content hash — editing a `.js` file does nothing for readers until
`build.py` is re-run.

Full detail (bucket, credentials and key permissions, the migration numbers, the Spanish
default card, where the Spanish book name comes from): `claude-docs/frontend_js.md` — read it
before touching any of those JS files or the verse-card pipeline.

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

## Eight Miles West (`/west/`)

`build_west.py` (standard library) — Michael's family history, published as a BOOK (numbered
`NN-slug.html` chapters in five fixed parts, read in order), not a blog. Must-knows: every
sentence is documented (cited prose), inferred (`<span class="infer">`) or family legend
(`<div class="doc legend">`, never promoted to fact later); `<ol class="sources">` is
REQUIRED; drafts keep the Regimen's posture (`draft: true` = not built, `--drafts` = local
preview, never committed) because later chapters concern living people. **Since 2026-09-24
his real name is OFF the web version** (`AUTHOR` = `"mistertranslation.com"`), except where he
is a cited SOURCE inside a chapter — and don't spread the real name to the other five
publications.

Full detail: `claude-docs/west.md` — read it before working on /west/.

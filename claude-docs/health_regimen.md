# The Librarian's Regimen (/health/)

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


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

- **The Spanish edition (2026-09-10 — the kidney-stone entry is for a Spanish friend).**
  Same conventions as the Bible project's: a twin is a `.es.html` file beside its English
  original — `source/health/YYYY-MM-DD-slug.es.html` (same front-matter vocabulary, its own
  Spanish title/summary/tags, body translated, SAME source list with the SAME citation
  numbers) builds to `health/<slug>.es.html`; the front page's twin is `es.html`; About /
  Ask / Thanks / Disclaimer have `.es.html` twins; the feed is `feed.es.xml`. Every page
  carries `lang`, `og:locale`, hreflang alternates (head + sitemap) and a header language
  link (to the twin when one exists, else the other front page); a paired entry also gets a
  "Read this entry in English / Leer esta entrada en español →" line under its date.
  **Tag pages are English-only** — a Spanish entry's chips hand off to `es.html?tag=…`.
  Every reader-visible string is in `UI[lang]` in `build_health.py`; `e["lang"]` is set at
  load, never sniffed from the filename. Site name in Spanish is "El Régimen del
  Bibliotecario"; the author stays "Mr. Librarian" (a name, as on the Spanish Bible pages).
  Spanish (Spain): `usted` for the reader, Spanish number format (43.545 / 1,17 / 67 %),
  112 ahead of 911 in the emergency line, and the Spanish disclaimer says the English text
  prevails on any discrepancy. ⭐ **Twin-diff before shipping**: the two editions must cite
  the same source numbers the same number of times (`Counter` over `href="#src-N"` in each
  body) — a translation that drops or moves a citation is a defect, same rule as the Bible
  chapters' notes.

**Adding an entry:** copy `source/health/_template.html` to
`source/health/YYYY-MM-DD-slug.html` (the header comment is the checklist), rebuild, commit
`health/` + `source/health/`, push. A Spanish twin is optional per entry and is the same file
with `.es.html`. Pictures go in `health/img/` web-sized and EXIF-stripped
(`tools/travel_photos.py` for a photo; for a public-domain illustration keep the source and
licence for `hero_credit:`). The sitemap is advertised in the root `robots.txt`; submit
`health/sitemap.xml` once in Google Search Console, same as the other two.

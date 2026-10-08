# The Librarian's Notebook (/notebook/)

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## The Librarian's Notebook (`/notebook/`)

A commonplace book — science & technology, the world, arts & culture, and whatever else
didn't fit. Built by `build_notebook.py` (standard library only, no network), source in
`source/notebook/`, output in `notebook/`. Added 2026-09-11, Michael's call, as **the one
ordinary blog on the domain** — the place where the person, not the subject, is the
through-line. The other four are special-purpose by design (scripture / money / the road /
the body), and everything Michael writes "every so often" outside them — a technology piece
with no Bitcoin in it, a geopolitics or news explainer, the rare arts piece — had nowhere to
go. **The tell that it was needed:** by 2026-09-11 three such pieces had already landed in the
Ledger under a soft `notes` tag (the Propst cubicle essay, the AI-token pricing piece, the
BIS/IMF/World Bank explainer). They stay where they are (live URLs; each has a money angle) —
`tools/make_redirect_stubs.py` exists if he ever wants one moved.

**Why ONE new publication and not two** (a science-&-tech vertical plus a general one was
considered): at "every so often" and "rarely" each would look dead within months, and a blog
whose last entry is four months old loses the reader on arrival. One publication at the
combined cadence is a living blog. The editorial line this leaves the Ledger with: **if the
spine of a piece is a price, a balance sheet, or an institution that moves money, it's the
Ledger; otherwise it's the Notebook.**

**What it is mechanically:** the WRITING half of `build_health.py`, near-verbatim (which is
itself the writing half of `build_finance.py`) — same front-matter vocabulary minus `draft`
plus `section`, same tile/list front page with the tag filter bar and header search, same
"Keep reading" recirculation, same tag-page/sitemap rules, same X comment layer, same
FormSubmit inbox (`_subject` tells it apart), same two-row header. Its mark is a notebook
page with a pen writing its last line (the ink draws itself via `stroke-dashoffset`, the nib
slides along it, then returns to the margin) — the SAME artwork is inlined on the root hub's
fifth card, so change both or neither. Accent is periwinkle ink `#8fa3ff`, the only cool
blue among the five. The front-page hero is folio 17v of Leonardo's *Codex on the Flight of
Birds* (public domain, Wikimedia `File:Codice_Volo_17V.jpg`), cropped to the page bounds
(the raw scan has a white margin all round; `object-position: center 5%` shows both bird
sketches). The builders do not import each other; a shared-mechanism fix goes in
`blogkit.py`, a page-chrome idea gets ported by hand.

**Conventions that differ from the other blogs — these are the ones to get right:**

- **`section:` is REQUIRED on every entry and must be one of `technology` / `world` /
  `culture` / `notes`** (the `SECTIONS` table in `build_notebook.py`; the build refuses any
  other value in `load_entries`). Each section is a nav link and its own page
  (`technology.html` etc.) built from the same listing code as the front page, filtered;
  always in the sitemap, even empty (it's navigation, not a duplicate). The section leads
  every tile's date line ("TECHNOLOGY · SEPTEMBER 11, 2026") and the entry page's date line,
  linked. Tags run underneath exactly as on the other blogs. ⭐ **The sections are the
  future split seam:** if one section outgrows the others, lift it into its own masthead with
  one redirect stub per entry and nothing else moves. Decide that from the counts, not now.
  To add a section, add a row to `SECTIONS` — nav, pages, sitemap and labels all read it.
- **NO DRAFTS, AT ALL** (Michael's call 2026-09-11: *"we don't need drafts. I can always go
  back and have you reword something"*). Unlike the Regimen there is no `draft:` key, no
  `--drafts` flag, no preview page — every file in `source/notebook/` builds and ships. So:
  write an entry in his voice, publish it, tell him plainly it is live and worth reading
  over. (`_template.html` is skipped by the leading-underscore rule, as everywhere.)
- **Sources are OPTIONAL** — an opinion piece may have none — but `<ol class="sources">`
  renders as on the Regimen when present, and the template asks for one wherever the entry
  leans on a figure or a document. `<div class="aside">` (accent-edged) is the one house
  box: a definition, a digression, the number behind a sentence.
- **No Spanish edition by default.** A twin doubles the cost of a post and the point of this
  publication is low friction. If a specific entry ever earns one, port the twin mechanism
  from `build_health.py` then — don't pre-build it.
- **One general disclaimer, once, in the small print** (`_legal`): not advice of any kind,
  one reader's opinions, not those of any employer. No per-page medical box (that's the
  Regimen's), no financial line (that's the Ledger's). The About page's "What it's not"
  points at those two for money and health.
- **Geopolitics next to a Bible translation is a real consideration**, and the structure is
  what makes it a choice rather than a leak: own feed, own section pages, so a translation
  reader or a Ledger subscriber never has to receive it. Keep the register analytical
  (the BIS/IMF explainer is the model — explain the thing, not the hot take).
- **Never invent his experience or his opinion** — the travel-blog rule. An opinion in an
  entry is one he actually holds and said, or it is left out.

**Adding an entry:** copy `source/notebook/_template.html` to
`source/notebook/YYYY-MM-DD-slug.html` (the header comment is the checklist; set `section:`),
rebuild, commit `notebook/` + `source/notebook/`, push. Pictures go in `notebook/img/`
web-sized and EXIF-stripped (`tools/travel_photos.py` for a photo; for a public-domain
illustration keep the source and licence for `hero_credit:`). The sitemap is advertised in
the root `robots.txt`; **submit `notebook/sitemap.xml` once in Google Search Console** — a
human step, same as the other three.


## Running stories (2026-10-05)

A **running page** is an ordinary Notebook entry that is rewritten in place while a story moves
(first one: `2026-10-05-siberia-plague-death-what-we-know.html`) — an infographic briefing on
top (stats, timeline, claim-check table; scoped `.ig` CSS and an inline SVG icon sprite, no
builder changes), the full written detail below, and an `updated:` date plus a dated update log
that is bumped on every change. Keep status labels honest (confirmed / reported / disputed /
unverified) and never present a viral claim as established.

**The rundown box and running pages.** The rundown box (`_rundown.json`) is rewritten every day
by a cloud routine, "Notebook daily rundown" (claude.ai routines, 13:00 UTC), which overwrites
the file and by default only writes items with an empty `href`. That left a running story with no
link from the front page, and the routine missed the Siberia story for four days because nothing
told it to follow one. So: **`source/notebook/_running.json` lists the active running pages**
(`href`, `title`, `search`, `since`, `active`). For each active row the routine searches the
phrase, and if there is news from the last ~48 hours it adds ONE rundown item whose `href` is that
page (the one exception to the empty-`href` rule) and whose `source_href` is the real article.
The routine does not edit the running page itself; it reports in its final message when the page
looks behind, and a session on this box or the Mac updates the page. When you create a running
page, add its row; when a story is over, set `active` to `false`.

A row's `href` may point at another publication with a relative path (the 2026-10-05 Bessent/eurozone
row points at `../finance/…`). That entry is NOT rewritten in place; the row only keeps the rundown
linking to it while the story is in the news. Set `active` to `false` once it goes quiet.



## Standing page: the minimum wage (2026-10-07)

`source/notebook/2026-10-07-minimum-wage-what-it-was-for-and-what-it-pays-now.html` is a running page
in the infographic format above, but for a number that drifts rather than a story that breaks. To
refresh it: (1) federal rate (DOL rate chart); (2) California general rate (DIR news release each
August) and the fast-food rate (check the Fast Food Council; it was $20 with no increase as of
2026-10-07); (3) CPI-U latest month and average hourly earnings, both from the BLS "Real Earnings"
release; (4) recompute: 25¢ x (latest CPI-U / 14.1), 1968 $1.60 x (latest CPI-U / 34.8), 7.25 / AHE,
and annual pay at 2,080 hours; (5) re-stamp the `updated:` front matter, the band, the stat tiles, the
bars, the claim-check table and the footer, then add a dated line to the update log. The page's own
"planned additions" list (poverty line, who works these jobs, rent, the job-effects studies) is the
backlog. Its `_running.json` row means the daily rundown routine may link it when minimum-wage news
breaks; set `active` to false if that gets noisy.

## Standing page: the AI Scorecard (2026-10-08)

`source/notebook/2026-10-08-ai-scorecard-which-model-is-best-by-whose-test.html` is a running page in the infographic
format for AI model rankings. Michael's call: a standing page plus one ordinary entry per big release, and each release entry
feeds the page (first one: `2026-10-08-gemini-4-argon-benchmarks-checked.html`). **The page's point:** which model is best
*according to the scoreboards the labs don't run*. Its three house rules are printed on the page: every ranking comes from a
named, dated outside source; a lab's own benchmark table goes in the claim check until someone independent confirms it; no
single number decides "best". **Claude never ranks Claude** (Michael uses Claude, and the page discloses that); the bars come
only from the sources.

To refresh: (1) LMArena text leaderboard, overall (arena.ai/leaderboard/text): top 8 with score, ±CI, preliminary flag. The
bars are CI ranges on a 1480–1540 axis, `left = (score−CI−1480)/60`, `width = 2·CI/60`; widen the axis if scores leave it.
(2) Artificial Analysis leaderboard: Intelligence Index, ONE bar per model at its best setting, 0–60 axis, plus the top three
open-weight models (artificialanalysis.ai/models/open-source). (3) The same page's cost-per-task column for the cost panel.
(4) ARC Prize leaderboard and blog (standard harness vs provider adapter). (5) METR time-horizons page: it has been quiet
since 2026-05-08; a new suite or model is a timeline event. (6) Epoch AI open-vs-closed gap. (7) Platformonomics capex after
each earnings season. Then re-stamp `updated:`, the band, the panel `asof` dates and the footer, and add an update-log line.
A new model announcement becomes a claim-check row plus a story-so-far card linking its entry. All charts are inline HTML/CSS
in the page; there is no generator script to keep.

## Standing page: GLP-1 evidence scorecard (2026-10-07)

`source/notebook/2026-10-07-glp-1-drugs-what-the-evidence-shows-organ-by-organ.html` is a running page in the infographic format, a claim-check table graded by study design (randomized / early / observational / not established). New GLP-1 claims go in as a table row plus a timeline event plus an update-log line; link, don't duplicate, the two Regimen posts it summarizes. Public voice: reporting only, never medical advice, never anything about Michael's own use. Row in `_running.json` keeps the daily rundown following it.

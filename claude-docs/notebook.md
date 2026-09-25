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

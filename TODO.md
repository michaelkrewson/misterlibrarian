# Bible Project — feature parity with the other five blogs

Found 2026-09-19 by comparing `bible.html`/`ask.html`/`toc.html`/`library.html`/`chronology.html`
against the equivalent pages in Ledger (`finance/`), Notebook, Regimen (`health/`), and
Eight Miles West (`west/`). Check items off as we ship them.

- [x] **Site search.** Shipped 2026-09-19. A header search box (`.headersearch`, desktop
      `.topnav` + mobile `.mobmenu-panel`) now sits on every Bible-project page, submitting to
      a new `search.html` that live-filters a build-time `search-index.json` (2,101 items:
      353 chapters, 1,257 dictionary terms, 472 encyclopedia entries, 7 Dear Mr. Librarian
      posts, 12 core pages). Scoped to titles+summaries, same as the sibling blogs' own header
      search — full verse text is what the Concordance already covers. `search.html` is
      noindex'd (results page, no static content of its own). English only for now — the
      Spanish header doesn't carry a search box yet. Built by `build_search_index()` /
      `build_search_page()` in `build.py`; verified with Playwright (desktop + mobile
      screenshots, a real form GET-submit from `ask.html` landing on 98 live "jehovah"
      results, zero console errors). **Moved 2026-09-19** from the `.topnav` pill row (where
      it wrapped onto its own line) into `.utilnav-right`, alongside the language switch —
      Michael's call, to match the corner-controls placement search boxes usually get rather
      than sit in a nav row this header was never designed to hold it in (this header is a
      centered/symmetric design, unlike the siblings' left-brand/right-utility bar). Mobile
      menu's own copy (`#headerSearchMob`) untouched. Same pass widened `.hero p` (dropped its
      `max-width:70ch` cap) — once the hero photo went full-width, that cap was the one thing
      in the section not matching, and read as an awkward empty gap rather than a deliberate
      readability choice for a two-paragraph intro.
- [x] **Footer cross-links to the other five blogs.** Shipped 2026-09-19. Every English page's
      footer now carries a line linking The Librarian's Ledger / The Librarian Abroad / The
      Librarian's Regimen / The Librarian's Notebook / Eight Miles West, same names/order the
      hub (`index.html`) already uses for their cards. Deliberately left the Spanish footer
      (`ES_FOOTER`) untouched — its own documented invariant is that a Spanish-only reader is
      never sent to English-only content, and none of the five siblings has a Spanish edition.
      Verified on a root page and a `dict/` subdirectory page (which resolves the relative
      `finance/`-style hrefs against its `<base>` tag) — both correct.
- [x] **RSS feed.** Shipped 2026-09-19. New `feed.xml` (RSS 2.0, via the shared
      `blogkit.build_feed()` the other five blogs already use), autodiscovery `<link
      rel="alternate">` in every English page's `<head>`, and an "RSS" link in the footer.
      The Bible project has no front-matter/date system for chapters (unlike finance/travel's
      dated entries — see blogkit.py's own module docstring), so the feed's `posts` list is
      synthesized in a new `build_feed_page()`: the 40 most-recently-published chapters +
      the 7 Dear Mr. Librarian posts, each dated by git's real "date this file was first
      added" (`_git_added_dates()`, `git log --diff-filter=A`) rather than blogkit's own
      most-recent-touch lastmod — so a later wording fix doesn't resurface a chapter as new.
      47 candidate items, 30 shown (blogkit's own default limit). English only for now,
      matching search.html. Verified: well-formed XML (`xml.dom.minidom`), sane item dates/
      links/descriptions, autodiscovery tag present on root + `dict/` subdirectory pages,
      absent from the Spanish edition.
- [x] **Tags/archive index page — N/A, closed 2026-09-19.** `finance/tags.html` is a topic
      cloud for a dated-entry blog: ~170 posts hand-tagged at authorship with editorial themes
      ("bitcoin," "cftc," "seed phrase"), grouping *articles* by *subject*. The Bible project
      has no equivalent data (no tags exist anywhere on a chapter/dictionary/encyclopedia
      entry), and retrofitting one would mean hand-tagging 353 already-published chapters +
      1,257 dictionary + 472 encyclopedia entries with themes invented after the fact — a real
      content-curation project, not a feature port. The Concordance (`concordance.html`) is
      this site's correct analog: an auto-generated word index (word · count · links) built
      from the translation's own vocabulary rather than editorial tags — zero curation debt,
      and each reference links straight to the verse (confirmed: `<a href="genesis-1.html#v5">`
      per occurrence, not just the chapter). Revisit only if *thematic* browsing (e.g. "every
      chapter touching prophecy," which the Concordance genuinely can't do) becomes a wanted
      feature in its own right — that's a separate project, not this parity pass.
- [x] **"Dear Mr. Librarian" pattern mismatch.** Shipped 2026-09-19 (Michael's call: match the
      other blogs' functionality/look, with updated cards). `ask.html` now opens with the same
      live question-submission form finance/notebook/health's own "Ask Mr. Librarian" pages
      are (name/email optional, question required, captcha note) via a new shared
      `_question_form_html()` (`id="ask-form"`), with the existing 7-post FAQ archive kept
      below it under a new "Answered so far" heading rather than thrown away — unique content
      the siblings don't have. `contact.html` still builds and works at its old URL (backward
      compat for anyone who bookmarked/shared it) but is no longer linked from the header/
      footer/mobmenu/per-post CTAs — those now point at `ask.html#ask-form`. Updated: the
      homepage's "Dear Mr. Librarian" card description (now mentions asking, not just
      browsing), `ask.html`'s own meta description, and the search index (merged the separate
      `contact.html` entry into the enriched "Dear Mr. Librarian" one, 2101→2100 items).
      Verified with Playwright: form renders correctly, footer/mobmenu links jump straight to
      `#ask-form`, `contact.html` still returns 200, zero console errors.
- [x] **Homepage hero photo is small/side-column, not a banner.** Shipped 2026-09-19. The
      Great Isaiah Scroll photo moved out of the 260–360px `.hero-grid` side column into a
      full-width `.fronthero` banner above the `<h1>`, matching finance/notebook/health/west's
      own `.fronthero` pattern (fixed-height, `object-fit:cover`, rounded, `loading="eager"`
      since it's now above the fold). Kept the richer figcaption sub-structure (bold
      manuscript-name line + body + a dimmer credit line) rather than flattening it to the
      siblings' single italic caption, since there's more real citation content here. Verified
      with Playwright on desktop + mobile — clean crop, everything below (CTA buttons, Verse
      of the Day, card grid) unaffected. Scoped to `bible.html` only (its Spanish twin,
      `es.html`, never used the old side-column layout).

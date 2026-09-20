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
      results, zero console errors).
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
- [ ] **Tags/archive index page.** Ledger has `finance/tags.html`. No equivalent for the
      Bible project.
- [ ] **"Dear Mr. Librarian" pattern mismatch.** On finance/notebook/health, that nav slot
      *is* the live question-submission form (name/email/question + captcha). On the Bible
      project it's a static FAQ digest, and the actual form lives a click deeper at
      `contact.html`. Decide: fold the form into `ask.html` to match, or leave as-is
      (arguably a reasonable variant, just inconsistent).
- [ ] **Homepage hero photo is small/side-column, not a banner.** `bible.html`'s hero photo
      (`.hero-fig`) sits in a 260–360px side column next to the intro text; every sibling
      blog leads with a full-width `loading="eager"` banner photo. Lower priority / cosmetic.

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
- [ ] **Footer cross-links to the other five blogs.** `finance/index.html`'s footer links out
      to all five siblings; `bible.html`'s footer only links back up to the hub
      (`mistertranslation.com`), not sideways to Ledger/Notebook/Regimen/Abroad/West.
- [ ] **RSS feed.** `finance/feed.xml`, `notebook/feed.xml`, `health/feed.xml` (+ a Spanish
      variant), `west/feed.xml` all exist. No `feed.xml` for the Bible project. (Needs a look
      at `build.py` to see how the other builders generate theirs.)
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

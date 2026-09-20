# Splitting "Dear Mr. Librarian" into its own blog

Scoped 2026-09-19, shipped 2026-09-19. Dear Mr. Librarian now has the same real structure
the other five blogs have (own home, own archive, dates, tags, sources, keep-reading, its
own feed) instead of living inside the Bible project's template — and stays OFF the
mistertranslation.com hub's card grid, per Michael's ask. Live at `/ask/`, reachable only via
the Bible project's own "📖 Dear Mr. Librarian" nav link.

## 0. The shape — decided

- [x] **Folder/URL: `/ask/`.** Confirmed — matches the fleet's own convention (finance/travel/
      health are generic topic nouns in the URL, not their fancy brand names, which only ever
      appear in `<title>`/header).
- [x] **Page names**: `ask/index.html` (archive homepage), `ask/ask.html` (the live submission
      form, matching `finance/ask.html`'s naming). Posts drop the `ask-` prefix now the folder
      carries it: `ask/great-tribulation.html`, not `ask-great-tribulation.html`.
- [x] **CSS: linked, not inlined.** `ask/style.css` layers blog-specific classes (entry
      dateline, tile grid, tag chips, tag filter bar) on top of the Bible's own shared
      `../style.css` (reused directly for `:root` vars, `.wrap`, `.panel`, `.fronthero`,
      `.notebtns`/`.respond-btn`, `.headersearch`, buttons — all already existed and needed no
      changes). One shared visual system, not a duplicated one.
- [x] **Feed: split.** The Bible's `feed.xml` is chapters-only again (`build_feed_page()`);
      `ask/feed.xml` is the real thing — front-matter dates via `blogkit.build_feed()`, not the
      git-history fallback the Bible's own feed needs.
- [x] **Sibling footer cross-links: off, deliberately.** `ask/`'s footer links back to the
      Bible project only ("Dear Mr. Librarian is part of The MisterLibrarian Bible Project") —
      it does NOT join the six-way Ledger/Abroad/Regimen/Notebook/Bible cross-link line that
      appears on every OTHER page across the domain. Same reasoning as no hub card: a footer
      cross-link is how a reader discovers a blog they didn't know existed, which is exactly
      the promotion Michael asked to skip.
- [x] **Revised during implementation, worth flagging:** the original plan proposed keeping
      the 7 posts listed in the Bible's own `search-index.json`/`feed.xml` too (repointed to
      the new URLs), reasoning that the nav link still lives in the Bible. Reconsidered while
      building: once the posts have a real home with their own archive/tags/feed, duplicating
      them in the Bible's OWN search index is just maintaining two listings for one thing.
      The Bible's search index now carries a single pointer entry ("Dear Mr. Librarian" →
      `ask/`, in the `Page` category, same as `Library`/`Concordance`) instead of all 7 posts
      individually — findable, not duplicated.

## 1. Scaffold — done

- [x] `build_ask.py` (new, ~470 lines) — own header/footer (`_chrome()`/`_foot()`), reusing the
      Bible's scroll-mark SVG for visual continuity. Nav: Home / Tags / Ask a question / ← The
      Bible — no topic pages the way finance has (Bitcoin Board etc.), so deliberately thin.
      No view-toggle/load-more pagination or live JS tag-filter bar (health/finance's kind) —
      a plain tile grid plus a static `/tags.html` is the honest amount of machinery for 7
      posts; the code is structured so the fuller pattern can be ported in later if the
      archive grows enough to need trimming.
- [x] `ask/index.html` — full-width `.fronthero` banner (reused the Great Isaiah Scroll photo
      already licensed/credited for `bible.html`'s own hero, rather than sourcing/licensing a
      new image), tag chip row, tile grid of all 7 posts.
- [x] `ask/tags.html` + 14 per-tag pages (4 indexable at `TAG_INDEX_MIN=2`, 10 held back
      noindex'd until they earn a second post — same convention as health/finance).
- [x] `ask/feed.xml` (7 items) + `ask/sitemap.xml` (14 URLs) — both validated well-formed.
- [x] `robots.txt` gained the `Sitemap: .../ask/sitemap.xml` line.

## 2. Migrated the 7 existing posts — done

- [x] Extracted each post's real body content (not re-typed) from the already-built, correct
      HTML output — more reliable than re-deriving from the Python generator functions — into
      `source/ask/YYYY-MM-DD-slug.html` front-matter files, stripping old-template boilerplate
      (the top-of-page "← Dear Mr. Librarian" back-link, the old hand-written "More from Dear
      Mr. Librarian" cross-link panels — 2 posts had these woven into otherwise-real content
      and got a manual, careful trim rather than a blanket regex strip).
- [x] Real per-post dates via git's "file first added" history (2026-07-10 through
      2026-09-19), not guessed.
- [x] Deleted all 8 `build_ask_*()` functions (7 posts + the old `build_ask_index()`) and the
      now-dead `_question_form_html()`/`_ask_comment_nudge()` helpers from `build.py`.
      **Caught and fixed a real mistake here**: the first removal pass swept up `ES_BOOK` (the
      158-entry English→Spanish book-name map, load-bearing across the Spanish edition) because
      it sat immediately after `build_ask_newton()` with no `def` boundary between them and my
      boundary-detection only looked for `def` lines. `python3 build.py` failed loudly
      (`NameError: name 'ES_BOOK' is not defined`) before this ever reached a commit — restored
      verbatim from git history, rebuilt clean. Worth remembering: a line-range removal based on
      `def`-boundaries alone can silently eat a plain assignment sitting between two functions.
- [x] Redirect stubs (`blogkit.redirect_stub()` — meta-refresh + canonical, `noindex,follow`)
      at every old URL: `ask.html`, `contact.html`, `thanks.html`, and all 7 `ask-*.html`
      files, each pointing at its new `ask/...` home. Verified the stub HTML directly (correct
      target URLs, correct noindex tag) rather than trusting a live cross-origin redirect to
      resolve cleanly in a local Playwright check.

## 3. Structural gaps — closed

- [x] **Dates** — real, from front matter, on every post and every archive tile.
- [x] **Tags** — 14 tags assigned across the 7 posts from a shared, reused vocabulary
      (`textual criticism` ×4, `church history`/`genesis`/`translation philosophy` ×2 each,
      the rest singletons): canon, christology, church history, dead sea scrolls, divine name,
      eschatology, genealogy, genesis, hebrew language, isaac newton, john, matthew, textual
      criticism, translation philosophy.
- [x] **Sources** — shipped as the honest, mechanical version: `_add_sources()` auto-generates
      an `<ol class="sources">` ("Read in the text") from every distinct Bible-chapter link
      already present in a post's own body, plus a standing line naming the seven-version
      shelf comparison. Never hand-typed (can't drift from what a post actually cites), never
      fabricated. `check_entries()` refuses to build any post missing this, same discipline as
      `build_health.py`.
      **Still open, deliberately not done here**: real EXTERNAL citations (the Newton post is
      the obvious candidate — a real biography, his actual published works) would need
      verified sources, which is a content-research task, not something to invent as part of
      a structural migration. Revisit if wanted.
- [x] **Keep reading** — `_related_block()`, ranked by shared-tag count then recency, same
      mechanism as health/finance.
- [x] **Backlink** — `← Back to Dear Mr. Librarian` on every post.
- [x] **Images** — skipped, as scoped. All 7 posts stay pure text; only the front-page hero
      banner has a photo (reused, not newly sourced).

## 4. Bible project repointed — done

- [x] `header()`'s "📖 Dear Mr. Librarian" (desktop nav + mobile menu) → `ask/`.
- [x] Mobile menu's separate "✉️ Ask a Question" link → `ask/ask.html`.
- [x] Bible homepage's "Dear Mr. Librarian" card → `ask/`, description unchanged (still
      accurate: "Ask a question, or browse what's already been answered…").
- [x] Footer's "Ask Mr. Librarian a question" → `ask/ask.html` (was `ask.html#ask-form`).
- [x] The one per-post CTA in the John 1:1 chapter page ("send yours to the librarian's desk")
      → `ask/ask.html`.
- [x] `search-index.json` — single pointer entry, not 7 (see the revised decision in §0).
- [x] `feed.xml` — chapters-only again (see §0).
- [x] `index.html` (the mistertranslation.com hub) — confirmed untouched, no seventh card.
      `build_hub.py`'s `_PUBS` dict was checked directly: it has no "ask" entry and never will
      unless someone adds one, so this isn't a suppression that could silently lapse — the hub
      simply doesn't know `/ask/` exists.

## 5. Verified

- [x] Every old URL's redirect stub inspected directly (target URL + noindex tag correct) for
      all 10 redirected paths.
- [x] `ask/` pages rendered with Playwright — front page, an entry (top + full scroll to the
      sources/tags/comment-box/keep-reading/backlink/footer), the tags page, the ask form —
      desktop (1280px) and mobile (390px). Zero console errors throughout.
- [x] Bible's search index confirmed to carry the single `ask/` pointer, not stale entries.
- [x] `robots.txt` + both sitemaps consistent: Bible's `sitemap.xml` dropped from 751→741 URLs
      (the 10 old ask paths correctly excluded as noindex'd redirects), `ask/sitemap.xml` is a
      clean 14 URLs.
- [x] Full `python3 build.py` run end to end with no errors (after the `ES_BOOK` fix above) —
      2,093 search-index items, 40 feed items, 10 ask redirects, 741 sitemap URLs.
- [x] `python3 build_ask.py` run end to end with no errors — 7 entries, 14 tag pages
      (4 indexable), valid `feed.xml`/`sitemap.xml`.

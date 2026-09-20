# Splitting "Dear Mr. Librarian" into its own blog

Scoped 2026-09-19. Goal: give Dear Mr. Librarian the same real structure the other five
blogs have (own home, own archive, dates, tags, sources, keep-reading, its own feed) instead
of living inside the Bible project's template — while keeping it OFF the mistertranslation.com
hub's card grid. The Bible's own nav link ("📖 Dear Mr. Librarian") stays and just points at
the new location. Check items off as we ship them; items marked 🤔 are my proposed default,
not a done deal — redirect me when we get there if you want something else.

## 0. Decide the shape (do this first — everything below depends on it)

- [ ] 🤔 **Folder/URL.** Proposing `/ask/` — short, matches the existing `ask-*.html` slugs so
      the migration is mostly a rename, and reads fine in a URL (`mistertranslation.com/ask/`).
      Alternative: something more brand-like (`/dearmrlibrarian/`?) matching how the other five
      are named after their own titles, not a generic word. **This is the one call worth
      confirming before I touch anything** — once real, it's expensive to rename again.
- [ ] 🤔 **Page names inside it**, matching the sibling convention exactly: `ask/index.html`
      (the archive homepage — hero photo, post list, tags), `ask/ask.html` (the live
      submission form — yes, "ask/ask.html", same pattern as `finance/ask.html`). Individual
      posts drop the `ask-` prefix now that the folder carries it: `ask/great-tribulation.html`
      instead of `ask-great-tribulation.html`.
- [ ] 🤔 **CSS approach.** The other five ship fully-inlined per-page `<style>` blocks (each
      page self-contained, no shared stylesheet). The Bible links a shared `style.css`.
      Proposing the Bible's approach (`ask/style.css`, linked) since there are only ~7 posts
      today — easier to keep consistent by hand than copy-pasting a `<style>` block into every
      new post the way the bigger blogs do.
- [ ] 🤔 **Feed relationship.** The Bible's `feed.xml` (built 2026-09-19) currently includes the
      7 Dear Mr. Librarian posts alongside chapters. Once this blog has its own `ask/feed.xml`,
      proposing the posts move OUT of the Bible's feed (avoid the same content in two feeds) —
      the Bible's feed becomes chapters-only again.
- [ ] 🤔 **Sibling footer cross-links.** Every page on all five blogs ends with a line linking
      the other five (`The Librarian's Ledger · The Librarian Abroad · …`), which I added to
      the Bible's own footer a few items back. Does the new Dear Mr. Librarian blog join that
      same six-way cross-link line on EVERY page across the whole site (all six blogs list all
      five *other* ones), or does it stay off that list too — same spirit as "no hub card,"
      just reachable through the Bible rather than promoted everywhere? Leaning toward
      **off the cross-link list**, consistent with "no card," but this is genuinely your call.

## 1. Scaffold the new blog (mechanical, no new content decisions)

- [ ] Own header/footer template in `build_ask.py` (new file) — own brand mark (reuse the
      scroll icon, or something distinct?), a thin nav (Home / Tags / [Ask a question] —
      there's no "topic pages" concept here the way finance has Bitcoin Board/Treasuries/etc.,
      so this nav is intentionally sparse compared to the siblings').
      🤔 also decide: reuse the Bible's own gold/parchment theme (visual continuity with where
      it came from) or give it a distinct palette (visual independence, matching how each of
      the other five has its own accent color)?
- [ ] `ask/index.html` — archive homepage: full-width hero banner (`.fronthero`, matching the
      now-standard pattern across all six), intro copy, and a post list. With only 7 posts,
      probably doesn't need finance's full load-more/view-toggle apparatus yet — a simple tile
      grid is enough, built so it can grow into the fuller pattern later without a rewrite.
- [ ] `ask/tags.html` + per-tag pages (`ask/tag-<slug>.html`), matching `blogkit.tag_slug()`.
- [ ] `ask/feed.xml` via `blogkit.build_feed()` (the real thing this time — front-matter dates,
      not the git-history-inferred dates the Bible's own feed had to fall back to).
- [ ] `ask/sitemap.xml`, and add its line to the root `robots.txt` (same pattern as the other
      five's `Sitemap:` lines).

## 2. Migrate the 7 existing posts

- [ ] Convert each `build_ask_*()` Python function in `build.py` into a front-matter source
      file at `source/ask/<slug>.html` (title/date/tags/summary/meta_desc/hero/hero_alt/
      hero_credit/draft, then the body HTML) — the same authoring format `source/health/`,
      `source/finance/`, etc. already use, parsed by `blogkit.parse_front_matter()`.
      **Date needs a real decision per post**: use each post's actual git "first added" date
      (same `_git_added_dates()` approach the Bible feed already uses) rather than guessing.
- [ ] Delete the 7 `build_ask_*()` functions from `build.py` once `build_ask.py` builds them
      instead — no duplicate source of truth for the same 7 posts.
- [ ] Redirect stubs at every old URL (`ask.html`, `ask-enoch.html`, `ask-jesus-god.html`,
      `ask-jehovah.html`, `ask-creation-days.html`, `ask-newton.html`, `ask-cain-seth.html`,
      `ask-great-tribulation.html`, `contact.html`) via `blogkit.redirect_stub()` — the same
      meta-refresh + canonical pattern already used elsewhere in this codebase for a moved
      page, so a bookmarked/shared/indexed link never dead-ends.

## 3. Close the structural gaps this whole split was for

- [ ] **Dates** — from front matter now, shown on each post (`<p class="edate">`, matching the
      siblings) and on the archive tiles.
- [ ] **Tags** — 🤔 needs a taxonomy invented from scratch (the 7 posts have none today).
      Rough cut from what's actually in them: `canon`, `textual-criticism`, `translation`,
      `christology`, `chronology`, `genealogy`, `eschatology`, `manuscripts` — I'll refine
      this against the real posts when we get here, not guess blind.
- [ ] **Sources** — 🤔 the real open question. Finance's "Sources" section is a numbered list
      of EXTERNAL citations (GiveWell, WHO, journal papers). These 7 posts don't route through
      outside reporting — their "sources" are internal (specific Bible chapters/verses/notes)
      plus the project's own 7-version shelf comparison (NIV/KJV/Douay-Rheims/Living
      Bible/Geneva/ASV/NWT) and, for the Newton post, real external biographical/historical
      sources. Proposing a "Sources" section that's honest about this: external citations
      where they exist (Newton's biography, historical-interpretation claims), and a distinct
      "Read in the text" list of the specific chapters/verses each post leans on where they
      don't. Needs a pass per post, not a mechanical port.
- [ ] **Keep reading** — auto-generated related-post tiles at the bottom of each post, same
      `data-search`/`data-tags` mechanism as the siblings. With only 7 posts this will surface
      most of the archive most of the time — fine at this size, revisit if the archive grows.
- [ ] **Backlink** — `← Back to Dear Mr. Librarian` line before the footer, matching the
      siblings' `← Back to the Ledger` etc.
- [ ] Images — 🤔 optional, not required. The 7 posts are argument/exegesis essays and read
      fine as pure text; the siblings' posts aren't ALWAYS illustrated either. Not scoping new
      image research/licensing per post unless you want it — flag if you do.

## 4. Point the Bible project at the new location

- [ ] `header()`'s "📖 Dear Mr. Librarian" nav link (desktop + mobile) → `ask/` (was `ask.html`).
- [ ] Bible homepage's "Dear Mr. Librarian" card → same new URL, description re-checked (still
      accurate once the form lives on `ask/ask.html` rather than this same page).
- [ ] Footer's "Ask Mr. Librarian a question" link → `ask/ask.html` (was `ask.html#ask-form`).
- [ ] The one per-post CTA in the John 1:1 post ("send yours to the librarian's desk") → same.
- [ ] Bible's `search-index.json` (`build_search_index()`) — drop the 7 hardcoded `ASK_ENTRIES`
      (now genuinely a different site) or keep them findable with repointed URLs? Proposing
      **keep them searchable** from the Bible's own search box (the nav link still lives in
      the Bible, so a reader would reasonably expect search to still find them) but pointing
      at `ask/...` URLs.
- [ ] Bible's `feed.xml` (`build_feed_page()`) — drop the 7 ask posts per the item-0 decision
      above, chapters-only again.
- [ ] Confirm `index.html` (the mistertranslation.com hub) is untouched — **no seventh card**.
      This is a guardrail line, not a task: nothing here should add one.

## 5. Verify before shipping

- [ ] Every old URL redirects correctly (curl/Playwright check, not just "should work").
- [ ] New `ask/` pages render correctly (Playwright screenshots, desktop + mobile, same
      discipline as the rest of this parity pass).
- [ ] Bible's search still finds Dear Mr. Librarian content, landing on the new URLs.
- [ ] `robots.txt` + both sitemaps (Bible's and the new one) are consistent — no duplicate or
      conflicting canonical claims on the same content.
- [ ] Spot-check a few inbound old links still resolve (anything in this repo's own
      `docs/`/`RETIRED.md`-style history, if any point at the old ask-*.html paths — unlikely
      here since this is a different repo's convention, but worth one grep pass).

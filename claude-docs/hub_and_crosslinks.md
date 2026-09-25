# Hub, cross-links and site-wide legal pages

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## The relationship rule — RETIRED 2026-09-09, all three now cross-link via the hub

**This used to say the Bible project links to neither of the other two publications and is
linked from neither.** That isolation was deliberate (see git history / RETIRED.md-style
context below), but Michael dropped the concern that motivated it and asked for a top-level
hub at `/` with one card per publication — Bitcoin & Finance, Food & Travel, and Religion
(the Bible project) — so all three are now mutually reachable through it. **Don't reintroduce
the isolation** — the current, correct state is: hub → all three; Bible project → back to the
hub only via its own nav's brand-name conventions (it doesn't carry a hub link of its own
today, and none was asked for).

⚡ **2026-09-18 (Michael's call): every one of the five blogs now links straight to the Bible
project too**, not just via the hub. Each builder's `SIBLINGS` list (`build_finance.py`,
`build_health.py`, `build_notebook.py`, `build_west.py`) and `build_travel.py`'s hand-rolled
header/footer sibling links gained a fifth entry — "Mr. Librarian's Bible" → `bible.html` — so
each blog's footer (and, for Travel, its mobile-menu sibling row too, the one place it lists
siblings twice) now names all FIVE other publications, not four. The Bible project's own
~2,772 pages (`build.py`) were deliberately left untouched — reachable from the blogs via the
hub-style pattern only, since adding a "visit our blogs" mention to a spare reference work at
that scale is a much bigger, more consequential change than a one-line addition to five
footers, and nothing prompted it. Known small imprecision: `build_health.py`'s Spanish (`es`)
footer tags every sibling link "(en inglés)" via a blanket per-entry suffix; that's correct for
the other four (English-only), but the Bible project also has its own Spanish edition (`es.html`)
that this doesn't route to — accepted rather than threading a per-language URL through
`SIBLINGS` for one entry.

Librarian Abroad ↔ finance board still link directly to each
other too (Michael's call, 2026-08-07), unaffected by the hub's addition.

**Why the Bible project's own pages didn't move:** `build.py` still emits ~2,772 pages at the
SAME root-level URLs they've always had (`genesis-1.html`, `toc.html`, etc.) — moving them
under a subpath would have broken every indexed URL for zero benefit. Only the ONE page that
used to occupy the bare root — the project's own homepage — moved, to `bible.html`
(`build.py`'s `HOME_URL` constant; every page's nav/brand link was repointed there in one
pass). The bare root itself is now the hub's file, not a `build.py` output at all.

Each of the five builders (`build.py`, `build_travel.py`, `build_finance.py`,
`build_health.py`, `build_notebook.py`) writes only inside its own output area and never globs or deletes elsewhere — that discipline is what
lets them all coexist safely in one repo. Keep it that way; don't import one builder from
another. The hub's `index.html` follows the same discipline by construction — it's a single
static file with no generator, so there's nothing for a builder to accidentally clobber it
with, and nothing it can accidentally glob into any of the three builders' own outputs.
⚠ **One guard does still reach it:** `build.py`'s `check_built_descriptions()` scans every
root `*.html` it finds, the hand-written hub included, and FAILS the Bible build when a
`<meta name="description">` runs past 160 characters. The hub's did (194 chars, from its
2026-09-10 fourth-card edit) and the next Bible chapter's build fell over on it, after every
page had already been written — trimmed to 156 (and again to 159 when the fifth card landed
2026-09-11 — the first cut was 163). Editing the hub's description by hand means
counting it; nothing else caps it.

**Site-wide legal pages at the hub root (2026-09-17, for the Google AdSense application):**
`privacy.html` (one policy for all six publications — GoatCounter, localStorage, FormSubmit,
the OSM/YouTube-nocookie embeds, and an AdSense section written to apply the day ads switch on)
and `librarian.html` (site-wide About & Contact — same FormSubmit endpoint as the Bible
project's `contact.html`, general subject line, returns to itself with `?sent=1` instead of
the Bible-styled `thanks.html`). Both hand-written in the hub's own visual language, same as
`index.html`; both under the same 160-char description cap. **Every footer links to the
policy:** the hub's, `build.py`'s `FOOTER`/`ES_FOOTER`, `build_travel.py`'s `FOOTER`, and the
`_legal()` small print of finance/health/notebook/west (via a `PRIVACY_URL` constant, absolute
because those live one level down). Change the policy → edit `privacy.html` and move its dated
line; don't fork per-publication copies. The AdSense wording (cookies, Ads Settings/aboutads
opt-outs, partner-sites link, EEA/UK consent) is what Google's program policy asks a publisher's
policy to say — keep it if the section is ever rewritten.

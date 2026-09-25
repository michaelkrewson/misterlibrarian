# Public notes (X) on Bible project pages

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## Public notes (X) — chapter / dictionary / encyclopedia / atlas / route pages

**Added 2026-09-09 (Michael's call), simplified and repositioned the same day.** Every chapter
page, dictionary/encyclopedia/atlas entry page, and route page carries a bare two-button row
(`build.py`'s `_note_nudge()`, class `.notebtns`): **✏️ Take a Note** (a pre-filled X compose
link, `blogkit.x_note_url`) and **🔍 View Notes by Others** (an exact-URL X search,
`blogkit.x_search_url`). X hosts, ranks, and moderates it — this domain runs no comment backend
of its own. **No pitch paragraph, no surrounding box, and no "Public" in the button label** —
the first cut had all three, and Michael's own read was that the prose+box "would scare people
off from actually taking a note" and that spelling out "public" on the button undercuts the same
goal, even though the note is genuinely public once posted.

**On chapter pages the row sits ABOVE VERSE 1**, not at the bottom — `_insert_before_first_verse()`
splices it in right before the first `<div class="vrs">`, the exact spot `reader-notes.js`'s
per-chapter "My notes for X" panel used to occupy (`.notebtns-top`, tight margin). **That private
panel was REMOVED the same day** (Michael's explicit call, after being told it was also the
site's ONLY export/import backup for a reader's whole notebook — every chapter's notes and
highlights, not just one — and choosing to remove it anyway rather than relocate the backup
UI elsewhere). Per-verse notes/highlights are UNCHANGED and still private/local; only the
chapter-wide textarea+share+backup panel is gone. On dictionary/encyclopedia/atlas/route pages
(no verses, so no panel to replace) the row stays at the bottom of the entry, unchanged.

**Same underlying mechanism as `build_travel.py`/`build_finance.py`'s own X-comment nudge**
(`_x_respond_nudge`/`_ask_nudge`), shared via `blogkit.py` — those two still use the full-size,
boxed version with the "Commenting on…" pitch text; only the Bible project's copy was slimmed
(~20% smaller pills) and stripped down. `x_comment_url` (travel/finance) pitches the link as
pushing back on something Michael wrote; `x_note_url` (here) pitches the identical link as the
reader's own note ("Note on…") — see `blogkit.py`'s X-comment-system section header for the full
reasoning. The Bible project has no draft concept for these pages (everything `build.py` outputs
is already live), so unlike the other two builders it calls this unconditionally, with no
per-page draft check. **Not yet wired into the Spanish (`.es.html`) entry-page builders** — an
easy follow-up, not done in the first pass.

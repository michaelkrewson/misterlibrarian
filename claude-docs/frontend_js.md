# Front-end JS — reader-notes.js / share.js / audio-reader.js and the verse cards

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## Front-end JS — the Spanish edition is a page, not a locale flag

`reader-notes.js`, `share.js` and `audio-reader.js` run on **both** editions off one file,
so anything they render or read has to branch. Two things must; one must not.

- **Language** is `(document.documentElement.lang || "").toLowerCase().indexOf("es") === 0`
  — that single line is the whole detection, identical in `share.js` and `reader-notes.js`.
  Don't sniff the `.es` filename for it (the stem gets stripped for URL-building and would
  lie), and don't leave a reader-visible string outside the string table.
- **The verse line** is `.eng` on the English page and **`.esp` on the Spanish one**. This
  is the trap: a selector written as `.eng` alone still *works* — no error, no blank page —
  it just silently reads nothing on every Spanish chapter. `reader-notes.js` shipped that
  way, so on the whole Spanish site "Copiar el versículo" copied a reference with no verse
  attached and "Compartir como imagen" produced a card with a reference, a divider, and
  empty space where the verse belongs. Both `reader-notes.js` and `audio-reader.js` were
  fixed on 2026-08-19 — the latter pre-emptively, since Spanish pages still ship no Listen
  button, so that adding the button is the only step left rather than the day it is added
  being the day this is found broken. ⚠ Whatever reads a verse must also strip the widget
  chrome reader-notes.js appends *inside* that same line (`.v-tools`, `.v-note`,
  `.v-editor`, `.notelink`, `.xrefs`, `.vclip`) — audio-reader stripped only `.notelink`
  and was therefore reading the "⋯" button glyph aloud after every verse, and would have
  read a reader's own saved note out loud.
- **What must NOT branch:** storage keys, the `/v/` stub URLs, download filenames. Those
  name a *verse*, not a page, so they are language-neutral — `baseStem()` strips `.es`
  precisely so the two editions can never disagree about which verse is which. ⚠ An earlier
  version of this section claimed the localStorage keys were already neutral. They were
  not: until 2026-08-19 the key was `location.pathname`, so one verse held two separate
  notebooks and the 🌐 toggle looked like it had wiped the reader's margin. `KEY_PATH` now
  drops the `.es`, and a one-time migration folds the legacy rows in — **losslessly**: where
  both editions held a note the newer leads and the older is kept beneath it rather than
  dropped. `PATH` itself is still the right thing for the chapter share URL, which must link
  to the edition actually being read; only the *keys* are neutral.

**Each edition has its OWN `/v/` share stub** (`numbers-14-1.html` /
`numbers-14-1.es.html`, fixed 2026-08-19). The STEM stays neutral so the pair sits
together, but the stub is not: it carries that edition's verse in its Open Graph card,
its own `lang`/`og:locale`/site name, and redirects to that edition's chapter. Before
this there was one neutral stub, so a Spanish reader sharing Números 14:1 handed the
recipient the ENGLISH verse and dropped them on the English page — the most public place
the site switched languages on its own readers, since a share link is what a Spanish
reader sends to other Spanish readers.

**Verse cards live in a PUBLIC S3 BUCKET, not in this repo** (moved 2026-08-19).
`mistertranslation-public` / `us-east-1` / prefix `public/verse-cards/`, served from the
plain bucket URL — **no CloudFront, deliberately** (Michael: "less future maintenance and
dependencies"; the bonus is that with no CDN there is no cache to invalidate, so a
re-rendered card is live immediately). Credentials: `~/.mstr-trader/cards.env`, mode 600,
a **different key from `backup.env`** — that one writes the private archive bucket holding
the bank/tax/medical records, and the two must never be shared. The key has PutObject +
ListBucket and deliberately **not** DeleteObject.

⚠ **Why they moved, so nobody moves them back:** cards are ~38 KB each and scale with
VERSES, and **GitHub Pages hard-caps a published site at 1 GB** — a limit, not a warning,
unlike the repo-size numbers usually quoted. At 291 of 1,189 chapters the site was 507 MB;
English alone at full coverage is ~1.1 GB, over the cap by itself. Moving the cards out
took the site to **~174 MB** and, far more importantly, stopped it growing.

⚠ **`img/v/.cards.json` is TRACKED, and that is load-bearing.** It is the record of which
cards are published, and `_ensure_verse_card` consults it BEFORE the network — a matching
hash returns the URL with no S3 call. That is what lets a build on a machine with no
credentials still emit correct `og:image` tags for every published card. Without it, one
credential-less build would silently strip the verse art off every share on the site. Only
a NEW or CHANGED card touches S3, and if that upload fails only that ONE card falls back to
the default.

`ES_VERSE_CARDS` is now **True** — turned on the same day, because it was only ever OFF for
as long as the cards lived in the repo. The bucket has no cap, so there is no reason left to
give the Spanish edition worse art. The **Spanish default card** (`img/og-default.es.png`)
stays as the fallback and is still load-bearing: the English default is an English *image*,
wordmark and tagline both, so falling back to it would put English straight back into the
most visible part of a Spanish share.

The Spanish book name is **not** duplicated in JS. `reader-notes.js` takes the reference a
reader sees from the page's own `<title>` ("Números 14 — La Traducción Mister"), falling
back to the slug only if that head doesn't end in the chapter's number — so `build.py`'s
`ES_BOOK` stays the single source and no JS copy can drift from it.

⚠ **`?v=` is a content hash** (`_asset_ver`), baked into all 2,772 pages at build time.
Editing any of these `.js` files does **nothing** for a real reader until you re-run
`build.py`; the browser keeps serving the cached old file under the old stamp.

# Eight Miles West (/west/)

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## Eight Miles West (`/west/`)

A family history — the Croesen / Kroesen / Kroessen / Kreuso / Cruse / Krewson line's four
centuries in America, from a cooper at Breuckelen c.1660 through Staten Island, Bucks County,
Ohio, Iowa and the Pacific, into the twentieth century's wars and breakages — published one
chapter at a time by `build_west.py` (standard library only), source in `source/west/`,
output in `west/`. Added 2026-09-11 (Michael's call). Michael's own family; the research
record behind it lives in the mstr-trader repo's private MiSTeRGenealogy (`genealogy.json`,
171 people, 32 story write-ups) and the family's own published genealogy, Warren D. Cruise,
*The Croesen Families of America*, Vol. I (1998), OCR'd in full in the fleet's S3
(`blobs/GENEALOGY_BOOK_OCR/`). Written to be read on the web first and compiled into a
KDP paperback later (plain KDP, not Select — Select's exclusivity conflicts with free web
chapters).

**It is a BOOK, not a blog — the one structural difference from the other five, and the
reason it is its own builder rather than a Notebook section:** a narrative has an ORDER.
Chapters are numbered in the filename (`NN-slug.html`) and read in that order inside five
fixed PARTS (`flags` / `will` / `west` / `broke` / `keepers` — the five eras the record
divides into on its own); the contents page IS the front page and shows all five parts from
day one, "Not yet written" where nothing is; chapter pages carry Previous/Next in reading
order. No tags, no tag pages, no search box, no newest-first. `date:` is the publish date
for the feed/sitemap only.

**The book's whole promise, enforced in markup:** every sentence is documented, inferred, or
family legend, and the reader can see which. Plain cited prose = documented; `<span
class="infer">` (italic) = worked back from an age or a gap; `<div class="doc legend">`
(gold rule) = a story the family told, stated as a story and NEVER promoted to fact in a
later chapter. `<div class="doc">` quotes a document verbatim with a `.cite` line — prefer
the original's words to a paraphrase every time the original survives. `<ol
class="sources">` is REQUIRED (the Regimen's rule; the build refuses without it).

**Drafts — the Regimen's posture, kept on purpose here** even though the Notebook dropped
drafts entirely: `draft: true` = not built; `--drafts` = local noindexed preview; no drafts
page. The later chapters are about living people and a father who left, and those get read
by Michael in his own voice before they get a URL. Never commit a `--drafts` build.

**Spine decided 2026-09-11 (Michael to ratify on the page):** Book I opens on Elizabeth
Cregier's baptism, Reformed Dutch Church, Manhattan, 5 July 1662 — witnesses Martin Kregier
(Burgomaster) and Nicasius de Silla (Schout-Fiscal), her two grandfathers; two years before
the English take the colony; she dies 1740 on a Bucks County farm. One person carries each
era after her. Working title stays until three chapters exist.

**⚠️ 2026-09-24 — his real name came OFF the web version** (Michael's call: it goes on the printed edition one day, not the web copy — "for now it will slow them down at least," not a claim of full anonymity). The front-page `<p class="byline">by ...</p>` line, the `<meta name="author">` tag (every page), and the © footer line were all switched to `mistertranslation.com` — the `AUTHOR` constant in `build_west.py` now reads `"mistertranslation.com"` and feeds the meta tag + © line (the byline paragraph itself was deleted outright, not re-pointed). **The About page's own prose was also de-named the same day** — "It is written by Michael V. Krewson... published under his name" → "written by a modern member of the family... under this domain's usual byline, Mr. Librarian." **⚠️ What's deliberately NOT touched: his name as a cited SOURCE inside the chapters themselves** (photo credits, email correspondence, the DNA panel, the genealogical record rows like "Michael V. Krewson (b. 1971)") — those are documented citations the book's own honesty convention requires, not authorship attribution, and scrubbing them would break the sourcing. Prior state (2026-09-11 → 2026-09-24): this was "the ONE publication on the domain with a real name on it." Everywhere else the domain stays "Mr. Librarian." Don't spread the real name to the other five.

**Same X comment layer, same FormSubmit inbox (`_subject` "Eight Miles West — a reader
wrote in"), same GoatCounter.** Mark: a compass whose needle settles west (the same SVG is
inlined on the root hub's sixth card — change both or neither). Accent Delft blue `#4fa8dc`.
Six cards now fill the hub's 2×3 grid, so the Notebook lost its full-width fifth-card rule.
Sibling link added to the other four blogs' footers (and the travel mobile menu, where a
duplicated Notebook line was fixed in passing).

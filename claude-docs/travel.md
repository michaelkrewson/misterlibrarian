# The Librarian Abroad (/travel/)

> Relocated verbatim from `CLAUDE.md` on 2026-09-25 to keep that file small (it is loaded into every session). Nothing here was reworded; `CLAUDE.md` keeps a short pointer with the current must-know rules. Add new dated history and incident notes for this surface HERE, not in `CLAUDE.md`.


## The Librarian Abroad (`/travel/`)

- **A new entry is one file:** `source/travel/YYYY-MM-DD-slug.html`, front matter then plain
  HTML (copy `source/travel/_template.html`). The build fails loudly on a typo'd key, a
  missing required field, or a filename date that disagrees with the front matter.
- **Photos are the source, not optional context.** If Michael says photos exist but they
  aren't attached, go get them — Photos.app AppleScript automation is already granted on his
  Mac. **This is a hard requirement: never tell him a photo is unreachable without having
  tried this first.** `ls`/`mdfind`/`find` on `~/Pictures/Photos Library.photoslibrary` will
  all fail with `Operation not permitted` — that's ordinary TCC sandboxing, not evidence the
  photos can't be reached. Paid for twice now (2026-07-28, 2026-08-22) by asking him to
  manually export before trying the workaround already documented right here. Working recipe:
  - `tell application "Photos" to count of media items` for the total; a `whose date` filter
    and some index forms throw `-1700`/`-2741`, so don't fight it — index from the tail
    (`media item i` counting down from the total, or `media item -(i+1)`), print
    `date`/`filename` for the last ~30–40 to find the right session by eye. "Last night" is
    a rough clock time, not a query predicate.
  - Build a list: `set theItems to {}` then `repeat … set end of theItems to media item i`.
  - **Export syntax is exact:** `export theItems to (POSIX file "/path")` with no options
    yields Photos' own JPEG conversions. To get true originals (HEIC/MOV, needed before the
    resizer below) the keyword is **`with using originals`** — `using originals` alone
    (missing `with`) throws `Expected expression but found end of line (-2741)`, which reads
    like the whole approach failed rather than one missing word.
  - Read `location` on each item for real GPS *before* exporting — `with using originals`
    strips it from the exported file.
  - **Write the script to a `.applescript` file and run `osascript path.scpt`**, not
    `osascript -e '...'` — multi-line `-e` scripts have thrown confusing, wrongly-numbered
    syntax errors here even on a script that was actually fine.
  **Every photo must go through `python3 tools/travel_photos.py <files>`** before it can be
  used — it resizes to web size and strips EXIF including GPS. Git history is forever; an
  oversized or geotagged original committed once can't really be taken back out. HEIC
  sources need `sips -s format jpeg -Z 1600 in.HEIC --out out.jpg` first (this machine's
  Pillow has no HEIC plugin).
- **Ask for a voice memo before writing a food entry.** Michael records ~30-second memos at
  the table; the sensory detail he actually noticed is exactly the part a photo or menu can't
  reconstruct, and it's the part worth reading an entry for. `python3
  tools/travel_transcribe.py <memo> --archive <slug>` runs Apple's on-device speech model —
  no upload, nothing leaves the Mac, deliberately, since a memo is his voice in a public
  place. ⚠️ **The memo's filename names the wrong venue** (Voice Memos names a recording
  after whatever its location lookup resolves to, which on a restaurant street is often a
  neighbor) — never infer the entry from the filename, ask. ⚠️ **The transcript is a draft,
  not a quote** — the model mishears menu terms; correct it in the archived transcript's
  CORRECTIONS block, don't overwrite the raw output.
- **Writing in Michael's first-person voice is normal and welcome** — that's the job, not a
  risk to hedge on. What matters is a *place*, not a permission: it goes into the drafts
  pipeline (`draft: true` → build → push → he reads it at
  `mistertranslation.com/travel/drafts.html`) before it's public, because he's the
  proofreader and that page exists for him to read on his phone. Don't skip straight to `main`.
- **Never invent a specific he didn't give you** — a dollar figure, a time, a founder detail,
  or (twice now, the standing failure mode to actually watch for) *his own experience of a
  dish*. Describing food from a photo is fine; saying he tasted it and liked it is not, unless
  it's in the photo, the memo, or something he actually told you. Per-sentence test while
  drafting: is this in a photo, or did he say it? If neither, cut it.
- **Librarian's Stars** (`stars: 1–5`, halves allowed) turns an entry into a review — only
  worth printing because the scale can say no. Three stars is a good meal, five is meant to
  stay rare; the published meaning lives on the About page. A post with no `stars:` renders
  no rating.
- **Readers write in via a form** (`write.html`), not comments — deliberate, to avoid
  trading the site's no-tracking posture for Disqus or a moderation chore on a notebook
  written irregularly by design.
- **Originals + video go to S3** via `python3 tools/travel_archive.py add <slug> <files...>`
  — content-addressed by sha256, so `add` is idempotent. ⚠️ The slug is the tool's **first
  positional argument** — a bare glob with no explicit slug silently makes the first matched
  photo the slug instead. Always write the slug explicitly and read the tool's own last line
  (`archived … under '<slug>'`) to confirm what it actually used.

#!/usr/bin/env python3
"""build_hub.py — keep the hub at mistertranslation.com/ (root `index.html`) current.

The hub is still a HAND-WRITTEN page (copy, cards, styling live in index.html itself);
this script only touches two things, so the page can't go stale the way a static
list of six projects otherwise would:

  1. The "Latest" line inside each card — `<div class="latest" data-pub="…">…</div>` —
     is refilled from each publication's own sources: the newest non-draft entry in
     source/finance|health|notebook|travel (YYYY-MM-DD-slug.html), the newest chapter
     by front-matter date in source/west (NN-slug.html), and the Bible project's own
     "Newest:" button as bible.html last printed it (build.py decides that order —
     PUBLISH_ORDER, not canonical order — so we read its answer, not recompute it).
  2. `img/og-hub.png`, the hub's OWN link-preview image. The root used to point at the
     Bible project's default card, so sharing mistertranslation.com/ advertised "A fresh
     translation of the Bible" and landed on a six-project hub (found 2026-09-18).
  3. The rundown box (`<section id="rundown" class="hubrundown">`, added 2026-09-21) —
     a full mirror of the Notebook's own front-page news roundup, so a daily visit to
     the bare domain shows it without a click into /notebook/ first. Rendered straight
     from source/notebook/_rundown.json (the SAME file the Notebook builds from — no
     second copy to drift), wholesale-replaced every run exactly like a card's .latest
     line. Empty/missing file → an empty <section>, which `.hubrundown:empty` hides.

Run directly (`python3 build_hub.py`) or — the point — it runs at the end of EVERY
builder's `__main__` (build.py, build_finance.py, build_health.py, build_notebook.py,
build_travel.py, build_west.py), so publishing an entry anywhere refreshes the hub.
It never raises out to a caller: a problem with one publication leaves that card's
existing line in place and prints a warning; a missing Pillow/font skips the image
(the committed PNG stays). The card line is plain text, not a link — each card is
already one big <a>, and an anchor can't nest inside an anchor.
"""
import datetime as _dt
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ROOT, "index.html")
OG_PATH = os.path.join(ROOT, "img", "og-hub.png")
RUNDOWN_FILE = os.path.join(ROOT, "source", "notebook", "_rundown.json")

# data-pub → (source dir, url prefix). The Bible is handled separately.
DATED = {
    "finance":  ("finance",  "finance/"),
    "health":   ("health",   "health/"),
    "notebook": ("notebook", "notebook/"),
    "travel":   ("travel",   "travel/"),
}
_DATED_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+?)\.html$")
_WEST_NAME = re.compile(r"^(\d{2})-(.+?)\.html$")
_LATEST_DIV = re.compile(r'<div class="latest" data-pub="([a-z]+)">.*?</div>', re.S)
_BIBLE_NEWEST = re.compile(r'href="([a-z0-9-]+\.html)">Newest: ([^<]+)<')
_RUNDOWN_SECTION = re.compile(
    r'<section id="rundown" class="hubrundown">.*?</section>', re.S)


def _front_matter(path):
    """The `key: value` lines above the first `---`, as a dict. Deliberately simpler
    than blogkit.parse_front_matter: we only need title/date/draft and must not
    refuse a file over a key we don't know about."""
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            if s.strip() == "---":
                break
            if ":" in s and not s.startswith((" ", "\t")):
                k, v = s.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def _is_draft(meta):
    return meta.get("draft", "").strip().lower() in ("true", "yes", "1")


def _newest_dated(pub_dir, url_prefix):
    src = os.path.join(ROOT, "source", pub_dir)
    best = None
    for fn in sorted(os.listdir(src)):
        if fn.startswith("_") or fn.endswith(".es.html"):
            continue
        m = _DATED_NAME.match(fn)
        if not m:
            continue
        meta = _front_matter(os.path.join(src, fn))
        if _is_draft(meta) or not meta.get("title"):
            continue
        key = (m.group(1), fn)
        if best is None or key > best[0]:
            best = (key, {"date": m.group(1), "title": meta["title"],
                          "url": url_prefix + m.group(2) + ".html"})
    return best[1] if best else None


def _newest_west():
    src = os.path.join(ROOT, "source", "west")
    best = None
    for fn in sorted(os.listdir(src)):
        m = _WEST_NAME.match(fn)
        if not m or fn.startswith("_"):
            continue
        meta = _front_matter(os.path.join(src, fn))
        if _is_draft(meta) or not meta.get("title") or not meta.get("date"):
            continue
        key = (meta["date"], m.group(1))
        if best is None or key > best[0]:
            best = (key, {"date": meta["date"], "title": meta["title"],
                          "url": "west/" + m.group(2) + ".html",
                          "label": "Chapter %d" % int(m.group(1))})
    return best[1] if best else None


def _newest_bible():
    """What bible.html itself currently calls newest. build.py owns that decision
    (PUBLISH_ORDER from the source's panel order) — read its printed answer."""
    with open(os.path.join(ROOT, "bible.html"), encoding="utf-8") as f:
        m = _BIBLE_NEWEST.search(f.read())
    if not m:
        return None
    return {"date": None, "title": m.group(2).strip(), "url": m.group(1)}


def latest():
    out = {}
    for pub, (d, prefix) in DATED.items():
        try:
            out[pub] = _newest_dated(d, prefix)
        except Exception as e:                      # one bad source dir ≠ a dead hub
            print("build_hub: %s: %s" % (pub, e), file=sys.stderr)
    try:
        out["west"] = _newest_west()
    except Exception as e:
        print("build_hub: west: %s" % e, file=sys.stderr)
    try:
        out["bible"] = _newest_bible()
    except Exception as e:
        print("build_hub: bible: %s" % e, file=sys.stderr)
    return out


def _pretty(date_iso):
    d = _dt.date.fromisoformat(date_iso)
    return d.strftime("%b %-d") if d.year == _dt.date.today().year else d.strftime("%b %-d, %Y")


def _line(pub, e):
    if not e:
        return ""
    if pub == "bible":
        return ('<span class="lk">Newest</span> %s' % html.escape(e["title"]))
    when = '<time datetime="%s">%s</time>' % (e["date"], _pretty(e["date"]))
    what = html.escape(e["title"])
    if e.get("label"):
        what = "%s · %s" % (e["label"], what)
    return '<span class="lk">Latest</span> %s · %s' % (when, what)


def refresh_index(entries, quiet=False):
    with open(INDEX, encoding="utf-8") as f:
        src = f.read()
    seen = set()

    def sub(m):
        pub = m.group(1)
        seen.add(pub)
        e = entries.get(pub)
        if e is None:                               # keep what's there rather than blank it
            return m.group(0)
        return '<div class="latest" data-pub="%s">%s</div>' % (pub, _line(pub, e))

    new = _LATEST_DIV.sub(sub, src)
    missing = set(entries) - seen
    if missing:
        print("build_hub: index.html has no latest-line slot for: %s"
              % ", ".join(sorted(missing)), file=sys.stderr)
    if new != src:
        with open(INDEX, "w", encoding="utf-8") as f:
            f.write(new)
    if not quiet:
        for pub in ("bible", "finance", "travel", "health", "notebook", "west"):
            e = entries.get(pub)
            print("  %-9s %s" % (pub, ("%s  %s" % (e.get("date") or "        ", e["title"]))
                                 if e else "(none)"))
    return new != src


# --- the rundown box: a full mirror of the Notebook's front-page news roundup -------
def _load_rundown():
    """Same contract as build_notebook.py's own _load_rundown: optional file, missing
    href defaults to "". Kept as an independent copy rather than an import — this is
    the one place build_hub.py reads a publication's source data directly instead of
    a rendered page, so it stays a plain read of the JSON, nothing more."""
    if not os.path.exists(RUNDOWN_FILE):
        return None
    with open(RUNDOWN_FILE, encoding="utf-8") as f:
        data = json.load(f)
    for sec in data.get("sections", []):
        for item in sec.get("items", []):
            item.setdefault("href", "")
    return data


def _pretty_date(date_iso):
    try:
        y, m, d = (int(p) for p in date_iso.split("-"))
        return _dt.date(y, m, d).strftime("%B %-d, %Y")
    except ValueError:
        return date_iso


def _rundown_html(data):
    if not data or not data.get("sections"):
        return '<section id="rundown" class="hubrundown"></section>'
    parts = ['<section id="rundown" class="hubrundown">',
             '  <h2 class="rdtitle">%s</h2>' % html.escape(data.get("title") or "Today's rundown")]
    date_label = data.get("date", "")
    if date_label:
        parts.append('  <p class="rddate">%s</p>' % html.escape(_pretty_date(date_label)))
    for sec in data["sections"]:
        items = sec.get("items", [])
        if not items:
            continue
        parts.append('  <h3 class="rdsec">%s</h3>' % html.escape(sec.get("label", "")))
        lis = []
        for it in items:
            text = html.escape(it.get("text", ""))
            href = it.get("href", "").strip()
            if href:
                lis.append('<li><a href="%s">%s</a></li>' % (html.escape(href), text))
            else:
                lis.append("<li>%s</li>" % text)
        parts.append('  <ul>%s</ul>' % "".join(lis))
    parts.append('  <p class="rdmore"><a href="notebook/">Read the whole Notebook →</a></p>')
    parts.append("</section>")
    return "\n".join(parts)


def refresh_rundown(quiet=True):
    """Wholesale-replaces <section id="rundown"> in index.html from the SAME
    source/notebook/_rundown.json the Notebook's own front page renders — no second
    copy of the day's stories to drift out of sync. Runs every time any builder
    finishes (via refresh(), below), same as the card .latest lines."""
    data = _load_rundown()
    html_block = _rundown_html(data)
    with open(INDEX, encoding="utf-8") as f:
        src = f.read()
    if not _RUNDOWN_SECTION.search(src):
        print('build_hub: index.html has no <section id="rundown"> slot', file=sys.stderr)
        return False
    new = _RUNDOWN_SECTION.sub(lambda m: html_block, src, count=1)
    if new != src:
        with open(INDEX, "w", encoding="utf-8") as f:
            f.write(new)
    if not quiet:
        n = sum(len(s.get("items", [])) for s in (data or {}).get("sections", []))
        print("  rundown   %s" % ("%d item%s" % (n, "" if n == 1 else "s") if n else "(none)"))
    return new != src


# --- the hub's own link-preview card ------------------------------------------------
# Same dark gradient + gold frame as build.py's _render_default_card (kept in step by
# hand; that renderer is buried in a 6,800-line module we don't want to import here).
_FONTS = {
    "serif_b": "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "sans":    "/System/Library/Fonts/Supplemental/Arial.ttf",
}
OG_LINES = ("A Bible translation, and the five other things",
            "Mr. Librarian keeps, one entry at a time.")


def render_og(path=OG_PATH):
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except Exception:
        return False
    if not all(os.path.exists(p) for p in _FONTS.values()):
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (13, 21, 32))
    d = ImageDraw.Draw(img)
    top, bot = (13, 21, 32), (6, 11, 20)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W * 0.5 - 520, -380, W * 0.5 + 520, 300],
                                 fill=(232, 201, 104, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=26, outline=(92, 84, 54), width=2)

    wf = ImageFont.truetype(_FONTS["serif_b"], 74)
    p1, p2 = "Mister ", "Library"
    w1 = d.textlength(p1, font=wf); w2 = d.textlength(p2, font=wf); sx = W / 2 - (w1 + w2) / 2
    d.text((sx, 205), p1, font=wf, fill=(247, 242, 226), anchor="lm")
    d.text((sx + w1, 205), p2, font=wf, fill=(232, 201, 104), anchor="lm")
    d.rectangle([W / 2 - 48, 278, W / 2 + 48, 282], fill=(232, 201, 104))
    sf = ImageFont.truetype(_FONTS["sans"], 30)
    d.text((W / 2, 332), OG_LINES[0], font=sf, fill=(200, 206, 214), anchor="mm")
    d.text((W / 2, 380), OG_LINES[1], font=sf, fill=(200, 206, 214), anchor="mm")
    d.text((W / 2, 452), "mistertranslation.com", font=ImageFont.truetype(_FONTS["sans"], 21),
           fill=(133, 147, 166), anchor="mm")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.quantize(colors=128, dither=Image.FLOYDSTEINBERG).save(path, "PNG", optimize=True)
    return True


def refresh(quiet=True):
    """The hook every builder calls last. Never raises."""
    try:
        changed = refresh_index(latest(), quiet=quiet)
        if not quiet:
            print("hub: index.html %s" % ("updated" if changed else "unchanged"))
    except Exception as e:
        print("build_hub: index refresh failed: %s" % e, file=sys.stderr)
    try:
        changed = refresh_rundown(quiet=quiet)
        if not quiet:
            print("hub: rundown box %s" % ("updated" if changed else "unchanged"))
    except Exception as e:
        print("build_hub: rundown refresh failed: %s" % e, file=sys.stderr)
    try:
        ok = render_og()
        if not quiet:
            print("hub: og-hub.png %s" % ("rendered" if ok else "skipped (no Pillow/fonts)"))
    except Exception as e:
        print("build_hub: og-hub.png failed: %s" % e, file=sys.stderr)


def main():
    refresh(quiet=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())

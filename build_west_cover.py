#!/usr/bin/env python3
"""Build the KDP cover — paperback and hardcover, one PDF each.

    python3 build_west_cover.py                  # both bindings, white paper
    python3 build_west_cover.py --binding hardcover --paper cream
    python3 build_west_cover.py --pages 300 --spine-in 0.7   # override the estimate

Produces:
  book/cover-paperback.pdf   full wrap (back + spine + front), one page
  book/cover-hardcover.pdf   same, with the case-binding wrap allowance

WHAT THIS DOES AND DOES NOT GET YOU RIGHT
──────────────────────────────────────────
KDP does not publish a fixed cover-dimension formula the way it publishes
interior margins — the real numbers come out of its own interactive Cover
Calculator (kdp.amazon.com/cover-calculator), which is JavaScript and reads
back your exact trim size, paper colour, binding, and FINAL page count. This
script cannot drive that tool, so the geometry below is built from KDP's own
published constants where they exist (bleed, safe margins, barcode box) and
from the best documented approximation of the rest (per-page spine thickness,
the hardcover case-wrap allowance). Numbers are computed, not guessed, and
the assumptions are named below — but treat every SPINE_IN / full-wrap number
this script prints as a draft to CONFIRM against the live calculator before
ordering a proof, the same way the interior's own DPI numbers are measured
and printed rather than assumed (see build_west_book.py's module docstring).
Reruning after ANY content change is required anyway, since the interior's
page count moves the spine width.

GEOMETRY
  Bleed              0.125 in on every outside edge of the flat cover (KDP:
                     "all book covers require bleed").
  Trim safe margin   0.375 in from any trim edge for live text/logos when
                     bleed is used (KDP's own paperback/hardcover figure).
  Spine-edge safety  0.0625 in paperback / 0.4 in hardcover — a hardcover's
                     hinge needs real clearance (the case board's turn-in),
                     a perfect-bound paperback spine does not.
  Spine width        pages * per-page thickness (0.002252 in/pg white,
                     0.0025 in/pg cream) — the same formula both bindings
                     use for the TEXT BLOCK; the case adds its own allowance
                     on top of this, not instead of it.
  Hardcover wrap     + 0.394 in width / + 0.236 in height (the case boards)
                     + 0.591 in on each remaining edge (the wrap-around).
                     These four constants are the least certain numbers in
                     this file — confirm them against the live calculator.
  Barcode safe box   2.0 x 1.2 in, back cover, >=0.76 in from the bottom
                     trim edge, >=0.25 in from the spine hinge. Left BLANK
                     here (no art under it) so KDP can place its own barcode
                     into it at upload time, which is the simplest correct
                     choice — hand-drawing one only to have KDP overlay its
                     own would waste the space twice.

STANDARD LIBRARY ONLY except Chrome for the PDF (same fail-soft posture as
build_west_book.py: no Chrome, no PDF, and the script says so).
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_west as W          # noqa: E402
import build_west_book as B     # noqa: E402

OUT = B.OUT
CHROME = B.CHROME
esc = W.esc

BLEED_IN = 0.125
TRIM_SAFE_IN = 0.375            # live text/logo margin from any trim edge
SPINE_SAFE_PAPERBACK_IN = 0.0625
SPINE_SAFE_HARDCOVER_IN = 0.4   # the case hinge needs real clearance

PER_PAGE_IN = {"white": 0.002252, "cream": 0.0025}

# Hardcover case-wrap allowance — least-certain numbers in this file; see the
# module docstring. Applied to the FULL WRAP only, never to the spine itself.
HC_EXTRA_W_IN = 0.394
HC_EXTRA_H_IN = 0.236
HC_WRAP_EDGE_IN = 0.591

BARCODE_W_IN, BARCODE_H_IN = 2.0, 1.2
BARCODE_BOTTOM_IN, BARCODE_HINGE_IN = 0.76, 0.25

ACCENT = "#4a1018"   # deep oxblood — the cover's own choice, not tied to the site's Delft blue
GOLD = "#cda43c"
GOLD_HI = "#f0d78c"
GOLD_SHADOW = "rgba(0,0,0,.45)"
PARCHMENT = "#f4ecd8"
INK_WARM = "#2a1c12"

MAP_SRC = os.path.join(B.WEB_IMG, "castello-plan-1660.jpg")  # the same plan used as the site's hero


def _leather_texture_b64(size=280):
    """A tileable grain, generated not sourced — same posture as the print
    plates: nothing here is a stock texture pack, and Pillow's absence just
    means a flat leather-colour panel instead of a failed build.

    Low-res noise upscaled with a blur reads as soft organic mottling
    (leather, or old paper); noise generated at the tile's own resolution
    reads as television static — the downsample-then-blur step is what
    makes the difference, not the noise source itself."""
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        return None
    small = Image.effect_noise((max(8, size // 7), max(8, size // 7)), 22).convert("L")
    im = small.resize((size, size), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(size / 45))
    lo, hi = im.getextrema()
    if hi > lo:
        # Compress to a narrow mid-tone band so the overlay blend adds gentle
        # mottling rather than fighting the base colour for dominance.
        im = im.point(lambda v: 95 + (v - lo) * 70 // (hi - lo))
    import io, base64
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _map_watermark_b64(path, tint=GOLD, max_alpha=130):
    """The Castello Plan, etched rather than pasted: greyscale, contrast-
    boosted so the linework reads, then recoloured with the map's own
    darkness as the alpha channel — dark ink becomes visible gold line, the
    plan's pale ground becomes fully transparent leather. A feathered edge
    (a blurred inset rectangle, multiplied into the alpha) fades the plate
    into the leather rather than cutting off in a hard rectangle — the same
    reason the plate's own border is never drawn. Same rule as every plate
    in the book otherwise: the original image, not a redrawn stand-in, and
    nothing upscaled past its own 1600px width."""
    try:
        from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageChops
    except ImportError:
        return None
    im = Image.open(path).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageOps.invert(im)  # dark ink -> high value -> high alpha
    r, g, b = tuple(int(tint.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    rgba = Image.new("RGBA", im.size, (r, g, b, 0))
    alpha = im.point(lambda v: int(v * max_alpha / 255))

    feather = Image.new("L", im.size, 0)
    m = int(min(im.size) * 0.16)
    ImageDraw.Draw(feather).rectangle([m, m, im.size[0] - m, im.size[1] - m], fill=255)
    feather = feather.filter(ImageFilter.GaussianBlur(m * 0.7))
    alpha = ImageChops.multiply(alpha, feather)

    rgba.putalpha(alpha)
    import io, base64
    buf = io.BytesIO()
    rgba.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def spine_in(pages, paper):
    return round(pages * PER_PAGE_IN[paper], 3)


def wrap_dims(trim_w, trim_h, spine, binding):
    """(full_width, full_height, spine_edge_safety) for the flat, bled cover."""
    if binding == "hardcover":
        w = 2 * trim_w + spine + HC_EXTRA_W_IN + 2 * HC_WRAP_EDGE_IN
        h = trim_h + HC_EXTRA_H_IN + 2 * HC_WRAP_EDGE_IN
        return w, h, SPINE_SAFE_HARDCOVER_IN
    w = 2 * trim_w + spine + 2 * BLEED_IN
    h = trim_h + 2 * BLEED_IN
    return w, h, SPINE_SAFE_PAPERBACK_IN


# ── back-cover copy — the same words as book/back-cover-copy.txt ────────────
BACK_BLURB = [
    "In 1662, in a stone church at the tip of Manhattan island, a Dutch "
    "cooper’s granddaughter was baptized with the colony’s two most "
    "powerful men standing witness. Two years later they surrendered New "
    "Amsterdam to England without firing a shot.",
    "Three hundred and sixty years later, a machinist’s grandson found his "
    "uncle’s letters, a genealogy book with the family’s name in it, and a "
    "private record that had just lost twenty-four of its own stories to a "
    "bad save — and set out to write down what four centuries of documents "
    "actually say about a family that crossed an ocean, then a colony, then "
    "a continent, and never once talked about why it kept breaking apart.",
    "Every sentence is marked: documented, inferred, or family legend. This "
    "is non-fiction, read from the wills, the church books, and sixty years "
    "of a family’s own letters.",
]


def _cover_css(w, h, trim_w, spine, binding, leather_b64):
    back_x0, back_x1 = 0.0, trim_w
    spine_x0, spine_x1 = trim_w, trim_w + spine
    front_x0, front_x1 = spine_x1, w
    leather = ("background-image: url('data:image/png;base64,%s'); "
               "background-size: 1.4in 1.4in; background-repeat: repeat; "
               "background-blend-mode: overlay;" % leather_b64) if leather_b64 else ""
    return """
@page { size: %(w).3fin %(h).3fin; margin: 0; }
html, body { margin: 0; padding: 0; width: %(w).3fin; height: %(h).3fin;
  background: %(parchment)s; font-family: "Iowan Old Style", Palatino, "Palatino Linotype", Georgia, serif; }
.wrap { position: relative; width: %(w).3fin; height: %(h).3fin; overflow: hidden; }
.panel { position: absolute; top: 0; height: %(h).3fin; box-sizing: border-box; }
.leather { background-color: %(accent)s; %(leather)s }
.back  { left: 0in; width: %(bx1).3fin; padding: %(safe)sin; }
.spine { left: %(sx0).3fin; width: %(spine).3fin; color: %(gold)s;
  display: flex; align-items: center; justify-content: center; }
.front { left: %(fx0).3fin; width: %(fw).3fin; color: %(gold)s;
  padding: %(safe)sin; box-sizing: border-box; }

.spine .t { writing-mode: vertical-rl; transform: rotate(180deg); text-align: center;
  font-size: 15pt; letter-spacing: .04em; line-height: 1.3;
  text-shadow: 0 1px 0 %(gshadow)s, 0 -.5pt 0 rgba(255,255,255,.12); }
.spine .t .ti { display: block; margin-bottom: .25in; }
.spine .t .au { display: block; font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; }

/* the back cover reads as a paper label set on the leather, not the leather itself */
.back .card { position: relative; z-index: 1; background: %(parchment)s;
  border: .75pt solid rgba(0,0,0,.12); padding: .3in; height: 100%%; box-sizing: border-box; }
.back h2 { font-size: 8.5pt; letter-spacing: .18em; text-transform: uppercase; color: %(accent)s;
  margin: 0 0 .18in; }
.back p { font-size: 10pt; line-height: 1.48; color: %(ink)s; margin: 0 0 .16in; }
.back .barcode { position: absolute; right: %(bcr)sin; bottom: %(bcb)sin;
  width: %(bcw)sin; height: %(bch)sin; border: .5pt dashed rgba(0,0,0,.35); }
.back .barcode span { position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: center; font-size: 6.5pt; color: rgba(0,0,0,.55); letter-spacing: .04em;
  text-align: center; padding: 2pt; }

.front { text-align: center; display: flex; flex-direction: column; justify-content: center;
  position: absolute; }
.front .mapwm { position: absolute; inset: 0; width: 100%%; height: auto; top: 50%%;
  transform: translateY(-50%%); opacity: .9; z-index: 0; }
.front .content { position: relative; z-index: 1; display: flex; flex-direction: column;
  align-items: center; height: 100%%; justify-content: center; }
.front .kicker { font-size: 9pt; letter-spacing: .3em; text-transform: uppercase;
  margin: 0 0 .35in; color: %(gold)s; opacity: .9; }
.front h1 { font-size: 34pt; font-weight: normal; letter-spacing: .02em; line-height: 1.12;
  margin: 0 0 .16in; color: %(goldhi)s; text-shadow: 0 1.5pt 0 %(gshadow)s, 0 -.5pt 0 rgba(255,255,255,.18); }
.front .sub { font-size: 13pt; font-style: italic; margin: 0 0 .12in; opacity: .95; }
.front .tag { font-size: 9.5pt; letter-spacing: .22em; text-transform: uppercase;
  margin: 0 0 .5in; opacity: .8; }
.front .compass circle, .front .compass line { stroke: %(gold)s; }
.front .compass polygon { fill: %(gold)s; }
.front .compass { width: .62in; height: .62in; margin: 0 auto .5in; }
.front .by { font-size: 11pt; letter-spacing: .16em; text-transform: uppercase;
  margin-top: auto; }
""" % {"w": w, "h": h, "bx1": back_x1, "sx0": spine_x0, "spine": spine, "fx0": front_x0,
       "fw": front_x1 - front_x0, "accent": ACCENT, "gold": GOLD, "goldhi": GOLD_HI,
       "gshadow": GOLD_SHADOW, "parchment": PARCHMENT, "ink": INK_WARM, "leather": leather,
       "safe": ("%.3f" % (max(TRIM_SAFE_IN, BLEED_IN + 0.25))),
       "bcr": BARCODE_HINGE_IN, "bcb": BARCODE_BOTTOM_IN,
       "bcw": BARCODE_W_IN, "bch": BARCODE_H_IN}


# A tiny inline SVG compass — the same mark used on the site's hub card —
# so the front cover carries it without needing a raster asset at all. Colour
# comes from the CSS above (.front .compass), not hardcoded here.
COMPASS_SVG = """<svg class="compass" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<circle cx="32" cy="32" r="29" fill="none" stroke-width="2"/>
<line x1="32" y1="8" x2="32" y2="56" stroke-width="1.4"/>
<line x1="8" y1="32" x2="56" y2="32" stroke-width="1.4"/>
<polygon points="32,14 37,32 32,50 27,32"/>
</svg>"""

TAGLINE = "A New York Story"


def build_cover_html(binding, pages, paper, spine_override=None):
    trim_w, trim_h = 6.0, 9.0
    spine = spine_override if spine_override is not None else spine_in(pages, paper)
    w, h, spine_safe = wrap_dims(trim_w, trim_h, spine, binding)
    leather_b64 = _leather_texture_b64()
    css = _cover_css(w, h, trim_w, spine, binding, leather_b64)
    map_b64 = _map_watermark_b64(MAP_SRC) if os.path.exists(MAP_SRC) else None

    barcode_note = ("BARCODE SAFE AREA<br/>leave blank &mdash;<br/>KDP places it at upload"
                     if spine >= 0.06 else "")
    back = ('<div class="panel back leather"><div class="card"><h2>%s</h2>%s'
            '<div class="barcode"><span>%s</span></div></div></div>') % (
        esc(B.TITLE), "".join('<p>%s</p>' % esc(p) for p in BACK_BLURB), barcode_note)
    spine_html = ('<div class="panel spine leather"><div class="t"><span class="ti">%s</span>'
                  '<span class="au">%s</span></div></div>') % (esc(B.TITLE), esc(B.AUTHOR))
    map_img = ('<img class="mapwm" src="data:image/png;base64,%s" alt=""/>' % map_b64) if map_b64 else ""
    front = ('<div class="panel front leather">%s<div class="content">'
             '<p class="kicker">A family history</p>%s<h1>%s</h1>'
             '<p class="sub">%s</p><p class="tag">%s</p><p class="by">%s</p></div></div>') % (
        map_img, COMPASS_SVG, esc(B.TITLE), esc(B.SUBTITLE), esc(TAGLINE), esc(B.AUTHOR))

    doc = """<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head>
<body><div class="wrap">%s%s%s</div></body></html>""" % (css, back, spine_html, front)
    return doc, w, h, spine, spine_safe


def _chrome_pdf(html_path, pdf_path, w, h):
    if not os.path.exists(CHROME):
        return False
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=" + pdf_path,
                        "--print-to-pdf-no-header",
                        "file://" + html_path],
                       capture_output=True, text=True, timeout=120)
    return os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000


def build_one(binding, pages, paper, spine_override=None):
    os.makedirs(OUT, exist_ok=True)
    doc, w, h, spine, spine_safe = build_cover_html(binding, pages, paper, spine_override)
    html_path = os.path.join(OUT, "cover-%s.html" % binding)
    pdf_path = os.path.join(OUT, "cover-%s.pdf" % binding)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    ok = _chrome_pdf(html_path, pdf_path, w, h)
    print("cover %-10s  %d pp, %s paper  ->  spine %.3fin, full wrap %.3f x %.3fin  (spine-edge safety %.3fin)%s"
          % (binding, pages, paper, spine, w, h,
             spine_safe, "" if ok else "   [Chrome not found — HTML only]"))
    return pdf_path if ok else html_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--binding", choices=["paperback", "hardcover", "both"], default="both")
    ap.add_argument("--paper", choices=["white", "cream"], default="white")
    ap.add_argument("--pages", type=int, default=None,
                     help="interior page count; default = read from book/eight-miles-west.pdf")
    ap.add_argument("--spine-in", type=float, default=None,
                     help="override the computed spine width (inches)")
    args = ap.parse_args()

    pages = args.pages
    if pages is None:
        interior = os.path.join(OUT, "eight-miles-west.pdf")
        try:
            from pypdf import PdfReader
            pages = len(PdfReader(interior).pages)
        except Exception:
            sys.exit("book refused — need a page count: run build_west_book.py first, "
                     "or pass --pages N")

    bindings = ["paperback", "hardcover"] if args.binding == "both" else [args.binding]
    print("interior: %d pages, %s paper (confirm the FINAL count with KDP's own calculator "
          "before ordering a proof)" % (pages, args.paper))
    for b in bindings:
        build_one(b, pages, args.paper, args.spine_in)


if __name__ == "__main__":
    main()

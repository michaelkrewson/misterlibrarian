#!/usr/bin/env python3
"""Compile Eight Miles West into a book — the KDP paperback and an EPUB.

    python3 build_west_book.py          # → book/eight-miles-west.{html,pdf,epub}
    python3 build_west_book.py --html   # just the print HTML (no Chrome)

Reads the same source/west/NN-slug.html chapters that build_west.py publishes
(drafts excluded, same front-matter rules), and produces:

  book/eight-miles-west.html   one print-ready HTML file, 6 x 9 in, KDP margins
  book/eight-miles-west.pdf    printed by headless Chrome, body pages numbered
                               (front matter unnumbered) with pypdf
  book/eight-miles-west.epub   a hand-packed EPUB 3 (stdlib zipfile)

STANDARD LIBRARY ONLY for the HTML and the EPUB — the repo's rule. The PDF step
shells out to Google Chrome (macOS path below) and uses pypdf if it is installed,
which is the one exception, and it fails soft: no Chrome → no PDF, the HTML and
EPUB are still built and the build says so.

DESIGN
The web build is dark, Delft-blue, one chapter per page. The book is the same
text set for paper: Iowan Old Style (the macOS book face; Palatino/Georgia
fallbacks), 11/15 pt, a half-title, a title page, a copyright page, Uncle Al's
epigraph, a contents page, five part-title pages, and each chapter with its
dateline, its "In the record" line, its summary as a lede, the text, and its
sources as chapter endnotes. The three registers survive in monochrome:
.doc blocks are indented with a rule; .doc.legend blocks carry a small
"FAMILY LEGEND" label; .infer spans get a dotted underline — the book's rule
(documented / inferred / legend, on the page) has to hold in print too.

Output lives in book/ which is gitignored — a PDF is a build product; the
chapters are the source. Rebuild any time with one command.
"""
import datetime as dt
import html
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_west as W  # noqa: E402

ROOT = W.ROOT
OUT = os.path.join(ROOT, "book")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TITLE = W.SITE_NAME
SUBTITLE = "A family's four centuries in America"
AUTHOR = W.AUTHOR
YEAR = dt.date.today().year
EPIGRAPH = ("Seems like the whole Krewson line all the way back to the 1600s had these problems "
            "with rifts over disagreements… but no one was talking about what they were.")
EPIGRAPH_BY = "Alfred G. M. Krewson to his nephew, 20 January 2005"

esc = W.esc


# ── print CSS ────────────────────────────────────────────────────────────────
CSS = """
@page { size: 6in 9in; margin: 0.7in 0.75in 0.8in 0.75in; }
html { font-size: 11pt; }
body { margin: 0; color: #111; background: #fff;
  font-family: "Iowan Old Style", "Palatino", "Palatino Linotype", "Book Antiqua", Georgia, serif;
  line-height: 1.42; text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased; }
p { margin: 0; text-indent: 1.4em; orphans: 2; widows: 2; hyphens: auto; -webkit-hyphens: auto; }
p.first, h2 + p, .lede, .doc p, .part-lede, .front p, .sources li p { text-indent: 0; }
a { color: inherit; text-decoration: none; }
i, em { font-style: italic; }

/* front matter */
.page { page-break-after: always; }
.half { padding-top: 3in; text-align: center; }
.half h1 { font-size: 16pt; font-weight: normal; letter-spacing: .18em; text-transform: uppercase; margin: 0; }
.tp { padding-top: 2.2in; text-align: center; }
.tp h1 { font-size: 30pt; font-weight: normal; letter-spacing: .06em; margin: 0 0 .25in; line-height: 1.1; }
.tp .sub { font-size: 12.5pt; font-style: italic; margin: 0 0 1.4in; }
.tp .by { font-size: 12pt; letter-spacing: .12em; text-transform: uppercase; }
.copy { padding-top: 5.2in; font-size: 8.5pt; line-height: 1.5; }
.copy p { text-indent: 0; margin: 0 0 .6em; }
.epi { padding-top: 2.6in; text-align: center; }
.epi p { text-indent: 0; font-style: italic; font-size: 12pt; line-height: 1.5; margin: 0 .3in .4in; }
.epi .by { font-style: normal; font-size: 8.4pt; letter-spacing: .1em; text-transform: uppercase; white-space: nowrap; }
.toc h1 { font-size: 14pt; font-weight: normal; letter-spacing: .18em; text-transform: uppercase; text-align: center; margin: .6in 0 .5in; }
.toc .tpart { margin: .35in 0 .1in; font-size: 8.6pt; letter-spacing: .12em; text-transform: uppercase; text-indent: 0; }
.toc .tpart b { font-weight: normal; }
.toc .tch { text-indent: 0; margin: 0 0 .06in .3in; font-size: 10.5pt; }
.toc .tch .n { display: inline-block; width: .3in; margin-left: -.3in; color: #555; font-variant-numeric: tabular-nums; }

/* parts */
.part { page-break-before: right; page-break-after: always; padding-top: 2.4in; text-align: center; }
.part .num { font-size: 10pt; letter-spacing: .3em; text-transform: uppercase; margin: 0 0 .3in; }
.part h1 { font-size: 24pt; font-weight: normal; margin: 0 0 .15in; line-height: 1.15; }
.part .span { font-size: 10pt; letter-spacing: .1em; margin: 0 0 .5in; }
.part-lede { font-style: italic; font-size: 11pt; margin: 0 .4in; line-height: 1.5; }

/* chapters */
.chapter { page-break-before: always; }
.chapter header { margin: .9in 0 .45in; text-align: center; page-break-after: avoid; }
.chapter .cnum { font-size: 9.5pt; letter-spacing: .28em; text-transform: uppercase; margin: 0 0 .2in; }
.chapter h1 { font-size: 21pt; font-weight: normal; margin: 0 0 .18in; line-height: 1.15; }
.chapter .dateline { font-size: 9.5pt; letter-spacing: .06em; text-transform: uppercase; margin: 0 0 .1in; color: #333; }
.chapter .people { font-size: 8.8pt; line-height: 1.45; color: #444; margin: 0 .2in; text-indent: 0; }
.chapter .people b { font-weight: normal; letter-spacing: .1em; text-transform: uppercase; font-size: 7.8pt; }
.lede { font-style: italic; margin: 0 0 .28in; line-height: 1.45; }
.chapter h2 { font-size: 10pt; font-weight: normal; letter-spacing: .16em; text-transform: uppercase; margin: .32in 0 .12in; page-break-after: avoid; }

/* the three registers, in monochrome */
.doc { margin: .16in .25in .16in .25in; padding: 0 0 0 .16in; border-left: 1.2pt solid #333; font-size: 10.2pt; line-height: 1.42; page-break-inside: avoid; }
.doc p { margin: 0 0 .05in; }
.doc .cite { display: block; font-size: 8.4pt; color: #444; letter-spacing: .02em; margin-top: .05in; }
.doc.legend { border-left-style: dotted; }
.doc.legend::before { content: "Family legend"; display: block; font-size: 7.6pt; letter-spacing: .16em; text-transform: uppercase; color: #444; margin-bottom: .05in; }
.infer { text-decoration: underline; text-decoration-style: dotted; text-decoration-color: #777; text-underline-offset: 2.5pt; }
.chapter ol:not(.sources) { margin: .1in 0 .1in .25in; padding: 0; font-size: 10.4pt; }
.chapter ol:not(.sources) li { margin: 0 0 .06in; }

/* sources as chapter endnotes */
.sources { margin: .35in 0 0; padding: .12in 0 0 .25in; border-top: .6pt solid #999; font-size: 8.6pt; line-height: 1.42; color: #222; }
.sources::before { content: "Sources"; display: block; margin: 0 0 .08in -.25in; font-size: 8pt; letter-spacing: .18em; text-transform: uppercase; }
.sources li { margin: 0 0 .05in; }

/* back matter */
.back { page-break-before: always; padding-top: 1.2in; }
.back h1 { font-size: 12pt; font-weight: normal; letter-spacing: .18em; text-transform: uppercase; text-align: center; margin: 0 0 .4in; }
.back p { text-indent: 0; margin: 0 0 .15in; }
.legend-key { font-size: 9.5pt; }
"""


def _front(chapters):
    parts = []
    parts.append('<section class="page half"><h1>%s</h1></section>' % esc(TITLE))
    parts.append('<section class="page tp"><h1>%s</h1><p class="sub">%s</p><p class="by">%s</p></section>'
                 % (esc(TITLE), esc(SUBTITLE), esc(AUTHOR)))
    parts.append("""<section class="page copy">
<p>%(t)s: %(s)s<br>Copyright &copy; %(y)s %(a)s. All rights reserved.</p>
<p>First published online, a chapter at a time, at mistertranslation.com/west/ in %(y)s. This edition compiled from the published chapters on %(d)s.</p>
<p>This is a work of non-fiction. Every chapter ends with its sources. In the text, a passage set off with a rule at the left is a document or a letter quoted as written; a passage marked <span class="doc legend" style="display:inline;border:0;padding:0;margin:0;font-size:inherit">family legend</span> is what the family says and no document shows; and a phrase with a dotted underline is the author's inference from the record, marked so the reader can weigh it. Where the book says a thing is period-general, it describes the time and place and not these people.</p>
<p>Names of living people appear as they appear in the family's own record and correspondence.</p>
</section>""" % {"t": esc(TITLE), "s": esc(SUBTITLE), "y": YEAR, "a": esc(AUTHOR),
                  "d": dt.date.today().strftime("%-d %B %Y")})
    parts.append('<section class="page epi"><p>&ldquo;%s&rdquo;</p><p class="by">&mdash; %s</p></section>'
                 % (esc(EPIGRAPH), esc(EPIGRAPH_BY)))
    # contents
    toc = ['<section class="page toc"><h1>Contents</h1>']
    cur = None
    for c in chapters:
        if c["part"] != cur:
            cur = c["part"]
            roman, name, span, _ = W.PARTS[cur]
            toc.append('<p class="tpart"><b>Part %s</b> &middot; %s &middot; %s</p>' % (esc(roman), esc(name), esc(span)))
        toc.append('<p class="tch"><span class="n">%d</span>%s</p>' % (c["num"], esc(c["title"])))
    toc.append("</section>")
    parts.append("\n".join(toc))
    return "\n".join(parts)


def _body_html(c):
    """The chapter body as written, plus print-only touches."""
    b = c["body"].strip()
    # first paragraph unindented
    b = re.sub(r"^<p>", '<p class="first">', b, count=1)
    return b


def _chapter(c):
    roman, name, _, _ = W.PARTS[c["part"]]
    people = ""
    if c["people"]:
        people = '<p class="people"><b>In the record</b> &middot; %s</p>' % esc(", ".join(c["people"]))
    dateline = '<p class="dateline">%s</p>' % esc(c["dateline"]) if c["dateline"] else ""
    return """<article class="chapter" id="ch%(n)d">
<header><p class="cnum">Chapter %(n)d</p><h1>%(t)s</h1>%(dl)s%(pp)s</header>
<p class="lede">%(s)s</p>
%(b)s
</article>""" % {"n": c["num"], "t": esc(c["title"]), "dl": dateline, "pp": people,
                 "s": esc(c["summary"]), "b": _body_html(c)}


def _parts_and_chapters(chapters):
    out = []
    cur = None
    for c in chapters:
        if c["part"] != cur:
            cur = c["part"]
            roman, name, span, lede = W.PARTS[cur]
            out.append('<section class="part" id="part-%s"><p class="num">Part %s</p><h1>%s</h1><p class="span">%s</p><p class="part-lede">%s</p></section>'
                       % (esc(cur), esc(roman), esc(name), esc(span), esc(lede)))
        out.append(_chapter(c))
    return "\n".join(out)


def _back():
    return """<section class="back">
<h1>About this book</h1>
<p>%(t)s was written and published one chapter at a time at mistertranslation.com/west/, where each chapter keeps its own page, its sources, and a place for readers to write. The family's private record — the letters, certificates, photographs and DNA results the book was read from — is kept by the author and is described in the last chapter, together with the list of what is still not known. Corrections and additions from cousins are the point; the address is on the website.</p>
<p>The book's rule, kept on every page: <i>documented</i>, <i>inferred</i>, or <i>family legend</i>, and say which.</p>
<p>%(a)s is the great-great-great-grandson of Lewis Krewson of Ohio and Iowa, and the ninth-generation descendant of Garret Dircksen Croesen of Breuckelen. He lives in California.</p>
</section>""" % {"t": esc(TITLE), "a": esc(AUTHOR)}


def build_html(chapters):
    body = _front(chapters) + "\n" + _parts_and_chapters(chapters) + "\n" + _back()
    doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>
<body>
%s
</body></html>""" % (esc(TITLE), CSS, body)
    return doc


# ── PDF via Chrome + pypdf page numbers ──────────────────────────────────────
def _chrome_pdf(src, dst):
    if not os.path.exists(CHROME):
        return False
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=" + dst, "file://" + src],
                       capture_output=True, text=True, timeout=300)
    return os.path.exists(dst) and os.path.getsize(dst) > 1000


def _number_pages(pdf_path, first_body_page):
    """Overlay page numbers (bottom centre) on every page from first_body_page
    (0-based) on. Numbers start at 1 there. Overlay is itself a Chrome-printed
    PDF of N blank pages with a number each, merged page-for-page with pypdf."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("  pypdf not installed — PDF left unnumbered")
        return False
    reader = PdfReader(pdf_path)
    n = len(reader.pages)
    body_n = n - first_body_page
    pages = []
    for i in range(body_n):
        pages.append('<div class="pg"><span>%d</span></div>' % (i + 1))
    ov_html = os.path.join(OUT, "_pagenums.html")
    with open(ov_html, "w", encoding="utf-8") as fh:
        fh.write("""<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: 6in 9in; margin: 0; }
body { margin: 0; font-family: "Iowan Old Style", Palatino, Georgia, serif; }
.pg { position: relative; width: 6in; height: 9in; page-break-after: always; }
.pg span { position: absolute; bottom: .42in; left: 0; right: 0; text-align: center; font-size: 9.5pt; color: #222; }
</style></head><body>%s</body></html>""" % "\n".join(pages))
    ov_pdf = os.path.join(OUT, "_pagenums.pdf")
    if not _chrome_pdf(ov_html, ov_pdf):
        return False
    ov = PdfReader(ov_pdf)
    w = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i >= first_body_page and (i - first_body_page) < len(ov.pages):
            page.merge_page(ov.pages[i - first_body_page])
        w.add_page(page)
    w.add_metadata({"/Title": TITLE, "/Author": AUTHOR})
    with open(pdf_path, "wb") as fh:
        w.write(fh)
    for f in (ov_html, ov_pdf):
        try: os.remove(f)
        except OSError: pass
    return True


def build_pdf(html_path, pdf_path, chapters):
    if not _chrome_pdf(html_path, pdf_path):
        print("  Chrome not found or print failed — no PDF")
        return None
    # front matter = 5 pages (half, title, copyright, epigraph, contents…) — the
    # contents can run to 2 pages; find the first part page by printing the
    # front matter alone and counting.
    front_html = os.path.join(OUT, "_front.html")
    with open(front_html, "w", encoding="utf-8") as fh:
        fh.write("""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>"""
                 % (CSS, _front(chapters)))
    front_pdf = os.path.join(OUT, "_front.pdf")
    first_body = 5
    if _chrome_pdf(front_html, front_pdf):
        try:
            from pypdf import PdfReader
            first_body = len(PdfReader(front_pdf).pages)
        except ImportError:
            pass
    for f in (front_html, front_pdf):
        try: os.remove(f)
        except OSError: pass
    _number_pages(pdf_path, first_body)
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf_path).pages)
    except ImportError:
        return -1


# ── EPUB (hand-packed, EPUB 3) ───────────────────────────────────────────────
EPUB_CSS = """
body { font-family: Georgia, serif; line-height: 1.5; margin: 0 4%; }
h1 { font-weight: normal; font-size: 1.6em; text-align: center; margin: 1.5em 0 .3em; }
h2 { font-weight: normal; font-size: .95em; letter-spacing: .14em; text-transform: uppercase; margin: 1.6em 0 .5em; }
p { margin: 0 0 .7em; }
.cnum, .dateline, .people, .by, .span, .num { text-align: center; font-size: .85em; letter-spacing: .08em; text-transform: uppercase; color: #444; }
.people { text-transform: none; letter-spacing: 0; }
.lede, .part-lede { font-style: italic; }
.doc { margin: 1em 1.2em; padding-left: .8em; border-left: 2px solid #444; font-size: .95em; }
.doc .cite { display: block; font-size: .8em; color: #555; }
.doc.legend { border-left-style: dotted; }
.doc.legend:before { content: "Family legend"; display: block; font-size: .75em; letter-spacing: .14em; text-transform: uppercase; color: #555; }
.infer { text-decoration: underline dotted; }
.sources { font-size: .85em; border-top: 1px solid #999; margin-top: 2em; padding-top: 1em; }
.sources:before { content: "Sources"; display: block; letter-spacing: .14em; text-transform: uppercase; font-size: .85em; margin-bottom: .5em; }
.tp, .half, .epi, .part { text-align: center; margin-top: 30%; }
.tp h1 { font-size: 2.2em; }
.copy { font-size: .85em; }
.toc p { margin: 0 0 .3em; }
"""


def _xhtml(title, body_html):
    return """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
%s
</body></html>""" % (esc(title), body_html)


def _to_xhtml_fragment(s):
    """Our chapter bodies are hand-written and already well-formed; make the
    few HTML-isms XML-safe and verify by parsing."""
    s = re.sub(r"<br\s*>", "<br/>", s)
    s = re.sub(r"<hr\s*>", "<hr/>", s)
    s = s.replace("&nbsp;", "&#160;").replace("&mdash;", "&#8212;").replace("&ndash;", "&#8211;") \
         .replace("&ldquo;", "&#8220;").replace("&rdquo;", "&#8221;").replace("&middot;", "&#183;") \
         .replace("&copy;", "&#169;").replace("&hellip;", "&#8230;")
    s = re.sub(r"&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", s)
    import xml.etree.ElementTree as ET
    ET.fromstring("<div>%s</div>" % s)  # raises if not well-formed
    return s


def build_epub(chapters, epub_path):
    uid = "urn:uuid:" + "8d1c0f0e-" + "west" + "-" + str(YEAR) + "-eight-miles"
    files = []  # (name, bytes, mediatype, id, in_spine)
    def add(name, text, mt="application/xhtml+xml", spine=True):
        files.append((name, text.encode("utf-8"), mt, re.sub(r"[^a-z0-9]", "_", name), spine))
    add("style.css", EPUB_CSS, "text/css", spine=False)
    add("title.xhtml", _xhtml(TITLE, '<section class="tp"><h1>%s</h1><p class="lede">%s</p><p class="by">%s</p></section>'
                              % (esc(TITLE), esc(SUBTITLE), esc(AUTHOR))))
    add("copyright.xhtml", _xhtml("Copyright", _to_xhtml_fragment(
        '<section class="copy"><p>%s: %s. Copyright &#169; %d %s. All rights reserved.</p>'
        '<p>First published online, a chapter at a time, at mistertranslation.com/west/ in %d.</p>'
        '<p>A work of non-fiction. Every chapter ends with its sources. A passage set off with a rule is a document or letter quoted as written; a passage labelled <i>family legend</i> is what the family says and no document shows; a phrase with a dotted underline is the author\'s inference from the record. Where the book says a thing is period-general, it describes the time and place and not these people.</p></section>'
        % (esc(TITLE), esc(SUBTITLE), YEAR, esc(AUTHOR), YEAR))))
    add("epigraph.xhtml", _xhtml("Epigraph", '<section class="epi"><p class="lede">&#8220;%s&#8221;</p><p class="by">&#8212; %s</p></section>'
                                 % (esc(EPIGRAPH), esc(EPIGRAPH_BY))))
    # nav / contents
    nav = ['<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>']
    cur = None
    for c in chapters:
        if c["part"] != cur:
            if cur is not None:
                nav.append("</ol></li>")
            cur = c["part"]
            roman, name, span, _ = W.PARTS[cur]
            nav.append('<li><a href="part-%s.xhtml">Part %s &#183; %s</a><ol>' % (esc(cur), esc(roman), esc(name)))
        nav.append('<li><a href="ch%02d.xhtml">%d. %s</a></li>' % (c["num"], c["num"], esc(c["title"])))
    nav.append("</ol></li></ol></nav>")
    add("nav.xhtml", _xhtml("Contents", "\n".join(nav)))
    cur = None
    for c in chapters:
        if c["part"] != cur:
            cur = c["part"]
            roman, name, span, lede = W.PARTS[cur]
            add("part-%s.xhtml" % cur, _xhtml("Part " + roman, '<section class="part"><p class="num">Part %s</p><h1>%s</h1><p class="span">%s</p><p class="part-lede">%s</p></section>'
                                             % (esc(roman), esc(name), esc(span), esc(lede))))
        people = '<p class="people">In the record: %s</p>' % esc(", ".join(c["people"])) if c["people"] else ""
        dateline = '<p class="dateline">%s</p>' % esc(c["dateline"]) if c["dateline"] else ""
        body = '<p class="cnum">Chapter %d</p><h1>%s</h1>%s%s<p class="lede">%s</p>\n%s' % (
            c["num"], esc(c["title"]), dateline, people, esc(c["summary"]), _to_xhtml_fragment(c["body"].strip()))
        add("ch%02d.xhtml" % c["num"], _xhtml(c["title"], body))
    add("about.xhtml", _xhtml("About this book", _to_xhtml_fragment(_back().replace('class="back"', 'class="back"'))))

    manifest = []
    spine = []
    for name, data, mt, fid, in_spine in files:
        props = ' properties="nav"' if name == "nav.xhtml" else ""
        manifest.append('<item id="%s" href="%s" media-type="%s"%s/>' % (fid, name, mt, props))
        if in_spine:
            spine.append('<itemref idref="%s"/>' % fid)
    opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">%s</dc:identifier>
<dc:title>%s</dc:title>
<dc:creator>%s</dc:creator>
<dc:language>en</dc:language>
<dc:description>%s</dc:description>
<meta property="dcterms:modified">%s</meta>
</metadata>
<manifest>
%s
</manifest>
<spine>
%s
</spine>
</package>""" % (uid, esc(TITLE), esc(AUTHOR), esc(W.BLURB),
                 dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "\n".join(manifest), "\n".join(spine))
    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        for name, data, mt, fid, in_spine in files:
            z.writestr("OEBPS/" + name, data, compress_type=zipfile.ZIP_DEFLATED)
    return len(files)


def main():
    html_only = "--html" in sys.argv
    chapters = W.load_chapters(include_drafts=False)
    W.check_chapters(chapters)
    os.makedirs(OUT, exist_ok=True)
    html_path = os.path.join(OUT, "eight-miles-west.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(build_html(chapters))
    words = sum(len(re.sub(r"<[^>]+>", " ", c["body"]).split()) for c in chapters)
    print("book: %d chapters, ~%s words → %s" % (len(chapters), format(words, ","), os.path.relpath(html_path, ROOT)))
    epub_path = os.path.join(OUT, "eight-miles-west.epub")
    n = build_epub(chapters, epub_path)
    print("epub: %d files → %s" % (n, os.path.relpath(epub_path, ROOT)))
    if html_only:
        return
    pdf_path = os.path.join(OUT, "eight-miles-west.pdf")
    pages = build_pdf(html_path, pdf_path, chapters)
    if pages:
        print("pdf: %s pages, 6 x 9 in → %s" % (pages, os.path.relpath(pdf_path, ROOT)))


if __name__ == "__main__":
    main()

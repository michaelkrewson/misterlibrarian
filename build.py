#!/usr/bin/env python3
"""Build the MisterLibrarian Bible Project static site.

Single source of truth: mstr-trader's dashboard/mister_translation.html
(each chapter lives there as a <div class="chapter-panel" id="chapter-genN">
block). This script extracts every chapter panel and regenerates the public
site: one page per chapter with prev/next navigation, a Table of Contents
with live progress, the home page, and the Ask Mr. Librarian posts.

Usage:
    python3 build.py [--source /path/to/mister_translation.html]

After adding a new chapter to the source file, re-run this and push.
"""
import argparse
import html
import os
import re

DEFAULT_SOURCE = os.path.expanduser(
    "~/projects/mstr-trader/dashboard/mister_translation.html")
OUT = os.path.dirname(os.path.abspath(__file__))

SITE_NAME = "The MisterLibrarian Bible Project"
TAGLINE = "Catalogued &amp; compared, one chapter at a time"
SITE_URL = "https://michaelkrewson.github.io/misterlibrarian"

# FormSubmit endpoint for the Ask-a-Question form. This is the activated form's
# random alias (delivers to the librarian's gmail without exposing the address in
# the page source). Verified working 2026-07-10 via a test submission.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

# Chapter registry: slug -> (book, chapter number, one-line teaser).
# Add a line here when a new chapter lands in the source file.
CHAPTERS = [
    ("gen1", "Genesis", 1, "The seven days — day one, the vault, and the image of God."),
    ("gen2", "Genesis", 2, "The sabbath, the divine name arrives, and “side,” not “rib.”"),
    ("gen3", "Genesis", 3, "The serpent, the fall, and the naked/crafty pun that spans the chapter break."),
    ("gen4", "Genesis", 4, "Cain and Abel, the first murder, and “am I my brother’s keeper?”"),
    ("gen5", "Genesis", 5, "Ten generations, one drumbeat — and the one man who never dies."),
    ("gen6", "Genesis", 6, "The sons of God, the Nephilim, the LORD’s regret, and the ark."),
    ("gen7", "Genesis", 7, "The flood: creation run in reverse, and “the LORD shut him in.”"),
]
NEXT_UP = "Genesis 8"          # shown greyed-out at the end of the nav chain
TOTAL_BIBLE_CHAPTERS = 1189

BOOKS_OT = [("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
    ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
    ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
    ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
    ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
    ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4)]
BOOKS_NT = [("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
    ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
    ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
    ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6),
    ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
    ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
    ("3 John", 1), ("Jude", 1), ("Revelation", 22)]

FAVICON = ("data:image/svg+xml," + html.escape(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 46 46'>"
    "<circle cx='23' cy='23' r='22.5' fill='#0b1929'/>"
    "<rect x='9' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='33.4' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='12.6' y='14.5' width='20.8' height='17' fill='#efe6cf'/>"
    "<path d='M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z' fill='#e8c968'/></svg>", quote=True))

SCROLL_SVG = """<svg class="mtlib-icon" viewBox="0 0 46 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="23" cy="23" r="22.5" fill="#0b1929"/>
  <circle cx="23" cy="23" r="22.5" fill="none" stroke="#e8c968" stroke-width="0.7" opacity="0.4"/>
  <rect x="9" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="33.4" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="12.6" y="14.5" width="20.8" height="17" fill="#efe6cf"/>
  <g stroke="#8a7ab0" stroke-width="1.1" stroke-linecap="round">
    <line x1="15.5" y1="19" x2="30.5" y2="19"/>
    <line x1="15.5" y1="23" x2="30.5" y2="23"/>
    <line x1="15.5" y1="27" x2="26.5" y2="27"/>
  </g>
  <path d="M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z" fill="#e8c968"/>
</svg>"""


def header(active=""):
    def cls(k):
        return ' class="on"' if k == active else ""
    return f"""<header class="site-head">
  <a class="brand" href="index.html">
    {SCROLL_SVG}
    <span class="brand-name">The Mister<span class="lib">Librarian</span> Bible Project</span>
  </a>
  <div class="rule"></div>
  <div class="tag">{TAGLINE}</div>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Home</a>
    <a href="toc.html"{cls('toc')}>Table of Contents</a>
    <a href="ask-enoch.html"{cls('ask')}>Ask Mr. Librarian</a>
    <a href="contact.html"{cls('contact')}>✉️ Ask a Question</a>
    <a href="about.html"{cls('about')}>About</a>
  </nav>
</header>"""


FOOTER = """<footer class="site-foot">
  <p>The MisterLibrarian Bible Project — a fresh translation of the Bible into modern English, made from
  the original Hebrew (the Masoretic Text) one chapter at a time, with translator's notes comparing every
  choice against seven landmark versions. Kept by Mr. Librarian; translated with Claude.</p>
  <p><a href="toc.html">Table of Contents</a> · <a href="contact.html">Ask Mr. Librarian a question</a> · <a href="about.html">About the project</a></p>
</footer>"""


def page(title, body, active="", desc=""):
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}
<link rel="icon" href="{FAVICON}"/>
<link rel="stylesheet" href="style.css"/>
</head>
<body>
<div class="wrap">
{header(active)}
{body}
{FOOTER}
</div>
</body>
</html>
"""


def extract_source(source_path):
    src = open(source_path, encoding="utf-8").read()
    chapters = {}
    for slug, _, _, _ in CHAPTERS:
        m = re.search(
            r'<div class="chapter-panel[^"]*" id="chapter-%s">(.*?)</div><!-- /chapter-%s -->'
            % (slug, slug), src, re.S)
        if not m:
            raise SystemExit(f"chapter panel {slug} not found in source")
        chapters[slug] = m.group(1).strip()
    return chapters


def clean_chapter(content):
    # In-page chapter-switch links (showChapter) -> plain text; the nav strip covers movement.
    content = re.sub(
        r'<a href="#" onclick="showChapter\(\'(gen\d+)\'[^"]*"[^>]*>([^<]+)</a>',
        lambda m: f'<a href="genesis-{m.group(1)[3:]}.html">{m.group(2)}</a>', content)
    return content


def nav_strip(idx, position):
    prev_html = ""
    if idx > 0:
        pslug, pbook, pnum, _ = CHAPTERS[idx - 1]
        prev_html = f'<a href="genesis-{pnum}.html">◄ {pbook} {pnum}</a>'
    if idx < len(CHAPTERS) - 1:
        nslug, nbook, nnum, _ = CHAPTERS[idx + 1]
        next_html = f'<a href="genesis-{nnum}.html">{nbook} {nnum} ►</a>'
    else:
        next_html = f'<span class="dis">{NEXT_UP} (coming soon)</span>'
    return (f'<div class="chnav {position}"><div class="side left">{prev_html}</div>'
            f'<div class="mid"><a href="toc.html">\U0001F4DC Table of Contents</a></div>'
            f'<div class="side right">{next_html}</div></div>')


def build_chapter_pages(chapters):
    for idx, (slug, book, num, teaser) in enumerate(CHAPTERS):
        content = clean_chapter(chapters[slug])
        toggle = ('<div class="togglebar"><button class="tgl" id="hebtgl" '
                  'onclick="toggleHeb()">Hide Hebrew</button></div>')
        body = f"""{nav_strip(idx, 'top')}
{toggle}
<article class="chapter">
{content}
</article>
{nav_strip(idx, 'bottom')}
<script>
function toggleHeb(){{
  var hidden = document.body.classList.toggle("hide-heb");
  document.getElementById("hebtgl").textContent = hidden ? "Show Hebrew" : "Hide Hebrew";
  try{{ localStorage.setItem("mtlib_hideheb", hidden ? "1" : "0"); }}catch(e){{}}
}}
(function(){{ try{{
  if (localStorage.getItem("mtlib_hideheb") === "1"){{
    document.body.classList.add("hide-heb");
    document.getElementById("hebtgl").textContent = "Show Hebrew";
  }}
}}catch(e){{}} }})();
</script>"""
        desc = (f"{book} {num} translated fresh from the Hebrew (Masoretic Text), with verse-by-verse "
                f"notes comparing NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and "
                f"NWT. {teaser}")
        out = page(f"{book} {num} — {SITE_NAME}", body, desc=desc)
        open(os.path.join(OUT, f"genesis-{num}.html"), "w", encoding="utf-8").write(out)


def build_toc():
    done = len(CHAPTERS)
    pct = round(done / TOTAL_BIBLE_CHAPTERS * 1000) / 10
    gen_total = 50
    chips = []
    done_nums = {num for _, _, num, _ in CHAPTERS}
    for i in range(1, gen_total + 1):
        if i in done_nums:
            chips.append(f'<a class="chch chch-done" href="genesis-{i}.html">{i}</a>')
        else:
            chips.append(f'<span class="chch">{i}</span>')
    def book_chip(name, n, active=False):
        if active:
            return f'<span class="book book-active">{name} <b>{done}/{n}</b></span>'
        return f'<span class="book">{name} <i>{n}</i></span>'
    ot = "".join(book_chip(n, c, n == "Genesis") for n, c in BOOKS_OT)
    nt = "".join(book_chip(n, c) for n, c in BOOKS_NT)
    rows = "".join(
        f'<a class="chrow" href="genesis-{num}.html"><span class="chrow-n">{book} {num}</span>'
        f'<span class="chrow-t">{teaser}</span></a>'
        for _, book, num, teaser in CHAPTERS)
    body = f"""<h1 class="pagetitle">\U0001F4DC Table of Contents</h1>
<p class="lede">Every chapter of the translation, tracked as it's finished. Gold numbers are published
and link to their chapter; everything else is still ahead.</p>

<h2>Progress</h2>
<div class="panel">
  <div class="progress-row">
    <div class="progress-num"><span>{done}</span> of {TOTAL_BIBLE_CHAPTERS} chapters</div>
    <div class="progress-label">{pct}% of the Bible</div>
  </div>
  <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>
</div>

<h2>Published chapters</h2>
<div class="panel chlist">
{rows}
</div>

<h2>Now Reading — Genesis</h2>
<div class="panel">
  <div class="now-reading"><span class="nr-badge">In Progress</span>
  <span class="nr-book">Genesis · {done} of {gen_total} chapters</span></div>
  <div class="chgrid">{''.join(chips)}</div>
</div>

<h2>All 66 Books</h2>
<div class="panel">
  <div class="testament">Old Testament · 39 books</div>
  <div class="bookgrid">{ot}</div>
  <div class="testament">New Testament · 27 books</div>
  <div class="bookgrid">{nt}</div>
</div>"""
    out = page(f"Table of Contents — {SITE_NAME}", body, active="toc",
               desc="Progress tracker for the MisterLibrarian Bible Project: every published chapter of "
                    "the fresh-from-the-Hebrew translation, and everything still ahead.")
    open(os.path.join(OUT, "toc.html"), "w", encoding="utf-8").write(out)


def build_index():
    latest = CHAPTERS[-1]
    cards = "".join(
        f'<a class="card" href="genesis-{num}.html"><div class="card-t">{book} {num}</div>'
        f'<div class="card-d">{teaser}</div></a>'
        for _, book, num, teaser in reversed(CHAPTERS))
    body = f"""<section class="hero">
  <h1>A new translation of the Bible,<br/>made one chapter at a time.</h1>
  <p>Welcome. This project translates the Bible into modern English directly from the original Hebrew —
  the Masoretic Text, reproduced verse-by-verse alongside the new rendering so every choice can be checked
  against the source. Beneath each chapter sit <strong>translator's notes, verse by verse</strong>,
  explaining each decision and comparing it against seven landmark versions: the NIV, the KJV, the
  Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the American Standard Version, and the New World
  Translation.</p>
  <p>No verse is smoothed over, no difficulty hidden: where the Hebrew puns, the translation puns or the
  notes confess it can't; where the text is uncertain or the manuscripts disagree, the notes say so plainly.
  The work advances one chapter per sitting — follow along from the beginning, or jump in at the newest
  chapter.</p>
  <div class="hero-cta">
    <a class="btn" href="genesis-1.html">Start at Genesis 1</a>
    <a class="btn btn-2" href="genesis-{latest[2]}.html">Newest: {latest[1]} {latest[2]}</a>
  </div>
</section>

<h2>Chapters — newest first</h2>
<div class="cardgrid">
{cards}
</div>

<h2>From the desk</h2>
<div class="cardgrid">
  <a class="card" href="ask-enoch.html"><div class="card-t">\U0001F4D6 Ask Mr. Librarian</div>
  <div class="card-d">Why isn't the Book of Enoch in this translation? A reader asked; here's the answer.</div></a>
  <a class="card" href="about.html"><div class="card-t">ℹ️ About the project</div>
  <div class="card-d">The method, the seven-version shelf, and what "essentially literal, modern register" means here.</div></a>
</div>"""
    out = page(SITE_NAME, body, active="home",
               desc="A fresh translation of the Bible into modern English, made from the original Hebrew "
                    "one chapter at a time, with verse-by-verse notes comparing seven landmark versions.")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)


def build_about():
    body = f"""<h1 class="pagetitle">About the project</h1>
<div class="panel prose">
  <p><strong>What this is.</strong> A fresh translation of the Bible into modern English, made one chapter
  at a time, directly from the <strong>Masoretic Text</strong> — the traditional Hebrew text of the Bible,
  as printed at <a href="https://mechon-mamre.org" rel="noopener">Mechon-Mamre</a>. The pointed Hebrew is
  reproduced verse-by-verse on every chapter page (a Hide&nbsp;Hebrew toggle is there for English-only
  reading), so every choice is checkable against the source.</p>
  <p><strong>The philosophy: essentially literal, in a natural modern register.</strong> Keep the Hebrew's
  word-plays, repetitions and structure wherever English can bear them; where it can't, say so in the notes
  rather than silently smoothing it over. Where the text is genuinely uncertain — a word that appears once
  in the whole Bible, a line the ancient manuscripts disagree on — the notes say that too, instead of
  pretending to a confidence the evidence doesn't support.</p>
  <p><strong>The seven-version shelf.</strong> Below every chapter, verse-by-verse translator's notes
  compare this translation's choices against seven landmark versions, chosen to span the full range of
  translation philosophy and history:</p>
  <div class="shelf">
    <div class="sv"><b>NIV</b> New International Version (2011) — committee, dynamic-leaning.</div>
    <div class="sv"><b>KJV</b> King James Version (1611) — the classic; built on Tyndale and Geneva.</div>
    <div class="sv"><b>DRB</b> Douay-Rheims (Challoner) — English of the Latin Vulgate; the historic Catholic text.</div>
    <div class="sv"><b>TLB</b> The Living Bible (1971) — Kenneth Taylor's one-man paraphrase.</div>
    <div class="sv"><b>GNV</b> Geneva Bible (1599) — the Reformation study Bible, before the KJV.</div>
    <div class="sv"><b>ASV</b> American Standard Version (1901) — famously literal.</div>
    <div class="sv"><b>NWT</b> New World Translation (1984) — the Watch Tower Society's translation.</div>
  </div>
  <p style="margin-top:14px"><strong>Honesty note.</strong> This translation is made by Claude (Anthropic's
  AI) working from the pointed Hebrew, guided and edited by Mr. Librarian. It is a study rendering, not the
  product of a translation committee — treat the notes as the argument for each choice, and check them
  against the shelf. Quotations from copyrighted versions are kept to brief phrases for comparison; the
  KJV, Geneva, Douay-Rheims, and ASV are public domain.</p>
  <p><strong>The name.</strong> A librarian's job is to catalogue, source, and compare — not to preach.
  That's the ethos here: every claim sourced, every alternative shown, disagreements between traditions
  presented rather than settled.</p>
</div>"""
    out = page(f"About — {SITE_NAME}", body, active="about",
               desc="How the MisterLibrarian Bible Project works: translated from the Masoretic Hebrew, "
                    "essentially literal in a modern register, compared against seven landmark versions.")
    open(os.path.join(OUT, "about.html"), "w", encoding="utf-8").write(out)


def build_ask_enoch():
    body = """<h1 class="pagetitle">\U0001F4D6 Ask Mr. Librarian</h1>
<h2 style="margin-top:4px">Why isn't the Book of Enoch in this translation?</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>"Why did you not include the Book of Enoch in your translation of the Bible?"</p>
</div>

<div class="panel prose">
  <p>This project's source text has been the <strong>Masoretic Hebrew Bible</strong> — the Tanakh, pointed
  Hebrew and all — since the very first line of the very first chapter. The Book of Enoch was never part of
  that corpus to begin with. There's no Masoretic Hebrew text of Enoch to translate from; it doesn't survive
  complete in Hebrew at all. The only complete text is in Ge'ez (classical Ethiopic), with fragments of the
  original Aramaic and some Greek turning up among the Dead Sea Scrolls and elsewhere. So leaving it out
  wasn't a judgment call about whether it belongs — it was outside this project's stated method before the
  question of canon ever came up.</p>
  <p>The broader canon question is genuinely interesting, though. Enoch isn't in the Jewish canon, the
  Protestant 66-book list this project's Table of Contents is built around, or even the Catholic
  Deuterocanon (the extra books the Douay-Rheims tradition includes — Tobit, Judith, Maccabees, and so on —
  don't include it either). The one tradition where it actually <em>is</em> canonical scripture is the
  <strong>Ethiopian Orthodox Tewahedo Church</strong>, which is often the detail people miss — it's not that
  Enoch was universally rejected, it's that one major, ancient Christian tradition kept it and the others
  didn't.</p>
  <p>And it wasn't obscure or forgotten in the meantime. Multiple Aramaic copies of it turned up at Qumran
  among the Dead Sea Scrolls, so it was clearly in real circulation in Second Temple Judaism. And the New
  Testament itself references it — the epistle of <strong>Jude, verses 14–15</strong>, cites "Enoch, the
  seventh from Adam" prophesying judgment, language that traces straight back to Enoch's text. So whatever
  the reasons different communities eventually settled their canons the way they did (and scholars don't
  agree on one tidy explanation — theories range from its pseudepigraphal authorship claim, to discomfort
  with its angelology and cosmology, to it simply falling outside the criteria later rabbinic and church
  authorities used), it was clearly read and taken seriously by people in a position to know it well.</p>
  <p>Two places in this translation touch Enoch's world directly: the man himself — "Enoch walked with God,
  and then he was not there, for God took him" — appears in <a href="genesis-5.html#v5-21">Genesis
  5:21–24</a>, the two-verse mystery from which the later book grew; and the "sons of God" episode the Book
  of Enoch expands so dramatically opens <a href="genesis-6.html#v6-1">Genesis 6</a>.</p>
  <p>If this project ever extends to it, that's a real possibility — but it would be a different kind of
  undertaking than the Hebrew chapters posted so far, since it means working from Ge'ez and the
  Aramaic/Greek fragments instead of pointed Masoretic Hebrew, and being upfront that it sits outside the
  Tanakh and the Protestant canon this translation has otherwise followed.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">Have a question about the project, a translation choice, or
  what's coming next? Reader questions are exactly how this series grows — the next one could be yours.</p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Ask Mr. Librarian: the Book of Enoch — {SITE_NAME}", body, active="ask",
               desc="Why the Book of Enoch isn't part of this Bible translation: the Masoretic source "
                    "text, the canon question, the Ethiopian exception, and the Dead Sea Scrolls.")
    open(os.path.join(OUT, "ask-enoch.html"), "w", encoding="utf-8").write(out)


def build_contact():
    body = f"""<h1 class="pagetitle">✉️ Ask Mr. Librarian a question</h1>
<p class="lede">A question about the project, a translation choice you'd argue with, a chapter request,
or something you've always wondered about the text — send it in. Good questions become
<a href="ask-enoch.html">Ask Mr. Librarian</a> posts (anonymously unless you say otherwise), and reader
questions are exactly how that series grows.</p>

<div class="panel">
  <form action="{FORM_ENDPOINT}" method="POST" class="askform">
    <input type="hidden" name="_subject" value="Ask Mr. Librarian — a question from the site"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="{SITE_URL}/thanks.html"/>
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>
    <label>Your name <span class="opt">(optional)</span>
      <input type="text" name="name" placeholder="However you'd like to be credited — or leave blank"/>
    </label>
    <label>Your email <span class="opt">(optional — only needed if you'd like a reply)</span>
      <input type="email" name="email" placeholder="you@example.com"/>
    </label>
    <label>Your question <span class="req">(required)</span>
      <textarea name="question" required rows="7"
        placeholder="Ask anything — a verse, a word choice, a comparison between versions, what's coming next…"></textarea>
    </label>
    <button class="btn" type="submit">Send to the librarian's desk</button>
    <p class="formnote">Sending shows a quick captcha (keeps the robots out of the library), then brings
    you back here. Nothing is posted publicly — questions go straight to Mr. Librarian's desk.</p>
  </form>
</div>"""
    out = page(f"Ask a question — {SITE_NAME}", body, active="contact",
               desc="Send Mr. Librarian a question about the translation, a verse, or the project — "
                    "good questions become Ask Mr. Librarian posts.")
    open(os.path.join(OUT, "contact.html"), "w", encoding="utf-8").write(out)


def build_thanks():
    body = """<h1 class="pagetitle">📬 It's on the librarian's desk</h1>
<div class="panel prose">
  <p><strong>Your question is in.</strong> Thank you — reader questions are the lifeblood of the
  <a href="ask-enoch.html">Ask Mr. Librarian</a> series, and every one gets read. If yours becomes a post,
  it will appear anonymously unless you asked otherwise; if you left an email, you may get a reply
  directly.</p>
  <p>Meanwhile, the shelves are open: the <a href="toc.html">Table of Contents</a> has every chapter
  published so far.</p>
</div>"""
    out = page(f"Question received — {SITE_NAME}", body,
               desc="Your question is on Mr. Librarian's desk.")
    open(os.path.join(OUT, "thanks.html"), "w", encoding="utf-8").write(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    args = ap.parse_args()
    chapters = extract_source(args.source)
    build_chapter_pages(chapters)
    build_toc()
    build_index()
    build_about()
    build_ask_enoch()
    build_contact()
    build_thanks()
    print(f"built {len(CHAPTERS)} chapter pages + index/toc/about/ask-enoch/contact/thanks from {args.source}")


if __name__ == "__main__":
    main()

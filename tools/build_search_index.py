#!/usr/bin/env python3
"""Build / refresh the m8k.io site-wide search index (Cloudflare D1 "m8k-search").

Every public page listed in this repo's sitemaps (the Bible project, Dear Mr.
Librarian, and the five blogs on their m8k.io subdomains) becomes one row:
title, description, main text (the page's <article>, else <main>, else <body>
minus nav/header/footer/scripts), publication, kind and language. Only pages
whose content hash changed are uploaded, and pages that left the sitemaps are
deleted, so a routine publish writes a handful of rows, not six thousand.

    python3 tools/build_search_index.py            # incremental refresh (remote D1)
    python3 tools/build_search_index.py --dry-run  # extract + diff, upload nothing
    python3 tools/build_search_index.py --full     # re-upload every page

Needs wrangler (Mac login, or CLOUDFLARE_API_TOKEN with D1 edit in CI).
Schema: search/schema.sql (applied idempotently on every run).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = "m8k-search"
BODY_MAX = 12000          # characters of main text kept per page
BATCH = 250               # rows per uploaded SQL file

# Public host → (repo folder, publication). The Bible site's sections are
# split further by path below.
HOSTS = {
    "mistertranslation.com": ("", "bible"),
    "ledger.m8k.io": ("finance", "ledger"),
    "notebook.m8k.io": ("notebook", "notebook"),
    "regimen.m8k.io": ("health", "regimen"),
    "abroad.m8k.io": ("travel", "abroad"),
    "west.m8k.io": ("west", "west"),
}
LEDGER_BOARDS = {"board.html", "bitcoin.html", "cebe.html", "crypto-screener.html",
                 "treasuries.html", "crypto.html", "humanity.html"}
PAGE_NAMES = {"index.html", "about.html", "ask.html", "thanks.html", "write.html",
              "bookmarked.html", "es.html", "about.es.html", "ask.es.html",
              "thanks.es.html", "disclaimer.html", "disclaimer.es.html", "search.html",
              "privacy.html", "contact.html", "contact.es.html", "tags.html"}
CHAPTER_RE = re.compile(r"^(?:\d-)?[a-z]+(?:-[a-z]+)*-\d+(?:\.es)?\.html$")
LOC_RE = re.compile(r"<url>\s*<loc>\s*([^<\s]+)\s*</loc>(?:\s*<lastmod>\s*([^<\s]+)\s*</lastmod>)?", re.S)
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript",
             "svg", "button", "select", "template", "iframe"}


class _Text(HTMLParser):
    """Collects title, meta description and the main text of one page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.descr = ""
        self._in_title = False
        self._skip = 0
        self._stack = []          # 'article' / 'main' depth markers
        self.parts = {"article": [], "main": [], "body": []}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.descr = self.descr or (a.get("content") or "")
        if tag in SKIP_TAGS:
            self._skip += 1
        if tag in ("article", "main"):
            self._stack.append(tag)
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "blockquote", "td", "br", "div"):
            self._emit(" ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1
        if tag in ("article", "main") and tag in self._stack:
            self._stack.remove(tag)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if not self._skip:
            self._emit(data)

    def _emit(self, s):
        self.parts["body"].append(s)
        for t in set(self._stack):
            self.parts[t].append(s)

    def main_text(self):
        for k in ("article", "main", "body"):
            t = re.sub(r"\s+", " ", "".join(self.parts[k])).strip()
            if len(t) > 80 or k == "body":
                return t
        return ""


def _clean_title(t):
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    segs = [s for s in t.split(" — ")]
    return " — ".join(segs[:-1]) if len(segs) > 1 else t


def _classify(host, path):
    folder, pub = HOSTS[host]
    name = path.rsplit("/", 1)[-1] or "index.html"
    lang = "es" if name.endswith(".es.html") or path.startswith("es") else "en"
    if pub == "bible":
        first = path.split("/", 1)[0] if "/" in path else ""
        if first == "ask":
            return "ask", ("page" if name in PAGE_NAMES or name.startswith("tag-") else "answer"), lang
        if first in ("dict", "ency", "atlas", "routes", "v"):
            return "bible", "reference", lang
        if name.startswith("book-"):
            return "bible", "book", lang
        if CHAPTER_RE.match(name):
            return "bible", "chapter", lang
        return "bible", "page", lang
    if pub == "ledger" and name in LEDGER_BOARDS or (pub == "ledger" and name.startswith("money-worldwide")):
        return pub, "board", lang
    if name in PAGE_NAMES or name.startswith("tag-"):
        return pub, "page", lang
    return pub, "post", lang


def collect():
    docs, missing = {}, 0
    for sm in [os.path.join(ROOT, "sitemap.xml")] + sorted(glob.glob(os.path.join(ROOT, "*", "sitemap.xml"))):
        for url, lastmod in LOC_RE.findall(open(sm, encoding="utf-8").read()):
            m = re.match(r"https://([^/]+)/(.*)$", url)
            if not m or m.group(1) not in HOSTS:
                continue
            host, path = m.group(1), m.group(2)
            folder = HOSTS[host][0]
            rel = path or "index.html"
            if rel.endswith("/"):
                rel += "index.html"
            f = os.path.join(ROOT, folder, rel) if folder else os.path.join(ROOT, rel)
            if not os.path.isfile(f):
                missing += 1
                continue
            p = _Text()
            try:
                p.feed(open(f, encoding="utf-8", errors="replace").read())
            except Exception:
                continue
            title = _clean_title(p.title) or rel
            descr = re.sub(r"\s+", " ", html.unescape(p.descr)).strip()
            body = p.main_text()[:BODY_MAX]
            pub, kind, lang = _classify(host, path)
            h = hashlib.sha1(f"{pub}|{kind}|{lang}|{title}|{descr}|{body}".encode()).hexdigest()
            docs[url] = dict(url=url, pub=pub, kind=kind, lang=lang, title=title,
                             descr=descr, body=body, date=(lastmod or "")[:10], hash=h)
    return docs, missing


def _wrangler(args, capture=True):
    cmd = ["npx", "--yes", "wrangler@4"] if not _has("wrangler") else ["wrangler"]
    r = subprocess.run(cmd + args, cwd=ROOT, capture_output=capture, text=True)
    if r.returncode != 0:
        sys.stderr.write((r.stdout or "") + (r.stderr or ""))
        raise SystemExit(f"wrangler failed: {' '.join(args[:4])}")
    return r.stdout


def _has(exe):
    return any(os.access(os.path.join(p, exe), os.X_OK) for p in os.environ.get("PATH", "").split(os.pathsep))


def _q(s):
    return "'" + s.replace("'", "''") + "'"


def remote_hashes():
    out = _wrangler(["d1", "execute", DB, "--remote", "--json", "--command", "SELECT url, hash FROM docs"])
    data = json.loads(out)
    rows = data[0]["results"] if data and "results" in data[0] else []
    return {r["url"]: r["hash"] for r in rows}


def run_sql_file(statements):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as fh:
        fh.write("\n".join(statements) + "\n")
        path = fh.name
    try:
        _wrangler(["d1", "execute", DB, "--remote", "--yes", "--file", path])
    finally:
        os.unlink(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()

    docs, missing = collect()
    kinds = {}
    for d in docs.values():
        kinds[(d["pub"], d["kind"])] = kinds.get((d["pub"], d["kind"]), 0) + 1
    print(f"extracted {len(docs)} pages ({missing} sitemap URLs had no local file)")
    for k in sorted(kinds):
        print(f"  {k[0]:9s} {k[1]:10s} {kinds[k]}")
    if a.dry_run:
        return

    run_sql_file([open(os.path.join(ROOT, "search", "schema.sql"), encoding="utf-8").read()])
    have = {} if a.full else remote_hashes()
    changed = [d for u, d in docs.items() if have.get(u) != d["hash"]]
    gone = [u for u in have if u not in docs]
    print(f"to upload: {len(changed)}   to delete: {len(gone)}")

    cols = ("url", "pub", "kind", "lang", "title", "descr", "body", "date", "hash")
    for i in range(0, len(changed), BATCH):
        stm = []
        for d in changed[i:i + BATCH]:
            vals = ", ".join(_q(d[c]) for c in cols)
            stm.append(f"INSERT INTO docs ({', '.join(cols)}) VALUES ({vals}) "
                       f"ON CONFLICT(url) DO UPDATE SET pub=excluded.pub, kind=excluded.kind, "
                       f"lang=excluded.lang, title=excluded.title, descr=excluded.descr, "
                       f"body=excluded.body, date=excluded.date, hash=excluded.hash;")
        run_sql_file(stm)
        print(f"  uploaded {min(i + BATCH, len(changed))}/{len(changed)}")
    for i in range(0, len(gone), 200):
        run_sql_file([f"DELETE FROM docs WHERE url IN ({', '.join(_q(u) for u in gone[i:i + 200])});"])
    print("search index up to date")


if __name__ == "__main__":
    main()

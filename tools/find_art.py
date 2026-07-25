#!/usr/bin/env python3
"""Find public-domain art for the chapter being translated, and prepare it for the page.

Michael's standing instruction (2026-07-25): "going forward, why don't we just add a
search for art really relevant to the chapter we're building out. So as we go forward,
we can build out slowly." This is that search, so the per-chapter step is cheap.

    python3 tools/find_art.py search "Rembrandt Christ in the Storm"
    python3 tools/find_art.py search "Dore Jeremiah potter" --limit 8
    python3 tools/find_art.py add "File:Foo.jpg" rembrandt-storm-galilee.jpg --slug jer18

`search` queries Wikimedia Commons and prints, for each candidate, the LICENCE, the
artist, the date and the pixel size -- the four things needed to decide. It never
downloads anything.

`add` fetches one file, writes a web-sized EXIF-stripped copy into img/art/, and
archives the full-resolution original to S3 (blobs/chapter_art/). It then prints a
ready-to-paste CHAPTER_ART stub with the real metadata filled in.

WHY THE SPLIT: the published copy must be committed to this repo, because GitHub
Pages can only serve what it hosts, and our S3 bucket is private -- it holds tax,
medical and financial records, so nothing in it may be made publicly readable. The
original goes to S3 so the full-quality file is never lost. Same live-in-git /
durable-in-S3 split as tools/travel_archive.py.

⚠ LICENCE RULE, AND IT IS THE OPPOSITE OF A STATUE. For a FLAT 2-D painting a
faithful photographic reproduction attracts no new copyright in the US (Bridgeman v.
Corel; Commons tags these "PD-Art"), so a photo of a public-domain painting is itself
public domain. For a 3-D object -- a stele, a statue -- the artefact may be ancient and
out of copyright while the PHOTOGRAPH carries its own fresh copyright, and then the
photographer's licence is the one that governs. Read the licence off the file page;
never infer it from the artist's death date.
⚠ Some European museums assert rights over reproductions anyway. The US position
governs a US-hosted site, but say so on the page rather than pretending it is settled.

⚠ Be polite to Wikimedia: upload.wikimedia.org rate-limits (429) if you pull several
large originals back to back. `add` handles one file at a time, with backoff.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(REPO, "img", "art")
BLOB_NAME = "chapter_art"
MAX_EDGE = 1200          # long edge of the published copy, in px
JPEG_QUALITY = 82
UA = {"User-Agent": "MisterLibrarianBibleProject/1.0 (mistertranslation.com; "
                    "educational, non-commercial)"}

MSTR_PATHS = [
    os.environ.get("MSTR_TRADER_DIR", ""),
    os.path.expanduser("~/projects/mstr-trader"),
    os.path.expanduser("~/mstr-trader"),
]


def store():
    """market_data_store from the mstr-trader checkout, or a clear explanation."""
    for p in MSTR_PATHS:
        if p and os.path.isfile(os.path.join(p, "market_data_store.py")):
            if p not in sys.path:
                sys.path.insert(0, p)
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import market_data_store as mds
            if not mds.enabled():
                sys.exit("S3 store present but not configured (check ~/.mstr-trader/backup.env).")
            return mds
    sys.exit("Could not find market_data_store.py -- set MSTR_TRADER_DIR.")


def _api(params):
    params.update(format="json", action="query")
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
        return json.load(r)


def _plain(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", str(x or ""))).strip()


def _meta(titles):
    """{title: {...}} licence/artist/date/size/url for up to 50 Commons files."""
    if not titles:
        return {}
    r = _api({"titles": "|".join(titles), "prop": "imageinfo",
              "iiprop": "extmetadata|url|size"})
    out = {}
    for pg in r.get("query", {}).get("pages", {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})

        def g(k):
            return _plain(md.get(k, {}).get("value"))

        # Commons appends a QuickStatements clause to the date; keep the human part.
        date = re.split(r"date QS:", g("DateTimeOriginal"))[0].strip()
        out[pg.get("title", "?")] = {
            "license": g("LicenseShortName") or g("UsageTerms"),
            "artist": g("Artist"),
            "date": date,
            "credit": g("Credit"),
            "width": ii.get("width"), "height": ii.get("height"),
            "size": ii.get("size"), "url": ii.get("url"),
            "descurl": ii.get("descriptionurl") or
                       ("https://commons.wikimedia.org/wiki/" +
                        urllib.parse.quote(pg.get("title", "").replace(" ", "_"))),
        }
    return out


def _looks_free(lic):
    low = (lic or "").lower()
    return any(k in low for k in ("public domain", "pd-", "cc0", "cc by", "cc-by"))


def cmd_search(args):
    r = _api({"list": "search", "srsearch": args.query, "srnamespace": 6,
              "srlimit": args.limit})
    titles = [h["title"] for h in r.get("query", {}).get("search", [])]
    if not titles:
        print("no files matched -- try the painter's name, or the scene in plain words")
        return
    meta = _meta(titles)
    for t in titles:
        m = meta.get(t, {})
        lic = m.get("license") or "?"
        flag = "OK  " if _looks_free(lic) else "CHECK"
        print(f"\n{flag} {t}")
        print(f"      licence : {lic}")
        print(f"      artist  : {(m.get('artist') or '?')[:72]}")
        print(f"      date    : {m.get('date') or '?'}")
        if m.get("width"):
            print(f"      pixels  : {m['width']}x{m['height']}  "
                  f"({(m.get('size') or 0)/1e6:.1f} MB)")
        print(f"      page    : {m.get('descurl')}")
    print("\n⚠ Read the licence above off the file page -- never infer it from the "
          "artist's death date. A 2-D painting's reproduction is PD-Art; a photo of a "
          "3-D object carries the photographer's own copyright.")


def cmd_add(args):
    title = args.title if args.title.startswith("File:") else "File:" + args.title
    meta = _meta([title]).get(title)
    if not meta or not meta.get("url"):
        sys.exit(f"could not resolve {title!r} on Commons")
    if not _looks_free(meta["license"]):
        sys.exit(f"REFUSING: licence reads {meta['license']!r}, which is not clearly "
                 f"public domain / CC0 / CC BY. Nothing was downloaded.")
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is needed to make the web-sized copy (pip install pillow)")

    data = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(meta["url"], headers=UA), timeout=240) as r:
                data = r.read()
            break
        except Exception as e:                                  # noqa: BLE001
            wait = 8 * (attempt + 1)
            print(f"   {type(e).__name__} -- backing off {wait}s", file=sys.stderr)
            time.sleep(wait)
    if data is None:
        sys.exit("download failed after retries (Wikimedia rate-limits large originals)")

    os.makedirs(ART_DIR, exist_ok=True)
    tmp = os.path.join("/tmp", args.filename)
    open(tmp, "wb").write(data)
    im = Image.open(tmp).convert("RGB")       # convert() drops EXIF along with the mode
    w, h = im.size
    if max(w, h) > MAX_EDGE:
        sc = MAX_EDGE / max(w, h)
        im = im.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
    dst = os.path.join(ART_DIR, args.filename)
    im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    mds = store()
    key = args.filename.rsplit(".", 1)[0] + "-original.jpg"
    ok = mds.put_blob(BLOB_NAME, key, data, "image/jpeg")

    print(f"\nweb copy  : img/art/{args.filename}  "
          f"{os.path.getsize(dst)//1024} KB  {im.size[0]}x{im.size[1]}")
    print(f"original  : {len(data)/1e6:.1f} MB -> S3 blobs/{BLOB_NAME}/{key}  ok={ok}")
    print("\n--- paste into library_data.CHAPTER_ART, filling in the prose ---")
    print(f'''    "{args.slug or 'SLUG'}": [dict(
        file="{args.filename}",
        title="",            title_es="",
        artist="{meta.get('artist', '')}",
        year="{meta.get('date', '')}",
        location="",         location_es="",
        alt="",
        note="",             note_es="",
        license="{meta.get('license', '')}",
        source_url="{meta.get('descurl', '')}",
    )],''')
    print("⚠ alt text is required and is not optional politeness -- it is what a "
          "screen-reader user gets instead of the painting.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search Commons and print licences")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=5)
    s.set_defaults(func=cmd_search)
    a = sub.add_parser("add", help="download one file, publish a web copy, archive the original")
    a.add_argument("title", help='Commons file title, e.g. "File:Foo.jpg"')
    a.add_argument("filename", help="local name, e.g. rembrandt-storm-galilee.jpg")
    a.add_argument("--slug", help="chapter slug, for the pasteable stub")
    a.set_defaults(func=cmd_add)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

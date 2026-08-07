#!/usr/bin/env python3
"""Cache company logos into finance/img/ so the board makes no third-party requests.

    python3 tools/finance_logos.py           # fetch anything missing
    python3 tools/finance_logos.py --force   # re-fetch everything

The About page promises "no tracking beyond an anonymous, cookie-less page counter."
An <img> pointing at Google's favicon service would quietly break that on every page
load — it hands a third party the reader's IP and referrer for free. So the logos are
fetched ONCE, here, and committed; the rendered page only ever loads from our own
origin.

Fetching from Google's s2 service is fine — that request is made by this script, on a
developer's machine or a CI runner, not by a reader. Using a company's mark to
identify that company in a comparative ranking is ordinary nominative use, the same
thing every market-cap site does.

Anything that fails to download is simply absent, and build_finance.py falls back to a
coloured monogram. The board never depends on a logo existing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = os.path.join(ROOT, "source", "finance", "asset_board.json")
IMGDIR = os.path.join(ROOT, "finance", "img")

# Two sources, tried in order. Neither covers everything: Google 404s on
# berkshirehathaway.com, and returns a generic placeholder for tsmc.com and visa.com
# that DuckDuckGo serves properly. Whatever both miss falls through to a monogram.
SOURCES = [
    ("google", "https://www.google.com/s2/favicons?domain={domain}&sz=128"),
    ("ddg",    "https://icons.duckduckgo.com/ip3/{domain}.ico"),
]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"

# A favicon service answers *something* for a domain it cannot resolve — usually a
# tiny generic globe, and DuckDuckGo serves one with a 404 status. Anything under
# this is treated as a miss so we fall back to a monogram rather than shipping a
# row of identical grey globes.
MIN_BYTES = 400


def slug(domain):
    """apple.com -> apple. Must match _logo_slug() in build_finance.py."""
    return domain.split(".")[0].lower()


def _try(url):
    """Raw bytes from one source, or None. Never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            blob = resp.read()
    except Exception:
        return None
    return blob if len(blob) >= MIN_BYTES else None


def fetch(domain, dest, force=False):
    if os.path.exists(dest) and not force:
        return "kept"
    for label, tmpl in SOURCES:
        blob = _try(tmpl.format(domain=domain))
        if blob:
            tmp = dest + ".tmp"
            with open(tmp, "wb") as fh:
                fh.write(blob)
            os.replace(tmp, dest)
            return f"{len(blob)//1024 or 1} KB ({label})"
    print(f"  ! {domain}: no source had it — monogram fallback", file=sys.stderr)
    return "monogram"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true", help="re-fetch logos already present")
    args = ap.parse_args()

    if not os.path.exists(BOARD):
        sys.exit("no source/finance/asset_board.json — run tools/fetch_asset_board.py first")

    with open(BOARD, encoding="utf-8") as fh:
        board = json.load(fh)

    os.makedirs(IMGDIR, exist_ok=True)
    domains = sorted({a["domain"] for a in board.get("assets", []) if a.get("domain")})
    print(f"{len(domains)} logo(s) -> finance/img/")
    for d in domains:
        dest = os.path.join(IMGDIR, f"{slug(d)}.png")
        print(f"  {slug(d):<20} {fetch(d, dest, args.force)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tell IndexNow (Bing, Yandex, Seznam, Naver — and through Bing, DuckDuckGo
and ChatGPT search) which mistertranslation.com pages are new or changed.

The key file has sat at the repo root since Bing verification
(`2078cdc5e8e74ac79f60518ddf2f9b03.txt`) but nothing ever pinged with it, so
Bing found pages only by crawling on its own schedule. This is the ping.

Only URLs that appear in one of the site's sitemaps are ever sent — that set
is exactly "pages we want indexed", so the noindexed /dict/ /ency/ /atlas/
stubs, the /v/ verse stubs and drafts can never be submitted by accident.

    python3 tools/indexnow_ping.py --changed <old-sha> <new-sha>   # what CI runs
    python3 tools/indexnow_ping.py --all                            # every sitemap URL
    python3 tools/indexnow_ping.py --all --dry-run                  # list, send nothing

Run by .github/workflows/indexnow.yml on every push to main. Pushes made with
the workflow GITHUB_TOKEN (the board refresh, the draft-publish button) do not
trigger other workflows, so those never ping; a later push's diff won't cover
them either. Standard library only. Exits 0 on a network failure (a ping is a
hint to a search engine, never something worth failing a deploy over).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HOST = "mistertranslation.com"
SITE = f"https://{HOST}/"
KEY = "2078cdc5e8e74ac79f60518ddf2f9b03"
ENDPOINT = "https://api.indexnow.org/indexnow"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def sitemap_urls():
    urls = set()
    for path in [os.path.join(ROOT, "sitemap.xml"),
                 *glob.glob(os.path.join(ROOT, "*", "sitemap.xml"))]:
        with open(path, encoding="utf-8") as f:
            urls.update(_LOC_RE.findall(f.read()))
    return urls


def path_urls(rel):
    """The URL(s) a repo-relative file is served at: `x/index.html` is also `x/`."""
    out = [SITE + rel]
    if rel == "index.html":
        out.append(SITE)
    elif rel.endswith("/index.html"):
        out.append(SITE + rel[: -len("index.html")])
    return out


def changed_urls(old, new, allowed):
    if not old or set(old) == {"0"}:      # first push of a branch: nothing to diff
        return []
    names = subprocess.run(
        ["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=AM", old, new],
        check=True, capture_output=True, text=True).stdout.split()
    urls = []
    for rel in names:
        if rel.endswith(".html"):
            urls += [u for u in path_urls(rel) if u in allowed]
    return sorted(set(urls))


def ping(urls):
    for i in range(0, len(urls), 10000):          # IndexNow's per-request cap
        body = json.dumps({"host": HOST, "key": KEY,
                           "keyLocation": f"{SITE}{KEY}.txt",
                           "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"IndexNow: {r.status} for {len(urls[i:i + 10000])} URL(s)")
        except urllib.error.HTTPError as e:
            # 202 = accepted, key not yet validated (normal on a first ping);
            # 403 = key file not reachable; 422 = URL not on this host.
            print(f"IndexNow: HTTP {e.code} {e.reason}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"IndexNow: network error, not sent: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--changed", nargs=2, metavar=("OLD", "NEW"))
    g.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    allowed = sitemap_urls()
    urls = sorted(allowed) if a.all else changed_urls(*a.changed, allowed)
    if not urls:
        print("IndexNow: nothing to send")
        return
    for u in urls[:20]:
        print("  " + u)
    if len(urls) > 20:
        print(f"  … and {len(urls) - 20} more")
    if not a.dry_run:
        ping(urls)


if __name__ == "__main__":
    main()

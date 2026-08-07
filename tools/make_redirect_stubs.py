#!/usr/bin/env python3
"""Leave a redirect stub where the Coldcard entry used to live.

GitHub Pages serves static files and cannot issue a 301, so this is the only
redirect available. Written once, by hand, rather than taught to build_travel.py:
this is a single historical move, not an ongoing feature, and giving the travel
builder a redirects subsystem for one entry would be machinery nobody maintains.

If entries move between publications often enough that this becomes a chore,
THAT is the moment to build it into blogkit — not before.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)          # blogkit lives at the repo root, not in tools/

import blogkit  # noqa: E402

OUT = os.path.join(ROOT, "travel")

# Keep this list. It is the record of what moved and where — the only place a
# future reader can find out why /travel/coldcard-bitkey-security.html is a stub.
MOVED = [
    {
        "old": "coldcard-bitkey-security.html",
        "to": "https://mistertranslation.com/finance/coldcard-bitkey-security.html",
        "title": "A Twenty-Five-Minute Window, and Why I Split the Key",
        "note": "It now lives on The Librarian's Ledger, where the money writing is.",
    },
]


def main():
    for m in MOVED:
        path = os.path.join(OUT, m["old"])
        html = blogkit.redirect_stub(m["to"], title=m["title"], note=m["note"])
        io.open(path, "w", encoding="utf-8").write(html)
        print("stub: travel/%s -> %s" % (m["old"], m["to"]))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read one WOL chapter through Michael's own Safari, for the editions with no other source.

    python3 tools/wol_from_safari.py "1 Kings" 12 tnm1987 tnm2019

Since 2026-11-05 wol.jw.org answers scripts with a bot challenge, and tools/shelf_text.py
can no longer fetch a chapter that is not already archived. Michael reads WOL in Safari as
an ordinary reader. With his go-ahead, and with WOL open there, this opens a temporary
background tab, reads the page, closes that tab, and stores it through shelf_text's normal
path, so its edition guard and archive apply.

ONE CHAPTER A CALL, ONLY AT HIS DIRECTION. This is a person reading the chapter being
translated. It is not a way to fill the archive, so never loop it over a book. It needs
Safari's Develop > Allow JavaScript from Apple Events, and it never touches his other tabs.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shelf_text as ST  # noqa: E402

SCRIPT = r'''
on run argv
    set theURL to item 1 of argv
    tell application "Safari"
        set t to make new tab at end of tabs of front window with properties {URL:theURL}
        set html to ""
        repeat 30 times
            delay 1
            try
                set pageState to do JavaScript "document.readyState + '|' + (document.querySelector('article') ? 'A' : '-')" in t
                if pageState is "complete|A" then exit repeat
            end try
        end repeat
        try
            set html to do JavaScript "document.documentElement.outerHTML" in t
        end try
        close t
    end tell
    return html
end run
'''


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("book")
    ap.add_argument("chapter", type=int)
    ap.add_argument("versions", nargs="+", choices=sorted(ST.EDITIONS))
    a = ap.parse_args()
    book_no, name = ST.resolve(a.book, a.chapter)
    bad = 0
    for version in a.versions:
        url = ST.url_for(version, book_no, a.chapter)
        out = subprocess.run(["osascript", "-e", SCRIPT, url], capture_output=True, timeout=60)
        raw = out.stdout.decode("utf-8", "replace")
        if out.returncode or len(raw) < ST.MIN_PAGE_BYTES:
            print(f"[{version}] Safari returned nothing usable: {out.stderr.decode()[:160]}")
            bad += 1
            continue
        pub, verses = ST.parse(raw)
        want = ST.EDITIONS[version][3]
        if pub != want or not verses:
            print(f"[{version}] REFUSED: page says {pub}, wanted {want}, {len(verses)} verses")
            bad += 1
            continue
        ST.store(version, book_no, a.chapter, raw)
        print(f"[{version}] stored {ST.blob_name(version, book_no, a.chapter)}: {len(verses)} verses")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

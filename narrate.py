#!/usr/bin/env python3
"""Record the narration of Mister Translation chapters, once, with Cloudflare's voice (MeloTTS), and keep it in R2.

How it works (AR-156): for each chapter page this reads the verses, sends them in pieces of about 1,000 characters to Micwyn's
narrate endpoint (which speaks them with MeloTTS and answers with WAV), joins and compresses the pieces to a small MP3 with ffmpeg,
uploads the MP3 (kept at https://micwyn.com/narration/<lang>/<slug>.mp3) and notes the chapter in audio/narrated.json. build.py reads
that file: a chapter with a recording gets a Listen button that plays it; a chapter without one has no Listen button.

    python3 narrate.py --only genesis-1             # one chapter (English)
    python3 narrate.py --limit 20                   # the next 20 chapters that have no recording
    python3 narrate.py                              # every chapter that has none (about 640 English chapters, under a dollar)
    python3 narrate.py --lang es                    # the Spanish editions (the *.es.html pages)
    python3 narrate.py --only genesis-1 --force     # record it again
    python3 narrate.py --dry-run                    # say what would be recorded

Needs: ffmpeg (brew install ffmpeg), and the Scribe key in the macOS Keychain (service agorai-scribe-api-key, account scribe), the same
key Claude posts to Micwyn with. The key is read from the Keychain each run and never printed or written anywhere.
Each recorded English chapter page gets its Listen button added in place (a full python3 build.py does the same for every recorded chapter).
Then: git add audio/narrated.json *.html && git commit && git push.
"""
import argparse, glob, html as _html, json, os, re, subprocess, sys, tempfile, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://micwyn.com/api/v1/narrate"
MANIFEST = os.path.join(HERE, "audio", "narrated.json")
CHUNK_CHARS = 1000
SPEED = 0.88          # 1.0 is the voice as it speaks; below 1 slows it down without changing its pitch (ffmpeg atempo). Michael asked for slower, 2026-11-01.
PAUSE_HEAD, PAUSE_PIECE = 0.9, 0.5      # seconds of quiet after the chapter heading, and between pieces
UA = "curl/8.7.1"        # Cloudflare refuses Python's default agent

HEAD = {"en": "{book}, chapter {num}.", "es": "{book}, capítulo {num}."}
VERSE_CLASS = {"en": "eng", "es": "esp"}
TAG = re.compile(r"<[^>]+>")


def key():
    out = subprocess.run(["security", "find-generic-password", "-a", "scribe", "-s", "agorai-scribe-api-key", "-w"], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("Couldn't read the Scribe key from the Keychain.")
    return out.stdout.strip()


def load_manifest():
    try:
        return json.load(open(MANIFEST, encoding="utf-8"))
    except (OSError, ValueError):
        return {"en": [], "es": []}


def save_manifest(m):
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    tmp = MANIFEST + ".tmp"
    json.dump({k: sorted(set(v)) for k, v in m.items()}, open(tmp, "w", encoding="utf-8"), indent=0)
    os.replace(tmp, MANIFEST)


def pages(lang):
    """(slug, path) for every chapter page of the language."""
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, "*.es.html" if lang == "es" else "*.html"))):
        name = os.path.basename(p)
        if lang == "en" and name.endswith(".es.html"):
            continue
        slug = name[: -len(".es.html" if lang == "es" else ".html")]
        out.append((slug, p))
    return out


def chapter(path, lang):
    """(spoken heading, [verse texts]) for a chapter page, or None if it isn't one."""
    page = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", page, re.S)
    m = re.match(r"\s*(.+?)\s+(\d+)\s+—", _html.unescape(title.group(1))) if title else None
    if not m:
        return None
    cls = VERSE_CLASS[lang]
    verses = []
    for raw in re.findall(r'id="v(?:\d+-)?\d+"[^>]*>.*?<div class="%s">(.*?)</div>' % cls, page, re.S):
        raw = re.sub(r'<a class="notelink".*?</a>', "", raw, flags=re.S)
        t = re.sub(r"\s+", " ", _html.unescape(TAG.sub("", raw))).strip()
        if t:
            verses.append(t)
    if len(verses) < 2:
        return None
    return HEAD[lang].format(book=m.group(1), num=m.group(2)), verses


def pieces(head, verses):
    """The heading as its own piece, then the verses in pieces of at most CHUNK_CHARS, cut between verses."""
    out, cur = [head], ""
    for v in verses:
        if len(cur) + 1 + len(v) > CHUNK_CHARS and cur:
            out.append(cur); cur = ""
        while len(v) > CHUNK_CHARS:                     # a very long verse: cut at a sentence end
            cut = v.rfind(". ", 0, CHUNK_CHARS) + 1 or CHUNK_CHARS
            out.append((cur + " " + v[:cut]).strip()); cur = ""; v = v[cut:].strip()
        cur = (cur + " " + v).strip() if cur else v
    if cur:
        out.append(cur)
    return out


def call(req, tries=4):
    for n in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:200]
            if e.code in (429, 502, 503) and n < tries - 1:
                time.sleep(3 * (n + 1)); continue
            raise RuntimeError(f"{e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if n < tries - 1:
                time.sleep(3 * (n + 1)); continue
            raise RuntimeError(str(e))


def silence(td, seconds, name):
    p = os.path.join(td, name)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(seconds), p], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[:200])
    return p


def record(slug, head, verses, lang, k, speed=SPEED):
    with tempfile.TemporaryDirectory() as td:
        wavs = []
        for i, text in enumerate(pieces(head, verses)):
            body = json.dumps({"lang": lang, "text": text}).encode()
            wav = call(urllib.request.Request(API, data=body, method="POST", headers={"Authorization": "Bearer " + k, "Content-Type": "application/json", "User-Agent": UA}))
            if wav[:4] != b"RIFF":
                raise RuntimeError("the voice didn't answer with audio")
            p = os.path.join(td, f"{i:03d}.wav"); open(p, "wb").write(wav); wavs.append(p)
        lst = os.path.join(td, "list.txt")
        long_gap, short_gap = silence(td, PAUSE_HEAD, "gap_head.wav"), silence(td, PAUSE_PIECE, "gap_piece.wav")
        rows = []
        for i, p in enumerate(wavs):
            rows.append(p)
            if i < len(wavs) - 1:
                rows.append(long_gap if i == 0 else short_gap)
        open(lst, "w").write("".join(f"file '{p}'\n" for p in rows))
        mp3 = os.path.join(td, "chapter.mp3")
        r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ac", "1", "-ar", "22050", "-filter:a", f"atempo={speed}",
                            "-codec:a", "libmp3lame", "-b:a", "64k", mp3], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("ffmpeg: " + r.stderr[:200])
        data = open(mp3, "rb").read()
        out = call(urllib.request.Request(f"{API}?lang={lang}&slug={slug}", data=data, method="PUT", headers={"Authorization": "Bearer " + k, "Content-Type": "audio/mpeg", "User-Agent": UA}))
        return len(wavs), len(data), json.loads(out)


LISTEN = '<button class="tgl tgl-audio" id="audiotgl" data-audio="{url}">🔊 Listen</button>'


def patch_page(path, lang, slug):
    """Give an already built chapter page its Listen button, without rebuilding the whole site (build.py does the same on a full build).
    Idempotent: a page that has the button just gets its address refreshed. English chapter pages only for now."""
    if lang != "en":
        return False
    url = f"https://micwyn.com/narration/{lang}/{slug}.mp3"
    page = open(path, encoding="utf-8").read()
    if 'id="audiotgl"' in page:
        new = re.sub(r'(id="audiotgl"[^>]*?data-audio=")[^"]*(")', r"\g<1>" + url + r"\g<2>", page, count=1)
    else:
        new = page.replace('<div class="tgl-group">', '<div class="tgl-group">' + LISTEN.format(url=url), 1)
    if new == page:
        return False
    open(path, "w", encoding="utf-8").write(new)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", choices=["en", "es"], default="en")
    ap.add_argument("--only", help="one chapter's slug, e.g. genesis-1")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many chapters")
    ap.add_argument("--force", action="store_true", help="record chapters that already have a recording")
    ap.add_argument("--speed", type=float, default=SPEED, help="0.5 to 1.0; lower is slower (default %s)" % SPEED)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not 0.5 <= a.speed <= 1.0:
        sys.exit("--speed must be between 0.5 and 1.0")
    m = load_manifest(); m.setdefault("en", []); m.setdefault("es", [])
    todo = []
    for slug, path in pages(a.lang):
        if a.only and slug != a.only:
            continue
        if slug in m[a.lang] and not a.force:
            continue
        c = chapter(path, a.lang)
        if c:
            todo.append((slug, c))
    if a.limit:
        todo = todo[: a.limit]
    chars = sum(len(h) + sum(len(v) for v in vs) for _, (h, vs) in todo)
    print(f"{len(todo)} chapter(s) to record ({a.lang}), about {chars:,} characters, about {chars / 900:.0f} minutes of speech.")
    if a.dry_run or not todo:
        for slug, _ in todo[:10]:
            print("  ", slug)
        return
    k = key()
    done = 0
    for slug, (head, verses) in todo:
        try:
            n, size, res = record(slug, head, verses, a.lang, k, a.speed)
        except RuntimeError as e:
            print(f"  FAILED {slug}: {e}")
            continue
        m[a.lang].append(slug); save_manifest(m); done += 1
        patched = patch_page(os.path.join(HERE, slug + ".html"), a.lang, slug)
        print(f"  {slug}: {n} pieces, {size / 1024:.0f} KB  → https://micwyn.com{res.get('url', '')}" + ("  (Listen button added to the page)" if patched else ""))
    print(f"Recorded {done} of {len(todo)}. Next: python3 build.py, then commit audio/narrated.json and the pages.")


if __name__ == "__main__":
    main()

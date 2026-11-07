#!/usr/bin/env python3
"""Record the narration of Mister Translation chapters, once, with Grok's voice, and keep it in R2.

How it works (AR-156): for each chapter page this reads the verses, sends them in pieces of about 1,000 characters to Micwyn's
narrate endpoint (which speaks them with Grok and answers with MP3), joins and compresses the pieces to one small MP3 with ffmpeg,
uploads the MP3 (kept at https://micwyn.com/narration/<lang>/<slug>.mp3) and notes the chapter in audio/narrated.json. build.py reads
that file: a chapter with a recording gets a Listen button that plays it; a chapter without one has no Listen button.
Chapters recorded before 2026-11-06 are in the old MeloTTS voice (Cloudflare retires it on 11-20); Michael said to leave them, not redo them.

    python3 narrate.py --only genesis-1             # one chapter (English)
    python3 narrate.py --limit 20                   # the next 20 chapters that have no recording
    python3 narrate.py                              # every chapter that has none (about $0.06 a chapter)
    python3 narrate.py --lang es                    # the Spanish editions (the *.es.html pages)
    python3 narrate.py --only genesis-1 --force     # record it again
    python3 narrate.py --dry-run                    # say what would be recorded

Needs: ffmpeg (brew install ffmpeg), and the Scribe key in the macOS Keychain (service agorai-scribe-api-key, account scribe), the same
key Claude posts to Micwyn with. The key is read from the Keychain each run and never printed or written anywhere.
Each recorded English chapter page gets its Listen button added in place (a full python3 build.py does the same for every recorded chapter).
Then: git add audio/narrated.json *.html && git commit && git push.
"""
import argparse, fcntl, glob, html as _html, json, os, re, subprocess, sys, tempfile, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://micwyn.com/api/v1/narrate"
MANIFEST = os.path.join(HERE, "audio", "narrated.json")
CHUNK_CHARS = 1000
SPEED = 1.0           # 1.0 is the voice as it speaks; below 1 slows it down without changing its pitch (ffmpeg atempo). Grok's own pace, measured 11-06 at 16.3 characters a second, is already a little slower than MeloTTS at the 0.88 Michael asked for (17.1).
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


def add_to_manifest(lang, slug):
    """Note a recorded chapter. Several lanes can run at once (--shard), so the file is re-read under a lock and added to, never overwritten."""
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        m = load_manifest(); m.setdefault("en", []); m.setdefault("es", [])
        m[lang] = sorted(set(m[lang]) | {slug})
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
        except (urllib.error.URLError, TimeoutError, OSError, ConnectionError) as e:      # includes ssl.SSLError and dropped connections
            if n < tries - 1:
                time.sleep(3 * (n + 1)); continue
            raise RuntimeError(str(e))


def silence(td, seconds, name):
    p = os.path.join(td, name)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(seconds), p], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[:200])
    return p


def to_wav(td, i, audio):
    """One spoken piece as a WAV in the same shape as the silences, so the pieces join cleanly whatever the voice answered with."""
    if audio[:4] == b"RIFF":
        ext = "wav"
    elif audio[:3] == b"ID3" or (len(audio) > 1 and audio[0] == 0xFF and audio[1] & 0xE0 == 0xE0):
        ext = "mp3"
    else:
        raise RuntimeError("the voice didn't answer with audio")
    src, out = os.path.join(td, f"raw{i:03d}.{ext}"), os.path.join(td, f"{i:03d}.wav")
    open(src, "wb").write(audio)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", out], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[:200])
    return out


def record(slug, head, verses, lang, k, speed=SPEED):
    with tempfile.TemporaryDirectory() as td:
        wavs = []
        for i, text in enumerate(pieces(head, verses)):
            body = json.dumps({"lang": lang, "text": text}).encode()
            audio = call(urllib.request.Request(API, data=body, method="POST", headers={"Authorization": "Bearer " + k, "Content-Type": "application/json", "User-Agent": UA}))
            wavs.append(to_wav(td, i, audio))
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
LISTEN_ES = '<button class="tgl tgl-audio" id="audiotgl" data-audio="{url}">🔊 Escuchar</button>'


def patch_page(path, lang, slug):
    """Give an already built chapter page its Listen button, without rebuilding the whole site (build.py does the same on a full build).
    Idempotent: a page that has the button just gets its address refreshed. """
    url = f"https://micwyn.com/narration/{lang}/{slug}.mp3"
    page = open(path, encoding="utf-8").read()
    if 'id="audiotgl"' in page:
        new = re.sub(r'(id="audiotgl"[^>]*?data-audio=")[^"]*(")', r"\g<1>" + url + r"\g<2>", page, count=1)
    else:
        new = page.replace('<div class="tgl-group">', '<div class="tgl-group">' + (LISTEN_ES if lang == "es" else LISTEN).format(url=url), 1)
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
    ap.add_argument("--list", help="a file of slugs, one per line: record exactly those (still skipping ones already recorded)")
    ap.add_argument("--shard", default="", help="k/n: do every n-th chapter starting at k (run n of these at once to go n times faster), e.g. 0/4")
    a = ap.parse_args()
    if not 0.5 <= a.speed <= 1.0:
        sys.exit("--speed must be between 0.5 and 1.0")
    a.list_slugs = set(x.strip() for x in open(a.list, encoding="utf-8") if x.strip()) if a.list else None
    m = load_manifest(); m.setdefault("en", []); m.setdefault("es", [])
    todo = []
    for slug, path in pages(a.lang):
        if a.only and slug != a.only:
            continue
        if a.list_slugs is not None and slug not in a.list_slugs:
            continue
        if slug in m[a.lang] and not a.force:
            continue
        c = chapter(path, a.lang)
        if c:
            todo.append((slug, c))
    if a.shard:
        k0, n0 = (int(x) for x in a.shard.split("/"))
        todo = todo[k0::n0]
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
        except Exception as e:      # one bad chapter never stops the lane
            print(f"  FAILED {slug}: {e}")
            continue
        add_to_manifest(a.lang, slug); done += 1
        patched = patch_page(path, a.lang, slug)
        print(f"  {slug}: {n} pieces, {size / 1024:.0f} KB  → https://micwyn.com{res.get('url', '')}" + ("  (Listen button added to the page)" if patched else ""))
    print(f"Recorded {done} of {len(todo)}. Next: python3 build.py, then commit audio/narrated.json and the pages.")


if __name__ == "__main__":
    main()

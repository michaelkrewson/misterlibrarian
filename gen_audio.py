#!/usr/bin/env python3
"""Pre-generate warm-narrator MP3s for each chapter of the MisterLibrarian Bible.

This is the OPTIONAL "premium voice" half of the site's audio feature. It reads
the English translation out of each built ``genesis-N.html`` page and turns it
into ``audio/genesis-N.mp3`` — one consistent, natural narration voice that
every reader hears. The site's Listen button plays that MP3 when it exists and
otherwise falls back to the reader's own browser voice (see audio-reader.js), so
you can generate audio for one chapter at a time and the rest keep working.

Nothing here runs during the normal ``build.py`` — generate audio deliberately,
because it costs a few cents per chapter and needs an API key.

    # 1. Build the site first so the chapter pages exist:
    python3 build.py

    # 2. Set your key and generate (OpenAI is the default engine):
    export OPENAI_API_KEY=sk-...
    python3 gen_audio.py                 # all chapters that don't have audio yet
    python3 gen_audio.py --only 3        # just Genesis 3
    python3 gen_audio.py --force         # re-generate even if the MP3 exists
    python3 gen_audio.py --voice nova    # pick a different OpenAI voice

    # 3. Re-run build.py (so the Listen buttons pick up the new files), then
    #    commit audio/*.mp3 and push:
    python3 build.py && git add audio *.html && git commit -m "audio" && git push

Engines:
  * openai       (default)  needs OPENAI_API_KEY. Voices: alloy, echo, fable,
                            onyx, nova, shimmer, sage, coral, ... Default
                            "fable" — a warm storyteller. Model gpt-4o-mini-tts
                            also honors a spoken-tone instruction (set below).
  * elevenlabs             needs ELEVENLABS_API_KEY. --voice is a voice_id.

No third-party packages — only the Python standard library.

(A totally free, no-key alternative for testing is macOS's built-in `say`:
   say -v Samantha -o audio/genesis-3.m4a "In the beginning..."
 but that's the same class of voice the browser fallback already uses, so this
 script targets the higher-quality cloud voices you actually chose it for.)
"""

import argparse
import glob
import html as _html
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")

# OpenAI's TTS input cap is ~4096 chars; keep a safe margin and split on verses.
CHUNK_CHARS = 3500

WARM_INSTRUCTIONS = (
    "Read in a warm, calm, reverent narrator's voice, at an unhurried pace, "
    "with clear enunciation, as if reading scripture aloud to a listener."
)

# --- Pull the English text out of a built chapter page ----------------------

_VERSE_RE = re.compile(
    r'id="v(?:\d+-)?\d+"[^>]*>.*?<div class="eng">(.*?)</div>', re.S
)
_TAG_RE = re.compile(r"<[^>]+>")


def chapter_text(num):
    """Genesis heading + every verse's English, cleaned of markup, in order."""
    path = os.path.join(HERE, f"genesis-{num}.html")
    if not os.path.exists(path):
        return None
    page = open(path, encoding="utf-8").read()
    verses = []
    for raw in _VERSE_RE.findall(page):
        raw = raw.replace('<a class="notelink"', '<!--notelink--><a class="notelink"')
        raw = re.sub(r'<a class="notelink".*?</a>', "", raw, flags=re.S)  # drop "note"
        txt = _html.unescape(_TAG_RE.sub("", raw))
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            verses.append(txt)
    if not verses:
        return None
    # A short spoken heading, then the verses separated so the voice pauses.
    return f"Genesis, chapter {num}.\n\n" + "\n\n".join(verses)


def chunk(text):
    """Split into <=CHUNK_CHARS pieces on paragraph (verse) boundaries."""
    parts, cur = [], ""
    for para in text.split("\n\n"):
        if cur and len(cur) + len(para) + 2 > CHUNK_CHARS:
            parts.append(cur)
            cur = ""
        cur = (cur + "\n\n" + para).strip() if cur else para
    if cur:
        parts.append(cur)
    return parts


def discover_chapters():
    nums = []
    for p in glob.glob(os.path.join(HERE, "genesis-*.html")):
        m = re.search(r"genesis-(\d+)\.html$", p)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)


# --- TTS engines (return MP3 bytes for one chunk) ---------------------------

def tts_openai(text, voice, model, api_key):
    body = {"model": model, "voice": voice, "input": text, "response_format": "mp3"}
    if model.startswith("gpt-4o"):  # only the newer model honors tone instructions
        body["instructions"] = WARM_INSTRUCTIONS
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def tts_elevenlabs(text, voice, model, api_key):
    voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # "Rachel" — a warm default
    body = {"text": text, "model_id": model or "eleven_multilingual_v2"}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": api_key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


ENGINES = {
    "openai": {"fn": tts_openai, "key": "OPENAI_API_KEY",
               "voice": "fable", "model": "gpt-4o-mini-tts"},
    "elevenlabs": {"fn": tts_elevenlabs, "key": "ELEVENLABS_API_KEY",
                   "voice": None, "model": "eleven_multilingual_v2"},
}


def synth_chapter(num, spec, voice, model, api_key):
    text = chapter_text(num)
    if not text:
        print(f"  Genesis {num}: no verse text found — skipping")
        return False
    audio = b""
    chunks = chunk(text)
    for i, piece in enumerate(chunks, 1):
        try:
            audio += spec["fn"](piece, voice, model, api_key)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            print(f"  Genesis {num}: API error on chunk {i}/{len(chunks)}: "
                  f"{e.code} {detail}")
            return False
        except Exception as e:  # noqa: BLE001 — surface anything and move on
            print(f"  Genesis {num}: failed on chunk {i}/{len(chunks)}: {e}")
            return False
        print(f"  Genesis {num}: chunk {i}/{len(chunks)} ok ({len(piece)} chars)")
    os.makedirs(AUDIO_DIR, exist_ok=True)
    out = os.path.join(AUDIO_DIR, f"genesis-{num}.mp3")
    with open(out, "wb") as f:
        f.write(audio)
    print(f"  Genesis {num}: wrote {out} ({len(audio) // 1024} KB)")
    return True


def main():
    ap = argparse.ArgumentParser(description="Generate narration MP3s per chapter.")
    ap.add_argument("--engine", choices=list(ENGINES), default="openai")
    ap.add_argument("--voice", default=None, help="voice name (openai) / voice_id (elevenlabs)")
    ap.add_argument("--model", default=None, help="override the TTS model")
    ap.add_argument("--only", type=int, default=None, help="just this chapter number")
    ap.add_argument("--force", action="store_true", help="re-generate existing MP3s")
    args = ap.parse_args()

    spec = ENGINES[args.engine]
    api_key = os.environ.get(spec["key"])
    if not api_key:
        print(f"No {spec['key']} in the environment.\n"
              f"  export {spec['key']}=...   then re-run.\n"
              f"(Meanwhile the site's Listen button still works via browser speech.)")
        sys.exit(1)

    voice = args.voice or spec["voice"]
    model = args.model or spec["model"]
    chapters = [args.only] if args.only else discover_chapters()
    if not chapters:
        print("No genesis-*.html pages found — run build.py first.")
        sys.exit(1)

    print(f"Engine: {args.engine}  voice: {voice or '(default)'}  model: {model}")
    made = 0
    for num in chapters:
        out = os.path.join(AUDIO_DIR, f"genesis-{num}.mp3")
        if os.path.exists(out) and not args.force:
            print(f"  Genesis {num}: already have {os.path.relpath(out, HERE)} — skipping "
                  f"(use --force to redo)")
            continue
        if synth_chapter(num, spec, voice, model, api_key):
            made += 1

    print(f"\nDone. {made} file(s) generated in audio/.")
    if made:
        print("Now re-run `python3 build.py` so the Listen buttons link to them, "
              "then commit audio/*.mp3 and the rebuilt pages.")


if __name__ == "__main__":
    main()

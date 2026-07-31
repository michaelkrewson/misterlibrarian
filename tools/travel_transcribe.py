#!/usr/bin/env python3
"""Turn a voice memo into tasting notes, on-device.

The blog is written from meals that happened hours or days earlier, and the
details that make an entry worth reading — what the texture actually was, which
element surprised you — are exactly the ones that do not survive the drive home.
A 30-second memo at the table fixes that, but only if the memo is easy to get
back OUT. Left as an .m4a on the Desktop it is worse than useless: it looks like
a chore, so it never gets opened, and the entry gets written without it.

    python3 tools/travel_transcribe.py ~/Desktop/memo.m4a
    python3 tools/travel_transcribe.py ~/Desktop/memo.m4a --archive st-honore-boulangerie
    python3 tools/travel_transcribe.py ~/Desktop/memo.m4a --archive ramen-ryoma \\
        --name 2026-07-25-chashu-note --date 2026-07-25

⚠ NOTHING LEAVES THE MACHINE. Transcription is Apple's on-device speech model
(see travel_transcribe.swift). There is no API key and no upload. The only
network access is a one-time download of the speech model itself. This matters
because a food memo is a recording of Michael's own voice in a public place, and
that is not something to hand to a transcription service for a sandwich.

⚠ THE FILENAME LIES ABOUT THE PLACE. Voice Memos names a recording after
whatever venue its location lookup resolves to, which on a street of restaurants
is regularly the wrong one — the St Honoré panini memo came over as "Domaine
Serene Wine Lounge", a wine bar a few doors down. Never take the entry from the
filename. Pass --archive yourself.

⚠ THE TRANSCRIPT IS A DRAFT, NOT A QUOTE. The model mishears proper nouns and
menu French in predictable ways ("brie" came back as "debris"). The written
transcript file has a CORRECTIONS block precisely so the fix is recorded next to
the raw output instead of silently replacing it — the raw text stays the
evidence of what was actually said.

WHAT --archive DOES
Copies the audio and writes a transcript .txt beside it, then hands both to
tools/travel_archive.py, so a memo lands in S3 next to that meal's photos under
the same slug. Originals do not go in git (see travel_archive.py for why), and
audio must never be published to the site: it is his voice plus, by way of the
filename, where he was standing.

REQUIRES macOS 26+ (SpeechAnalyzer). The helper is compiled on first use and
cached; afconvert and swiftc both ship with macOS, so there is nothing to
install.
"""
import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
SWIFT_SRC = os.path.join(TOOLS, "travel_transcribe.swift")
CACHE_DIR = os.path.expanduser("~/Library/Caches/misterlibrarian")
BINARY = os.path.join(CACHE_DIR, "travel_transcribe")

# A CLI binary that touches a privacy-gated API is killed on the spot unless an
# Info.plist is linked into its __TEXT segment. SpeechAnalyzer does not appear
# to need it, but it costs nothing and turns a possible silent SIGABRT into a
# normal permission prompt if a future macOS tightens this.
INFO_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key><string>com.mistertranslation.travel-transcribe</string>
  <key>CFBundleName</key><string>travel_transcribe</string>
  <key>CFBundleExecutable</key><string>travel_transcribe</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>NSSpeechRecognitionUsageDescription</key>
  <string>Transcribes a travel voice memo on this Mac. No audio leaves the machine.</string>
</dict>
</plist>
"""

TRANSCRIPT_TEMPLATE = """\
TASTING NOTE — voice memo, transcribed
Entry:  {slug}
Audio:  {audio}
Recorded/attributed date: {date}

PROVENANCE
Transcribed on-device with Apple's speech model (macOS SpeechAnalyzer, {locale})
by tools/travel_transcribe.py on {stamp}. No audio left the machine.
Source file as supplied: {source_name}

⚠ Voice Memos names recordings after whatever venue its location lookup finds,
which is often a neighbouring business rather than the one the note is about.
The entry above was set by hand, not read off the filename.

RAW TRANSCRIPT (verbatim machine output — do not edit; this is the evidence)
{raw}

CORRECTIONS (fill in by hand; the model mishears proper nouns and menu French)
  -

CLEANED
  -

NOT IN THE MEMO — do not attribute to him
  -
"""


def die(msg, code=1):
    sys.exit("travel_transcribe: " + msg)


def ensure_macos():
    if sys.platform != "darwin":
        die("this only runs on macOS — it uses Apple's on-device speech model.")
    try:
        ver = subprocess.run(["sw_vers", "-productVersion"], capture_output=True,
                             text=True, check=True).stdout.strip()
        if int(ver.split(".")[0]) < 26:
            die("needs macOS 26 or newer for SpeechAnalyzer (this is %s)." % ver)
    except (subprocess.CalledProcessError, ValueError, IndexError):
        pass            # Version unreadable is not a reason to refuse to try.


def build_helper(verbose=True):
    """Compile the Swift helper if it is missing or older than its source."""
    if (os.path.exists(BINARY)
            and os.path.getmtime(BINARY) >= os.path.getmtime(SWIFT_SRC)):
        return BINARY
    if not os.path.exists(SWIFT_SRC):
        die("missing %s" % SWIFT_SRC)
    if not shutil.which("swiftc"):
        die("swiftc not found — install the Xcode command line tools:\n"
            "    xcode-select --install")

    os.makedirs(CACHE_DIR, exist_ok=True)
    if verbose:
        print("  compiling the speech helper (first run only)…", file=sys.stderr)
    with tempfile.TemporaryDirectory() as tmp:
        plist = os.path.join(tmp, "Info.plist")
        with open(plist, "w") as fh:
            fh.write(INFO_PLIST)
        cmd = ["swiftc", "-O", "-parse-as-library", SWIFT_SRC, "-o", BINARY,
               "-Xlinker", "-sectcreate", "-Xlinker", "__TEXT",
               "-Xlinker", "__info_plist", "-Xlinker", plist]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            die("could not compile the speech helper:\n" + r.stderr.strip())
    subprocess.run(["codesign", "-s", "-", "-f", BINARY], capture_output=True)
    return BINARY


def to_wav(src, tmpdir):
    """16 kHz mono WAV — what the speech model wants, and it strips the spatial
    audio track an iPhone memo carries, which AVAudioFile will not read."""
    out = os.path.join(tmpdir, "audio.wav")
    r = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1",
                        src, out], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        die("afconvert could not read %s\n%s" % (src, r.stderr.strip()))
    return out


def duration_seconds(src):
    try:
        r = subprocess.run(["afinfo", src], capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines():
            if "estimated duration" in line:
                return float(line.split(":")[1].strip().split()[0])
    except Exception:
        pass
    return None


def transcribe(src, locale="en-US", verbose=True):
    ensure_macos()
    binary = build_helper(verbose=verbose)
    with tempfile.TemporaryDirectory() as tmp:
        wav = to_wav(src, tmp)
        r = subprocess.run([binary, wav, "--locale", locale],
                           capture_output=True, text=True)
        if verbose and r.stderr.strip():
            for line in r.stderr.strip().splitlines():
                print("  " + line, file=sys.stderr)
        if r.returncode != 0:
            die("transcription failed (exit %d)" % r.returncode)
        return r.stdout.strip()


def archive(src, raw, slug, name, date, locale, dry_run=False):
    """Put the audio + a transcript into S3 under the entry's slug.

    An upload is effectively permanent — the backup IAM user has no
    DeleteObject — so --dry-run exists to check the pair before committing to it.
    """
    sys.path.insert(0, TOOLS)
    archiver = os.path.join(TOOLS, "travel_archive.py")
    if not os.path.exists(archiver):
        die("missing %s — cannot archive." % archiver)

    ext = os.path.splitext(src)[1].lower() or ".m4a"
    # .qta is what a spatial-audio memo arrives as; it is a QuickTime container,
    # so .mov is both accurate and double-clickable everywhere.
    if ext == ".qta":
        ext = ".mov"

    with tempfile.TemporaryDirectory() as tmp:
        audio_name = name + ext
        audio_path = os.path.join(tmp, audio_name)
        shutil.copy2(src, audio_path)

        txt_path = os.path.join(tmp, name + ".txt")
        with open(txt_path, "w", encoding="utf-8") as fh:
            fh.write(TRANSCRIPT_TEMPLATE.format(
                slug=slug, audio=audio_name, date=date,
                locale=locale, source_name=os.path.basename(src),
                stamp=dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                raw='"' + raw + '"'))

        cmd = [sys.executable, archiver, "add", slug, audio_path, txt_path]
        if dry_run:
            cmd.append("--dry-run")
            print("\n--- transcript that would be written ---", file=sys.stderr)
            sys.stderr.write(open(txt_path, encoding="utf-8").read())
            print("--- end ---\n", file=sys.stderr)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            die("archiving failed — the transcript is above, nothing was lost.")
    return name + ext, name + ".txt"


def main():
    ap = argparse.ArgumentParser(
        description="Transcribe a travel voice memo on-device.")
    ap.add_argument("audio", help="the voice memo (.m4a, .qta, .mov, .wav …)")
    ap.add_argument("--archive", metavar="SLUG",
                    help="also archive audio + transcript to S3 under this entry slug")
    ap.add_argument("--name", help="base filename for the archived pair "
                                   "(default: <date>-<slug>-note)")
    ap.add_argument("--date", help="date to attribute the recording to "
                                   "(default: today; the file's own timestamp is "
                                   "the export, not the meal)")
    ap.add_argument("--locale", default="en-US")
    ap.add_argument("--quiet", action="store_true", help="transcript only")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --archive: show the pair, upload nothing")
    args = ap.parse_args()

    src = os.path.expanduser(args.audio)
    if not os.path.isfile(src):
        die("no such file: %s" % src)

    verbose = not args.quiet
    if verbose:
        secs = duration_seconds(src)
        print("  %s%s" % (os.path.basename(src),
                          "  (%.0fs)" % secs if secs else ""), file=sys.stderr)

    raw = transcribe(src, locale=args.locale, verbose=verbose)
    print(raw)
    sys.stdout.flush()      # keep the transcript above the archiver's chatter

    if args.archive:
        date = args.date or dt.date.today().isoformat()
        name = args.name or "%s-%s-note" % (date, args.archive)
        audio_name, txt_name = archive(src, raw, args.archive, name, date,
                                       args.locale, dry_run=args.dry_run)
        if verbose and not args.dry_run:
            print("\n  archived under '%s': %s + %s" %
                  (args.archive, audio_name, txt_name), file=sys.stderr)
            print("  ⚠ fill in the CORRECTIONS block in the .txt before quoting it.",
                  file=sys.stderr)


if __name__ == "__main__":
    main()

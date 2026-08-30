#!/usr/bin/env python3
"""Full git-history backup of this repo, mirrored to Michael's private S3.

Why this exists: the translation + library content (chapters, dictionary,
encyclopedia entries, build.py, library_data.py, etc.) lives in git and is
pushed to GitHub -- already a solid off-machine backup. Michael asked for
redundancy beyond that (2026-08-29), the same instinct behind the
source-text archive (tools/archive_sources.py) and the travel-media archive
(tools/travel_archive.py): before trusting a single external service, keep
our own copy too.

A `git bundle` is a single file holding the FULL commit history of a
branch -- not a working-tree snapshot. `git clone <bundle>` reconstructs the
whole repo from scratch, so this is a complete, restorable mirror of
everything ever committed to main (every chapter, every dict/ency entry,
all the code), independent of both GitHub and this Mac.

PRIVATE ARCHIVE -- same private S3 bucket as the source-text and travel
archives (this repo/site itself is public; the backup copy doesn't need
to be, and there's no reason to make it so).

Usage:
    python3 tools/archive_repo.py                 # bundle main -> S3
    python3 tools/archive_repo.py --verify         # check the S3 copy's hash
    python3 tools/archive_repo.py --restore-test   # verify + full test-clone

Re-run this any time after a session that added real content (a new
chapter, a batch of dict/ency entries) -- it's cheap and just overwrites
the prior bundle. S3 layout: blobs/misterlibrarian_repo/repo.bundle +
blobs/misterlibrarian_repo/MANIFEST.json. Restore via
market_data_store.get_blob or `git clone repo.bundle`.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MSTR_TRADER = Path.home() / "projects" / "mstr-trader"  # for market_data_store
S3_CATEGORY = "misterlibrarian_repo"
BRANCH = "main"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _s3():
    sys.path.insert(0, str(MSTR_TRADER))
    import market_data_store as mds  # noqa: PLC0415
    if not mds.enabled():
        raise SystemExit("S3 store not enabled (missing ~/.mstr-trader/backup.env?)")
    return mds


def _head_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", BRANCH], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _make_bundle(dest: Path) -> None:
    subprocess.run(
        ["git", "bundle", "create", str(dest), BRANCH],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    out = subprocess.run(
        ["git", "bundle", "verify", str(dest)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout
    if "complete history" not in out:
        raise SystemExit(f"bundle failed self-verify:\n{out}")


def push() -> None:
    mds = _s3()
    with tempfile.TemporaryDirectory() as td:
        bundle_path = Path(td) / "repo.bundle"
        _make_bundle(bundle_path)
        data = bundle_path.read_bytes()
    digest = _sha256(data)
    commit = _head_commit()
    manifest = {
        "branch": BRANCH,
        "commit": commit,
        "bytes": len(data),
        "sha256": digest,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if not mds.put_blob(S3_CATEGORY, "repo.bundle", data, "application/octet-stream"):
        raise SystemExit("S3 push of repo.bundle failed")
    mds.put_blob(S3_CATEGORY, "MANIFEST.json",
                 json.dumps(manifest, indent=1, sort_keys=True).encode(),
                 "application/json")
    print(f"pushed {BRANCH}@{commit[:10]} ({len(data):,}b, "
          f"sha256 {digest[:12]}...) to S3", flush=True)


def verify(restore_test: bool = False) -> None:
    mds = _s3()
    manifest_blob = mds.get_blob(S3_CATEGORY, "MANIFEST.json")
    if manifest_blob is None:
        raise SystemExit("no MANIFEST.json in S3 -- run without a flag first")
    manifest = json.loads(manifest_blob)
    data = mds.get_blob(S3_CATEGORY, "repo.bundle")
    if data is None:
        raise SystemExit("no repo.bundle in S3")
    digest = _sha256(data)
    if digest != manifest["sha256"]:
        raise SystemExit(f"sha256 MISMATCH: manifest says "
                          f"{manifest['sha256'][:12]}, got {digest[:12]}")
    print(f"S3 bundle sha256 OK ({manifest['bytes']:,}b, "
          f"{BRANCH}@{manifest['commit'][:10]}, pushed {manifest['created_at']})",
          flush=True)
    current = _head_commit()
    if current != manifest["commit"]:
        print(f"  note: local {BRANCH} is now @{current[:10]} -- the S3 "
              f"backup is behind; re-run without a flag to refresh it",
              flush=True)
    if restore_test:
        with tempfile.TemporaryDirectory() as td:
            bundle_path = Path(td) / "repo.bundle"
            bundle_path.write_bytes(data)
            restored = Path(td) / "restored"
            out = subprocess.run(
                ["git", "clone", "-q", str(bundle_path), str(restored)],
                capture_output=True, text=True,
            )
            if out.returncode != 0:
                raise SystemExit(f"restore-test clone FAILED:\n{out.stderr}")
            restored_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=restored,
                capture_output=True, text=True,
            ).stdout.strip()
            if restored_head != manifest["commit"]:
                raise SystemExit("restore-test HEAD mismatch")
            print(f"  restore-test OK: cloned the bundle from scratch, "
                  f"HEAD lands at @{restored_head[:10]}", flush=True)


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    elif "--restore-test" in sys.argv:
        verify(restore_test=True)
    else:
        push()

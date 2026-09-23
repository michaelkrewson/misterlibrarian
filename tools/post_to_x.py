#!/usr/bin/env python3
"""Post a single announcement to X (formerly Twitter) from the command line.

Built 2026-09-23 (Michael's ask) so a new blog entry can actually be announced
on X, not just drafted in chat. Nothing else in this repo posts anywhere —
`blogkit.py`'s `x_comment_url`/`x_note_url` only build a pre-filled COMPOSE
LINK for a *reader* to comment with; this is the only thing that authors and
posts on Michael's own behalf.

No third-party packages — only the Python standard library. OAuth 1.0a
signing (HMAC-SHA1) is implemented by hand below rather than pulling in
`tweepy`/`requests`, matching this repo's "standard library only" builders.

ONE-TIME SETUP (Michael does this once; the rest is automatic after)
──────────────────────────────────────────────────────────────────
1. Go to https://console.x.com and create a Project + App (or reuse one).
   Under the App's "User authentication settings": enable OAuth 1.0a, set
   App permissions to **Read and Write** (posting fails with a 403 under
   read-only permissions).
   ⚠️ GENERATE THE ACCESS TOKEN/SECRET *AFTER* SETTING PERMISSIONS TO
   READ+WRITE — a token generated while the app was still read-only keeps
   read-only scope even after you flip the app's permission setting, and
   the fix is to regenerate the token, not just change the app setting.

2. From the app's "Keys and tokens" tab, copy four values: API Key (consumer
   key), API Key Secret (consumer secret), Access Token, Access Token Secret.

3. Save them to ~/.misterlibrarian/x_credentials.json (NOT in this repo —
   nothing under version control should ever hold these) as:
     {
       "api_key": "...",
       "api_key_secret": "...",
       "access_token": "...",
       "access_token_secret": "..."
     }
   Then lock it down: chmod 600 ~/.misterlibrarian/x_credentials.json

4. X moved off tiered plans to pay-per-use on 2026-02-06 — there is no free
   tier. You buy credits up front in the Developer Console and each call
   bills against the balance: about $0.015 for a plain-text post, about
   $0.20 for one that contains a URL (the announcement tweets this script
   sends always contain the article link, so budget for the $0.20 rate).
   Buy a starting credit balance before the first real post — a $0 balance
   fails every call, same as missing credentials.

USAGE
─────
    python3 tools/post_to_x.py "Tweet text with a link at the end"
    python3 tools/post_to_x.py --file tweet.txt
    echo "Tweet text" | python3 tools/post_to_x.py
    python3 tools/post_to_x.py "..." --dry-run     # sign + print, post nothing
    python3 tools/post_to_x.py --selftest          # verify the OAuth 1.0a
                                                    # signing math against the
                                                    # official worked example,
                                                    # no credentials needed

Always run with --dry-run first for anything new — it builds the exact
request (including the signed Authorization header) and prints it without
spending a credit or touching the network, so a credential or signing
mistake shows up before it costs money or posts something wrong.

TROUBLESHOOTING
────────────────
  401 Unauthorized  → usually a bad/expired credential, a system clock more
                       than ~5 minutes off (the signature embeds a timestamp),
                       or (per user reports since the pay-per-use switch)
                       OAuth 1.0a user-context auth intermittently rejected
                       on some pay-per-use apps — if credentials and clock
                       both check out, that's the next thing to search X's
                       developer forum for.
  403 Forbidden     → the app (or its access token) is read-only; see step 1.
  429 Too Many...   → rate limited; wait and retry.
  A JSON error body with "insufficient" / balance language → buy more
                       pay-per-use credits in the Developer Console.
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

CREDENTIALS_PATH = os.path.expanduser("~/.misterlibrarian/x_credentials.json")
POST_URL = "https://api.x.com/2/tweets"
REQUIRED_KEYS = ("api_key", "api_key_secret", "access_token", "access_token_secret")

# The classic worked example from X/Twitter's own "Creating a signature" OAuth
# 1.0a documentation — reproduced (independent of that page) as a fixed test
# vector so `--selftest` can confirm the signing math below is correct without
# needing real credentials or a network call.
_SELFTEST = {
    "method": "POST",
    "url": "https://api.twitter.com/1.1/statuses/update.json",
    "params": {
        "status": "Hello Ladies + Gentlemen, a signed OAuth request!",
        "include_entities": "true",
        "oauth_consumer_key": "xvz1evFS4wEEPTGEFPHBog",
        "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": "1318622958",
        "oauth_token": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
        "oauth_version": "1.0",
    },
    "consumer_secret": "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",
    "token_secret": "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2oAmc",
    # Verified independently via `openssl dgst -sha1 -hmac` against the exact
    # signature base string these params produce (that base string itself
    # matches X/Twitter's own published worked example byte-for-byte) —
    # see the commit that added this file for the verification transcript.
    "expected_signature": "EZFSPDI3sbzgHcUTFwIHfGpH2lc=",
}


def _percent_encode(s):
    """RFC 3986 percent-encoding, leaving only unreserved chars (A-Za-z0-9-._~)
    unescaped — exactly what OAuth 1.0a's signing spec requires. Python's
    urllib.parse.quote already treats '~' as always-safe (3.7+), so `safe=""`
    is enough; this wrapper exists so that fact doesn't have to be re-verified
    at every call site."""
    return urllib.parse.quote(str(s), safe="")


def _signature_base_string(method, url, params):
    param_string = "&".join(
        "%s=%s" % (_percent_encode(k), _percent_encode(v))
        for k, v in sorted(params.items())
    )
    return "&".join([
        method.upper(),
        _percent_encode(url),
        _percent_encode(param_string),
    ])


def _oauth_signature(method, url, params, consumer_secret, token_secret):
    base = _signature_base_string(method, url, params)
    signing_key = "%s&%s" % (_percent_encode(consumer_secret), _percent_encode(token_secret))
    digest = hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def _oauth_header(method, url, creds, extra_params=None):
    """Build the full `Authorization: OAuth ...` header for one request. For a
    JSON-body POST (X API v2's /2/tweets) there are no form/query params to
    sign beyond the oauth_* ones themselves — the JSON body is never part of
    an OAuth 1.0a signature, only query-string and x-www-form-urlencoded
    params are. `extra_params` exists for a future caller that DOES need
    query params signed (there is none today)."""
    oauth_params = {
        "oauth_consumer_key": creds["api_key"],
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds["access_token"],
        "oauth_version": "1.0",
    }
    all_params = dict(oauth_params)
    all_params.update(extra_params or {})
    oauth_params["oauth_signature"] = _oauth_signature(
        method, url, all_params, creds["api_key_secret"], creds["access_token_secret"])
    header = "OAuth " + ", ".join(
        '%s="%s"' % (_percent_encode(k), _percent_encode(v))
        for k, v in sorted(oauth_params.items()))
    return header


def _load_credentials():
    if not os.path.exists(CREDENTIALS_PATH):
        sys.exit(
            "No credentials at %s — see the ONE-TIME SETUP section at the "
            "top of tools/post_to_x.py (`python3 tools/post_to_x.py --help` "
            "also prints it)." % CREDENTIALS_PATH)
    with open(CREDENTIALS_PATH) as f:
        creds = json.load(f)
    missing = [k for k in REQUIRED_KEYS if not creds.get(k)]
    if missing:
        sys.exit("%s is missing: %s" % (CREDENTIALS_PATH, ", ".join(missing)))
    mode = oct(os.stat(CREDENTIALS_PATH).st_mode)[-3:]
    if mode != "600":
        print("warning: %s is mode %s, not 600 — `chmod 600` it." % (CREDENTIALS_PATH, mode),
              file=sys.stderr)
    return creds


def _tco_length(text):
    """X shortens every URL in a post to a fixed-width t.co link regardless of
    its real length (23 chars as of this writing). This is a rough,
    non-authoritative length estimate for the --dry-run heads-up only — X's
    own server-side count is the one that actually matters."""
    T_CO_LEN = 23
    words = text.split(" ")
    total = 0
    for w in words:
        total += T_CO_LEN if w.startswith("http://") or w.startswith("https://") else len(w)
    return total + max(0, len(words) - 1)  # spaces between words


def post_tweet(text, dry_run=False):
    creds = None if dry_run else _load_credentials()
    approx_len = _tco_length(text)
    if approx_len > 280:
        print("warning: approx %d chars (limit 280) — X will reject this as-is."
              % approx_len, file=sys.stderr)
    body = json.dumps({"text": text}).encode()

    if dry_run:
        # Sign with placeholder creds so the header's SHAPE is still visible,
        # without needing real ones or touching the network.
        fake = {"api_key": "<api_key>", "api_key_secret": "<api_key_secret>",
                "access_token": "<access_token>", "access_token_secret": "<access_token_secret>"}
        header = _oauth_header("POST", POST_URL, fake)
        print("DRY RUN — nothing sent, no credit spent.")
        print("POST %s" % POST_URL)
        print("Authorization: %s" % header)
        print("Body: %s" % body.decode())
        print("Approx length (t.co-adjusted): %d / 280" % approx_len)
        return None

    header = _oauth_header("POST", POST_URL, creds)
    req = urllib.request.Request(
        POST_URL, data=body, method="POST",
        headers={"Authorization": header, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        sys.exit("X API error %s %s:\n%s" % (e.code, e.reason, err_body))
    tweet_id = result.get("data", {}).get("id")
    if tweet_id:
        print("Posted: https://x.com/i/web/status/%s" % tweet_id)
    else:
        print("Response (no tweet id found): %s" % json.dumps(result))
    return result


def _selftest():
    v = _SELFTEST
    got = _oauth_signature(v["method"], v["url"], v["params"],
                            v["consumer_secret"], v["token_secret"])
    if got == v["expected_signature"]:
        print("OK — signature matches the official worked example:\n  %s" % got)
        return 0
    print("FAILED — signing math is wrong.\n  expected: %s\n  got:      %s"
          % (v["expected_signature"], got), file=sys.stderr)
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="tweet text; omit to read from --file or stdin")
    ap.add_argument("--file", help="read tweet text from this file instead")
    ap.add_argument("--dry-run", action="store_true", help="sign and print, post nothing")
    ap.add_argument("--selftest", action="store_true",
                     help="verify OAuth 1.0a signing against the official example, no creds needed")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())

    if args.text:
        text = args.text
    elif args.file:
        with open(args.file) as f:
            text = f.read().strip()
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        ap.error("give tweet text as an argument, --file, or piped stdin")

    post_tweet(text, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

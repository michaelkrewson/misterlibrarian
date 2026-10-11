#!/usr/bin/env bash
# Deploy moved blogs to their m8k.io Workers (2026-10-10).
#
#   bash tools/deploy_blogs.sh            # every moved blog
#   bash tools/deploy_blogs.sh ledger     # just one (name = cf/<name>.wrangler.jsonc)
#
# A blog counts as "moved" once cf/<name>.wrangler.jsonc exists. mt-redirects is
# the mistertranslation.com 301 Worker, not a blog — deployed only when asked by name.
# Locally wrangler uses the Mac's login; in CI it reads CLOUDFLARE_API_TOKEN.
set -euo pipefail
cd "$(dirname "$0")/.."

WRANGLER="npx --yes wrangler@4"
command -v wrangler >/dev/null 2>&1 && WRANGLER="wrangler"

if [ "$#" -gt 0 ]; then
  names=("$@")
else
  names=()
  for f in cf/*.wrangler.jsonc; do
    n=$(basename "$f" .wrangler.jsonc)
    [ "$n" = "mt-redirects" ] && continue
    names+=("$n")
  done
fi

for n in "${names[@]}"; do
  cfg="cf/$n.wrangler.jsonc"
  if [ ! -f "$cfg" ]; then
    echo "skip $n — no $cfg (not moved yet)"
    continue
  fi
  echo "::group::deploy $n"
  $WRANGLER deploy -c "$cfg"
  echo "::endgroup::"
done

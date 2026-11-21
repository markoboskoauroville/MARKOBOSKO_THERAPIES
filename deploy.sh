#!/bin/bash
# deploy.sh: Marko Bosko Therapies -> Cloudflare Pages project markoboskotherapies, from the Mac.
# Only `wrangler pages deploy` (never `wrangler deploy`, no wrangler.jsonc, no Worker). The project must already exist.
# The token is read from ~/Downloads/API for the deploy only, never printed.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT=${PROJECT:-markoboskotherapies}
export CLOUDFLARE_ACCOUNT_ID=$(python3 -c "
import re,os; raw=open(os.path.expanduser('~/Downloads/API/Cloudflare.api.txt')).read(); m=re.findall(r'dash\.cloudflare\.com/([0-9a-f]{32})', raw); print(m[0] if m else 'b9255970e1438e7e5c4446260c6a320d')")
export CLOUDFLARE_API_TOKEN=$(python3 -c "
import re,os; raw=open(os.path.expanduser('~/Downloads/API/Cloudflare.api.txt')).read(); print([l.strip() for l in raw.splitlines() if re.fullmatch(r'[A-Za-z0-9_\-]{30,}', l.strip())][-1])")
cd "$HERE"
# confirm the project exists first; stop if it does not
npx --yes wrangler pages project list 2>/dev/null | grep -q " $PROJECT " || { echo "Pages project $PROJECT not found: stop"; exit 1; }
# deploy a clean copy: research notes (*.md) stay in the repo, never on the site
STAGE=$(mktemp -d); rsync -a --exclude='*.md' site/ "$STAGE/"
# /admin goes live ONLY when Cloudflare Access protects it: run with ACCESS_ON=1 after the Access app for markoboskotherapies.pages.dev/admin* exists
if [ "${ACCESS_ON:-0}" = "1" ]; then cp -R admin_pending/admin "$STAGE/admin"; fi
npx --yes wrangler pages deploy "$STAGE" --project-name "$PROJECT" --branch main --commit-dirty=true 2>&1 | grep -E "Uploading|https://|Success|rror" | head -6
sleep 5
for p in / /robots.txt /sitemap.xml /favicon.svg /img/room.jpg /img/setup.jpg; do curl -s -o /dev/null -w "https://$PROJECT.pages.dev$p -> %{http_code}\n" --max-time 25 "https://$PROJECT.pages.dev$p"; done

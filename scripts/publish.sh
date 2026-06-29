#!/usr/bin/env bash
# One-shot blog publish:
#   1. Run sync-content.sh (Obsidian DongLog → content/, dates, covers, index)
#   2. Commit any content changes
#   3. Push to GitHub (triggers GitHub Pages deploy)
#
# Triggered from Obsidian via the Shell Commands plugin.

set -euo pipefail

BLOG_DIR="/Users/djlim00/Desktop/GIt/dj-blog"
cd "$BLOG_DIR"

# Make sure Node 22 is on PATH for any sub-commands that might need it later.
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

echo "==> Syncing notes from Obsidian..."
bash "$BLOG_DIR/sync-content.sh"

if [[ -z "$(git status --porcelain content)" ]]; then
  echo "==> No content changes. Nothing to push."
  exit 0
fi

echo
echo "==> Committing content changes..."
git add content
TIMESTAMP="$(date '+%Y-%m-%d %H:%M')"
git commit -m "publish: $TIMESTAMP"

echo "==> Pushing to GitHub..."
git push

echo
echo "✅ Done. GitHub Pages will deploy in ~1-2 min."

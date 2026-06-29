#!/usr/bin/env bash
# Sync selected folders from Obsidian vault into Quartz content/
# Edit FOLDERS array to control which folders are published.

set -euo pipefail

VAULT="/Users/djlim00/Desktop/Obsidian/DJ's Life"
DEST="$(cd "$(dirname "$0")" && pwd)/content"

FOLDERS=(
  "🎓 대학교"
  "🎉 컨퍼런스"
  "😎 취준/📖개인공부"
  "😎 취준/📚유레카2기"
)

echo "==> Cleaning synced folders in $DEST (preserving index.md, .gitkeep, root files)"
find "$DEST" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true

for folder in "${FOLDERS[@]}"; do
  src="$VAULT/$folder"
  if [[ ! -d "$src" ]]; then
    echo "!! Skipping (not found): $src"
    continue
  fi
  echo "==> Copying: $folder"
  rsync -a \
    --max-size=50m \
    --exclude '.obsidian/' \
    --exclude '.trash/' \
    --exclude '*.excalidraw.md' \
    --exclude '*.base' \
    --exclude '*.pdf' \
    --exclude 'Lamda 개발.md' \
    "$src" "$DEST/"
done

echo "==> Sync complete (folders). Now copying referenced attachments..."
python3 "$(cd "$(dirname "$0")" && pwd)/sync-attachments.py"

echo "==> Injecting created/modified dates from Obsidian vault..."
python3 "$(cd "$(dirname "$0")" && pwd)/scripts/add-dates.py"

echo "==> Adding cover frontmatter (first embedded image)..."
python3 "$(cd "$(dirname "$0")" && pwd)/scripts/add-cover.py"

if [[ -d "$(cd "$(dirname "$0")" && pwd)/.quartz/plugins/recent-notes" ]]; then
  echo "==> Patching recent-notes widget for cover support..."
  node "$(cd "$(dirname "$0")" && pwd)/scripts/patch-recent-notes.mjs" || true
else
  echo "(skipping recent-notes patch — run 'npx quartz plugin install' first, then 'node scripts/patch-recent-notes.mjs')"
fi

echo "==> All done."

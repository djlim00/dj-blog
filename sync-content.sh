#!/usr/bin/env bash
# Sync the Obsidian DongLog folder into Quartz content/.
# DongLog is a single "publish" folder in the vault — its sub-folders are
# treated as blog categories and synced directly into content/<category>/.

set -euo pipefail

VAULT="/Users/djlim00/Desktop/Obsidian/DJ's Life"
DEST="$(cd "$(dirname "$0")" && pwd)/content"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Single source folder in Obsidian: DongLog/<Category>/<note>.md
# Its CONTENTS are synced directly into content/ (trailing slash flattens).
SOURCE_ROOT="$VAULT/DongLog"

echo "==> Cleaning synced folders in $DEST (preserving index.md, .gitkeep, root files)"
find "$DEST" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true

if [[ ! -d "$SOURCE_ROOT" ]]; then
  echo "!! Source folder not found: $SOURCE_ROOT"
  exit 1
fi

echo "==> Copying contents of: $SOURCE_ROOT"
rsync -a \
  --max-size=50m \
  --exclude '.obsidian/' \
  --exclude '.trash/' \
  --exclude '*.excalidraw.md' \
  --exclude '*.base' \
  --exclude '*.pdf' \
  "$SOURCE_ROOT/" "$DEST/"

echo "==> Sync complete. Now copying referenced attachments..."
python3 "$SCRIPT_DIR/sync-attachments.py"

echo "==> Injecting created/modified dates from Obsidian vault..."
python3 "$SCRIPT_DIR/scripts/add-dates.py"

echo "==> Adding cover frontmatter (first embedded image)..."
python3 "$SCRIPT_DIR/scripts/add-cover.py"

echo "==> Generating homepage (categories + recent post stream)..."
python3 "$SCRIPT_DIR/scripts/build-index.py"

if [[ -d "$SCRIPT_DIR/.quartz/plugins/recent-notes" ]]; then
  echo "==> Patching recent-notes widget for cover support..."
  node "$SCRIPT_DIR/scripts/patch-recent-notes.mjs" || true
else
  echo "(skipping recent-notes patch — run 'npx quartz plugin install' first, then 'node scripts/patch-recent-notes.mjs')"
fi

echo "==> All done."

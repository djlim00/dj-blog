#!/usr/bin/env bash
# Sync selected folders from Obsidian vault into Quartz content/
# Edit FOLDERS array to control which folders are published.

set -euo pipefail

VAULT="/Users/djlim00/Desktop/Obsidian/DJ's Life"
DEST="$(cd "$(dirname "$0")" && pwd)/content"

FOLDERS=(
  "🎓 대학교"
  "⭐️ 소프트웨어 마에스트로"
  "🎉 컨퍼런스"
)

echo "==> Cleaning $DEST (keeping .gitkeep)"
find "$DEST" -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true

for folder in "${FOLDERS[@]}"; do
  src="$VAULT/$folder"
  if [[ ! -d "$src" ]]; then
    echo "!! Skipping (not found): $src"
    continue
  fi
  echo "==> Copying: $folder"
  rsync -a \
    --exclude '.obsidian/' \
    --exclude '.trash/' \
    --exclude '*.excalidraw.md' \
    --exclude '*.base' \
    "$src" "$DEST/"
done

echo "==> Sync complete."

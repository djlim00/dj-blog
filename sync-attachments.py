#!/usr/bin/env python3
"""Copy only the attachments actually referenced by synced markdown files.

Run AFTER sync-content.sh has copied the selected folders into content/.
Scans every .md in content/, finds wikilink / markdown image / file references,
locates the matching file in the vault (recursively), and copies it into
content/_첨부파일/. Anything not referenced is skipped.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

VAULT = Path("/Users/djlim00/Desktop/Obsidian/DJ's Life")
CONTENT = Path(__file__).resolve().parent / "content"
DEST = CONTENT / "_첨부파일"

# Extensions we treat as attachments worth copying
ATTACHMENT_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp",
    ".mp4", ".mov", ".webm", ".m4v",
    ".mp3", ".wav", ".m4a", ".ogg",
}

MAX_FILE_BYTES = 50 * 1024 * 1024  # Skip individual attachments larger than 50MB

# ![[name]] or [[name]] with optional |alias and #anchor
WIKILINK_RE = re.compile(r"!?\[\[([^\[\]\|#]+?)(?:#[^\|\]]*)?(?:\|[^\]]*)?\]\]")
# ![alt](path) — capture path before optional " title"
MDLINK_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def extract_refs(md_text: str) -> set[str]:
    refs: set[str] = set()
    for m in WIKILINK_RE.finditer(md_text):
        refs.add(m.group(1).strip())
    for m in MDLINK_RE.finditer(md_text):
        refs.add(m.group(1).strip())
    return refs


def is_attachment(name: str) -> bool:
    return Path(name).suffix.lower() in ATTACHMENT_EXTS


def build_vault_index() -> dict[str, list[Path]]:
    """Map basename -> list of matching vault paths (excluding .obsidian, .trash)."""
    index: dict[str, list[Path]] = {}
    for p in VAULT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in {".obsidian", ".trash"} for part in p.parts):
            continue
        index.setdefault(p.name, []).append(p)
    return index


def resolve(ref: str, vault_index: dict[str, list[Path]]) -> Path | None:
    # Strip URL fragments / query if any
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    # Skip external URLs
    if ref.startswith(("http://", "https://", "mailto:")):
        return None
    name = Path(ref).name
    if not is_attachment(name):
        return None
    candidates = vault_index.get(name, [])
    if not candidates:
        return None
    # Prefer one inside _첨부파일 if multiple matches
    for c in candidates:
        if "_첨부파일" in c.parts:
            return c
    return candidates[0]


def main() -> int:
    if not CONTENT.exists():
        print(f"!! content folder missing: {CONTENT}", file=sys.stderr)
        return 1

    # Wipe any previously-copied attachment subtree
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    md_files = [p for p in CONTENT.rglob("*.md") if "_첨부파일" not in p.parts]
    print(f"==> Scanning {len(md_files)} markdown files for attachment references")

    all_refs: set[str] = set()
    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        all_refs.update(extract_refs(text))

    vault_index = build_vault_index()

    copied = 0
    missing: list[str] = []
    skipped_large: list[tuple[str, int]] = []
    for ref in sorted(all_refs):
        src = resolve(ref, vault_index)
        if src is None:
            if is_attachment(ref):
                missing.append(ref)
            continue
        size = src.stat().st_size
        if size > MAX_FILE_BYTES:
            skipped_large.append((src.name, size))
            continue
        target = DEST / src.name
        if target.exists():
            continue
        shutil.copy2(src, target)
        copied += 1

    print(f"==> Copied {copied} referenced attachment(s) to {DEST}")
    if skipped_large:
        print(f"!! Skipped {len(skipped_large)} file(s) over {MAX_FILE_BYTES // (1024*1024)}MB:")
        for name, size in skipped_large:
            print(f"   - {name} ({size // (1024*1024)}MB)")
    if missing:
        print(f"!! {len(missing)} attachment reference(s) could not be resolved:")
        for m in missing[:20]:
            print(f"   - {m}")
        if len(missing) > 20:
            print(f"   ... and {len(missing) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())

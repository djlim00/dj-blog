#!/usr/bin/env python3
"""Add `cover:` frontmatter (first embedded image basename) to each note.

Scans content/**/*.md, finds the first image embed (Obsidian wikilink or
Markdown image), and inserts `cover: <basename>` into the frontmatter if
the image file exists in `content/_첨부파일/`. Files that already have
`cover:` are left untouched.

The cover value is just the basename (e.g. `Pasted image 20250601163053.png`).
The patched recent-notes widget resolves it to `_첨부파일/<basename>`.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
ATTACHMENT_DIR = CONTENT_DIR / "_첨부파일"

IMG_EXTS = ("png", "jpg", "jpeg", "gif", "webp", "svg", "avif")
EXT_GROUP = "|".join(IMG_EXTS)

WIKILINK_IMG = re.compile(
    rf"!\[\[([^\]|]+\.(?:{EXT_GROUP}))(?:\|[^\]]*)?\]\]",
    re.IGNORECASE,
)
MD_IMG = re.compile(
    rf"!\[[^\]]*\]\(([^)]+\.(?:{EXT_GROUP}))\)",
    re.IGNORECASE,
)


def find_first_image(content: str) -> str | None:
    earliest_pos = -1
    earliest_name: str | None = None

    for match in WIKILINK_IMG.finditer(content):
        if earliest_pos == -1 or match.start() < earliest_pos:
            earliest_pos = match.start()
            earliest_name = os.path.basename(match.group(1).strip())

    for match in MD_IMG.finditer(content):
        url = match.group(1).strip()
        if url.startswith(("http://", "https://", "data:")):
            continue
        if earliest_pos == -1 or match.start() < earliest_pos:
            earliest_pos = match.start()
            earliest_name = os.path.basename(url)

    return earliest_name


def split_frontmatter(content: str) -> tuple[str | None, str]:
    if not content.startswith("---\n") and not content.startswith("---\r\n"):
        return None, content
    end = content.find("\n---\n", 4)
    if end == -1:
        end_crlf = content.find("\r\n---\r\n", 4)
        if end_crlf == -1:
            return None, content
        return content[4:end_crlf], content[end_crlf + 7:]
    return content[4:end], content[end + 5:]


def already_has_cover(frontmatter: str | None) -> bool:
    if not frontmatter:
        return False
    return bool(re.search(r"^cover:\s*\S", frontmatter, re.MULTILINE))


def yaml_escape(value: str) -> str:
    if re.search(r"[:#\"'\\{}\[\],&*?|<>=!%@`]", value) or value.strip() != value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def slugify_filename(name: str) -> str:
    """Mirror Quartz's slugifyFilePath: slugify stem, preserve extension."""
    dot = name.rfind(".")
    if dot <= 0:
        stem, ext = name, ""
    else:
        stem, ext = name[:dot], name[dot:]
    slug = (
        stem.replace(" ", "-")
        .replace("\t", "-")
        .replace("&", "-and-")
        .replace("%", "-percent")
        .replace("?", "")
        .replace("#", "")
    )
    slug = re.sub(r"[<>:\"|*]", "", slug)
    return slug.lower() + ext


def attachment_exists(name: str) -> bool:
    return (ATTACHMENT_DIR / name).is_file()


def remove_cover_line(frontmatter: str) -> str:
    return re.sub(r"^cover:[^\n]*\n?", "", frontmatter, flags=re.MULTILINE)


def process_file(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    frontmatter, body = split_frontmatter(content)

    search_text = body if frontmatter is not None else content
    cover = find_first_image(search_text)
    if not cover:
        return False
    if not attachment_exists(cover):
        return False

    cover_slug = slugify_filename(cover)
    cover_field = f"cover: {yaml_escape(cover_slug)}\n"

    if frontmatter is None:
        new_content = f"---\n{cover_field}---\n\n{content}"
    else:
        cleaned_fm = remove_cover_line(frontmatter).rstrip("\n")
        new_fm = (cleaned_fm + "\n" if cleaned_fm else "") + cover_field
        new_content = f"---\n{new_fm}---\n{body}"

    if new_content == content:
        return False

    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    if not CONTENT_DIR.is_dir():
        print(f"!! Content dir not found: {CONTENT_DIR}", file=sys.stderr)
        return 1

    added = 0
    skipped = 0
    for md in CONTENT_DIR.rglob("*.md"):
        if md.name == "index.md":
            continue
        if "_첨부파일" in md.parts:
            continue
        if process_file(md):
            added += 1
        else:
            skipped += 1

    print(f"==> add-cover: added cover to {added} files (skipped {skipped})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

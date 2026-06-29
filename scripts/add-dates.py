#!/usr/bin/env python3
"""Inject `created` and `modified` frontmatter dates from the Obsidian vault.

For each `.md` file under `content/`, we look up the corresponding source file
in the Obsidian vault and read its filesystem birth time (creation) and mtime
(modification). We write these as ISO-8601 strings into the file's frontmatter.

`stat -f %B` (birth time) and `%m` (mtime) are macOS-specific. Run on macOS.

The Quartz `created-modified-date` plugin reads `frontmatter.created` and
`frontmatter.modified`, so setting these makes Quartz use the real Obsidian
authoring times — independent of git commit history.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
VAULT = Path("/Users/djlim00/Desktop/Obsidian/DJ's Life")

# All content under content/ is synced from $VAULT/DongLog/.
# A note at content/<X>/.../foo.md maps to $VAULT/DongLog/<X>/.../foo.md.
VAULT_ROOT = VAULT / "DongLog"


def stat_field(path: Path, fmt: str) -> int | None:
    """Run `stat -f <fmt>` on macOS to read a single timestamp."""
    try:
        result = subprocess.run(
            ["stat", "-f", fmt, str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def to_iso(ts: int) -> str:
    """Convert Unix timestamp to ISO-8601 string in local timezone."""
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def resolve_vault_path(content_path: Path) -> Path | None:
    """Map content/<rel...> -> $VAULT/DongLog/<rel...>."""
    rel = content_path.relative_to(CONTENT_DIR)
    if not rel.parts:
        return None
    return VAULT_ROOT.joinpath(*rel.parts)


def split_frontmatter(content: str) -> tuple[str | None, str]:
    if not content.startswith("---\n"):
        return None, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return None, content
    return content[4:end], content[end + 5:]


def remove_date_lines(frontmatter: str) -> str:
    return re.sub(
        r"^(created|modified|date|publishDate):[^\n]*\n?",
        "",
        frontmatter,
        flags=re.MULTILINE,
    )


def process_file(content_path: Path) -> str:
    vault_path = resolve_vault_path(content_path)
    if not vault_path or not vault_path.exists():
        return "no-source"

    created_ts = stat_field(vault_path, "%B")
    modified_ts = stat_field(vault_path, "%m")
    if created_ts is None or modified_ts is None:
        return "stat-failed"

    created_iso = to_iso(created_ts)
    modified_iso = to_iso(modified_ts)

    content = content_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(content)

    date_block = f"created: {created_iso}\nmodified: {modified_iso}\n"

    if frontmatter is None:
        new_content = f"---\n{date_block}---\n\n{content}"
    else:
        cleaned = remove_date_lines(frontmatter).rstrip("\n")
        new_fm = (cleaned + "\n" if cleaned else "") + date_block
        new_content = f"---\n{new_fm}---\n{body}"

    if new_content == content:
        return "unchanged"

    content_path.write_text(new_content, encoding="utf-8")
    return "updated"


def main() -> int:
    if sys.platform != "darwin":
        print("!! add-dates: macOS-only (stat -f). Skipping.", file=sys.stderr)
        return 0
    if not CONTENT_DIR.is_dir():
        print(f"!! Content dir not found: {CONTENT_DIR}", file=sys.stderr)
        return 1

    counts = {"updated": 0, "unchanged": 0, "no-source": 0, "stat-failed": 0}
    for md in CONTENT_DIR.rglob("*.md"):
        if md.name == "index.md" and md.parent == CONTENT_DIR:
            continue
        if "_첨부파일" in md.parts:
            continue
        result = process_file(md)
        counts[result] = counts.get(result, 0) + 1

    print(
        f"==> add-dates: updated {counts['updated']}, "
        f"unchanged {counts['unchanged']}, "
        f"no-source {counts['no-source']}, "
        f"stat-failed {counts['stat-failed']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

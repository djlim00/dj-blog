#!/usr/bin/env python3
"""Generate the homepage (content/index.md): hero + categories + post stream.

The homepage has two sections:
- Hero (kept verbatim from existing index.md, above the AUTO marker)
- Auto block (categories grid + recent post cards with Prologue excerpts)

Only the auto block is rewritten — the user's hero stays intact across syncs.
If the marker is missing, the file is treated as hero-only and the auto block
is appended; subsequent runs replace just the auto block.
"""

from __future__ import annotations

import html
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
INDEX = CONTENT / "index.md"

AUTO_MARKER = "<!-- AUTO-GENERATED BELOW: managed by scripts/build-index.py -->"
RECENT_LIMIT = 10
PREVIEW_CHAR_LIMIT = 220
PROLOGUE_BULLETS_MAX = 4

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
TITLE_FM_RE = re.compile(r"^title:\s*(.+?)\s*$", re.M)
AUTHOR_FM_RE = re.compile(r"^author:\s*(.+?)\s*$", re.M)
CREATED_FM_RE = re.compile(r"^created:\s*(.+?)\s*$", re.M)
MODIFIED_FM_RE = re.compile(r"^modified:\s*(.+?)\s*$", re.M)

# Match a Prologue/intro section: "## Prologue" through to next "## ..." or EOF.
PROLOGUE_SECTION_RE = re.compile(
    r"^##+\s*(?:Prologue|prologue|개요|머리말|소개|Intro|intro)\s*\n(?P<body>.*?)(?=\n##+\s|\Z)",
    re.S | re.M,
)

DEFAULT_AUTHOR = "djlim00"


def slug_segment(name: str) -> str:
    """Mirror Quartz slugifyPath for a single path segment (no extension handling)."""
    return (
        name.replace(" ", "-")
        .replace("&", "-and-")
        .replace("%", "-percent")
        .replace("?", "")
        .replace("#", "")
    ).translate(str.maketrans("", "", '<>:"|*')).lower()


def slugify_filename(name: str) -> str:
    dot = name.rfind(".")
    if dot <= 0:
        return slug_segment(name)
    return slug_segment(name[:dot]) + name[dot:]


def slug_for_post(md_path: Path) -> str:
    rel = md_path.relative_to(CONTENT)
    parts = list(rel.parts)
    # last part is filename with .md — strip ext and slugify stem
    last = parts[-1]
    stem = last[: -len(".md")] if last.endswith(".md") else last
    parts[-1] = slug_segment(stem)
    parts[:-1] = [slug_segment(p) for p in parts[:-1]]
    return "./" + "/".join(parts)


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    fm_text = m.group(1)
    fm: dict[str, str] = {}
    for line in fm_text.split("\n"):
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, raw[m.end():]


def strip_md(text: str) -> str:
    """Light markdown-to-plaintext for previews."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"!\[\[[^\]]+\]\]", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"[#>*_~]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_bullets(prologue_body: str, limit: int) -> list[str]:
    """Pull leading bullet items from a prologue section (Obsidian style)."""
    bullets: list[str] = []
    for line in prologue_body.split("\n"):
        m = re.match(r"^\s*[-*+]\s+(.*\S.*)$", line)
        if m:
            cleaned = strip_md(m.group(1))
            if cleaned:
                bullets.append(cleaned)
                if len(bullets) >= limit:
                    break
        elif bullets and line.strip() == "":
            continue
        elif bullets:
            break
    return bullets


def extract_preview(body: str) -> tuple[list[str], str]:
    """Return (bullets, plain_paragraph). Bullets take precedence if present."""
    m = PROLOGUE_SECTION_RE.search(body)
    section = m.group("body") if m else body

    bullets = extract_bullets(section, PROLOGUE_BULLETS_MAX)
    if bullets:
        return bullets, ""

    plain = strip_md(section)[:PREVIEW_CHAR_LIMIT].rstrip()
    if plain and len(strip_md(section)) > PREVIEW_CHAR_LIMIT:
        plain += "…"
    return [], plain


def parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def relative_category(md_path: Path) -> str:
    """The top-level folder under content/ — used as the post's category label."""
    rel = md_path.relative_to(CONTENT)
    return rel.parts[0] if len(rel.parts) > 1 else "Uncategorized"


def parse_post(md_path: Path) -> dict | None:
    try:
        raw = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    fm, body = parse_frontmatter(raw)
    title = fm.get("title") or md_path.stem
    author = fm.get("author") or DEFAULT_AUTHOR
    created = parse_date(fm.get("created"))
    modified = parse_date(fm.get("modified"))
    sort_dt = modified or created or datetime.fromtimestamp(md_path.stat().st_mtime).astimezone()
    display_dt = created or modified or sort_dt
    bullets, paragraph = extract_preview(body)

    return {
        "path": md_path,
        "title": title,
        "author": author,
        "category": relative_category(md_path),
        "date": display_dt,
        "sort_dt": sort_dt,
        "bullets": bullets,
        "paragraph": paragraph,
        "slug": slug_for_post(md_path),
    }


def render_post_card(post: dict) -> str:
    date_str = post["date"].strftime("%Y-%m-%d")
    title_esc = html.escape(post["title"])
    author_esc = html.escape(post["author"])
    category_esc = html.escape(post["category"])
    category_slug = slug_segment(post["category"])

    if post["bullets"]:
        preview_html = (
            "<ul class=\"post-card-bullets\">"
            + "".join(f"<li>{html.escape(b)}</li>" for b in post["bullets"])
            + "</ul>"
        )
    elif post["paragraph"]:
        preview_html = f"<p class=\"post-card-paragraph\">{html.escape(post['paragraph'])}</p>"
    else:
        preview_html = ""

    return f'''<article class="post-card">
  <h2 class="post-card-title"><a href="{post['slug']}">{title_esc}</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">📅 {date_str}</span>
    <span class="post-card-author">👤 {author_esc}</span>
    <a class="post-card-category" href="./{category_slug}/">🏷 {category_esc}</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    {preview_html}
  </div>
  <p class="post-card-readall"><a href="{post['slug']}">📖 Read All →</a></p>
</article>'''


def render_categories(categories: dict[str, int]) -> str:
    if not categories:
        return ""
    items = []
    for name, count in sorted(categories.items(), key=lambda kv: (-kv[1], kv[0])):
        slug = slug_segment(name)
        items.append(
            f'<a class="cat-chip" href="./{slug}/">'
            f'<span class="cat-chip-name">{html.escape(name)}</span>'
            f'<span class="cat-chip-count">{count}</span>'
            f'</a>'
        )
    return '<nav class="cat-grid">' + "".join(items) + "</nav>"


def build_auto_block(posts: list[dict]) -> str:
    if not posts:
        return (
            f"{AUTO_MARKER}\n\n"
            "_아직 게시된 글이 없습니다. Obsidian의 `DongLog/` 폴더에 노트를 추가한 뒤_\n"
            "_`./sync-content.sh`를 실행하면 자동으로 이곳에 카테고리와 최근 글이 채워집니다._\n"
        )

    categories: dict[str, int] = {}
    for p in posts:
        categories[p["category"]] = categories.get(p["category"], 0) + 1

    recent = posts[:RECENT_LIMIT]

    cat_html = render_categories(categories)
    cards_html = "\n\n".join(render_post_card(p) for p in recent)

    return f'''{AUTO_MARKER}

## 📂 Categories

{cat_html}

## 📰 Recent Posts

<div class="post-stream">

{cards_html}

</div>
'''


def split_existing(index_text: str) -> str:
    """Return only the portion above the AUTO marker (hero). If marker missing, keep all."""
    idx = index_text.find(AUTO_MARKER)
    if idx == -1:
        return index_text.rstrip() + "\n\n"
    return index_text[:idx]


def main() -> int:
    if not CONTENT.is_dir():
        print(f"!! content folder missing: {CONTENT}", file=sys.stderr)
        return 1

    md_files = [
        p for p in CONTENT.rglob("*.md")
        if "_첨부파일" not in p.parts and p.name != "index.md"
    ]

    posts: list[dict] = []
    for md in md_files:
        info = parse_post(md)
        if info:
            posts.append(info)

    posts.sort(key=lambda p: p["sort_dt"], reverse=True)

    if not INDEX.exists():
        hero = "---\ntitle: DJ's Blog\n---\n\nHey there 👋\n\n"
    else:
        hero = split_existing(INDEX.read_text(encoding="utf-8"))

    new_index = hero.rstrip() + "\n\n" + build_auto_block(posts) + "\n"
    INDEX.write_text(new_index, encoding="utf-8")

    print(
        f"==> build-index: wrote {INDEX} — {len(posts)} post(s), "
        f"{len({p['category'] for p in posts})} categor(ies)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

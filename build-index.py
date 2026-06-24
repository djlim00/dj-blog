#!/usr/bin/env python3
"""Generate content/index.md with category list + recent post cards.

Scans all .md in content/ (excluding _첨부파일 and index.md), extracts
title, first image, preview text, and modified date for each, then writes
a homepage with categories on top and recent post cards below.

Cards have thumbnail on the right (matching the user's reference image).
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent / "content"
INDEX = CONTENT / "index.md"
RECENT_LIMIT = 12

WIKILINK_IMG = re.compile(r"!\[\[([^\[\]\|#]+?\.(?:png|jpe?g|gif|webp|svg))(?:#[^\|\]]*)?(?:\|[^\]]*)?\]\]", re.I)
MDLINK_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+\.(?:png|jpe?g|gif|webp|svg))\)", re.I)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
TITLE_FM_RE = re.compile(r"^title:\s*(.+?)$", re.M)

CATEGORIES = [
    ("🎓 대학교", "🎓 대학교", "학교 수업 노트와 과제"),
    ("⭐️ 소프트웨어 마에스트로", "⭐️ 소프트웨어 마에스트로", "소마 활동 기록"),
    ("🎉 컨퍼런스", "🎉 컨퍼런스", "참석한 컨퍼런스 정리"),
    ("📖개인공부", "📖개인공부", "개인 공부 기록"),
    ("📚유레카2기", "📚유레카2기", "유레카 2기 활동"),
]


def strip_md(text: str) -> str:
    """Crude markdown-to-plaintext for previews."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)        # code blocks
    text = re.sub(r"`[^`]*`", "", text)                       # inline code
    text = re.sub(r"!\[\[[^\]]+\]\]", "", text)               # embeds
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)          # md images
    text = re.sub(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)      # md links
    text = re.sub(r"[#>*_~`]+", "", text)                     # md symbols
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_post(md_path: Path):
    try:
        raw = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    fm_match = FRONTMATTER_RE.match(raw)
    body = raw[fm_match.end():] if fm_match else raw
    fm_block = fm_match.group(1) if fm_match else ""

    title_m = TITLE_FM_RE.search(fm_block)
    title = title_m.group(1).strip().strip('"').strip("'") if title_m else md_path.stem

    img = None
    for m in WIKILINK_IMG.finditer(body):
        img = m.group(1).strip()
        break
    if not img:
        for m in MDLINK_IMG.finditer(body):
            img = m.group(1).strip()
            break

    preview = strip_md(body)[:120].strip()
    if preview:
        preview = preview + "…"

    mtime = md_path.stat().st_mtime
    return {
        "path": md_path,
        "title": title,
        "image": img,
        "preview": preview,
        "mtime": mtime,
    }


def slug_path(md_path: Path) -> str:
    """Build href from content/.../X.md → ./X/X (Quartz slugifies)."""
    rel = md_path.relative_to(CONTENT).with_suffix("")
    parts = [str(p).replace(" ", "-") for p in rel.parts]
    return "./" + "/".join(parts)


def image_href(image_name: str) -> str:
    return "./_첨부파일/" + image_name.replace(" ", "%20")


def render_card(post: dict) -> str:
    href = slug_path(post["path"])
    title = html.escape(post["title"])
    preview = html.escape(post["preview"])
    from datetime import datetime
    date_str = datetime.fromtimestamp(post["mtime"]).strftime("%Y.%m.%d")

    if post["image"]:
        thumb = f'<img src="{image_href(post["image"])}" alt=""/>'
    else:
        initial = html.escape(post["title"][:2])
        thumb = f'<div class="post-card-thumb-fallback">{initial}</div>'

    return f'''<a href="{href}" class="post-card">
  <div class="post-card-text">
    <h3>{title}</h3>
    <p>{preview}</p>
    <span class="post-card-date">{date_str}</span>
  </div>
  <div class="post-card-thumb">{thumb}</div>
</a>'''


def render_index(recent: list[dict]) -> str:
    cat_lines = "\n".join(
        f"- [[{link}|{label}]] — {desc}" for link, label, desc in CATEGORIES
    )
    cards = "\n".join(render_card(p) for p in recent)

    return f'''---
title: DJ's Blog
---

<style>
.post-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin: 2rem 0;
}}
.post-card {{
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 1.1rem 1.25rem;
  border-radius: 12px;
  background: var(--lightgray);
  text-decoration: none !important;
  transition: transform 0.15s ease, background 0.15s ease;
  color: var(--darkgray);
}}
.post-card:hover {{
  transform: translateY(-2px);
  background: var(--highlight);
}}
.post-card-text {{
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}}
.post-card-text h3 {{
  margin: 0;
  font-size: 1.15rem;
  color: var(--dark);
  font-weight: 700;
  line-height: 1.35;
}}
.post-card-text p {{
  margin: 0;
  font-size: 0.92rem;
  color: var(--gray);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.post-card-date {{
  font-size: 0.78rem;
  color: var(--gray);
  margin-top: auto;
}}
.post-card-thumb {{
  flex: 0 0 110px;
  width: 110px;
  height: 110px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--light);
  display: flex;
  align-items: center;
  justify-content: center;
}}
.post-card-thumb img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
}}
.post-card-thumb-fallback {{
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--secondary);
  text-align: center;
  padding: 0.5rem;
}}
@media (max-width: 600px) {{
  .post-card-thumb {{
    flex-basis: 80px;
    width: 80px;
    height: 80px;
  }}
}}
.categories {{
  margin: 1rem 0 2rem;
}}
</style>

안녕하세요. 임동주의 개인 블로그입니다.

기록하고 공유하고 싶은 글들을 모아둔 공간입니다.

## 카테고리

<div class="categories">

{cat_lines}

</div>

## 최근 글

<div class="post-grid">

{cards}

</div>

## Links

- GitHub: [@djlim00](https://github.com/djlim00)
'''


def main() -> int:
    if not CONTENT.exists():
        print(f"!! content folder missing: {CONTENT}", file=sys.stderr)
        return 1

    md_files = [
        p for p in CONTENT.rglob("*.md")
        if "_첨부파일" not in p.parts and p.name != "index.md"
    ]

    posts = []
    for md in md_files:
        info = parse_post(md)
        if info:
            posts.append(info)

    posts.sort(key=lambda p: p["mtime"], reverse=True)
    recent = posts[:RECENT_LIMIT]

    INDEX.write_text(render_index(recent), encoding="utf-8")
    print(f"==> Wrote {INDEX} with {len(recent)} recent post card(s) (from {len(posts)} total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

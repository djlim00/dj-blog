#!/usr/bin/env node
/**
 * Patch the installed `recent-notes` plugin dist to render a cover thumbnail
 * read from `page.frontmatter.cover`. The cover value is the basename of an
 * image inside `content/_첨부파일/`.
 *
 * This patch is idempotent: it sets a marker comment so re-runs are no-ops.
 * If `npx quartz plugin install` is run again, this script should be re-run
 * to re-apply the patch (sync-content.sh wires that up).
 */

import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, "..")
const target = path.join(
  repoRoot,
  ".quartz",
  "plugins",
  "recent-notes",
  "dist",
  "components",
  "index.js",
)

const MARKER = "/* PATCHED_COVER_SUPPORT_v1 */"

if (!fs.existsSync(target)) {
  console.error(`!! recent-notes dist not found: ${target}`)
  console.error("   Run `npx quartz plugin install` first.")
  process.exit(1)
}

let src = fs.readFileSync(target, "utf-8")

if (src.includes(MARKER)) {
  console.log("==> patch-recent-notes: already patched, skipping")
  process.exit(0)
}

const helper = `${MARKER}
function __coverUrl(slug, cover) {
  if (!cover) return null;
  const parts = String(slug || "").split("/").filter((p) => p && p !== "index");
  const up = parts.length === 0 ? "./" : "../".repeat(parts.length);
  const enc = String(cover).split("/").map(encodeURIComponent).join("/");
  return up + "_%EC%B2%A8%EB%B6%80%ED%8C%8C%EC%9D%BC/" + enc;
}
`

const sectionOpen = `children: /* @__PURE__ */ u2("div", { class: "section", children: [`
if (!src.includes(sectionOpen)) {
  console.error("!! Could not locate render marker in recent-notes dist.")
  console.error("   The plugin version may have changed — update this patcher.")
  process.exit(1)
}

const injection =
  sectionOpen +
  `\n          page.frontmatter && page.frontmatter.cover && /* @__PURE__ */ u2("img", { class: "cover", loading: "lazy", src: __coverUrl(slug2, page.frontmatter.cover), alt: "" }),`

src = helper + "\n" + src.replace(sectionOpen, injection)

fs.writeFileSync(target, src)
console.log("==> patch-recent-notes: patched cover thumbnail rendering")

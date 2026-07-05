#!/usr/bin/env node
/**
 * Patch obsidian-flavored-markdown to treat .svg as a renderable image.
 * The plugin's image-extension allow-list omits SVG, so `![[foo.svg]]`
 * wikilinks render as broken embeds instead of <img> tags.
 *
 * Idempotent — checks for a marker before rewriting.
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
  "obsidian-flavored-markdown",
  "dist",
  "index.js",
)

const MARKER = "/* PATCHED_SVG_v1 */"

if (!fs.existsSync(target)) {
  console.error(`!! obsidian-flavored-markdown dist not found: ${target}`)
  console.error("   Run `npx quartz plugin install` first.")
  process.exit(1)
}

let src = fs.readFileSync(target, "utf-8")

if (src.includes(MARKER)) {
  console.log("==> patch-ofm-svg: already patched, skipping")
  process.exit(0)
}

const from = '".jxl", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"'
const to = '".jxl", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"'

if (!src.includes(from)) {
  console.error("!! Could not locate image-extension list — plugin may have changed.")
  process.exit(1)
}

src = MARKER + "\n" + src.replace(from, to)
fs.writeFileSync(target, src)
console.log("==> patch-ofm-svg: added .svg to renderable image extensions")

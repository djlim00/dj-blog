import { i18n } from "../i18n"
import { FullSlug, getFileExtension, joinSegments, pathToRoot } from "../util/path"
import { CSSResourceToStyleElement, JSResourceToScriptElement } from "../util/resources"
import { googleFontHref, googleFontSubsetHref } from "../util/theme"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { unescapeHTML } from "../util/escape"
import { CustomOgImagesEmitterName } from "../../.quartz/plugins"
export default (() => {
  const Head: QuartzComponent = ({
    cfg,
    fileData,
    externalResources,
    ctx,
  }: QuartzComponentProps) => {
    const titleSuffix = cfg.pageTitleSuffix ?? ""
    const title =
      (fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title) + titleSuffix
    const description =
      fileData.frontmatter?.socialDescription ??
      fileData.frontmatter?.description ??
      unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)

    const { css, js, additionalHead } = externalResources

    const url = new URL(`https://${cfg.baseUrl ?? "example.com"}`)
    const path = url.pathname as FullSlug
    const baseDir = fileData.slug === "404" ? path : pathToRoot(fileData.slug!)
    const iconPath = joinSegments(baseDir, "static/icon.png")

    // Url of current page
    const socialUrl =
      fileData.slug === "404" ? url.toString() : joinSegments(url.toString(), fileData.slug!)

    const usesCustomOgImage = ctx.cfg.plugins.emitters.some(
      (e) => e.name === CustomOgImagesEmitterName,
    )
    const ogImageDefaultPath = `https://${cfg.baseUrl}/static/og-image.png`

    const coreStylesheet = css[0]?.content
    const coreScript = js.find(
      (r) => r.loadTime === "beforeDOMReady" && r.contentType === "external",
    )

    return (
      <head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        {coreStylesheet && <link rel="preload" href={coreStylesheet} as="style" />}
        {coreScript && coreScript.contentType === "external" && (
          <link rel="preload" href={coreScript.src} as="script" />
        )}
        {cfg.theme.cdnCaching && cfg.theme.fontOrigin === "googleFonts" && (
          <>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" />
            <link rel="stylesheet" href={googleFontHref(cfg.theme)} />
            {cfg.theme.typography.title && (
              <link rel="stylesheet" href={googleFontSubsetHref(cfg.theme, cfg.pageTitle)} />
            )}
          </>
        )}
        <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossOrigin="anonymous" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <meta name="og:site_name" content={cfg.pageTitle}></meta>
        <meta property="og:title" content={title} />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta property="og:description" content={description} />
        <meta property="og:image:alt" content={description} />

        {!usesCustomOgImage && (
          <>
            <meta property="og:image" content={ogImageDefaultPath} />
            <meta property="og:image:url" content={ogImageDefaultPath} />
            <meta name="twitter:image" content={ogImageDefaultPath} />
            <meta
              property="og:image:type"
              content={`image/${getFileExtension(ogImageDefaultPath) ?? "png"}`}
            />
          </>
        )}

        {cfg.baseUrl && (
          <>
            <meta property="twitter:domain" content={cfg.baseUrl}></meta>
            <meta property="og:url" content={socialUrl}></meta>
            <meta property="twitter:url" content={socialUrl}></meta>
          </>
        )}

        <link rel="icon" href={iconPath} />
        <meta name="description" content={description} />
        <meta name="generator" content="Quartz" />

        {css.map((resource) => CSSResourceToStyleElement(resource, true))}
        {js
          .filter((resource) => resource.loadTime === "beforeDOMReady")
          .map((res) => JSResourceToScriptElement(res, true))}
        {additionalHead.map((resource) => {
          if (typeof resource === "function") {
            return resource(fileData)
          } else {
            return resource
          }
        })}
        {/* Global top navigation bar — injected on load and on SPA nav. */}
        <script
          data-persist="true"
          dangerouslySetInnerHTML={{
            __html: `
(function () {
  function computeBase() {
    // Use basepath from body (set by Quartz Head): '' for localhost, '/dj-blog' for GH Pages.
    var basepath = document.body.dataset.basepath || '';
    return basepath + '/';
  }
  function ensureTopNav() {
    var existing = document.getElementById('site-topnav');
    if (existing) existing.remove();
    var base = computeBase();
    var links = [
      { href: base, label: '🏠 메인', slug: '' },
      { href: base + 'archives', label: '📚 아카이브', slug: 'archives' },
      { href: base + 'about', label: '👤 About me', slug: 'about' },
    ];
    var curSlug = document.body.dataset.slug || '';
    var nav = document.createElement('nav');
    nav.id = 'site-topnav';
    nav.setAttribute('aria-label', 'Site navigation');
    var brand = document.createElement('a');
    brand.className = 'topnav-brand';
    brand.href = base;
    brand.textContent = "Dong-Log";
    nav.appendChild(brand);
    var list = document.createElement('div');
    list.className = 'topnav-links';
    links.forEach(function (l) {
      var a = document.createElement('a');
      a.className = 'topnav-link internal';
      a.href = l.href;
      a.textContent = l.label;
      if (curSlug === l.slug || (curSlug === '' && l.slug === '')) {
        a.classList.add('active');
      }
      list.appendChild(a);
    });
    nav.appendChild(list);
    document.body.prepend(nav);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureTopNav);
  } else {
    ensureTopNav();
  }
  document.addEventListener('nav', ensureTopNav);

  // Force-expand all explorer folders when folderDefaultState="open".
  // The quartz-community/explorer plugin ignores that option at runtime;
  // we watch its rendering with a MutationObserver and add the .open class
  // to every .folder-outer that appears.
  function expandFolderNodes(root) {
    (root || document).querySelectorAll('.explorer[data-collapsed="open"] .folder-outer').forEach(function (el) {
      el.classList.add('open');
    });
  }
  function watchExplorer() {
    document.querySelectorAll('.explorer[data-collapsed="open"] .explorer-ul').forEach(function (ul) {
      if (ul.__expandObserver) return;
      var obs = new MutationObserver(function () {
        expandFolderNodes(ul);
      });
      obs.observe(ul, { childList: true, subtree: true });
      ul.__expandObserver = obs;
      expandFolderNodes(ul);
    });
  }
  document.addEventListener('nav', watchExplorer);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', watchExplorer);
  } else {
    watchExplorer();
  }

  // Global categories widget in the right sidebar on ALL pages.
  // Reads Quartz's global fetchData (contentIndex.json) and groups posts
  // by top-level folder, using each folder-index entry's title as the
  // category display name.
  var SKIP_ROOT_SLUGS = { index: 1, about: 1, archives: 1 };
  async function ensureCategoriesWidget() {
    var sidebar = document.querySelector('.sidebar.right');
    if (!sidebar) return;
    var existing = document.getElementById('homepage-categories-widget');
    if (existing) existing.remove();
    try {
      if (typeof fetchData === 'undefined') return;
      var data = await fetchData;
      if (!data) return;
      var content = data.content || data;
      var folders = {};
      Object.keys(content).forEach(function (slug) {
        if (SKIP_ROOT_SLUGS[slug]) return;
        if (slug.indexOf('tags/') === 0) return;
        var parts = slug.split('/');
        if (parts.length < 2) return;
        var top = parts[0];
        if (!folders[top]) folders[top] = { title: top, count: 0 };
        var isFolderIndex = parts.length === 2 && parts[1] === 'index';
        if (isFolderIndex) {
          folders[top].title = (content[slug] && content[slug].title) || top;
        } else {
          folders[top].count += 1;
        }
      });
      var entries = Object.keys(folders).map(function (k) { return [k, folders[k]]; });
      if (entries.length === 0) return;
      entries.sort(function (a, b) {
        return b[1].count - a[1].count || a[0].localeCompare(b[0]);
      });
      var basepath = document.body.dataset.basepath || '';
      var widget = document.createElement('aside');
      widget.id = 'homepage-categories-widget';
      var html = '<div class="cat-widget-title">카테고리</div><nav class="cat-grid">';
      entries.forEach(function (e) {
        var slug = e[0];
        var info = e[1];
        var href = basepath + '/' + slug + '/';
        html += '<a class="cat-chip" href="' + href + '">' +
          '<span class="cat-chip-name">' + info.title + '</span>' +
          '<span class="cat-chip-count">' + info.count + '</span>' +
          '</a>';
      });
      html += '</nav>';
      widget.innerHTML = html;
      sidebar.appendChild(widget);
    } catch (e) {
      console.error('[Categories] failed:', e);
    }
  }
  document.addEventListener('nav', ensureCategoriesWidget);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureCategoriesWidget);
  } else {
    ensureCategoriesWidget();
  }
})();
`,
          }}
        />
      </head>
    )
  }

  return Head
}) satisfies QuartzComponentConstructor

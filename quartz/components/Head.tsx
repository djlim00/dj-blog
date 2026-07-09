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
  // Remove any stale top navbar left over from previous versions — the left
  // icon rail now owns Home/Archives/About navigation.
  var staleNav = document.getElementById('site-topnav');
  if (staleNav) staleNav.remove();

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
  // Dedupe concurrent callers: nav and DOMContentLoaded can both fire, and the
  // async fetchData await previously created a race where two calls each saw
  // "no existing widget" and both appended one.
  var _catWidgetPending = false;
  async function ensureCategoriesWidget() {
    if (_catWidgetPending) return;
    _catWidgetPending = true;
    try {
      var sidebar = document.querySelector('.sidebar.right');
      if (!sidebar) return;
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
      // Use the same relative-root computation the rail uses. Absolute paths
      // built from data-basepath break on localhost (server at /) and depend
      // on the deploy path being set correctly.
      var root = computeRoot();
      var widget = document.createElement('aside');
      widget.id = 'homepage-categories-widget';
      var html = '<div class="cat-widget-title">카테고리</div><nav class="cat-grid">';
      entries.forEach(function (e) {
        var slug = e[0];
        var info = e[1];
        html += '<a class="cat-chip" href="' + root + slug + '/">' +
          '<span class="cat-chip-name">' + info.title + '</span>' +
          '<span class="cat-chip-count">' + info.count + '</span>' +
          '</a>';
      });
      html += '</nav>';
      widget.innerHTML = html;
      // Remove any prior widget atomically right before we append the new one
      // — must happen AFTER the await, not before, or a concurrent call could
      // slip in and both would append (the source of the duplicate).
      var stale = document.getElementById('homepage-categories-widget');
      if (stale) stale.remove();
      sidebar.appendChild(widget);
    } catch (e) {
      console.error('[Categories] failed:', e);
    } finally {
      _catWidgetPending = false;
    }
  }
  document.addEventListener('nav', ensureCategoriesWidget);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureCategoriesWidget);
  } else {
    ensureCategoriesWidget();
  }

  // PartyRock-style left icon rail + slide-out panel.
  // Rail is always visible (thin, dark). Clicking Categories opens a wider
  // panel with category chips; other icons navigate directly. State (open
  // panel) persists to localStorage across SPA navigation.
  var RAIL_ICONS = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11.5 12 3l9 8.5V21H14v-6h-4v6H3z"/></svg>',
    categories: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    archives: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8"/><path d="M10 12h4"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    about: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>',
    collapse: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>'
  };
  var RAIL_STORAGE = 'partyrock-rail-v1';

  function loadRailState() {
    try {
      var raw = localStorage.getItem(RAIL_STORAGE);
      if (!raw) return { open: null };
      return JSON.parse(raw);
    } catch (e) { return { open: null }; }
  }
  function saveRailState(state) {
    try { localStorage.setItem(RAIL_STORAGE, JSON.stringify(state)); } catch (e) {}
  }

  // Relative path from current page back to the site root — works on both
  // localhost (served at /) and GH Pages (served at /dj-blog/).
  //
  // Quartz emits each page as slug.html at its slug's parent directory —
  // e.g. "about" becomes /about.html (root-level file), NOT
  // /about/index.html (subdirectory). The number of ../ needed to reach
  // site root equals the FOLDER depth of the current file, which is
  // (segment count - 1): "about" → 0 dirs → ./, "카프카/1" → 1 dir → ../
  function computeRoot() {
    var slug = document.body.dataset.slug || '';
    if (!slug || slug === 'index' || slug === '404') return './';
    var parts = slug.split('/');
    var dirs = parts.length - 1;
    if (dirs <= 0) return './';
    var up = '';
    for (var i = 0; i < dirs; i++) up += '../';
    return up;
  }

  function buildCategoriesPanelHTML(cb) {
    if (typeof fetchData === 'undefined') { cb('<div class="rail-panel-empty">데이터 준비 중…</div>'); return; }
    Promise.resolve(fetchData).then(function (data) {
      if (!data) { cb('<div class="rail-panel-empty">비어있음</div>'); return; }
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
      entries.sort(function (a, b) { return b[1].count - a[1].count || a[0].localeCompare(b[0]); });
      var root = computeRoot();
      var html = '<div class="rail-panel-title">카테고리</div><nav class="rail-cat-list">';
      entries.forEach(function (e) {
        var slug = e[0]; var info = e[1];
        html += '<a class="rail-cat-item" href="' + root + slug + '/">' +
          '<span class="rail-cat-name">' + info.title + '</span>' +
          '<span class="rail-cat-count">' + info.count + '</span>' +
          '</a>';
      });
      html += '</nav>';
      cb(html);
    }).catch(function () { cb('<div class="rail-panel-empty">불러오기 실패</div>'); });
  }

  function openPanel(key, rail) {
    var panel = rail.querySelector('.site-rail-panel');
    if (!panel) return;
    if (key === 'categories') {
      panel.innerHTML = '<div class="rail-panel-empty">불러오는 중…</div>';
      buildCategoriesPanelHTML(function (html) { panel.innerHTML = html; });
    }
    rail.classList.add('is-open');
    rail.dataset.openKey = key;
    document.body.classList.add('has-rail-open');
    saveRailState({ open: key });
    rail.querySelectorAll('.rail-icon-btn').forEach(function (b) {
      b.classList.toggle('is-active', b.dataset.key === key);
    });
  }
  function closePanel(rail) {
    rail.classList.remove('is-open');
    delete rail.dataset.openKey;
    document.body.classList.remove('has-rail-open');
    saveRailState({ open: null });
    rail.querySelectorAll('.rail-icon-btn').forEach(function (b) {
      b.classList.remove('is-active');
    });
  }

  function ensureRail() {
    var existing = document.getElementById('site-rail');
    if (existing) existing.remove();
    var root = computeRoot();
    var rail = document.createElement('aside');
    rail.id = 'site-rail';
    rail.setAttribute('aria-label', 'Primary navigation rail');
    rail.innerHTML = [
      '<div class="site-rail-bar">',
        '<button class="rail-collapse-btn" aria-label="Toggle rail" title="닫기/열기">',
          RAIL_ICONS.collapse,
        '</button>',
        '<div class="rail-brand">DL</div>',
        '<nav class="rail-icons">',
          '<a class="rail-icon-btn" data-key="home" href="' + root + '" title="Home">' + RAIL_ICONS.home + '</a>',
          '<button class="rail-icon-btn" data-key="categories" title="Categories">' + RAIL_ICONS.categories + '</button>',
          '<a class="rail-icon-btn" data-key="archives" href="' + root + 'archives" title="Archives">' + RAIL_ICONS.archives + '</a>',
          '<button class="rail-icon-btn" data-key="search" title="Search">' + RAIL_ICONS.search + '</button>',
          '<a class="rail-icon-btn" data-key="about" href="' + root + 'about" title="About">' + RAIL_ICONS.about + '</a>',
        '</nav>',
      '</div>',
      '<div class="site-rail-panel" role="region" aria-label="Rail panel"></div>'
    ].join('');
    document.body.prepend(rail);
    document.body.classList.add('has-site-rail');

    rail.querySelector('.rail-collapse-btn').addEventListener('click', function () {
      if (rail.classList.contains('is-open')) {
        closePanel(rail);
      } else {
        openPanel('categories', rail);
      }
    });

    rail.querySelectorAll('.rail-icon-btn').forEach(function (btn) {
      var key = btn.dataset.key;
      if (key === 'categories') {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          if (rail.dataset.openKey === 'categories') closePanel(rail);
          else openPanel('categories', rail);
        });
      } else if (key === 'search') {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          var searchBtn = document.querySelector('.search-button');
          if (searchBtn) searchBtn.click();
        });
      }
    });

    var state = loadRailState();
    if (state.open) openPanel(state.open, rail);
  }

  if (!window.__railOutsideClickBound) {
    window.__railOutsideClickBound = true;
    document.addEventListener('click', function (e) {
      var rail = document.getElementById('site-rail');
      if (!rail || !rail.classList.contains('is-open')) return;
      if (rail.contains(e.target)) return;
      closePanel(rail);
    });
  }

  document.addEventListener('nav', ensureRail);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureRail);
  } else {
    ensureRail();
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

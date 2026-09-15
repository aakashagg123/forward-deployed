function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/"/g, '&quot;');
}

// Sun/moon pair for the theme toggle — CSS shows whichever icon represents
// the mode a click switches *to* (moon while light, sun while dark).
const THEME_TOGGLE_ICONS = `<svg class="icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></svg><svg class="icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z"/></svg>`;

// Renders a link node's own <li>, plus a nested <ul> for its children (valid
// HTML nesting: <ul> only ever contains <li>, which may itself hold a <ul>).
function renderLinkItem(node, currentHref) {
  const active = node.href === currentHref ? ' active' : '';
  const nested = node.children.length ? `<ul>${node.children.map((c) => renderLinkItem(c, currentHref)).join('')}</ul>` : '';
  return `<li><a href="${node.href}" class="${active.trim()}">${escapeHtml(node.title)}</a>${nested}</li>`;
}

// Top level of the sidebar is a flat sequence of blocks — a heading (<p> +
// its own <ul>) or a bare top-level link folded into a shared leading <ul> —
// never link and heading siblings inside one <ul>, which HTML disallows.
function renderNavTree(root, currentHref) {
  const blocks = [];
  let pendingLinks = [];
  const flushLinks = () => {
    if (pendingLinks.length) {
      blocks.push(`<ul>${pendingLinks.map((n) => renderLinkItem(n, currentHref)).join('')}</ul>`);
      pendingLinks = [];
    }
  };
  for (const child of root.children) {
    if (child.type === 'heading') {
      flushLinks();
      blocks.push(`<p class="fd-nav-heading">${escapeHtml(child.title)}</p>`);
      if (child.children.length) {
        blocks.push(`<ul>${child.children.map((c) => renderLinkItem(c, currentHref)).join('')}</ul>`);
      }
    } else {
      pendingLinks.push(child);
    }
  }
  flushLinks();
  return blocks.join('');
}

// Drops a trailing ancestor that just repeats the page's own title — e.g. a
// book's index page nested under a heading of the same name would otherwise
// show "Forward-deployed / Forward-deployed" in both the visible breadcrumb
// and the BreadcrumbList structured data.
function dedupeBreadcrumb(breadcrumb, title) {
  if (!breadcrumb.length) return breadcrumb;
  const last = breadcrumb[breadcrumb.length - 1];
  if (last.title.trim().toLowerCase() === title.trim().toLowerCase()) {
    return breadcrumb.slice(0, -1);
  }
  return breadcrumb;
}

function renderBreadcrumb(breadcrumb, title) {
  const trail = dedupeBreadcrumb(breadcrumb, title)
    .map((b) => (b.href ? `<a href="${b.href}">${escapeHtml(b.title)}</a>` : escapeHtml(b.title)))
    .concat(escapeHtml(title));
  return trail.join(' <span aria-hidden="true">/</span> ');
}

function renderSpaceSwitcher(space, spaces) {
  const options = spaces
    .map((s) => `<a href="/${s.id}/${s.indexHref}" class="${s.id === space.id ? 'on' : ''}">${escapeHtml(s.title)}</a>`)
    .join('');
  return `
    <div class="fd-switch" id="fdSwitch">
      <button class="fd-switch-btn" id="fdSwitchBtn" aria-expanded="false" aria-controls="fdSwitchMenu">${escapeHtml(space.title)}<span aria-hidden="true">⌄</span></button>
      <div class="fd-switch-menu" id="fdSwitchMenu">${options}</div>
    </div>`;
}

function renderOutline(outline) {
  if (!outline.length) return '';
  const links = outline
    .map((h) => `<a class="fd-outline-link" href="#${h.id}" data-level="${h.level}">${escapeHtml(h.title)}</a>`)
    .join('');
  return `<nav class="fd-outline"><p class="fd-outline-label">On this page</p>${links}</nav>`;
}

// Shared <head> block: title, description, canonical, Open Graph, Twitter
// card, favicon, and any JSON-LD blocks the caller supplies.
const GA_TAG = `<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-R9EN43HKXY"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-R9EN43HKXY');
</script>`;

function renderHead({ site, title, description, canonicalUrl, image, jsonLd, markdownUrl }) {
  const fullTitle = title === site.title ? title : `${title} · ${site.title}`;
  const ld = (jsonLd || [])
    .map((obj) => `<script type="application/ld+json">${JSON.stringify(obj)}</script>`)
    .join('\n');
  return `${GA_TAG}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(fullTitle)}</title>
<meta name="description" content="${escapeAttr(description)}">
<link rel="canonical" href="${escapeAttr(canonicalUrl)}">
<link rel="icon" href="/mark-64.png">
<link rel="apple-touch-icon" href="/mark-180.png">
${markdownUrl ? `<link rel="alternate" type="text/markdown" href="${escapeAttr(markdownUrl)}">\n` : ''}<meta property="og:type" content="website">
<meta property="og:site_name" content="${escapeAttr(site.title)}">
<meta property="og:title" content="${escapeAttr(fullTitle)}">
<meta property="og:description" content="${escapeAttr(description)}">
<meta property="og:url" content="${escapeAttr(canonicalUrl)}">
<meta property="og:image" content="${escapeAttr(image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${escapeAttr(fullTitle)}">
<meta name="twitter:description" content="${escapeAttr(description)}">
<meta name="twitter:image" content="${escapeAttr(image)}">
<link rel="stylesheet" href="/theme.css">
${ld}`;
}

export function renderPage({ site, space, spaces, navTree, page, prev, next, contentHtml, outline, description, extraJsonLd, markdownUrl }) {
  const pagenav = `
    <nav class="fd-pagenav">
      ${prev ? `<a class="fd-pn-prev" href="${prev.href}"><span class="fd-pn-label">Previous</span>${escapeHtml(prev.title)}</a>` : '<span></span>'}
      ${next ? `<a class="fd-pn-next" href="${next.href}"><span class="fd-pn-label">Next</span>${escapeHtml(next.title)}</a>` : '<span></span>'}
    </nav>`;

  const canonicalUrl = site.baseUrl + page.href;
  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: dedupeBreadcrumb(page.breadcrumb, page.title)
        .concat([{ title: page.title, href: page.href }])
        .map((b, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          name: b.title,
          item: b.href ? site.baseUrl + b.href : undefined,
        })),
    },
    {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: page.title,
      description,
      url: canonicalUrl,
      isPartOf: { '@type': 'WebSite', name: site.title, url: site.baseUrl },
    },
    ...(extraJsonLd || []),
  ];

  return `<!doctype html>
<html lang="en">
<head>
${renderHead({ site, title: page.title, description, canonicalUrl, image: `${site.baseUrl}/social.jpg`, jsonLd, markdownUrl })}
</head>
<body>
<header class="fd-header">
  <button class="fd-mobile-toggle" id="fdMobileToggle" aria-label="Toggle navigation">☰</button>
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
  <a class="fd-toplink" href="/">Home</a>
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle light or dark theme">${THEME_TOGGLE_ICONS}</button>
</header>
<div class="fd-layout">
  <aside class="fd-sidebar" id="fdSidebar">
    ${renderSpaceSwitcher(space, spaces)}
    <nav class="fd-nav">${renderNavTree(navTree, page.href)}</nav>
  </aside>
  <main class="fd-main">
    <p class="fd-breadcrumb">${renderBreadcrumb(page.breadcrumb, page.title)}</p>
    <article class="fd-content" id="fdContent">${contentHtml}</article>
    ${pagenav}
    <div class="fd-feedback" id="fdFeedback">
      <span>Was this helpful?</span>
      <button class="fd-face" data-val="good" aria-label="Yes"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/></svg></button>
      <button class="fd-face" data-val="ok" aria-label="Somewhat"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M8 14h8"/></svg></button>
      <button class="fd-face" data-val="bad" aria-label="No"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M8 16s1.5-2 4-2 4 2 4 2"/></svg></button>
      <span class="fd-feedback-thanks" id="fdFeedbackThanks" hidden>Thanks.</span>
    </div>
  </main>
  ${renderOutline(outline)}
</div>
<script src="/theme.js"></script>
</body>
</html>`;
}

export function renderLanding({ site, spaces, landing, latestBook }) {
  const about = spaces.find((s) => s.id === 'about');

  const pillars = landing.pillars
    .map(
      (p) => `
        <div class="fd-pillar">
          <h4>${escapeHtml(p.label)}</h4>
          <p>${escapeHtml(p.body)}</p>
        </div>`,
    )
    .join('');

  const release = latestBook
    ? `
    <a class="fd-release" href="${latestBook.href}">
      <img class="fd-release-cover" src="${latestBook.cover}" alt="Cover of ${escapeAttr(latestBook.title)}" loading="lazy">
      <span class="fd-release-body">
        <span class="fd-release-badge">Latest release</span>
        <h5>${escapeHtml(latestBook.title)}</h5>
        <p>${escapeHtml(latestBook.tagline)}</p>
      </span>
      <span class="fd-release-link">Read free →</span>
    </a>`
    : '';

  const spaceRows = spaces
    .map(
      (s) => `
        <a href="/${s.id}/${s.indexHref}">
          <h4>${escapeHtml(s.title)}</h4>
          <p>${escapeHtml(s.blurb)}</p>
        </a>`,
    )
    .join('');

  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: site.title,
      url: site.baseUrl,
      description: site.thesis,
      author: { '@type': 'Person', name: site.author, url: `${site.baseUrl}/about/README.html` },
    },
  ];

  return `<!doctype html>
<html lang="en">
<head>
${renderHead({ site, title: site.title, description: site.thesis, canonicalUrl: site.baseUrl + '/', image: `${site.baseUrl}/social.jpg`, jsonLd })}
</head>
<body class="fd-landing-body">
<header class="fd-header fd-header-landing">
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle light or dark theme">${THEME_TOGGLE_ICONS}</button>
</header>
<div class="wrap">
  <div class="fd-hero">
    <div class="fd-glow"></div>
    <p class="fd-eyebrow"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.author)}</p>
    <h1 class="fd-hero-title">${escapeHtml(landing.headline)}</h1>
    <p class="fd-hero-lede">${landing.lede}${about ? ` <a class="fd-lede-link" href="/${about.id}/${about.indexHref}">Read the full story →</a>` : ''}</p>
  </div>
  <div class="fd-pillars">${pillars}</div>
  ${release}
  <div class="fd-spaces-row" id="spaces">${spaceRows}</div>
</div>
<script src="/theme.js"></script>
</body>
</html>`;
}

// A filterable grid of product case studies, appended after the portfolio
// space's own README prose — the tag filter is real JS, not decorative.
export function renderProductGrid(products) {
  const tags = Array.from(new Set(products.flatMap((p) => p.tags))).sort();
  const filterBtns = ['All', ...tags]
    .map((t, i) => `<button class="fd-pf-filter${i === 0 ? ' on' : ''}" data-tag="${escapeAttr(t)}">${escapeHtml(t)}</button>`)
    .join('');
  const cards = products
    .map(
      (p) => `
        <a class="fd-pf-card" href="${p.href}" data-tags="${escapeAttr(p.tags.join('|'))}">
          <span class="fd-pf-status">${escapeHtml(p.status)}</span>
          <h4>${escapeHtml(p.title)}</h4>
          <p>${escapeHtml(p.tagline)}</p>
          <div class="fd-pf-tags">${p.tags.map((t) => `<span>${escapeHtml(t)}</span>`).join('')}</div>
        </a>`,
    )
    .join('');
  return `
    <div class="fd-pf-filters" role="group" aria-label="Filter by tag">${filterBtns}</div>
    <div class="fd-pf-grid" id="fdPfGrid">${cards}</div>`;
}

// The Books space's own digital-library grid — a cover, title, tagline and
// status per book, appended after the space's README prose.
export function renderBookGrid(books) {
  const cards = books
    .map(
      (b) => `
        <a class="fd-book-card" href="${b.href}">
          <span class="fd-book-cover"><img src="${b.cover}" alt="Cover of ${escapeAttr(b.title)}" loading="lazy"></span>
          <span class="fd-book-info">
            <span class="fd-book-status">${escapeHtml(b.status)}</span>
            <h4>${escapeHtml(b.title)}</h4>
            <p>${escapeHtml(b.tagline)}</p>
          </span>
        </a>`,
    )
    .join('');
  return `<div class="fd-book-grid">${cards}</div>`;
}

// A small interactive architecture figure for the JSW One MSME product page's
// deeper dive: a stable core with two journeys built outward from it —
// pre-order (Salesforce) and post-order (ERP) — toggled by the reader rather
// than shown as two static diagrams.
export function renderJswArchitecture() {
  const node = (label, phase) => `<div class="fd-arch-node" data-phase="${phase}">${escapeHtml(label)}</div>`;
  return `
    <div class="fd-arch" id="fdArch">
      <div class="fd-arch-toggle" role="group" aria-label="Select journey">
        <button type="button" data-phase="pre">Pre-order journey</button>
        <button type="button" data-phase="post">Post-order journey</button>
      </div>
      <div class="fd-arch-diagram">
        <div class="fd-arch-persona">Customer</div>
        <div class="fd-arch-zone">
          <span class="fd-arch-zone-label">Core</span>
          ${node('Customer & onboarding', 'both')}
          ${node('Catalogue & pricing', 'both')}
          ${node('Ledger', 'both')}
        </div>
        <div class="fd-arch-arrow" aria-hidden="true">→</div>
        <div class="fd-arch-zone">
          <span class="fd-arch-zone-label">Transaction</span>
          ${node('Opportunity (Salesforce)', 'pre')}
          ${node('Cart', 'pre')}
          ${node('Order', 'pre')}
          ${node('Credit', 'pre')}
        </div>
        <div class="fd-arch-arrow" aria-hidden="true">→</div>
        <div class="fd-arch-zone">
          <span class="fd-arch-zone-label">Fulfillment</span>
          ${node('Shipment & documents', 'post')}
          ${node('Payments & payouts', 'post')}
          ${node('Reporting', 'post')}
        </div>
        <div class="fd-arch-persona">Seller</div>
      </div>
      <p class="fd-arch-caption" id="fdArchCaption"></p>
    </div>
    <script>
    (function(){
      var root = document.getElementById('fdArch');
      if (!root) return;
      var btns = root.querySelectorAll('.fd-arch-toggle button');
      var nodes = root.querySelectorAll('.fd-arch-node');
      var caption = document.getElementById('fdArchCaption');
      var captions = {
        pre: 'Pre-order to order journey — enabled through the customer portal and the Opportunity workflow on Salesforce.',
        post: 'Post-order to order-completion journey — enabled via ERP.'
      };
      function setPhase(phase) {
        btns.forEach(function (b) { b.classList.toggle('on', b.dataset.phase === phase); });
        nodes.forEach(function (n) {
          var active = n.dataset.phase === 'both' || n.dataset.phase === phase;
          n.classList.toggle('fd-arch-on', active);
          n.classList.toggle('fd-arch-dim', !active);
        });
        caption.textContent = captions[phase];
      }
      btns.forEach(function (b) { b.addEventListener('click', function () { setPhase(b.dataset.phase); }); });
      setPhase('pre');
    })();
    </script>`;
}

export function render404({ site }) {
  const canonicalUrl = site.baseUrl + '/404.html';
  return `<!doctype html>
<html lang="en">
<head>
${renderHead({ site, title: 'Page not found', description: 'This page does not exist.', canonicalUrl, image: `${site.baseUrl}/social.jpg`, jsonLd: [] })}
<meta name="robots" content="noindex">
</head>
<body class="fd-landing-body">
<header class="fd-header fd-header-landing">
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
</header>
<div class="wrap" style="padding-block:120px;text-align:left;">
  <h1 style="font-size:clamp(28px,5vw,46px);font-weight:800;letter-spacing:-.02em;margin:0 0 16px;">Page not found.</h1>
  <p style="color:var(--ink-2);font-size:16px;max-width:52ch;margin:0 0 28px;">Whatever you were looking for isn't here — it may have moved when a space was reorganized.</p>
  <a href="/" style="display:inline-block;border:1px solid var(--rule);padding:11px 20px;font-weight:600;font-size:14px;">Back to the index</a>
</div>
</body>
</html>`;
}

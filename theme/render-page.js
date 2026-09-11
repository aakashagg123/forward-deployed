function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/"/g, '&quot;');
}

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

function renderBreadcrumb(breadcrumb, title) {
  const trail = breadcrumb
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
function renderHead({ site, title, description, canonicalUrl, image, jsonLd }) {
  const fullTitle = title === site.title ? title : `${title} · ${site.title}`;
  const ld = (jsonLd || [])
    .map((obj) => `<script type="application/ld+json">${JSON.stringify(obj)}</script>`)
    .join('\n');
  return `<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(fullTitle)}</title>
<meta name="description" content="${escapeAttr(description)}">
<link rel="canonical" href="${escapeAttr(canonicalUrl)}">
<link rel="icon" href="/mark-64.png">
<link rel="apple-touch-icon" href="/mark-180.png">
<meta property="og:type" content="website">
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

export function renderPage({ site, space, spaces, navTree, page, prev, next, contentHtml, outline, description }) {
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
      itemListElement: page.breadcrumb
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
  ];

  return `<!doctype html>
<html lang="en">
<head>
${renderHead({ site, title: page.title, description, canonicalUrl, image: `${site.baseUrl}/social.jpg`, jsonLd })}
</head>
<body>
<header class="fd-header">
  <button class="fd-mobile-toggle" id="fdMobileToggle" aria-label="Toggle navigation">☰</button>
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
  <a class="fd-toplink" href="/">Home</a>
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle theme">Aa</button>
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

export function renderLanding({ site, spaces, chapters }) {
  const marqueeItems = chapters
    .map((c) => `<span><b>${String(c.n).padStart(2, '0')}</b> ${escapeHtml(c.title)}</span>`)
    .join('');
  const marquee = marqueeItems + marqueeItems;

  const cards = spaces
    .map(
      (s) => `
        <a class="fd-cat-card" href="/${s.id}/${s.indexHref}">
          <h4>${escapeHtml(s.title)}</h4>
          <p>${escapeHtml(s.blurb)}</p>
          <span class="fd-cat-count">${s.pageCount} page${s.pageCount === 1 ? '' : 's'}${s.status ? ` · ${escapeHtml(s.status)}` : ''}</span>
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
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle theme">Aa</button>
</header>
<div class="wrap">
  <div class="fd-hero" id="fdHero">
    <div class="fd-torch" id="fdTorch"></div>
    <div class="fd-hero-inner">
      <p class="fd-eyebrow"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</p>
      <h1 class="fd-hero-title">A field manual for putting engineers where the work actually is.</h1>
      <p class="fd-hero-lede">${escapeHtml(site.thesis)}</p>
      <p class="fd-hero-hint">Move your cursor over this page.</p>
    </div>
  </div>
  <div class="fd-marquee-wrap"><div class="fd-marquee">${marquee}</div></div>
  <div class="fd-cat-grid">${cards}</div>
  <footer class="fd-foot">forward-deployed.in — built with a custom generator, deployed on GitHub Pages.</footer>
</div>
<script src="/theme.js"></script>
</body>
</html>`;
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

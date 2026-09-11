function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
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

export function renderPage({ site, space, spaces, navTree, page, prev, next, contentHtml, outline }) {
  const pagenav = `
    <nav class="fd-pagenav">
      ${prev ? `<a class="fd-pn-prev" href="${prev.href}"><span class="fd-pn-label">Previous</span>${escapeHtml(prev.title)}</a>` : '<span></span>'}
      ${next ? `<a class="fd-pn-next" href="${next.href}"><span class="fd-pn-label">Next</span>${escapeHtml(next.title)}</a>` : '<span></span>'}
    </nav>`;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(page.title)} · ${escapeHtml(site.title)}</title>
<link rel="icon" href="/mark-64.png">
<link rel="apple-touch-icon" href="/mark-180.png">
<link rel="stylesheet" href="/theme.css">
</head>
<body>
<header class="fd-header">
  <button class="fd-mobile-toggle" id="fdMobileToggle" aria-label="Toggle navigation">☰</button>
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
  <a class="fd-toplink" href="/">Home</a>
  <a class="fd-toplink" href="${site.repoUrl}">GitHub</a>
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle theme">Aa</button>
</header>
<div class="fd-layout">
  <aside class="fd-sidebar" id="fdSidebar">
    ${renderSpaceSwitcher(space, spaces)}
    <nav class="fd-nav">${renderNavTree(navTree, page.href)}</nav>
  </aside>
  <main class="fd-main">
    <div class="fd-crumb-row">
      <p class="fd-breadcrumb">${renderBreadcrumb(page.breadcrumb, page.title)}</p>
      <button class="fd-copy-btn" id="fdCopyBtn" data-idle="Copy" data-done="Copied">Copy</button>
    </div>
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

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(site.title)}</title>
<link rel="icon" href="/mark-64.png">
<link rel="apple-touch-icon" href="/mark-180.png">
<link rel="stylesheet" href="/theme.css">
</head>
<body class="fd-landing-body">
<header class="fd-header fd-header-landing">
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(site.title)}</a>
  <a class="fd-toplink" href="${site.repoUrl}">GitHub</a>
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

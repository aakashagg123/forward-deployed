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

export function renderPage({ site, space, spaces, navTree, page, prev, next, contentHtml }) {
  const spaceLinks = spaces
    .map(
      (s) =>
        `<a class="fd-space-link${s.id === space.id ? ' active' : ''}" href="/${s.id}/${s.indexHref}">${escapeHtml(s.title)}</a>`,
    )
    .join('');

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
<link rel="stylesheet" href="/theme.css">
</head>
<body>
<header class="fd-header">
  <button class="fd-mobile-toggle" id="fdMobileToggle" aria-label="Toggle navigation">☰</button>
  <span class="fd-brand">${escapeHtml(site.title)}</span>
  <nav class="fd-spaces">${spaceLinks}</nav>
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle theme">Aa</button>
</header>
<div class="fd-layout">
  <aside class="fd-sidebar" id="fdSidebar">
    <nav class="fd-nav">${renderNavTree(navTree, page.href)}</nav>
  </aside>
  <main class="fd-main">
    <p class="fd-breadcrumb">${renderBreadcrumb(page.breadcrumb, page.title)}</p>
    <article class="fd-content">${contentHtml}</article>
    ${pagenav}
  </main>
</div>
<script src="/theme.js"></script>
</body>
</html>`;
}

export function renderLanding({ site, spaces }) {
  const cards = spaces
    .map(
      (s) =>
        `<a href="/${s.id}/${s.indexHref}" style="display:block;padding:20px;border:1px solid var(--rule);border-radius:10px;margin-bottom:14px;">
           <strong style="font-size:17px;">${escapeHtml(s.title)}</strong>
         </a>`,
    )
    .join('');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(site.title)}</title>
<link rel="stylesheet" href="/theme.css">
</head>
<body>
<header class="fd-header"><span class="fd-brand">${escapeHtml(site.title)}</span></header>
<div style="max-width:640px;margin:60px auto;padding:0 20px;">
  <h1 style="margin-bottom:24px;">${escapeHtml(site.title)}</h1>
  ${cards}
</div>
</body>
</html>`;
}

import { createHash } from 'node:crypto';

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/"/g, '&quot;');
}

// Sun/moon pair for the theme toggle — CSS shows whichever icon represents
// the mode a click switches *to* (moon while light, sun while dark).
export const THEME_TOGGLE_ICONS = `<svg class="icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></svg><svg class="icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z"/></svg>`;

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

// The one top-level navigation, rendered identically in the header of every
// page (landing, docs pages, 404) and mirrored in the Learning Zone bar.
export const NAV_ITEMS = [
  { key: 'about', label: 'About', href: '/about/' },
  { key: 'portfolio', label: 'Portfolio', href: '/portfolio/' },
  { key: 'book', label: 'Forward-Deployed (Book)', href: '/books/forward-deployed/' },
  { key: 'musings', label: 'Essays & Projects', href: '/musings/' },
  { key: 'learning-zone', label: 'AI Knowledge Graph', href: '/learning-zone/' },
];

// Which nav item a page belongs to. Anything under /books/ other than the
// retired guide counts as the book; the guide itself highlights nothing.
export function navKeyFor(href) {
  if (href.startsWith('/about/')) return 'about';
  if (href.startsWith('/portfolio/')) return 'portfolio';
  if (href.startsWith('/books/forward-deployed/')) return 'book';
  if (href.startsWith('/musings/')) return 'musings';
  if (href.startsWith('/learning-zone/')) return 'learning-zone';
  return null;
}

export function renderTopNav(activeKey, className = 'fd-topnav') {
  const links = NAV_ITEMS.map(
    (n) => `<a href="${n.href}"${n.key === activeKey ? ' class="on" aria-current="page"' : ''}>${escapeHtml(n.label)}</a>`,
  ).join('');
  return `<nav class="${className}" aria-label="Primary">${links}</nav>`;
}

// "Where I can help" block: appended to the homepage, About, and Portfolio.
export function renderCtaFooter({ linkedinUrl, githubUsername }) {
  const areas = [
    {
      title: '0→1 AI-native fintech & credit architecture',
      body: 'Lending origination, CRM, and an AI charter for digital-first lenders. The work I lead at JSW One Finance.',
    },
    {
      title: 'B2B marketplace systems',
      body: 'Order booking, pricing, credit, and CRM/ERP integration. The work behind JSW One MSME’s run to a $1B GMV exit rate.',
    },
    {
      title: 'Forward-deployed AI transformation inside incumbents',
      body: 'A small team of engineers and AI placed in one workflow, with authority to rewire it. The subject of the book.',
    },
  ]
    .map((a) => `<div class="fd-talk-area"><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.body)}</p></div>`)
    .join('');
  return `
    <section class="fd-talk" id="lets-talk" aria-labelledby="fdTalkTitle">
      <h2 class="fd-talk-title" id="fdTalkTitle">Where I Can Help / Let’s Talk</h2>
      <div class="fd-talk-areas">${areas}</div>
      <div class="fd-talk-ctas">
        <a class="fd-cta" href="${escapeAttr(linkedinUrl)}" target="_blank" rel="noopener">Connect on LinkedIn →</a>
        <a class="fd-cta" href="https://github.com/${escapeAttr(githubUsername)}" target="_blank" rel="noopener">@${escapeHtml(githubUsername)} on GitHub →</a>
        <a class="fd-cta" href="${escapeAttr(linkedinUrl)}" target="_blank" rel="noopener">Message me →</a>
      </div>
    </section>`;
}

function renderSpaceSwitcher(space, spaces) {
  const options = spaces
    .map((s) => `<a href="/${s.id}/${s.indexHref}" class="${s.id === space.id ? 'on' : ''}">${escapeHtml(s.title)}</a>`)
    .concat('<a href="/learning-zone/">AI Knowledge Graph</a>')
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
const GA_INLINE_SCRIPT = `
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-R9EN43HKXY');
`;
const GA_TAG = `<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-R9EN43HKXY"></script>
<script>${GA_INLINE_SCRIPT}</script>`;

// CSP script-src can't use 'unsafe-inline', so the one inline script this
// site ships (GA's config snippet above) is allow-listed by its exact
// content hash instead — computed here so it can never drift out of sync
// with GA_INLINE_SCRIPT.
const GA_INLINE_SCRIPT_HASH = `sha256-${createHash('sha256').update(GA_INLINE_SCRIPT).digest('base64')}`;

// Whitelist-model CSP: default-src 'none' plus explicit allowances for
// exactly the resource types this site uses (self-hosted CSS/JS/images, and
// Google Analytics' two script/beacon origins). Delivered via <meta> because
// GitHub Pages cannot send custom HTTP response headers at all — which also
// means two of the asks a real security header sweep would include can't be
// done from here: `frame-ancestors` is a CSP directive the spec explicitly
// excludes from meta-tag delivery (browsers silently ignore it there, so
// it's omitted rather than included for false reassurance), and
// Cross-Origin-Opener-Policy has no meta-tag form at all. Clickjacking and
// origin-isolation protection would need the domain fronted by a
// header-capable edge layer (e.g. Cloudflare) — out of scope for this repo.
const CSP = [
  "default-src 'none'",
  `script-src 'self' https://www.googletagmanager.com '${GA_INLINE_SCRIPT_HASH}'`,
  "style-src 'self'",
  "img-src 'self'",
  "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://www.googletagmanager.com",
  "font-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  'upgrade-insecure-requests',
  "require-trusted-types-for 'script'",
].join('; ');

function renderHead({ site, title, rawTitle, description, canonicalUrl, image, jsonLd, markdownUrl }) {
  const fullTitle = rawTitle || (title === site.title ? title : `${title} · ${site.title}`);
  const ld = (jsonLd || [])
    .map((obj) => `<script type="application/ld+json">${JSON.stringify(obj)}</script>`)
    .join('\n');
  // Charset/viewport first, then CSP — a meta-delivered CSP only governs
  // elements that appear *after* it in the document, so it has to come
  // before the stylesheet link and any script tag. The render-blocking
  // stylesheet still loads as early as possible right after; the async GA
  // tag doesn't need to be early too — it fires the same regardless of
  // position in <head>.
  return `<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="${escapeAttr(CSP)}">
<link rel="preconnect" href="https://www.googletagmanager.com">
<link rel="stylesheet" href="${escapeAttr(site.cssHref || '/theme.css')}">
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
${ld}
${GA_TAG}`;
}

export function renderPage({ site, space, spaces, navTree, page, prev, next, contentHtml, outline, description, extraJsonLd, markdownUrl, noindex }) {
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
${noindex ? '<meta name="robots" content="noindex">' : ''}
</head>
<body>
<header class="fd-header">
  <button class="fd-mobile-toggle" id="fdMobileToggle" aria-label="Toggle navigation">☰</button>
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt=""><span class="fd-brand-text">${escapeHtml(site.title)}</span></a>
  ${renderTopNav(navKeyFor(page.href))}
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle light or dark theme">${THEME_TOGGLE_ICONS}</button>
</header>
<div class="fd-layout">
  <aside class="fd-sidebar" id="fdSidebar">
    ${renderTopNav(navKeyFor(page.href), 'fd-sidenav-primary')}
    ${renderSpaceSwitcher(space, spaces)}
    <nav class="fd-nav">${renderNavTree(navTree, page.href)}</nav>
  </aside>
  <main class="fd-main">
    <p class="fd-breadcrumb">${renderBreadcrumb(page.breadcrumb, page.title)}</p>
    <article class="fd-content" id="fdContent">${contentHtml}</article>
    ${pagenav}
  </main>
  ${renderOutline(outline)}
</div>
<script src="${escapeAttr(site.jsHref || '/theme.js')}" defer></script>
</body>
</html>`;
}

// "Open-source & builder stack": concrete shipped artifacts in place of a
// contribution counter. Each card is { name, kind, body, links:[{label,href}] }.
export function renderBuilderStack(items) {
  const cards = items
    .map(
      (it) => `
        <article class="fd-build-card">
          <p class="fd-build-kind">${escapeHtml(it.kind)}</p>
          <h4><code>${escapeHtml(it.name)}</code></h4>
          <p class="fd-build-body">${escapeHtml(it.body)}</p>
          <p class="fd-build-links">${it.links
            .map((l) => `<a href="${escapeAttr(l.href)}"${/^https?:/.test(l.href) ? ' target="_blank" rel="noopener"' : ''}>${escapeHtml(l.label)}</a>`)
            .join('')}</p>
        </article>`,
    )
    .join('');
  return `
  <section class="fd-build" aria-labelledby="fdBuildTitle">
    <h3 class="fd-section-label" id="fdBuildTitle">Open-Source &amp; Builder Stack</h3>
    <!-- TODO(Aakash): verify 405 nodes / 1,550 cross-references / 19 tracks against the latest gatsby build -->
    <div class="fd-build-grid">${cards}</div>
  </section>`;
}

export function renderLanding({ site, spaces, landing, flagshipBook, builderStack, linkedinUrl, githubUsername }) {
  const about = spaces.find((s) => s.id === 'about');
  const linkedinCta = linkedinUrl
    ? `<a class="fd-cta" href="${escapeAttr(linkedinUrl)}" target="_blank" rel="noopener">Connect on LinkedIn →</a>`
    : '';

  const pillars = landing.pillars
    .map(
      (p) => `
        <div class="fd-pillar">
          <h4>${escapeHtml(p.label)}</h4>
          <p>${escapeHtml(p.body)}</p>
        </div>`,
    )
    .join('');

  const doctrine = flagshipBook
    ? `
    <a class="fd-release" href="${flagshipBook.href}">
      <img class="fd-release-cover" src="${flagshipBook.cover}" alt="Cover of ${escapeAttr(flagshipBook.title)}" loading="lazy">
      <span class="fd-release-body">
        <span class="fd-release-badge">My operating doctrine · flagship book</span>
        <h5>${escapeHtml(flagshipBook.title)}</h5>
        <p>${escapeHtml(landing.doctrine)}</p>
      </span>
      <span class="fd-release-link">Read the 16-chapter book →</span>
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
    .join('') + `
        <!-- TODO(Aakash): verify 405 nodes / 1,550 cross-references / 19 tracks against the latest gatsby build -->
        <a href="/learning-zone/">
          <h4>AI Knowledge Graph</h4>
          <p>${escapeHtml(landing.learningZoneBlurb)}</p>
        </a>`;

  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: site.title,
      url: site.baseUrl,
      description: site.thesis,
      author: { '@type': 'Person', name: site.author, url: `${site.baseUrl}/about/` },
    },
  ];

  return `<!doctype html>
<html lang="en">
<head>
${renderHead({ site, title: site.title, rawTitle: `${site.author} — ${landing.role}`, description: site.thesis, canonicalUrl: site.baseUrl + '/', image: `${site.baseUrl}/social.jpg`, jsonLd })}
</head>
<body class="fd-landing-body">
<header class="fd-header fd-header-landing">
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt=""><span class="fd-brand-text">${escapeHtml(site.title)}</span></a>
  ${renderTopNav(null)}
  <button class="fd-theme-toggle" id="fdThemeToggle" aria-label="Toggle light or dark theme">${THEME_TOGGLE_ICONS}</button>
</header>
<div class="wrap">
  <div class="fd-hero">
    <div class="fd-glow"></div>
    <p class="fd-eyebrow"><img class="fd-mark" src="/mark-64.png" alt="">${escapeHtml(landing.eyebrow)}</p>
    <h1 class="fd-hero-title">${escapeHtml(site.author)}<span class="fd-hero-role"> — ${escapeHtml(landing.role)}</span></h1>
    <p class="fd-hero-lede">${landing.lede}${about ? ` <a class="fd-lede-link" href="/${about.id}/${about.indexHref}">Read the full story →</a>` : ''}</p>
    ${linkedinCta ? `<div class="fd-hero-ctas">${linkedinCta}</div>` : ''}
  </div>
  <div class="fd-pillars">${pillars}</div>
  ${doctrine}
  ${renderBuilderStack(builderStack)}
  <div class="fd-spaces-row" id="spaces">${spaceRows}</div>
  ${renderCtaFooter({ linkedinUrl, githubUsername })}
</div>
<script src="${escapeAttr(site.jsHref || '/theme.js')}" defer></script>
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
  return `<div class="fd-book-grid${books.length === 1 ? ' fd-book-grid-single' : ''}">${cards}</div>`;
}

// A full-width interactive product-stack figure for the JSW One MSME product
// page's deeper dive: the platform's building blocks laid out between the
// Customer and Seller personas, with the pre-order (Salesforce) and
// post-order (ERP) journeys toggled by the reader. Built as a plain CSS grid
// rather than fixed-coordinate SVG text so it reflows instead of overlapping
// at any width.
export function renderJswArchitecture() {
  const cell = (label, phase) => `<div class="fd-stack-cell" data-phase="${phase}">${escapeHtml(label)}</div>`;
  const row = (label) => `<div class="fd-stack-row">${escapeHtml(label)}</div>`;
  return `
    <div class="fd-stack" id="fdStack">
      <div class="fd-stack-toggle" role="group" aria-label="Select journey">
        <button type="button" data-phase="pre">Pre-order journey (Salesforce)</button>
        <button type="button" data-phase="post">Post-order journey (ERP)</button>
      </div>
      <div class="fd-stack-grid">
        <div class="fd-stack-persona">Customer</div>
        <div class="fd-stack-cells">
          ${cell('Catalogue', 'pre')}
          ${cell('Pricing', 'pre')}
          ${cell('Cart', 'pre')}
          ${cell('Shipment', 'post')}
          ${cell('Documents', 'post')}
          ${cell('Ledger', 'pre')}
          ${cell('Credit', 'pre')}
          ${cell('Order', 'pre')}
          ${cell('Payments', 'post')}
          ${cell('Payouts', 'post')}
        </div>
        <div class="fd-stack-persona">Seller</div>
      </div>
      <div class="fd-stack-shared">
        ${row('Opportunity workflow')}
        ${row('Notifications')}
        ${row('Masters (material master, vendor master)')}
        ${row('Customer service')}
        ${row('Reporting')}
      </div>
      <p class="fd-stack-caption" id="fdStackCaption"></p>
    </div>`;
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
  <a class="fd-brand" href="/"><img class="fd-mark" src="/mark-64.png" alt=""><span class="fd-brand-text">${escapeHtml(site.title)}</span></a>
  ${renderTopNav(null)}
</header>
<div class="wrap fd-404-wrap">
  <h1 class="fd-404-title">Page not found.</h1>
  <p class="fd-404-body">Whatever you were looking for isn't here — it may have moved when a space was reorganized.</p>
  <a href="/" class="fd-404-back">Back to the index</a>
</div>
</body>
</html>`;
}

import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import matter from 'gray-matter';
import { createHighlighter } from 'shiki';
import { parseSummary, flattenPages } from './lib/summary.js';
import { createRenderer } from './lib/markdown.js';
import { renderPage, renderLanding, render404, renderProductGrid, renderBookGrid, renderJswArchitecture, renderCtaFooter, renderTopNav, THEME_TOGGLE_ICONS } from '../theme/render-page.js';

const ROOT = path.resolve(import.meta.dirname, '..');
const CONTENT_DIR = path.join(ROOT, 'content');
const THEME_STATIC_DIR = path.join(ROOT, 'theme', 'static');
const LEARNING_ZONE_DIR = path.join(ROOT, 'learning-zone');
const DIST_DIR = path.join(ROOT, 'dist');

const SITE = {
  title: 'Forward-deployed',
  baseUrl: 'https://forward-deployed.in',
  author: 'Aakash Aggarwal',
  thesis: 'AI-native product leader and 0→1 fintech builder. Leading lending origination, CRM, and the AI charter at JSW One Finance.',
};

const LINKEDIN_URL = 'https://in.linkedin.com/in/aakash-aggarwal-1010';
const GITHUB_USERNAME = 'aakashagg123';

// Spaces excluded from the build entirely — content stays on disk, just not
// built/linked/indexed. Remove an id here to bring the space back.
const HIDDEN_SPACES = new Set();

const SPACE_META = {
  books: { title: 'Books', blurb: 'Forward-deployed: the flagship book, free to read here.' },
  about: { title: 'About me', blurb: 'Who I am, what I do, and what I’m building right now.' },
  portfolio: { title: 'Portfolio & experience', blurb: 'A decade of shipping — one founder run, three product leadership roles.' },
  musings: { title: 'Essays & Built Systems', blurb: 'One essay and two documented systems: astack and gatsby.' },
};

// Pages kept live (so inbound links never 404) but removed from the Books
// index, the sidebar, the homepage, the sitemap and llms.txt, and marked
// noindex. Matched against the page's source path within its space.
const UNLISTED = [{ space: 'books', prefix: 'prompt-engineering-guide/' }];
function isUnlisted(spaceId, sourcePath) {
  return UNLISTED.some((u) => u.space === spaceId && sourcePath && sourcePath.startsWith(u.prefix));
}

// Same tree, minus unlisted pages and any heading left empty by that.
function listedTree(node, spaceId) {
  const children = node.children
    .filter((c) => !(c.type === 'link' && isUnlisted(spaceId, c.sourcePath)))
    .map((c) => ({ ...c, children: listedTree(c, spaceId).children }))
    .filter((c) => c.type !== 'heading' || c.children.length > 0);
  return { ...node, children };
}

// Landing page copy. The hero identity is the person; Forward-deployed is
// the operating doctrine and flagship book, shown right under the bio.
const LANDING = {
  eyebrow: 'Mumbai, India',
  role: 'AI-Native Product Leader & 0→1 Fintech Builder',
  lede:
    'Leading Lending Origination (LOS), CRM, and the AI Charter at JSW One Finance. Previously built B2B commerce to a $1B GMV run-rate at JSW One MSME, scaled embedded insurance to 5M+ lives at Marsh, and co-founded AutoO2.',
  pillars: [
    {
      label: 'What I do',
      body: 'Take an ambiguous, complex problem statement, design the product, process and people systems around it, and drive adoption until it runs inside the organisation.',
    },
    {
      label: "What I'm doing now",
      body: 'Leading product for LOS, CRM, and the AI charter at JSW One Finance, a digital-first NBFC where commercial lending runs 100% digital, lead to disbursement.',
    },
    {
      label: 'How I think',
      body: 'A systems thinker grounded in business fundamentals, with a background in physics, engineering, and an MBA. I prefer structure over opinions.',
    },
  ],
  doctrine:
    'Put a small team of engineers and AI inside the workflow that is failing, with the authority to rewire it. Sixteen chapters on why transformation stalls inside incumbents and what to do instead.',
  // TODO(Aakash): verify 405 nodes / 1,550 cross-references / 19 tracks against the latest gatsby build
  learningZoneBlurb:
    'An open-source, 405-node AI & Systems Engineering reference graph (1,550 cross-references across 19 tracks), compiled by gatsby, a pure-Python + Claude Code knowledge pipeline.',
};

const ASTACK_URL = 'https://github.com/aakashagg123/astack';
const GATSBY_URL = 'https://github.com/aakashagg123/gatsby';

// Homepage "Open-Source & Builder Stack" cards: shipped artifacts, not telemetry.
// TODO(Aakash): verify 405 nodes / 1,550 cross-references against the latest gatsby build
const BUILDER_STACK = [
  {
    name: 'astack',
    kind: 'Claude Code skill router',
    body: '44 slash commands across discovery, spec, TDD, security review, and staged shipping, dispatched through a single /astack router.',
    links: [
      { label: 'Repo & architecture →', href: ASTACK_URL },
      { label: 'Essays & Projects →', href: '/musings/' },
    ],
  },
  {
    name: 'gatsby',
    kind: 'AI Knowledge Engine',
    body: 'A pure-Python static compiler and knowledge-graph generator behind the 405-node AI Engineering curriculum, with 1,550 cross-references.',
    links: [
      { label: 'Repo & architecture →', href: GATSBY_URL },
      { label: 'Browse the graph →', href: '/learning-zone/' },
    ],
  },
];

// The Books index spotlights one flagship monograph.
const BOOKS = [
  {
    title: 'Forward-deployed',
    tagline: 'Putting engineers and AI inside the companies too slow to save themselves.',
    cover: '/books/forward-deployed/covers/cover.jpg',
    href: '/books/forward-deployed/',
    status: 'Draft · 16 chapters',
  },
];

// Case studies on the Portfolio & experience index page get a real,
// filterable grid — status and body copy per case study still fill in over
// time, but the grid itself is live from day one.
const PRODUCTS = [
  {
    title: 'JSW One Finance — lending origination platform',
    tagline: 'Commercial lending, 100% digital, lead to disbursement.',
    tags: ['Fintech', 'Lending', 'AI'],
    status: 'Current',
    href: '/portfolio/products/jsw-one-finance-los.html',
  },
  {
    title: 'JSW One MSME — B2B marketplace',
    tagline: 'A credit-enabled marketplace for MSMEs, built to a $1B exit rate.',
    tags: ['Fintech', 'E-commerce'],
    status: 'Shipped',
    href: '/portfolio/products/jsw-one-msme-marketplace.html',
  },
  {
    title: 'Marsh — BenefitsCircle & QoverPro',
    tagline: 'Voluntary benefits and embedded insurance for Amazon, Ashok Leyland, and more.',
    tags: ['Insurance'],
    status: 'Shipped',
    href: '/portfolio/products/marsh-embedded-insurance.html',
  },
  {
    title: 'AutoO2 — motor insurance claims SaaS',
    tagline: 'Co-founded and built to 500+ onboarded workshops.',
    tags: ['Insurance', '0→1', 'Founder'],
    status: 'Shipped',
    href: '/portfolio/products/autoo2-claims-saas.html',
  },
];

function readTitleFromMarkdown(md, fallback) {
  const match = md.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : fallback;
}

function rmrf(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

// Renames a just-copied static file to a content-hashed name (theme.js ->
// theme.a1b2c3d4.js) and returns the new root-relative href. Without this,
// every deploy reuses the exact same /theme.js URL, so a browser or CDN
// that cached the previous version's response keeps serving it past that
// deploy — stale JS/CSS silently shipped indefinitely, not just until the
// cache's TTL happens to expire.
function hashAndRename(distDir, filename) {
  const filePath = path.join(distDir, filename);
  const hash = createHash('sha256').update(fs.readFileSync(filePath)).digest('hex').slice(0, 8);
  const ext = path.extname(filename);
  const base = filename.slice(0, -ext.length);
  const hashedName = `${base}.${hash}${ext}`;
  fs.renameSync(filePath, path.join(distDir, hashedName));
  return `/${hashedName}`;
}

// The Learning Zone is a pre-built static site (its own inline styles, a
// GitHub-Primer look). Rather than hand-editing those ~435 pages — and
// redoing it on every re-sync from the gatsby repo — the build themes the
// copy: it links a shared stylesheet that remaps the pages to this site's
// design language, adds the site bar (with the theme toggle) and a script
// that applies the saved theme before first paint. Idempotent: any bar a
// previous sync left in the committed copy is replaced, not doubled.
// The Learning Zone is a compiled artifact, so its landing page says so:
// the hero is reframed as an automated knowledge-engineering system, with a
// "How this was built" banner pointing at the gatsby pipeline that produces
// it. Done here, at build time, so it survives every re-sync from gatsby.
// Returns a transform for the landing page's HTML, or null if the page is
// missing (the transform itself warns when the expected hero is not found).
const LZ_HERO_RE = /<h1>[^<]*<\/h1>\s*<p class="lede">[^<]*<\/p>/;
// TODO(Aakash): verify 405 nodes / 1,550 cross-references / 19 tracks against the latest gatsby build
const LZ_HERO = `<h1>AI &amp; Systems Engineering Knowledge Graph</h1>
  <p class="lede">An open-source, 405-node AI &amp; Systems Engineering reference graph (1,550 cross-references across 19 tracks)—compiled, cross-linked, and maintained via <code>gatsby</code>, a pure-Python + Claude Code knowledge pipeline built for Product Builders.</p>
  <aside class="fd-lz-built" aria-label="How this was built">
    <p class="fd-lz-built-label">How this was built</p>
    <p>The pages in this graph are generated. <code>gatsby</code> compiles them from source content, cross-links every concept, and builds the knowledge graph. The source and architecture are public, so you can judge the pipeline.</p>
    <p><a href="${GATSBY_URL}" target="_blank" rel="noopener">Read the gatsby architecture →</a></p>
  </aside>`;
function applyLearningZoneFraming(indexPath) {
  if (!fs.existsSync(indexPath)) return null;
  return (html) => {
    if (!LZ_HERO_RE.test(html)) {
      console.warn('Learning Zone: hero <h1>/lede not found in index.html; framing not applied');
      return html;
    }
    return html.replace(LZ_HERO_RE, LZ_HERO);
  };
}

function themeLearningZone(dir, { cssHref, jsHref }) {
  const bar = `<div id="fd-lz-bar" class="fd-lz-bar">
  <a class="fd-lz-brand" href="/"><img src="/mark-64.png" alt=""><span>Forward-deployed</span></a>
  <span class="fd-lz-sep">/</span>
  <a class="fd-lz-crumb" href="/learning-zone/">AI Knowledge Graph</a>
  ${renderTopNav('learning-zone', 'fd-lz-nav')}
  <button class="fd-lz-theme" id="fdLzTheme" type="button" aria-label="Toggle light or dark theme">${THEME_TOGGLE_ICONS}</button>
</div>
`;
  const headTags = `<script src="${jsHref}"></script>\n<link rel="stylesheet" href="${cssHref}">\n`;
  let count = 0;
  const framed = applyLearningZoneFraming(path.join(dir, 'index.html'));
  const walk = (d) => {
    for (const entry of fs.readdirSync(d, { withFileTypes: true })) {
      const full = path.join(d, entry.name);
      if (entry.isDirectory()) { walk(full); continue; }
      if (!entry.name.endsWith('.html')) continue;
      let html = fs.readFileSync(full, 'utf8');
      html = html.replace(/<div id="fd-lz-bar"[\s\S]*?<\/div>\s*/, '');
      html = html.replace(/<style>\s*\.bar\{ top:44px !important; \}[\s\S]*?<\/style>\s*/, '');
      if (!/<\/head>/i.test(html) || !/<body[^>]*>/i.test(html)) continue;
      if (path.relative(dir, full) === 'index.html' && framed) html = framed(html);
      html = html.replace(/<\/head>/i, `${headTags}</head>`);
      html = html.replace(/<body[^>]*>/i, (m) => `${m}\n${bar}`);
      if (path.relative(dir, full) === path.join('graph', 'index.html')) {
        html = html.replace(/<html/i, '<html data-lz="graph"');
      }
      fs.writeFileSync(full, html);
      count++;
    }
  };
  walk(dir);
  return count;
}

// Recursively finds every "assets" or "covers" folder under a space
// (a book subfolder may nest its own, rather than one living at the space
// root) and mirrors each to the same relative path in dist.
function copyNestedAssetDirs(spaceDir, spaceDistDir, relDir = '') {
  const dir = path.join(spaceDir, relDir);
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const rel = path.join(relDir, entry.name);
    if (entry.name === 'assets' || entry.name === 'covers') {
      copyDir(path.join(spaceDir, rel), path.join(spaceDistDir, rel));
    } else {
      copyNestedAssetDirs(spaceDir, spaceDistDir, rel);
    }
  }
}

// Groups pages by their top-level breadcrumb heading (e.g. each book in the
// Books space) so prev/next navigation stays within one book instead of
// running off the end of one into the start of the next.
function computePrevNext(pages) {
  const groups = new Map();
  pages.forEach((page, i) => {
    const key = page.breadcrumb[0]?.title || '';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(i);
  });
  const map = new Map();
  for (const indices of groups.values()) {
    indices.forEach((idx, pos) => {
      map.set(idx, {
        prev: pos > 0 ? pages[indices[pos - 1]] : null,
        next: pos < indices.length - 1 ? pages[indices[pos + 1]] : null,
      });
    });
  }
  return map;
}

function discoverSpaces() {
  return fs
    .readdirSync(CONTENT_DIR, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}

// Sentence case, derived from the folder name — not the page's own H1, so a
// space's display name stays distinct from whatever its landing page is titled.
// SPACE_META.title overrides this when the folder name alone can't express it
// (e.g. "portfolio" -> "Portfolio & experience").
function spaceTitle(spaceId) {
  if (SPACE_META[spaceId]?.title) return SPACE_META[spaceId].title;
  const words = spaceId.split('-');
  return words.map((w, i) => (i === 0 ? w[0].toUpperCase() + w.slice(1) : w)).join(' ');
}

function slugify(text, seen) {
  let base = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'section';
  let slug = base;
  let n = 2;
  while (seen.has(slug)) {
    slug = `${base}-${n}`;
    n++;
  }
  seen.add(slug);
  return slug;
}

// Tags every h2/h3 with an id and returns the outline used for the
// "on this page" rail — done as a post-process on rendered HTML rather than
// inside the markdown renderer, since ids only need to be unique per page.
function extractOutline(html) {
  const seen = new Set();
  const outline = [];
  const updated = html.replace(/<(h[23])>(.*?)<\/\1>/gs, (match, tag, inner) => {
    // The rail re-escapes titles, so decode the entities markdown-it emitted.
    const text = inner
      .replace(/<[^>]+>/g, '')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&amp;/g, '&')
      .trim();
    const id = slugify(text, seen);
    outline.push({ level: tag === 'h2' ? 2 : 3, id, title: text });
    return `<${tag} id="${id}">${inner}</${tag}>`;
  });
  return { html: updated, outline };
}

// Musings posts carry a `date:` frontmatter field (YYYY-MM-DD); rendered as
// a byline right under the H1, matching how a blog post would show one.
function injectAfterH1(html, markup) {
  return html.replace(/(<h1>.*?<\/h1>)/s, `$1\n${markup}`);
}

function injectPostDate(html, date) {
  // gray-matter parses an unquoted YAML date (2026-09-26) into a Date
  // already; a quoted string arrives as-is, so accept either.
  const d = date instanceof Date ? date : new Date(`${date}T00:00:00Z`);
  const formatted = d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  });
  return injectAfterH1(html, `<p class="fd-post-date">${formatted}</p>`);
}

// Legacy "<dir>/README.html" URLs: a canonical + meta-refresh stub pointing
// at the directory index ("./" from README.html is the same directory).
function renderRedirectStub() {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="./">
<meta http-equiv="refresh" content="0; url=./">
</head>
<body>
<p>This page moved. <a href="./">Continue</a>.</p>
</body>
</html>
`;
}

function renderLinkedinCta(linkedinUrl) {
  return `<a class="fd-cta" href="${linkedinUrl}" target="_blank" rel="noopener">Connect on LinkedIn →</a>`;
}

const MAX_DESCRIPTION = 155;

// Meta-description source: the raw markdown's first plain paragraph — not
// a heading, blockquote, image, or a paragraph made entirely of a ⟦slot⟧ —
// with markdown emphasis/slot markers stripped and cut to a clean word break.
function extractDescription(raw, fallback) {
  const blocks = raw.split(/\n\s*\n/);
  for (const block of blocks) {
    const line = block.trim();
    if (!line) continue;
    if (/^#{1,6}\s/.test(line)) continue;
    if (line.startsWith('>')) continue;
    if (line.startsWith('!')) continue;
    if (line === '---') continue;
    const plain = line
      .replace(/\*\*(.+?)\*\*/g, '$1')
      .replace(/\*(.+?)\*/g, '$1')
      .replace(/⟦.+?⟧/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    if (!plain) continue;
    if (plain.length <= MAX_DESCRIPTION) return plain;
    const cut = plain.slice(0, MAX_DESCRIPTION);
    return cut.slice(0, cut.lastIndexOf(' ')) + '…';
  }
  return fallback;
}

const KINDLE_URL = 'https://amzn.in/d/0c3cehuZ';

// Per-page structured data beyond the generic BreadcrumbList/Article every
// page already gets — a Person entity for the About page, and a Book entity
// for each book's own index, so an LLM or search engine can resolve "who is
// this site about" and "what are these books" directly from the markup.
function buildExtraJsonLd(spaceId, page) {
  if (spaceId === 'about' && page.sourcePath === 'README.md') {
    return [
      {
        '@context': 'https://schema.org',
        '@type': 'Person',
        name: SITE.author,
        url: SITE.baseUrl + page.href,
        jobTitle: 'Product leader',
        worksFor: { '@type': 'Organization', name: 'JSW One Finance' },
        sameAs: [LINKEDIN_URL],
      },
    ];
  }
  if (spaceId === 'books' && page.sourcePath === 'forward-deployed/README.md') {
    return [
      {
        '@context': 'https://schema.org',
        '@type': 'Book',
        name: 'Forward-deployed',
        author: { '@type': 'Person', name: SITE.author },
        url: SITE.baseUrl + page.href,
        bookFormat: 'https://schema.org/EBook',
        inLanguage: 'en',
        isAccessibleForFree: true,
      },
    ];
  }
  if (spaceId === 'books' && page.sourcePath === 'prompt-engineering-guide/README.md') {
    return [
      {
        '@context': 'https://schema.org',
        '@type': 'Book',
        name: 'Prompt engineering guide for product managers',
        author: { '@type': 'Person', name: SITE.author },
        url: SITE.baseUrl + page.href,
        bookFormat: 'https://schema.org/EBook',
        inLanguage: 'en',
        datePublished: '2025-05-05',
        isAccessibleForFree: true,
        sameAs: [KINDLE_URL],
      },
    ];
  }
  return [];
}

// llms.txt (the llmstxt.org convention): a compact, curated map of the site
// for an AI agent to fetch before crawling — plus llms-full.txt, the same
// map with every page's raw markdown inlined for one-shot ingestion.
function writeLlmsTxt({ spaces, spaceData }) {
  const lines = [`# ${SITE.title}`, '', `> ${SITE.thesis}`, ''];
  const fullParts = [`# ${SITE.title}\n\n> ${SITE.thesis}\n`];

  for (const space of spaces) {
    const data = spaceData.find((s) => s.spaceId === space.id);
    lines.push(`## ${space.title}`);
    fullParts.push(`\n## ${space.title}\n`);
    for (const page of data.pages) {
      if (page.external || page.unlisted) continue;
      lines.push(`- [${page.title}](${SITE.baseUrl}${page.href}): ${page.description || space.blurb}`);
      const abs = path.join(data.spaceDir, page.sourcePath);
      const raw = fs.readFileSync(abs, 'utf8');
      fullParts.push(`\n### ${SITE.baseUrl}${page.href}\n\n${raw}\n`);
    }
    lines.push('');
  }

  fs.writeFileSync(path.join(DIST_DIR, 'llms.txt'), lines.join('\n'));
  fs.writeFileSync(path.join(DIST_DIR, 'llms-full.txt'), fullParts.join('\n'));
}

async function build() {
  rmrf(DIST_DIR);
  fs.mkdirSync(DIST_DIR, { recursive: true });

  // Copied and hashed up front so every page render below can reference
  // the correct cache-busted URLs via SITE.cssHref/SITE.jsHref.
  copyDir(THEME_STATIC_DIR, DIST_DIR);
  SITE.cssHref = hashAndRename(DIST_DIR, 'theme.css');
  SITE.jsHref = hashAndRename(DIST_DIR, 'theme.js');
  const lzCssHref = hashAndRename(DIST_DIR, 'learning-zone.css');
  const lzJsHref = hashAndRename(DIST_DIR, 'learning-zone.js');

  const highlighter = await createHighlighter({
    themes: ['github-dark'],
    langs: ['javascript', 'typescript', 'python', 'bash', 'json', 'html', 'css', 'markdown'],
  });
  const md = createRenderer({ highlighter });

  const spaceIds = discoverSpaces().filter((id) => !HIDDEN_SPACES.has(id));
  if (spaceIds.length === 0) {
    throw new Error(`No spaces found under ${CONTENT_DIR}`);
  }

  const spaces = [];
  const spaceData = [];

  for (const spaceId of spaceIds) {
    const spaceDir = path.join(CONTENT_DIR, spaceId);
    const summaryPath = path.join(spaceDir, 'SUMMARY.md');
    if (!fs.existsSync(summaryPath)) {
      throw new Error(`Space "${spaceId}" is missing SUMMARY.md`);
    }
    const tree = parseSummary(fs.readFileSync(summaryPath, 'utf8'), { spaceDir, spaceId });
    const pages = flattenPages(tree);
    for (const page of pages) page.unlisted = isUnlisted(spaceId, page.sourcePath);
    if (pages.length === 0) {
      throw new Error(`Space "${spaceId}" SUMMARY.md defines no pages`);
    }

    for (const page of pages) {
      if (page.external) continue;
      const abs = path.join(spaceDir, page.sourcePath);
      if (!fs.existsSync(abs)) {
        throw new Error(
          `Broken link in ${spaceId}/SUMMARY.md: "${page.sourcePath}" (${abs}) does not exist`,
        );
      }
    }

    const title = spaceTitle(spaceId);
    const indexHref = pages[0].href.replace(`/${spaceId}/`, '');
    const meta = SPACE_META[spaceId] || {};
    spaces.push({
      id: spaceId,
      title,
      indexHref,
      blurb: meta.blurb || `${title} space.`,
      status: meta.status || null,
      pageCount: pages.length,
    });
    spaceData.push({ spaceId, spaceDir, tree, navTreeListed: listedTree(tree, spaceId), pages });
  }

  const sitemapUrls = [{ loc: SITE.baseUrl + '/' }];

  for (const { spaceId, spaceDir, tree, navTreeListed, pages } of spaceData) {
    const prevNext = computePrevNext(pages);
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      if (page.external) continue;
      const abs = path.join(spaceDir, page.sourcePath);
      const raw = fs.readFileSync(abs, 'utf8');
      const { data: frontmatter, content: body } = matter(raw);
      const rendered = md.render(body);
      let { html: contentHtml, outline } = extractOutline(rendered);
      if (spaceId === 'musings' && frontmatter.date) {
        contentHtml = injectPostDate(contentHtml, frontmatter.date);
      }
      if (spaceId === 'about' && page.sourcePath === 'README.md') {
        contentHtml = injectAfterH1(contentHtml, renderLinkedinCta(LINKEDIN_URL));
        contentHtml += renderCtaFooter({ linkedinUrl: LINKEDIN_URL, githubUsername: GITHUB_USERNAME });
      }
      if (spaceId === 'portfolio' && page.sourcePath === 'README.md') {
        contentHtml += renderProductGrid(PRODUCTS);
        contentHtml += renderCtaFooter({ linkedinUrl: LINKEDIN_URL, githubUsername: GITHUB_USERNAME });
      }
      if (spaceId === 'books' && page.sourcePath === 'README.md') {
        contentHtml += renderBookGrid(BOOKS);
      }
      if (spaceId === 'portfolio' && page.sourcePath === 'products/jsw-one-msme-marketplace.md') {
        // The interactive stack figure sits at the marker when the page has
        // one (inside its architecture section); otherwise it goes last.
        const STACK_MARKER = '<!--fd:jsw-stack-->';
        contentHtml = contentHtml.includes(STACK_MARKER)
          ? contentHtml.replace(STACK_MARKER, renderJswArchitecture())
          : contentHtml + renderJswArchitecture();
      }
      const description = extractDescription(body, SITE.thesis);
      page.description = description;

      const { prev, next } = prevNext.get(i);
      // The markdown mirror always sits at the source path ("/about/README.md").
      const markdownUrl = `/${spaceId}/${page.sourcePath}`;
      const extraJsonLd = buildExtraJsonLd(spaceId, page);

      const html = renderPage({
        site: SITE,
        space: { id: spaceId, title: spaceTitle(spaceId) },
        spaces,
        navTree: page.unlisted ? tree : navTreeListed,
        page: { title: page.title, href: page.href, breadcrumb: page.breadcrumb },
        prev,
        next,
        contentHtml,
        outline,
        description,
        extraJsonLd,
        markdownUrl,
        noindex: page.unlisted,
      });

      // A directory index ("/about/") is written as <dir>/index.html.
      const outRel = page.href.endsWith('/') ? `${page.href}index.html` : page.href;
      const outPath = path.join(DIST_DIR, outRel.replace(/^\//, ''));
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, html);
      // The old "<dir>/README.html" URL keeps working as a redirect stub.
      if (page.href.endsWith('/')) {
        fs.writeFileSync(path.join(path.dirname(outPath), 'README.html'), renderRedirectStub());
      }
      // A clean markdown mirror of every page, for agents/crawlers that
      // prefer fetching source content over HTML-with-chrome.
      fs.writeFileSync(path.join(DIST_DIR, markdownUrl.replace(/^\//, '')), raw);
      if (!page.unlisted) sitemapUrls.push({ loc: SITE.baseUrl + page.href });
    }

    copyNestedAssetDirs(spaceDir, path.join(DIST_DIR, spaceId));
  }

  fs.writeFileSync(
    path.join(DIST_DIR, 'index.html'),
    renderLanding({ site: SITE, spaces, landing: LANDING, flagshipBook: BOOKS[0], builderStack: BUILDER_STACK, linkedinUrl: LINKEDIN_URL, githubUsername: GITHUB_USERNAME }),
  );
  fs.writeFileSync(path.join(DIST_DIR, '404.html'), render404({ site: SITE }));

  // Learning Zone: a pre-built static site (its own design system, not run
  // through the markdown pipeline) copied wholesale into dist/learning-zone/.
  if (fs.existsSync(LEARNING_ZONE_DIR)) {
    copyDir(LEARNING_ZONE_DIR, path.join(DIST_DIR, 'learning-zone'));
    themeLearningZone(path.join(DIST_DIR, 'learning-zone'), { cssHref: lzCssHref, jsHref: lzJsHref });
    sitemapUrls.push({ loc: SITE.baseUrl + '/learning-zone/' });
  }

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapUrls.map((u) => `  <url><loc>${u.loc}</loc></url>`).join('\n')}
</urlset>
`;
  fs.writeFileSync(path.join(DIST_DIR, 'sitemap.xml'), sitemap);

  // Named groups (rather than relying on "*" alone) for the crawlers behind
  // ChatGPT, Claude, Perplexity, and other AI tools — explicit allow, so
  // access here is a stated choice, not an accident of a wildcard.
  const AI_CRAWLERS = [
    'GPTBot',
    'ChatGPT-User',
    'OAI-SearchBot',
    'ClaudeBot',
    'Claude-User',
    'anthropic-ai',
    'PerplexityBot',
    'Perplexity-User',
    'Google-Extended',
    'CCBot',
    'Applebot-Extended',
  ];
  const robots = `User-agent: *
Allow: /

${AI_CRAWLERS.map((ua) => `User-agent: ${ua}\nAllow: /`).join('\n\n')}

Sitemap: ${SITE.baseUrl}/sitemap.xml
`;
  fs.writeFileSync(path.join(DIST_DIR, 'robots.txt'), robots);

  writeLlmsTxt({ spaces, spaceData });

  const cnamePath = path.join(ROOT, 'CNAME');
  if (fs.existsSync(cnamePath)) {
    fs.copyFileSync(cnamePath, path.join(DIST_DIR, 'CNAME'));
  }

  highlighter.dispose();

  const pageCount = spaceData.reduce((sum, s) => sum + s.pages.length, 0);
  console.log(`Built ${spaces.length} space(s), ${pageCount} page(s) → ${DIST_DIR}`);
}

build().catch((err) => {
  console.error('Build failed:', err.message);
  process.exit(1);
});

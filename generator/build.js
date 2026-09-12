import fs from 'node:fs';
import path from 'node:path';
import { createHighlighter } from 'shiki';
import { parseSummary, flattenPages } from './lib/summary.js';
import { createRenderer } from './lib/markdown.js';
import { renderPage, renderLanding, render404, renderProductGrid, renderBookGrid } from '../theme/render-page.js';

const ROOT = path.resolve(import.meta.dirname, '..');
const CONTENT_DIR = path.join(ROOT, 'content');
const THEME_STATIC_DIR = path.join(ROOT, 'theme', 'static');
const DIST_DIR = path.join(ROOT, 'dist');

const SITE = {
  title: 'Forward deployed',
  baseUrl: 'https://forward-deployed.in',
  author: 'Aakash Aggarwal',
  thesis:
    "The unit of change is not a deck — it's a small team of engineers and AI placed at the point of the problem, with the authority to rewire the workflow rather than recommend one.",
};

const SPACE_META = {
  books: { title: 'Books', blurb: 'A small digital library — two long-reads, free to read here.' },
  about: { title: 'About me', blurb: 'Who I am, what I do, and what I’m building right now.' },
  portfolio: { title: 'Portfolio & experience', blurb: 'A decade of shipping — one founder run, three product leadership roles.' },
  musings: { title: 'Musings & side projects', blurb: 'Running notes on AI, product ideas, and prototypes worth poking at.' },
};

// The library's two books, each rendered as a cover card on the Books index.
const BOOKS = [
  {
    title: 'Forward-deployed',
    tagline: 'Why transformation fails inside incumbents, and the operating model that fixes it.',
    cover: '/books/forward-deployed/covers/cover.jpg',
    href: '/books/forward-deployed/README.html',
    status: 'Draft · 16 chapters',
  },
  {
    title: 'Prompt engineering guide for product managers',
    tagline: 'A practical guidebook for turning AI into daily leverage as a product leader.',
    cover: '/books/prompt-engineering-guide/covers/cover.jpg',
    href: '/books/prompt-engineering-guide/README.html',
    status: 'Published · 10 chapters',
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
    const text = inner.replace(/<[^>]+>/g, '').trim();
    const id = slugify(text, seen);
    outline.push({ level: tag === 'h2' ? 2 : 3, id, title: text });
    return `<${tag} id="${id}">${inner}</${tag}>`;
  });
  return { html: updated, outline };
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

const KINDLE_URL = 'https://amzn.in/d/04Wv46eH';

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
        // LinkedIn/other profile URLs go in sameAs once confirmed.
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
      if (page.external) continue;
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

  const highlighter = await createHighlighter({
    themes: ['github-dark'],
    langs: ['javascript', 'typescript', 'python', 'bash', 'json', 'html', 'css', 'markdown'],
  });
  const md = createRenderer({ highlighter });

  const spaceIds = discoverSpaces();
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
    spaceData.push({ spaceId, spaceDir, tree, pages });
  }

  const sitemapUrls = [{ loc: SITE.baseUrl + '/' }];

  for (const { spaceId, spaceDir, tree, pages } of spaceData) {
    const prevNext = computePrevNext(pages);
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      if (page.external) continue;
      const abs = path.join(spaceDir, page.sourcePath);
      const raw = fs.readFileSync(abs, 'utf8');
      const rendered = md.render(raw);
      let { html: contentHtml, outline } = extractOutline(rendered);
      if (spaceId === 'portfolio' && page.sourcePath === 'README.md') {
        contentHtml += renderProductGrid(PRODUCTS);
      }
      if (spaceId === 'books' && page.sourcePath === 'README.md') {
        contentHtml += renderBookGrid(BOOKS);
      }
      const description = extractDescription(raw, SITE.thesis);
      page.description = description;

      const { prev, next } = prevNext.get(i);
      const markdownUrl = page.href.replace(/\.html$/, '.md');
      const extraJsonLd = buildExtraJsonLd(spaceId, page);

      const html = renderPage({
        site: SITE,
        space: { id: spaceId, title: spaceTitle(spaceId) },
        spaces,
        navTree: tree,
        page: { title: page.title, href: page.href, breadcrumb: page.breadcrumb },
        prev,
        next,
        contentHtml,
        outline,
        description,
        extraJsonLd,
        markdownUrl,
      });

      const outPath = path.join(DIST_DIR, page.href.replace(/^\//, ''));
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, html);
      // A clean markdown mirror of every page, for agents/crawlers that
      // prefer fetching source content over HTML-with-chrome.
      fs.writeFileSync(path.join(DIST_DIR, markdownUrl.replace(/^\//, '')), raw);
      sitemapUrls.push({ loc: SITE.baseUrl + page.href });
    }

    copyNestedAssetDirs(spaceDir, path.join(DIST_DIR, spaceId));
  }

  const booksSpace = spaceData.find((s) => s.spaceId === 'books');
  const forwardDeployedChapters = booksSpace
    ? booksSpace.pages.filter(
        (p) => p.breadcrumb[0]?.title === 'Forward-deployed' && p.sourcePath.includes('/chapters/'),
      )
    : [];
  const chapters = forwardDeployedChapters.map((p, i) => ({ n: i + 1, title: p.title, href: p.href, part: '' }));

  fs.writeFileSync(path.join(DIST_DIR, 'index.html'), renderLanding({ site: SITE, spaces, chapters }));
  fs.writeFileSync(path.join(DIST_DIR, '404.html'), render404({ site: SITE }));

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

  copyDir(THEME_STATIC_DIR, DIST_DIR);

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

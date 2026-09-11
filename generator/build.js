import fs from 'node:fs';
import path from 'node:path';
import { createHighlighter } from 'shiki';
import { parseSummary, flattenPages } from './lib/summary.js';
import { createRenderer } from './lib/markdown.js';
import { renderPage, renderLanding } from '../theme/render-page.js';

const ROOT = path.resolve(import.meta.dirname, '..');
const CONTENT_DIR = path.join(ROOT, 'content');
const THEME_STATIC_DIR = path.join(ROOT, 'theme', 'static');
const DIST_DIR = path.join(ROOT, 'dist');

const SITE = {
  title: 'Forward deployed',
  repoUrl: 'https://github.com/aakashagg123/forward-deployed',
  thesis:
    "The unit of change is not a deck — it's a small team of engineers and AI placed at the point of the problem, with the authority to rewire the workflow rather than recommend one.",
};

const SPACE_META = {
  manuscripts: { blurb: 'Forward-deployed — 16 chapters, four parts, one thesis.', status: 'Draft' },
  'personal-notes': { blurb: "Running frameworks and working notes, added as they're written." },
  'project-docs': { blurb: 'Documentation for projects and products, one space per body of work.' },
  research: { blurb: 'Investment and research notes, structured for later reference.' },
};

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

function discoverSpaces() {
  return fs
    .readdirSync(CONTENT_DIR, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}

// Sentence case, derived from the folder name — not the page's own H1, so a
// space's display name stays distinct from whatever its landing page is titled.
function spaceTitle(spaceId) {
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

  for (const { spaceId, spaceDir, tree, pages } of spaceData) {
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      if (page.external) continue;
      const abs = path.join(spaceDir, page.sourcePath);
      const raw = fs.readFileSync(abs, 'utf8');
      const rendered = md.render(raw);
      const { html: contentHtml, outline } = extractOutline(rendered);

      const prev = i > 0 ? pages[i - 1] : null;
      const next = i < pages.length - 1 ? pages[i + 1] : null;

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
      });

      const outPath = path.join(DIST_DIR, page.href.replace(/^\//, ''));
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, html);
    }

    copyDir(path.join(spaceDir, 'assets'), path.join(DIST_DIR, spaceId, 'assets'));
  }

  const manuscriptSpace = spaceData.find((s) => s.spaceId === 'manuscripts');
  const chapters = manuscriptSpace
    ? manuscriptSpace.pages
        .filter((p) => p.sourcePath !== 'README.md')
        .map((p, i) => ({ n: i + 1, title: p.title }))
    : [];

  fs.writeFileSync(path.join(DIST_DIR, 'index.html'), renderLanding({ site: SITE, spaces, chapters }));

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

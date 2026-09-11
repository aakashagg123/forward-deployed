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

const SITE = { title: 'Forward Deployed' };

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

function spaceTitle(spaceId, spaceDir) {
  const readmePath = path.join(spaceDir, 'README.md');
  if (fs.existsSync(readmePath)) {
    const title = readTitleFromMarkdown(fs.readFileSync(readmePath, 'utf8'), null);
    if (title) return title;
  }
  return spaceId
    .split('-')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
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

    const title = spaceTitle(spaceId, spaceDir);
    const indexHref = pages[0].href.replace(`/${spaceId}/`, '');
    spaces.push({ id: spaceId, title, indexHref });
    spaceData.push({ spaceId, spaceDir, tree, pages });
  }

  for (const { spaceId, spaceDir, tree, pages } of spaceData) {
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      if (page.external) continue;
      const abs = path.join(spaceDir, page.sourcePath);
      const raw = fs.readFileSync(abs, 'utf8');
      const contentHtml = md.render(raw);

      const prev = i > 0 ? pages[i - 1] : null;
      const next = i < pages.length - 1 ? pages[i + 1] : null;

      const html = renderPage({
        site: SITE,
        space: { id: spaceId },
        spaces,
        navTree: tree,
        page: { title: page.title, href: page.href, breadcrumb: page.breadcrumb },
        prev,
        next,
        contentHtml,
      });

      const outPath = path.join(DIST_DIR, page.href.replace(/^\//, ''));
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, html);
    }

    copyDir(path.join(spaceDir, 'assets'), path.join(DIST_DIR, spaceId, 'assets'));
  }

  fs.writeFileSync(path.join(DIST_DIR, 'index.html'), renderLanding({ site: SITE, spaces }));

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

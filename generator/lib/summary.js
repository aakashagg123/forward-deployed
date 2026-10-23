// Parses a GitBook-style SUMMARY.md into a nav tree.
// Supported syntax: "# Title" (space title, first line, informational only),
// "## Heading" (grouping header, no link), and "- [Label](path.md)" bullets,
// nested by two-space indentation, which may repeat under multiple headings.

const LINK_RE = /^(\s*)-\s+\[([^\]]*)\]\(([^)]+)\)\s*$/;
const HEADING_RE = /^(#{2,6})\s+(.+?)\s*$/;

export function parseSummary(text, { spaceDir, spaceId }) {
  const lines = text.split('\n');
  const root = { type: 'root', children: [] };
  const stack = [{ indent: -1, node: root }];

  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, '');
    if (!line.trim()) continue;

    const heading = line.match(HEADING_RE);
    if (heading) {
      const node = { type: 'heading', title: heading[2], children: [] };
      root.children.push(node);
      // reset stack so bullets after a heading nest under it
      stack.length = 1;
      stack.push({ indent: -1, node });
      continue;
    }

    const link = line.match(LINK_RE);
    if (link) {
      const [, indentStr, title, href] = link;
      const indent = indentStr.length;
      const target = href.startsWith('http') ? href : normalizeHref(spaceId, spaceDir, href);
      const node = {
        type: 'link',
        title,
        href: target,
        external: href.startsWith('http'),
        sourcePath: href.startsWith('http') ? null : href,
        children: [],
      };

      while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
        stack.pop();
      }
      stack[stack.length - 1].node.children.push(node);
      stack.push({ indent, node });
      continue;
    }
    // "# Title" or any other line — ignored, informational only
  }

  return root;
}

// README.md (at a space root or in any subfolder) is that directory's index:
// it compiles to <dir>/index.html and links as the clean "/dir/" URL, so no
// "/README.html" ever shows in an address bar. Every other page keeps its
// ".html" URL.
function normalizeHref(spaceId, spaceDir, relPath) {
  const clean = relPath.replace(/^\.\//, '');
  if (/(^|\/)README\.md$/.test(clean)) {
    const dir = clean.replace(/README\.md$/, '');
    return `/${spaceId}/${dir}`;
  }
  return `/${spaceId}/${clean.replace(/\.md$/, '.html')}`;
}

// Flattens the tree into document-order list of link nodes, each carrying
// its breadcrumb chain (ancestor headings + link titles).
export function flattenPages(tree) {
  const pages = [];

  function walk(node, breadcrumb) {
    if (node.type === 'link') {
      const page = { ...node, breadcrumb };
      pages.push(page);
      for (const child of node.children) {
        walk(child, [...breadcrumb, { title: node.title, href: node.href }]);
      }
      return;
    }
    if (node.type === 'heading') {
      for (const child of node.children) {
        walk(child, [...breadcrumb, { title: node.title, href: null }]);
      }
      return;
    }
    for (const child of node.children) walk(child, breadcrumb);
  }

  walk(tree, []);
  return pages;
}

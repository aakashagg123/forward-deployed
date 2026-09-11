import MarkdownIt from 'markdown-it';

// Renders markdown to HTML with two custom conventions layered on GFM:
//   1. An image immediately followed by an italic-only paragraph becomes a
//      <figure><img><figcaption> instead of a bare <img> + <p><em>.
//   2. ⟦bracketed text⟧ becomes <span class="fd-slot"> — a visibly marked
//      placeholder for content the author still needs to fill in.
// A paragraph that is *entirely* bold text becomes a <p class="fd-claim">
// display statement, matching how the source manuscript uses bold-only
// paragraphs as standalone claims rather than emphasis within prose.
export function createRenderer({ highlighter }) {
  const md = new MarkdownIt({ html: false, linkify: true, typographer: true });

  md.renderer.rules.image = (tokens, idx) => {
    const token = tokens[idx];
    const src = token.attrGet('src');
    const alt = token.content;
    return `<img src="${src}" alt="${escapeAttr(alt)}" loading="lazy">`;
  };

  const defaultParagraphOpen = md.renderer.rules.paragraph_open || ((t, i, o, e, s) => s.renderToken(t, i, o));
  md.renderer.rules.paragraph_open = (tokens, idx, options, env, self) => {
    if (isBoldOnlyParagraph(tokens, idx)) return '<p class="fd-claim">';
    return defaultParagraphOpen(tokens, idx, options, env, self);
  };

  md.renderer.rules.text = (tokens, idx) => {
    return escapeHtml(tokens[idx].content).replace(
      /⟦([^⟧]+)⟧/g,
      '<span class="fd-slot">⟦$1⟧</span>',
    );
  };

  if (highlighter) {
    md.options.highlight = (code, lang) => {
      try {
        return highlighter.codeToHtml(code, { lang: lang || 'text', theme: 'github-dark' });
      } catch {
        return `<pre class="fallback"><code>${escapeHtml(code)}</code></pre>`;
      }
    };
  }

  return { render: (src) => mergeFigureCaptions(md.render(src)) };
}

// String-level post-process: "<p><img ...></p>\n<p><em>Figure ...</em></p>"
// becomes a proper <figure>/<figcaption> pair. Simpler and far more robust
// than mutating markdown-it's token stream mid-render.
const FIGURE_RE =
  /<p><img ([^>]*)><\/p>\s*<p><em>(Figure[\s\S]*?)<\/em><\/p>/g;

function mergeFigureCaptions(html) {
  return html.replace(FIGURE_RE, (_match, imgAttrs, caption) => {
    return `<figure class="fd-plate"><div class="fd-plate-frame"><img ${imgAttrs}></div><figcaption>${caption}</figcaption></figure>`;
  });
}

function isBoldOnlyParagraph(tokens, openIdx) {
  const inline = tokens[openIdx + 1];
  if (!inline || inline.type !== 'inline') return false;
  const c = inline.children;
  if (!c || c.length < 3) return false;
  return (
    c[0].type === 'strong_open' &&
    c[c.length - 1].type === 'strong_close' &&
    !c.some((t) => t.type === 'softbreak' || t.type === 'hardbreak')
  );
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/"/g, '&quot;');
}

# forward-deployed

A personal GitBook-style site, built by a small custom static site generator and deployed to [forward-deployed.in](https://forward-deployed.in) via GitHub Pages.

## Structure

```
content/<space>/SUMMARY.md   # nav tree for that space
content/<space>/**/*.md      # pages
content/<space>/assets/      # images referenced by that space's pages
generator/                   # the build tool (markdown -> static HTML)
theme/                       # page template + CSS/JS
```

Each top-level folder under `content/` is a "space" (its own sidebar and URL prefix). Current spaces: `manuscripts`, `personal-notes`, `project-docs`, `research`.

## Adding a page

1. Add a markdown file under the right space's folder.
2. Link it from that space's `SUMMARY.md` (nest it under a `##` heading to group it, or indent two spaces under another link to nest it in the sidebar).
3. Push to `main` — GitHub Actions rebuilds and redeploys automatically.

A build fails loudly (and does not deploy) if `SUMMARY.md` links to a file that doesn't exist.

## URLs

A `README.md` compiles to `index.html` in its folder, so it is served at the clean directory URL (`/about/`, `/books/forward-deployed/`). The build also writes a `README.html` redirect stub next to each one, so old links keep working.

Pages listed in `UNLISTED` in `generator/build.js` stay live but are removed from indexes, the sidebar, the sitemap and `llms.txt`, and marked `noindex`.

## Audit

```
npm run build
npm run audit   # internal links, README.html stubs, removed widgets
```

## Local development

```
npm install
npm run build   # writes static site to dist/
npm run serve   # serve dist/ locally
```

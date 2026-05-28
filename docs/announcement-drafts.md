# Announcement drafts

Honest, no-hype copy for posting around v0.1.0 (after first PyPI upload + GitHub release). Each version targets a different audience and reading style.

---

## Hacker News — Show HN

**Title:** `Show HN: excalidraw-render – Pure-Python renderer for .excalidraw files`

**Text post:**

I needed to render .excalidraw files in a CI pipeline without spinning up Chromium or fighting node-canvas. The existing options are excalidraw_export (Node + node-canvas, SVG only) or @excalidraw/excalidraw (React + headless browser). Both are heavier than the job warrants when all you want is a PNG.

excalidraw-render is a small Python tool: parse the .excalidraw JSON, emit SVG, optionally rasterize to PNG via cairosvg. ~2k lines, ~10 MB installed. Single-file or batch-directory modes, mypy strict.

```
pip install excalidraw-render
excalidraw-render diagram.excalidraw
```

Honest trade-off: it doesn't reproduce Excalidraw's hand-drawn / squiggly look. That requires roughjs (JavaScript) and no native Python port exists yet. The output is clean vector, which is what I and most doc-pipeline users actually want. A pyroughjs port is on the v0.2 roadmap.

Element coverage and known gaps are in the README and CHANGELOG. v0.1 covers rectangle, ellipse, diamond, arrow (all 10 arrowhead variants), line, text, freedraw, image, frame. PDF/JPEG output, terminal output (iTerm/Kitty/Sixel), a Markdown preprocessor that inlines .excalidraw refs, and watch mode are queued for v0.2.

Repo: https://github.com/shivama205/excalidraw-render

Happy to take suggestions on what's missing for your use case.

---

## Reddit r/Python

**Title:** `excalidraw-render: render .excalidraw files to PNG/SVG in pure Python, no Node, no headless browser`

**Body:**

Shipping a small tool I built for a docs pipeline at work. Cleanly converts .excalidraw to PNG or SVG without needing Node, node-canvas, or a headless Chrome.

Quick taste:

```bash
pip install excalidraw-render
excalidraw-render diagram.excalidraw          # → diagram.png
excalidraw-render diagram.excalidraw -f svg
excalidraw-render ./docs/                     # batch mode
```

Why a new tool? The existing options:

- `excalidraw_export` (npm): SVG-only, depends on node-canvas which is famously hard to install
- `@excalidraw/excalidraw` (npm): React library, needs a headless browser to render

For automating diagram exports in CI/docs generators, both are heavy. excalidraw-render is just Python + cairosvg.

Honest trade-off: no roughjs hand-drawn style — that's a JS library with no native Python port. The output is clean vector instead, which is usually what doc pipelines want. A pyroughjs port is on the roadmap.

v0.1 covers most element types (rectangle, ellipse, diamond, arrow with all 10 arrowhead variants, line, text, freedraw, image, frame). v0.2 adds PDF/JPEG, terminal output for iTerm2/Kitty/Sixel, a Markdown preprocessor that inlines .excalidraw references, and watch mode.

Repo: https://github.com/shivama205/excalidraw-render

Feedback welcome, especially on element edge cases I might've missed.

---

## Reddit r/excalidraw

**Title:** `New tool — render .excalidraw to PNG/SVG from the command line (pure Python)`

**Body:**

Built this for our docs pipeline at work and figured it might help others — `excalidraw-render` takes a `.excalidraw` file and produces PNG or SVG without needing Node or a browser.

```bash
pip install excalidraw-render
excalidraw-render my-drawing.excalidraw          # → my-drawing.png
excalidraw-render my-drawing.excalidraw -f svg
excalidraw-render ./drawings/                    # batch mode
```

It's complementary to the official Excalidraw app — not a replacement. Use Excalidraw to draw; use this when you want automated exports for docs, slide decks, or CI.

Honest caveat: doesn't reproduce the hand-drawn / squiggly look (that's roughjs, JS-only). Output is clean vector instead. If you need the squiggly look for a particular doc, keep using Excalidraw's built-in export. If you want consistent, scriptable output for a build pipeline, this is for you.

Repo + docs: https://github.com/shivama205/excalidraw-render

---

## Twitter / X

**Tweet 1 (announcement):**

shipped excalidraw-render — render .excalidraw files to PNG or SVG in pure Python

no Node, no headless browser, no node-canvas. ~10 MB install.

useful for docs pipelines, CI, MkDocs/Sphinx/Hugo, slide generators

→ github.com/shivama205/excalidraw-render

**Tweet 2 (follow-up — honesty thread):**

trade-off worth being upfront about: it doesn't render the hand-drawn squiggly style. that's roughjs and there's no native Python port yet.

it gives you clean vector output instead, which is what most doc pipelines actually want.

pyroughjs port is on the v0.2 list.

**Tweet 3 (technical detail):**

v0.1 element coverage:
• rectangle / ellipse / diamond
• arrow (10 arrowhead variants incl. crowfoot)
• line / text / freedraw / image / frame
• stroke styles, opacity, rotation, multi-line text

mypy strict, 30 tests, batch mode, ready for `pip install`

---

## Dev.to / Personal blog

**Title:** `Why I built excalidraw-render: A pure-Python exporter for Excalidraw diagrams`

**Lede:**

I love Excalidraw. The sketchy aesthetic, the speed, the fact that the file format is just JSON — all of it. What I don't love is exporting them from a CI pipeline.

The two existing options are excalidraw_export (Node + node-canvas, which is famously hard to install) and embedding @excalidraw/excalidraw in a headless browser. For automatically baking diagrams into a docs site at build time, both are heavier than they need to be.

So I built `excalidraw-render`.

**What it does**

(insert install + usage demo from README)

**What it doesn't do (yet)**

(insert trade-off section about roughjs)

**The technical bits**

The renderer parses `.excalidraw` JSON into typed Python dataclasses. Each element type gets its own SVG fragment renderer. cairosvg rasterizes SVG to PNG. The whole thing is ~2k lines, mypy strict.

I aimed for it to be useful for:
- Static-site generators (Hugo / MkDocs / Sphinx) baking diagrams at build time
- CI/screenshot pipelines without Chromium
- Doc + slide generators wanting deterministic output

**What's next**

v0.2 is the bigger release: pyroughjs port for hand-drawn style, PDF/JPEG output, terminal output (iTerm/Kitty/Sixel), a Markdown preprocessor that inlines .excalidraw refs.

Repo: https://github.com/shivama205/excalidraw-render
Install: `pip install excalidraw-render`

---

## A note on timing & honesty

- Don't post until v0.1.0 is actually on PyPI and `pip install excalidraw-render` works.
- Don't oversell. v0.1 has real limitations (no roughness, no PDF, fixture-driven tests rather than exhaustive Excalidraw-export round-trips). Be upfront and the audience will respect it.
- Hacker News tends to react badly to overclaiming. The drafts above are deliberately calibrated.
- Best window: Tuesday–Thursday, ~9am Pacific (peak HN traffic). Reddit posts work any time but new-subscriber visibility is best on weekdays.

## Lists to submit to (lower-effort marketing)

- [awesome-python](https://github.com/vinta/awesome-python) — under "Image Processing" or "CLI Utilities"
- [awesome-excalidraw](https://github.com/excalidraw/awesome-excalidraw) — under "Tools & Integrations"
- [PyCoder's Weekly](https://pycoders.com/) — submit at https://pycoders.com/submit
- [Python Weekly](https://www.pythonweekly.com/) — email curated newsletter

# excalidraw-render

Clean, deterministic, browser-free renderer for `.excalidraw` files.

```bash
pip install excalidraw-render
excalidraw-render diagram.excalidraw          # writes diagram.png
excalidraw-render diagram.excalidraw -f svg   # writes diagram.svg
excalidraw-render diagram.excalidraw --width 1200
excalidraw-render ./docs/                     # batch mode: every .excalidraw in directory
```

## Why

The Excalidraw ecosystem's existing renderers either need Node + `node-canvas` (`excalidraw_export`) or a headless browser running React (`@excalidraw/excalidraw`). Both are heavy, fragile in CI, and slow to start.

`excalidraw-render` is Python + cairosvg. No JS. No browser. Single-digit-megabyte install. Useful for:

- Doc site / static-site generators (Hugo, MkDocs, Sphinx) that need to bake `.excalidraw` to PNG at build time
- Screenshot pipelines / regression tests
- Terminal viewers (Kitty, iTerm2, Sixel) — coming in v0.2
- Any CI where you want diagrams rendered without spinning up Chromium

## Status

**Pre-alpha**, v0.1 in progress. Element coverage and feature checklist in `docs/elements.md`.

## Trade-off: no "hand-drawn" style

`excalidraw-render` produces **clean vector output**, not the squiggly hand-drawn look that Excalidraw's official export uses. The hand-drawn style requires roughjs, a JS library with no native Python port. This is a deliberate trade-off — clean output is what most doc / slide / report pipelines actually want, and skipping roughjs removes the heaviest dependency.

A roughjs Python port (`pyroughjs`) is on the v0.2 roadmap.

## Comparison

| | `excalidraw-render` (this) | `excalidraw_export` (npm) | `@excalidraw/excalidraw` (npm) |
|---|---|---|---|
| Language | Python | Node | React + Node |
| Hand-drawn (roughjs) style | No (v0.2 stretch) | Yes | Yes |
| PNG output | Yes | via rsvg-convert | Yes |
| SVG output | Yes | Yes | Yes |
| PDF output | v0.2 | via rsvg-convert | No |
| Headless browser needed | No | No | Yes |
| Native canvas / image libs needed | No | Yes (node-canvas) | No |
| Install size | ~10MB | ~150MB | Depends |
| Batch / watch mode | Yes (v0.1 / v0.2) | No | No |
| Terminal protocols | v0.2 (iTerm/Kitty/Sixel) | No | No |

## License

MIT

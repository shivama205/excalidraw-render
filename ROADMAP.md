# Roadmap

Where `excalidraw-render` is headed, one release at a time. One real feature
per minor release, roughly every 1–3 weeks. Pre-1.0, minor versions may break
API; every break is flagged in [CHANGELOG.md](CHANGELOG.md).

## The 1.0.0 promise

1.0.0 is a commitment, not a feature count:

1. **Rendering fidelity** — output you can trust to match the Excalidraw
   editor, proven by golden-image tests against official exports.
2. **API stability** — the public surface (`load_scene`, `render_svg`,
   `render_png`, `render_pdf`, `render_jpg`, the element model) is frozen and
   documented; strict semver from then on.
3. **Completeness** — every standard Excalidraw element and cross-cutting
   feature renders, including the hand-drawn look.

## Release ladder

| Version | Feature | Status |
|---|---|---|
| 0.1.0 | Core renderer: 9 element types, arrowheads, styling, CLI, batch mode | ✅ shipped 2026-05-29 |
| 0.2.0 | PDF + JPEG output, container-bound text layout fix | ✅ shipped 2026-06-12 |
| 0.3.0 | Watch mode (`--watch`) | 🔜 merged, releasing ~2026-06-19 |
| 0.4.0 | Fill patterns (hachure, cross-hatch, zigzag, dots, dashed) | 🔜 merged, next after 0.3.0 |
| 0.5.0 | Markdown preprocessor subcommand — render `.excalidraw` references in a docs tree | planned |
| 0.6.0 | Terminal output (Kitty graphics, iTerm2 OSC-1337, Sixel) | planned |
| 0.7.0 | `pyroughjs` alpha — hand-drawn look behind a `--rough` flag | planned |
| 0.8.0 | Real text metrics + Excalidraw font embedding (Excalifont/Virgil, Cascadia) | planned |
| 0.9.0 | Golden round-trip tests vs official Excalidraw exports; API freeze (RC) | planned |
| 1.0.0 | Stable | planned |

Versions between these may appear for bugfixes (patch) or small features that
don't warrant a slot of their own (`link` anchors, group transforms, frame
clipping, `magicframe`).

## The long pole: pyroughjs

A pure-Python, seeded-deterministic port of [roughjs](https://roughjs.com/) is
the largest single work item and the most-requested gap. It runs as a
background track well before its 0.7.0 slot — possibly as its own package so
other Python projects can use it too.

## Suggesting changes

Open an issue at
https://github.com/shivama205/excalidraw-render/issues — the ladder above is
a plan, not a contract; real usage reports reorder it.

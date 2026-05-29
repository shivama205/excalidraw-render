# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-05-29

### Fixed
- Restore `pillow` as a runtime dependency. `cairosvg`'s `surface.py`
  imports PIL at module load even when we don't render embedded SVG
  `<image>` elements, so dropping it in 0.1.1 broke `render_png` for
  every input. v0.1.1 should be considered broken — use 0.1.2 or later.

## [0.1.1] - 2026-05-29 (broken — do not use)

### Fixed
- Removed unused `pillow` runtime dependency. Reverted in 0.1.2 because
  cairosvg actually does need it at module-load time.

## [0.1.0] - 2026-05-29

### Added
- Initial repo scaffold: `pyproject.toml`, package layout (`src/excalidraw_render/`), MIT license, ruff + mypy + pytest config.
- Typed element model (`element.py`): dataclasses for every common Excalidraw element type with a tolerant JSON parser.
- Renderers (`renderers/`): SVG output for `rectangle`, `ellipse`, `diamond`, `arrow`, `line`, `text`, `freedraw`, `image`, `frame`.
- Arrowhead variants: `arrow`, `triangle`, `triangle_outline`, `bar`, `dot`, `diamond`, `diamond_outline`, `crowfoot_one`, `crowfoot_many`, `crowfoot_one_or_many`.
- Stroke styles: `solid`, `dashed`, `dotted`. Opacity. Element rotation via `angle`.
- Multi-line text with `text_align` and `vertical_align`, mapped to web-safe font families.
- Freedraw smoothing via Catmull-Rom to cubic Bezier conversion.
- Image elements decoded from the scene's `files` dict (data URLs embedded into SVG).
- Frame elements rendered as labeled dashed boundary rectangles.
- Top-level `render_svg(scene)` and `render_png(scene, out, ...)` entry points.
- CLI `excalidraw-render FILE [DIR]` with `-o/--output`, `-f/--format {png,svg}`, `--width`, `--scale`, `--no-background`, `--padding`. Single-file and batch-directory modes.
- 30 tests (`test_element.py`, `test_render.py`, `test_cli.py`) with hand-crafted fixtures covering every supported element type. Ruff + mypy clean.

### Deferred to v0.2
- Roughness (`roughjs`-style hand-drawn look). Pure-Python port (`pyroughjs`) on the roadmap.
- PDF and JPEG output.
- Container-bound text positioning fidelity (`containerId` lookup → padding-respecting text placement).
- Hachure / cross-hatch / zigzag / dots fill patterns (currently fall back to solid).
- Terminal output subcommands (iTerm2 OSC-1337, Kitty graphics protocol, Sixel).
- Markdown preprocessor subcommand (replaces `mdview`).
- Watch mode (re-render on file change).
- Real Excalidraw export round-trip tests against the public Excalidraw repo's example files.

### Known limitations
- Shorthand `label` field on shapes (an MCP / `mdview` extension, not standard Excalidraw) is not rendered. Use a separate `text` element with `containerId` instead. Adding shorthand support is tracked for v0.2.
- Text positioning inside container shapes is currently text-element-driven (x/y must already match the container). True container-relative layout (padding, vertical alignment relative to container) is deferred.
- Group-level transforms are not yet applied as a single matrix; per-element rotation/transform works.

# Element Coverage

Tracks our support for each Excalidraw element type and feature, against
[Excalidraw's element schema](https://github.com/excalidraw/excalidraw/blob/master/packages/excalidraw/element/types.ts).

Legend: ☐ not started · ⏳ in progress · ☑ done · — N/A · skip not in v0.1

## Element types

| Type | Status | Notes |
|---|---|---|
| `rectangle` | ☐ | Includes `roundness` (rounded corners). |
| `ellipse` | ☐ | |
| `diamond` | ☐ | Includes `roundness`. |
| `line` | ☐ | Straight line, optional curve via `points` array. |
| `arrow` | ☐ | All arrowhead variants: `arrow`, `bar`, `dot`, `triangle`, `triangle_outline`, `diamond`, `diamond_outline`, `crowfoot_one`, `crowfoot_many`, `crowfoot_one_or_many`. |
| `text` | ☐ | Multi-line, font family, alignment, container-bound (positioning vs. its container shape). |
| `freedraw` | ☐ | Smooth path through points (Catmull-Rom spline). Pressure curves not in v0.1. |
| `image` | ☐ | Embedded via `files` dict (data URLs). |
| `frame` | ☐ | Clip-path + frame label. |
| `magicframe` | skip | AI-generated frame; same shape as `frame`. v0.2. |
| `iframe` | skip | Web embed; not meaningful in static export. |
| `embeddable` | skip | Same as iframe for our purposes. |

## Cross-cutting features

| Feature | Status | Notes |
|---|---|---|
| `strokeColor` | ☐ | Hex colors. |
| `backgroundColor` | ☐ | Hex colors. |
| `strokeWidth` | ☐ | Integer pixels. |
| `strokeStyle` | ☐ | `solid` / `dashed` / `dotted`. |
| `fillStyle` | ☐ | `solid` first. `hachure` / `cross-hatch` as SVG pattern approximations (v0.1). |
| `opacity` | ☐ | 0–100 → SVG `opacity` 0–1. |
| `angle` | ☐ | Element rotation in radians; SVG `transform="rotate(...)"`. |
| `roughness` | — | Not supported in v0.1 — see README. |
| `groupIds` | ☐ | Group transforms (rotation/translation applied to group as a unit). |
| `boundElements` | ☐ | Text bound to a container — positioning + clipping. |
| `containerId` (on text) | ☐ | Same as above, from the text side. |
| `link` | skip | SVG `<a xlink:href="...">` wrap; v0.2. |

## Rendering pipeline

1. Parse `.excalidraw` JSON → typed dataclasses (`element.py`).
2. Resolve group transforms and container relationships (`layout.py`).
3. Compute scene bounding box for viewBox.
4. Emit SVG fragments per element (`renderers/<type>.py`).
5. Wrap in `<svg>` document with background.
6. Optional: cairosvg → PNG.

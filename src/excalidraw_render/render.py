"""Scene → SVG, optionally → PNG. Top-level rendering entry points."""

from __future__ import annotations

import json
import math
from io import BytesIO
from pathlib import Path
from typing import IO, Any

from excalidraw_render.element import (
    ArrowElement,
    DiamondElement,
    EllipseElement,
    ExcalidrawElement,
    FrameElement,
    FreeDrawElement,
    ImageElement,
    LineElement,
    RectangleElement,
    Scene,
    TextElement,
    UnknownElement,
    parse_scene,
)
from excalidraw_render.renderers import (
    render_arrow,
    render_diamond,
    render_ellipse,
    render_frame,
    render_freedraw,
    render_image,
    render_line,
    render_rectangle,
    render_text,
)
from excalidraw_render.renderers._util import fmt

DEFAULT_PADDING = 20
DEFAULT_BACKGROUND = "#ffffff"


def _render_element(el: ExcalidrawElement, scene: Scene) -> str:
    if isinstance(el, RectangleElement):
        return render_rectangle(el)
    if isinstance(el, EllipseElement):
        return render_ellipse(el)
    if isinstance(el, DiamondElement):
        return render_diamond(el)
    if isinstance(el, ArrowElement):
        return render_arrow(el)
    if isinstance(el, LineElement):
        return render_line(el)
    if isinstance(el, TextElement):
        return render_text(el)
    if isinstance(el, FreeDrawElement):
        return render_freedraw(el)
    if isinstance(el, ImageElement):
        return render_image(el, scene.files)
    if isinstance(el, FrameElement):
        return render_frame(el)
    if isinstance(el, UnknownElement):
        return f'<!-- unhandled element type: {el.type} -->'
    return ""


def _scene_bbox(scene: Scene) -> tuple[float, float, float, float]:
    """Compute the bounding box covering all rendered elements."""
    if not scene.elements:
        return (0.0, 0.0, 100.0, 100.0)

    min_x = math.inf
    min_y = math.inf
    max_x = -math.inf
    max_y = -math.inf

    for el in scene.elements:
        # Account for rotation when computing the bbox.
        if el.angle:
            cx = el.x + el.width / 2
            cy = el.y + el.height / 2
            corners = [
                (el.x, el.y),
                (el.x + el.width, el.y),
                (el.x + el.width, el.y + el.height),
                (el.x, el.y + el.height),
            ]
            cos_a = math.cos(el.angle)
            sin_a = math.sin(el.angle)
            for px, py in corners:
                rx = cx + (px - cx) * cos_a - (py - cy) * sin_a
                ry = cy + (px - cx) * sin_a + (py - cy) * cos_a
                min_x = min(min_x, rx)
                max_x = max(max_x, rx)
                min_y = min(min_y, ry)
                max_y = max(max_y, ry)
        else:
            min_x = min(min_x, el.x)
            max_x = max(max_x, el.x + el.width)
            min_y = min(min_y, el.y)
            max_y = max(max_y, el.y + el.height)

    if min_x == math.inf:
        return (0.0, 0.0, 100.0, 100.0)
    return (min_x, min_y, max_x, max_y)


def render_svg(
    scene: Scene,
    *,
    padding: float = DEFAULT_PADDING,
    background: str | None = DEFAULT_BACKGROUND,
) -> str:
    """Render a Scene to a complete SVG document string."""
    min_x, min_y, max_x, max_y = _scene_bbox(scene)
    width = max_x - min_x + 2 * padding
    height = max_y - min_y + 2 * padding
    vx = min_x - padding
    vy = min_y - padding

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{fmt(width)}" height="{fmt(height)}" '
        f'viewBox="{fmt(vx)} {fmt(vy)} {fmt(width)} {fmt(height)}">'
    ]
    if background:
        parts.append(
            f'<rect x="{fmt(vx)}" y="{fmt(vy)}" '
            f'width="{fmt(width)}" height="{fmt(height)}" fill="{background}"/>'
        )
    parts.extend(_render_element(el, scene) for el in scene.elements)
    parts.append("</svg>")
    return "\n".join(p for p in parts if p)


def render_png(
    scene: Scene,
    out: IO[bytes] | Path | str,
    *,
    width: int | None = None,
    scale: float = 1.0,
    padding: float = DEFAULT_PADDING,
    background: str | None = DEFAULT_BACKGROUND,
) -> None:
    """Render a Scene to a PNG. Writes to `out` (file path or binary file-like)."""
    import cairosvg  # local import — cairosvg is heavy; let SVG-only use skip it.

    svg = render_svg(scene, padding=padding, background=background)
    target: str | IO[bytes] = str(out) if isinstance(out, (str, Path)) else out

    kwargs: dict[str, Any] = {}
    if width:
        kwargs["output_width"] = width
    else:
        kwargs["scale"] = scale

    if isinstance(target, str):
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=target, **kwargs)
    else:
        buf = BytesIO()
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=buf, **kwargs)
        target.write(buf.getvalue())


def load_scene(path: Path | str) -> Scene:
    """Read a .excalidraw file from disk and parse to a Scene."""
    p = Path(path)
    data = json.loads(p.read_text())
    return parse_scene(data, source=str(p))

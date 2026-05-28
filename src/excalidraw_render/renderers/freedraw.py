"""Freedraw element — smooth path through user-drawn points."""

from __future__ import annotations

from excalidraw_render.element import FreeDrawElement
from excalidraw_render.renderers._util import (
    fmt,
    opacity_fraction,
    stroke_dasharray,
    transform_attr,
)


def _absolute(el: FreeDrawElement) -> list[tuple[float, float]]:
    return [(el.x + p[0], el.y + p[1]) for p in el.points]


def _catmull_rom_path(points: list[tuple[float, float]]) -> str:
    """Convert points to an SVG path using Catmull-Rom → Bezier conversion.

    Produces a smooth path; with very few points, falls back to straight lines.
    """
    if not points:
        return ""
    if len(points) < 3:
        head = f"M {fmt(points[0][0])} {fmt(points[0][1])}"
        rest = " ".join(f"L {fmt(x)} {fmt(y)}" for x, y in points[1:])
        return f"{head} {rest}".rstrip()

    # Catmull-Rom to cubic Bezier conversion.
    # For each segment p1→p2, control points derive from p0, p1, p2, p3.
    extended = [points[0], *points, points[-1]]
    d = [f"M {fmt(points[0][0])} {fmt(points[0][1])}"]
    for i in range(1, len(extended) - 2):
        p0 = extended[i - 1]
        p1 = extended[i]
        p2 = extended[i + 1]
        p3 = extended[i + 2]
        c1x = p1[0] + (p2[0] - p0[0]) / 6
        c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6
        c2y = p2[1] - (p3[1] - p1[1]) / 6
        d.append(
            f"C {fmt(c1x)} {fmt(c1y)}, {fmt(c2x)} {fmt(c2y)}, {fmt(p2[0])} {fmt(p2[1])}"
        )
    return " ".join(d)


def render_freedraw(el: FreeDrawElement) -> str:
    pts = _absolute(el)
    if not pts:
        return ""
    d = _catmull_rom_path(pts)
    parts = [
        'fill="none"',
        f'stroke="{el.stroke_color}"',
        f'stroke-width="{fmt(el.stroke_width)}"',
        'stroke-linecap="round"',
        'stroke-linejoin="round"',
    ]
    dash = stroke_dasharray(el.stroke_style, el.stroke_width)
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    parts.append(f'opacity="{fmt(opacity_fraction(el.opacity), precision=3)}"')
    return f'<path d="{d}" {" ".join(parts)}{transform_attr(el)} />'

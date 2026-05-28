"""Shared rendering helpers — coordinate formatting, stroke styles, transforms."""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

from excalidraw_render.element import ExcalidrawElementBase, StrokeStyle


def fmt(value: float, *, precision: int = 2) -> str:
    """Format a float with stripped trailing zeros — for SVG coordinate compactness."""
    s = f"{value:.{precision}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def fmt_xy(point: tuple[float, float]) -> str:
    """Format a 2D point as `x,y` for SVG polygon/polyline `points` attributes."""
    return f"{fmt(point[0])},{fmt(point[1])}"


def text_escape(text: str) -> str:
    """XML-escape text content."""
    return escape(text)


def stroke_dasharray(style: StrokeStyle, stroke_width: float) -> str:
    """Return the SVG `stroke-dasharray` value (without attribute name) for an Excalidraw style."""
    if style == "dashed":
        return f"{stroke_width * 4} {stroke_width * 2}"
    if style == "dotted":
        return f"{stroke_width} {stroke_width * 2}"
    return ""


def opacity_fraction(opacity_pct: float) -> float:
    """Excalidraw stores opacity as 0-100; SVG wants 0-1."""
    return max(0.0, min(1.0, opacity_pct / 100.0))


def transform_attr(element: ExcalidrawElementBase) -> str:
    """SVG transform attribute for element rotation around its center.

    Empty string if angle == 0.
    """
    if not element.angle:
        return ""
    cx = element.x + element.width / 2
    cy = element.y + element.height / 2
    deg = math.degrees(element.angle)
    return f' transform="rotate({fmt(deg)} {fmt(cx)} {fmt(cy)})"'


def stroke_style_attrs(element: ExcalidrawElementBase) -> str:
    """Compose stroke + opacity attributes for an element."""
    parts = [
        f'stroke="{element.stroke_color}"',
        f'stroke-width="{fmt(element.stroke_width)}"',
    ]
    dash = stroke_dasharray(element.stroke_style, element.stroke_width)
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
        parts.append('stroke-linecap="round"')
    parts.append(f'opacity="{fmt(opacity_fraction(element.opacity), precision=3)}"')
    return " ".join(parts)


def fill_attr(element: ExcalidrawElementBase) -> str:
    """Return the SVG `fill` attribute value for an element.

    `transparent` background → `none` fill.
    `fill_style` other than `solid` → handled by a separate pattern reference in v0.2.
    """
    bg = element.background_color
    if not bg or bg.lower() in ("transparent", "none"):
        return 'fill="none"'
    # v0.1: render hachure / cross-hatch / etc. as solid fills.
    # Real hatch patterns come in v0.2.
    return f'fill="{bg}"'

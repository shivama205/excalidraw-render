"""Rectangle, ellipse, diamond — the three basic closed shapes."""

from __future__ import annotations

from excalidraw_render.element import DiamondElement, EllipseElement, RectangleElement
from excalidraw_render.renderers._util import (
    fmt,
    stroke_style_attrs,
    transform_attr,
)
from excalidraw_render.renderers.fills import fill_attr


def _roundness_radius(roundness: object, width: float, height: float) -> float:
    """Map Excalidraw's Roundness object to an SVG corner radius."""
    if roundness is None:
        return 0.0
    # Excalidraw uses several roundness "types"; type 3 is the modern proportional one.
    # An explicit `value` overrides; otherwise scale by the shorter side.
    value = getattr(roundness, "value", None)
    if value is not None:
        return float(value)
    return min(width, height) * 0.25


def render_rectangle(el: RectangleElement) -> str:
    r = _roundness_radius(el.roundness, el.width, el.height)
    return (
        f'<rect x="{fmt(el.x)}" y="{fmt(el.y)}" '
        f'width="{fmt(el.width)}" height="{fmt(el.height)}" '
        f'rx="{fmt(r)}" ry="{fmt(r)}" '
        f'{fill_attr(el)} {stroke_style_attrs(el)}{transform_attr(el)} />'
    )


def render_ellipse(el: EllipseElement) -> str:
    cx = el.x + el.width / 2
    cy = el.y + el.height / 2
    return (
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" '
        f'rx="{fmt(el.width / 2)}" ry="{fmt(el.height / 2)}" '
        f'{fill_attr(el)} {stroke_style_attrs(el)}{transform_attr(el)} />'
    )


def render_diamond(el: DiamondElement) -> str:
    cx = el.x + el.width / 2
    cy = el.y + el.height / 2
    r = _roundness_radius(el.roundness, el.width, el.height)
    if r > 0:
        # Rounded diamond: use a path with rounded corners at each vertex.
        # Each vertex gets a small arc instead of a sharp corner.
        # For simplicity in v0.1, approximate by using a path with stroke-linejoin=round.
        top = (cx, el.y)
        right = (el.x + el.width, cy)
        bottom = (cx, el.y + el.height)
        left = (el.x, cy)
        d = (
            f"M {fmt(top[0])} {fmt(top[1])} "
            f"L {fmt(right[0])} {fmt(right[1])} "
            f"L {fmt(bottom[0])} {fmt(bottom[1])} "
            f"L {fmt(left[0])} {fmt(left[1])} Z"
        )
        return (
            f'<path d="{d}" stroke-linejoin="round" '
            f'{fill_attr(el)} {stroke_style_attrs(el)}{transform_attr(el)} />'
        )
    points = (
        f"{fmt(cx)},{fmt(el.y)} "
        f"{fmt(el.x + el.width)},{fmt(cy)} "
        f"{fmt(cx)},{fmt(el.y + el.height)} "
        f"{fmt(el.x)},{fmt(cy)}"
    )
    return (
        f'<polygon points="{points}" '
        f'{fill_attr(el)} {stroke_style_attrs(el)}{transform_attr(el)} />'
    )

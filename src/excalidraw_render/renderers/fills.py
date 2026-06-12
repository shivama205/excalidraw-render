"""SVG pattern fills approximating Excalidraw's roughjs fill styles.

Excalidraw fills shapes by drawing roughjs hachure / cross-hatch / zigzag /
dots strokes. Without roughjs we approximate each style with a deterministic
SVG `<pattern>`. Geometry follows roughjs defaults: fill weight =
strokeWidth / 2, hachure gap = strokeWidth * 4, hachure angle = -41°.

Pattern ids are derived from (fill_style, background_color, stroke_width), so
`fill_attr()` on an element and `pattern_def()` collected by `render_svg()`
agree without coordination, and identical fills share one def.
"""

from __future__ import annotations

import re

from excalidraw_render.element import ExcalidrawElementBase
from excalidraw_render.renderers._util import fmt

PATTERN_FILL_STYLES = frozenset(
    {"hachure", "cross-hatch", "zigzag", "zigzag-line", "dots", "dashed"}
)

_HACHURE_ANGLE = -41


def _paintable(el: ExcalidrawElementBase) -> bool:
    bg = el.background_color
    return bool(bg) and bg.lower() not in ("transparent", "none")


def uses_pattern_fill(el: ExcalidrawElementBase) -> bool:
    """True if this element's fill is rendered via a pattern def."""
    return el.fill_style in PATTERN_FILL_STYLES and _paintable(el)


def _geometry(stroke_width: float) -> tuple[float, float]:
    """(tile size aka hachure gap, line weight) per roughjs defaults."""
    gap = max(stroke_width * 4, 4.0)
    weight = max(stroke_width / 2, 0.5)
    return gap, weight


def pattern_id(el: ExcalidrawElementBase) -> str:
    color = re.sub(r"[^a-zA-Z0-9]", "", el.background_color)
    width = fmt(el.stroke_width).replace(".", "-")
    return f"fill-{el.fill_style}-{color}-{width}"


def pattern_def(el: ExcalidrawElementBase) -> str:
    """The `<pattern>` element for an element's fill, for the SVG `<defs>` block."""
    g, w = _geometry(el.stroke_width)
    color = el.background_color
    style = el.fill_style
    head = (
        f'<pattern id="{pattern_id(el)}" patternUnits="userSpaceOnUse" '
        f'width="{fmt(g)}" height="{fmt(g)}"'
    )
    rotate = f' patternTransform="rotate({_HACHURE_ANGLE})"'
    vline = (
        f'<line x1="0" y1="0" x2="0" y2="{fmt(g)}" '
        f'stroke="{color}" stroke-width="{fmt(w)}"/>'
    )

    if style == "hachure":
        return f"{head}{rotate}>{vline}</pattern>"
    if style == "cross-hatch":
        hline = (
            f'<line x1="0" y1="0" x2="{fmt(g)}" y2="0" '
            f'stroke="{color}" stroke-width="{fmt(w)}"/>'
        )
        return f"{head}{rotate}>{vline}{hline}</pattern>"
    if style in ("zigzag", "zigzag-line"):
        path = (
            f'<path d="M 0 {fmt(g * 0.75)} L {fmt(g / 2)} {fmt(g * 0.25)} '
            f'L {fmt(g)} {fmt(g * 0.75)}" fill="none" stroke="{color}" '
            f'stroke-width="{fmt(w)}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        return f"{head}{rotate}>{path}</pattern>"
    if style == "dots":
        r = fmt(w * 1.2)
        dots = (
            f'<circle cx="{fmt(g / 4)}" cy="{fmt(g / 4)}" r="{r}" fill="{color}"/>'
            f'<circle cx="{fmt(g * 3 / 4)}" cy="{fmt(g * 3 / 4)}" r="{r}" fill="{color}"/>'
        )
        return f"{head}>{dots}</pattern>"
    # dashed — dashed hachure lines; dash period == tile size so tiles join seamlessly.
    dline = (
        f'<line x1="0" y1="0" x2="0" y2="{fmt(g)}" stroke="{color}" '
        f'stroke-width="{fmt(w)}" stroke-dasharray="{fmt(g / 2)} {fmt(g / 2)}"/>'
    )
    return f"{head}{rotate}>{dline}</pattern>"


def fill_attr(element: ExcalidrawElementBase) -> str:
    """Return the SVG `fill` attribute for an element.

    `transparent` background → `none`; pattern fill styles → `url(#...)`
    reference (the matching def is emitted by `render_svg`); otherwise solid.
    """
    if not _paintable(element):
        return 'fill="none"'
    if element.fill_style in PATTERN_FILL_STYLES:
        return f'fill="url(#{pattern_id(element)})"'
    return f'fill="{element.background_color}"'

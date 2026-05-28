"""Arrow + line renderers, including arrowhead variants."""

from __future__ import annotations

import math

from excalidraw_render.element import ArrowElement, Arrowhead, LinearElement, LineElement
from excalidraw_render.renderers._util import (
    fmt,
    fmt_xy,
    opacity_fraction,
    stroke_dasharray,
    transform_attr,
)


def _absolute_points(el: LinearElement) -> list[tuple[float, float]]:
    return [(el.x + p[0], el.y + p[1]) for p in el.points]


def _polyline_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    head = f"M {fmt(points[0][0])} {fmt(points[0][1])}"
    rest = " ".join(f"L {fmt(x)} {fmt(y)}" for x, y in points[1:])
    return f"{head} {rest}".rstrip()


def _line_attrs(el: LinearElement) -> str:
    parts = [
        'fill="none"',
        f'stroke="{el.stroke_color}"',
        f'stroke-width="{fmt(el.stroke_width)}"',
        'stroke-linejoin="round"',
        'stroke-linecap="round"',
    ]
    dash = stroke_dasharray(el.stroke_style, el.stroke_width)
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    parts.append(f'opacity="{fmt(opacity_fraction(el.opacity), precision=3)}"')
    return " ".join(parts)


def _arrowhead(p_prev: tuple[float, float], p_last: tuple[float, float],
               kind: Arrowhead, color: str, stroke_w: float) -> str:
    """Render an arrowhead at p_last, pointing away from p_prev."""
    dx = p_last[0] - p_prev[0]
    dy = p_last[1] - p_prev[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    px, py = -uy, ux  # perpendicular unit vector

    size = max(8.0, stroke_w * 4)
    half_width = size * 0.5
    base_x = p_last[0] - ux * size
    base_y = p_last[1] - uy * size
    left = (base_x + px * half_width, base_y + py * half_width)
    right = (base_x - px * half_width, base_y - py * half_width)

    if kind in ("arrow", "triangle"):
        pts = f"{fmt_xy(p_last)} {fmt_xy(left)} {fmt_xy(right)}"
        return f'<polygon points="{pts}" fill="{color}" stroke="{color}" />'
    if kind == "triangle_outline":
        pts = f"{fmt_xy(p_last)} {fmt_xy(left)} {fmt_xy(right)}"
        return (
            f'<polygon points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{fmt(stroke_w)}" stroke-linejoin="round" />'
        )
    if kind == "bar":
        end_x = p_last[0] + px * half_width
        end_y = p_last[1] + py * half_width
        start_x = p_last[0] - px * half_width
        start_y = p_last[1] - py * half_width
        return (
            f'<line x1="{fmt(start_x)}" y1="{fmt(start_y)}" '
            f'x2="{fmt(end_x)}" y2="{fmt(end_y)}" '
            f'stroke="{color}" stroke-width="{fmt(stroke_w)}" stroke-linecap="round" />'
        )
    if kind == "dot":
        r = half_width
        return (
            f'<circle cx="{fmt(p_last[0])}" cy="{fmt(p_last[1])}" r="{fmt(r)}" '
            f'fill="{color}" />'
        )
    if kind in ("diamond", "diamond_outline"):
        far = (p_last[0] - ux * size * 1.6, p_last[1] - uy * size * 1.6)
        mid = (p_last[0] - ux * size * 0.8, p_last[1] - uy * size * 0.8)
        side_l = (mid[0] + px * half_width, mid[1] + py * half_width)
        side_r = (mid[0] - px * half_width, mid[1] - py * half_width)
        pts = f"{fmt_xy(p_last)} {fmt_xy(side_l)} {fmt_xy(far)} {fmt_xy(side_r)}"
        if kind == "diamond":
            return f'<polygon points="{pts}" fill="{color}" stroke="{color}" />'
        return (
            f'<polygon points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{fmt(stroke_w)}" stroke-linejoin="round" />'
        )
    if kind == "crowfoot_many":
        bar_pos = (p_last[0] - ux * size * 1.4, p_last[1] - uy * size * 1.4)
        left_tip = (p_last[0] + px * half_width, p_last[1] + py * half_width)
        right_tip = (p_last[0] - px * half_width, p_last[1] - py * half_width)
        return (
            f'<polyline points="{fmt_xy(left_tip)} {fmt_xy(bar_pos)} {fmt_xy(right_tip)}" '
            f'fill="none" stroke="{color}" stroke-width="{fmt(stroke_w)}" '
            f'stroke-linejoin="round" stroke-linecap="round" />'
        )
    if kind == "crowfoot_one":
        end_x = p_last[0] + px * half_width
        end_y = p_last[1] + py * half_width
        start_x = p_last[0] - px * half_width
        start_y = p_last[1] - py * half_width
        return (
            f'<line x1="{fmt(start_x)}" y1="{fmt(start_y)}" '
            f'x2="{fmt(end_x)}" y2="{fmt(end_y)}" '
            f'stroke="{color}" stroke-width="{fmt(stroke_w)}" stroke-linecap="round" />'
        )
    if kind == "crowfoot_one_or_many":
        # Combine a bar (one) with the crow's foot (many) — bar slightly inset.
        bar_offset = size * 0.7
        bar_left = (p_last[0] - ux * bar_offset + px * half_width,
                    p_last[1] - uy * bar_offset + py * half_width)
        bar_right = (p_last[0] - ux * bar_offset - px * half_width,
                     p_last[1] - uy * bar_offset - py * half_width)
        bar = (
            f'<line x1="{fmt(bar_left[0])}" y1="{fmt(bar_left[1])}" '
            f'x2="{fmt(bar_right[0])}" y2="{fmt(bar_right[1])}" '
            f'stroke="{color}" stroke-width="{fmt(stroke_w)}" stroke-linecap="round" />'
        )
        crow = _arrowhead(p_prev, p_last, "crowfoot_many", color, stroke_w)
        return bar + crow

    # Unknown arrowhead — render as filled triangle (closest to "arrow").
    pts = f"{fmt_xy(p_last)} {fmt_xy(left)} {fmt_xy(right)}"
    return f'<polygon points="{pts}" fill="{color}" stroke="{color}" />'


def _render_linear(el: LinearElement) -> str:
    pts = _absolute_points(el)
    if len(pts) < 2:
        return ""
    line = (
        f'<path d="{_polyline_path(pts)}" {_line_attrs(el)}{transform_attr(el)} />'
    )
    heads: list[str] = []
    if el.end_arrowhead:
        heads.append(_arrowhead(pts[-2], pts[-1], el.end_arrowhead,
                                el.stroke_color, el.stroke_width))
    if el.start_arrowhead:
        heads.append(_arrowhead(pts[1], pts[0], el.start_arrowhead,
                                el.stroke_color, el.stroke_width))
    if not heads:
        return line
    return f'<g{transform_attr(el)}><path d="{_polyline_path(pts)}" {_line_attrs(el)} />' + "".join(heads) + "</g>"


def render_arrow(el: ArrowElement) -> str:
    return _render_linear(el)


def render_line(el: LineElement) -> str:
    return _render_linear(el)

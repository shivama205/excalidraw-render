"""Text element renderer — multi-line, alignment, container-bound positioning."""

from __future__ import annotations

from excalidraw_render.element import TextElement
from excalidraw_render.renderers._util import (
    fmt,
    opacity_fraction,
    text_escape,
    transform_attr,
)

# Excalidraw font family integer → CSS font-family string.
# 1=Virgil (handwritten), 2=Helvetica, 3=Cascadia, 4=Lilita One, 5=Comic Sans, ...
# We map to widely-available web-safe fonts.
_FONT_FAMILY_MAP: dict[int, str] = {
    1: "Virgil, Segoe Print, Comic Sans MS, sans-serif",
    2: "Helvetica, Arial, sans-serif",
    3: "Cascadia, Cascadia Code, Menlo, Consolas, monospace",
    4: "Lilita One, Helvetica, sans-serif",
    5: "Comic Sans MS, Comic Sans, cursive",
}


def _font_family(family: int) -> str:
    return _FONT_FAMILY_MAP.get(family, _FONT_FAMILY_MAP[2])


def _text_anchor(align: str) -> str:
    return {"left": "start", "center": "middle", "right": "end"}.get(align, "start")


def render_text(el: TextElement) -> str:
    if not el.text:
        return ""
    lines = el.text.split("\n")
    line_h = el.font_size * el.line_height
    anchor = _text_anchor(el.text_align)
    # SVG text x-position depends on anchor.
    if anchor == "middle":
        x = el.x + el.width / 2
    elif anchor == "end":
        x = el.x + el.width
    else:
        x = el.x
    # Baseline of first line. Excalidraw measures text top-to-bottom.
    # Approximate: first line baseline = top + 0.85 * font_size + per vertical_align offset.
    n = len(lines)
    total_h = n * line_h
    if el.vertical_align == "middle":
        first_baseline = el.y + (el.height - total_h) / 2 + el.font_size * 0.85
    elif el.vertical_align == "bottom":
        first_baseline = el.y + el.height - total_h + el.font_size * 0.85
    else:
        first_baseline = el.y + el.font_size * 0.85

    opacity = opacity_fraction(el.opacity)
    family = _font_family(el.font_family)

    parts: list[str] = []
    for i, line in enumerate(lines):
        baseline = first_baseline + i * line_h
        parts.append(
            f'<text x="{fmt(x)}" y="{fmt(baseline)}" '
            f'font-family="{family}" font-size="{fmt(el.font_size)}" '
            f'fill="{el.stroke_color}" text-anchor="{anchor}" '
            f'opacity="{fmt(opacity, precision=3)}">'
            f'{text_escape(line)}</text>'
        )
    if not el.angle:
        return "\n".join(parts)
    return f"<g{transform_attr(el)}>" + "".join(parts) + "</g>"

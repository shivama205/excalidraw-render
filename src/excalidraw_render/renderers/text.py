"""Text element renderer — multi-line, alignment, container-bound positioning."""

from __future__ import annotations

import math

from excalidraw_render.element import ExcalidrawElementBase, TextElement
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

# Excalidraw's BOUND_TEXT_PADDING (constants.ts).
_BOUND_TEXT_PADDING = 5.0

# Container types whose bound text gets padding-aware layout. Text bound to
# arrows (labels) keeps its stored coordinates — Excalidraw keeps those synced
# to the midpoint on save.
_LAYOUT_CONTAINER_TYPES = frozenset({"rectangle", "ellipse", "diamond"})


def _font_family(family: int) -> str:
    return _FONT_FAMILY_MAP.get(family, _FONT_FAMILY_MAP[2])


def _text_anchor(align: str) -> str:
    return {"left": "start", "center": "middle", "right": "end"}.get(align, "start")


def _bound_text_box(el: TextElement, container: ExcalidrawElementBase) -> tuple[float, float]:
    """Top-left corner of the text box laid out inside its container.

    Port of Excalidraw's computeBoundTextPosition / getContainerCoords /
    getBoundTextMaxWidth (textElement.ts). For ellipse and diamond the text
    area is the largest inscribed rectangle, inset by BOUND_TEXT_PADDING.
    """
    pad = _BOUND_TEXT_PADDING
    off_x = pad
    off_y = pad
    max_w = container.width - 2 * pad
    max_h = container.height - 2 * pad
    if container.type == "ellipse":
        off_x += (container.width / 2) * (1 - math.sqrt(2) / 2)
        off_y += (container.height / 2) * (1 - math.sqrt(2) / 2)
        max_w = (container.width / 2) * math.sqrt(2) - 2 * pad
        max_h = (container.height / 2) * math.sqrt(2) - 2 * pad
    elif container.type == "diamond":
        off_x += container.width / 4
        off_y += container.height / 4
        max_w = container.width / 2 - 2 * pad
        max_h = container.height / 2 - 2 * pad

    cx = container.x + off_x
    cy = container.y + off_y

    if el.vertical_align == "middle":
        y = cy + (max_h - el.height) / 2
    elif el.vertical_align == "bottom":
        y = cy + (max_h - el.height)
    else:
        y = cy

    if el.text_align == "center":
        x = cx + (max_w - el.width) / 2
    elif el.text_align == "right":
        x = cx + (max_w - el.width)
    else:
        x = cx
    return x, y


def render_text(el: TextElement, container: ExcalidrawElementBase | None = None) -> str:
    if not el.text:
        return ""
    bound = container is not None and container.type in _LAYOUT_CONTAINER_TYPES

    lines = el.text.split("\n")
    line_h = el.font_size * el.line_height
    anchor = _text_anchor(el.text_align)

    if bound:
        assert container is not None
        box_x, box_y = _bound_text_box(el, container)
    else:
        box_x, box_y = el.x, el.y

    # SVG text x-position depends on anchor.
    if anchor == "middle":
        x = box_x + el.width / 2
    elif anchor == "end":
        x = box_x + el.width
    else:
        x = box_x

    # Baseline of first line. Excalidraw measures text top-to-bottom.
    # Approximate: first line baseline = top + 0.85 * font_size.
    # For bound text the box position already encodes vertical_align; for
    # free-standing text apply it within the element's own box.
    n = len(lines)
    total_h = n * line_h
    if bound:
        first_baseline = box_y + el.font_size * 0.85
    elif el.vertical_align == "middle":
        first_baseline = box_y + (el.height - total_h) / 2 + el.font_size * 0.85
    elif el.vertical_align == "bottom":
        first_baseline = box_y + el.height - total_h + el.font_size * 0.85
    else:
        first_baseline = box_y + el.font_size * 0.85

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

    # Bound text rotates with its container, around the container's center.
    if bound:
        assert container is not None
        if not container.angle:
            return "\n".join(parts)
        return f"<g{transform_attr(container)}>" + "".join(parts) + "</g>"
    if not el.angle:
        return "\n".join(parts)
    return f"<g{transform_attr(el)}>" + "".join(parts) + "</g>"

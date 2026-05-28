"""Frame element renderer — boundary box + optional label."""

from __future__ import annotations

from excalidraw_render.element import FrameElement
from excalidraw_render.renderers._util import (
    fmt,
    opacity_fraction,
    text_escape,
    transform_attr,
)


def render_frame(el: FrameElement) -> str:
    """Render frame as a labeled, dashed boundary rectangle.

    Frames in Excalidraw act as visual groupings. Their contents are still
    individual elements drawn separately; we just draw the frame outline + label.
    """
    box = (
        f'<rect x="{fmt(el.x)}" y="{fmt(el.y)}" '
        f'width="{fmt(el.width)}" height="{fmt(el.height)}" '
        f'rx="6" ry="6" fill="none" stroke="#bbbbbb" '
        f'stroke-width="1.5" stroke-dasharray="6 4" '
        f'opacity="{fmt(opacity_fraction(el.opacity), precision=3)}"'
        f'{transform_attr(el)} />'
    )
    if not el.name:
        return box
    label = (
        f'<text x="{fmt(el.x + 8)}" y="{fmt(el.y - 6)}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="13" '
        f'fill="#888888">{text_escape(el.name)}</text>'
    )
    return box + "\n" + label

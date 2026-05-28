"""Image element renderer — embeds raster data from the scene's `files` dict."""

from __future__ import annotations

from excalidraw_render.element import EmbeddedFile, ImageElement
from excalidraw_render.renderers._util import fmt, opacity_fraction, transform_attr


def render_image(el: ImageElement, files: dict[str, EmbeddedFile]) -> str:
    if not el.file_id or el.file_id not in files:
        # Render a placeholder rectangle so the layout doesn't collapse.
        return (
            f'<rect x="{fmt(el.x)}" y="{fmt(el.y)}" '
            f'width="{fmt(el.width)}" height="{fmt(el.height)}" '
            f'fill="#f4f4f4" stroke="#cccccc" stroke-dasharray="4,4" />'
        )
    file = files[el.file_id]
    if not file.data_url:
        return ""
    # Optional horizontal/vertical flip via scale.
    sx, sy = el.scale
    extra_transform = ""
    if sx < 0 or sy < 0:
        cx = el.x + el.width / 2
        cy = el.y + el.height / 2
        extra_transform = f' transform="translate({fmt(cx)},{fmt(cy)}) scale({fmt(sx)},{fmt(sy)}) translate({fmt(-cx)},{fmt(-cy)})"'
    return (
        f'<image x="{fmt(el.x)}" y="{fmt(el.y)}" '
        f'width="{fmt(el.width)}" height="{fmt(el.height)}" '
        f'href="{file.data_url}" preserveAspectRatio="none" '
        f'opacity="{fmt(opacity_fraction(el.opacity), precision=3)}"'
        f'{extra_transform}{transform_attr(el)} />'
    )

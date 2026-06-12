"""Pattern fill tests — hachure / cross-hatch / zigzag / dots / dashed."""

from __future__ import annotations

from typing import Any

import pytest

from excalidraw_render.element import parse_scene
from excalidraw_render.render import render_svg


def _rect(eid: str = "r1", **overrides: Any) -> dict[str, Any]:
    el: dict[str, Any] = {
        "id": eid,
        "type": "rectangle",
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 60,
        "backgroundColor": "#a5d8ff",
        "fillStyle": "hachure",
        "strokeWidth": 2,
    }
    el.update(overrides)
    return el


def _svg_for(*elements: dict[str, Any]) -> str:
    return render_svg(parse_scene({"elements": list(elements)}))


@pytest.mark.parametrize("style", ["hachure", "cross-hatch", "zigzag", "zigzag-line", "dots", "dashed"])
def test_pattern_styles_emit_def_and_reference(style: str) -> None:
    svg = _svg_for(_rect(fillStyle=style))
    pid = f"fill-{style}-a5d8ff-2"
    assert f'<pattern id="{pid}"' in svg
    assert f'fill="url(#{pid})"' in svg
    assert "<defs>" in svg


def test_solid_fill_has_no_defs() -> None:
    svg = _svg_for(_rect(fillStyle="solid"))
    assert "<defs>" not in svg
    assert 'fill="#a5d8ff"' in svg


def test_transparent_background_has_no_fill_or_defs() -> None:
    svg = _svg_for(_rect(backgroundColor="transparent"))
    assert "<defs>" not in svg
    assert 'fill="none"' in svg


def test_identical_fills_share_one_def() -> None:
    svg = _svg_for(_rect("r1"), _rect("r2", x=200))
    assert svg.count("<pattern ") == 1
    assert svg.count('fill="url(#fill-hachure-a5d8ff-2)"') == 2


def test_different_colors_get_separate_defs() -> None:
    svg = _svg_for(_rect("r1"), _rect("r2", x=200, backgroundColor="#ffc9c9"))
    assert svg.count("<pattern ") == 2
    assert 'fill="url(#fill-hachure-a5d8ff-2)"' in svg
    assert 'fill="url(#fill-hachure-ffc9c9-2)"' in svg


def test_stroke_width_scales_pattern_geometry() -> None:
    # roughjs defaults: gap = strokeWidth * 4, weight = strokeWidth / 2.
    svg = _svg_for(_rect(strokeWidth=4))
    assert 'fill="url(#fill-hachure-a5d8ff-4)"' in svg
    assert 'width="16" height="16"' in svg
    assert 'stroke-width="2"/>' in svg


def test_patterns_apply_to_ellipse_and_diamond() -> None:
    ellipse = _rect("e1", fillStyle="cross-hatch")
    ellipse["type"] = "ellipse"
    diamond = _rect("d1", x=200, fillStyle="dots")
    diamond["type"] = "diamond"
    svg = _svg_for(ellipse, diamond)
    assert 'fill="url(#fill-cross-hatch-a5d8ff-2)"' in svg
    assert 'fill="url(#fill-dots-a5d8ff-2)"' in svg


def test_pattern_fill_renders_to_png(tmp_path: Any) -> None:
    """cairosvg must actually rasterize <pattern> fills, not choke on them."""
    from excalidraw_render.render import render_png

    scene = parse_scene({"elements": [_rect()]})
    out = tmp_path / "hachure.png"
    render_png(scene, out, width=300)
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

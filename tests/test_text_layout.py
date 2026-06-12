"""Container-bound text layout tests.

Expected coordinates are hand-computed from Excalidraw's
computeBoundTextPosition / getContainerCoords / getBoundTextMaxWidth
(textElement.ts), with BOUND_TEXT_PADDING = 5.
"""

from __future__ import annotations

import math
from typing import Any

from excalidraw_render.element import parse_scene
from excalidraw_render.render import render_svg


def _container(ctype: str, **overrides: Any) -> dict[str, Any]:
    el: dict[str, Any] = {
        "id": "container-1",
        "type": ctype,
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 80,
        "boundElements": [{"type": "text", "id": "txt-1"}],
    }
    el.update(overrides)
    return el


def _bound_text(**overrides: Any) -> dict[str, Any]:
    el: dict[str, Any] = {
        "id": "txt-1",
        "type": "text",
        "x": 0,  # deliberately wrong — layout must come from the container
        "y": 0,
        "width": 60,
        "height": 25,
        "text": "Hi",
        "fontSize": 20,
        "fontFamily": 2,
        "textAlign": "center",
        "verticalAlign": "middle",
        "containerId": "container-1",
        "lineHeight": 1.25,
    }
    el.update(overrides)
    return el


def _svg_for(*elements: dict[str, Any]) -> str:
    return render_svg(parse_scene({"elements": list(elements)}))


def test_rectangle_left_top_uses_bound_text_padding() -> None:
    svg = _svg_for(
        _container("rectangle"),
        _bound_text(textAlign="left", verticalAlign="top"),
    )
    # box top-left = container + padding = (105, 105); baseline = 105 + 0.85*20.
    assert '<text x="105" y="122"' in svg


def test_rectangle_center_middle_centers_in_container() -> None:
    svg = _svg_for(_container("rectangle"), _bound_text())
    # anchor x = container center = 200; box_y = 105 + (70-25)/2 = 127.5.
    assert '<text x="200" y="144.5"' in svg
    assert 'text-anchor="middle"' in svg


def test_rectangle_right_bottom() -> None:
    svg = _svg_for(
        _container("rectangle"),
        _bound_text(textAlign="right", verticalAlign="bottom"),
    )
    # box_x = 105 + (190-60) = 235 → anchor x = 235 + 60 = 295.
    # box_y = 105 + (70-25) = 150 → baseline = 167.
    assert '<text x="295" y="167"' in svg


def test_ellipse_centered_text_lands_on_ellipse_center() -> None:
    svg = _svg_for(
        _container("ellipse", x=0, y=0, width=200, height=100),
        _bound_text(width=80),
    )
    # Inscribed-rect offsets cancel for centered text: anchor x = 100,
    # box_y = 37.5 → baseline = 54.5.
    assert '<text x="100" y="54.5"' in svg


def test_diamond_centered_text_lands_on_diamond_center() -> None:
    svg = _svg_for(
        _container("diamond", x=0, y=0, width=200, height=100),
        _bound_text(width=80),
    )
    # offsets (55, 30), max (90, 40): box = (60, 37.5) → anchor x = 100.
    assert '<text x="100" y="54.5"' in svg


def test_bound_text_rotates_with_container_around_container_center() -> None:
    svg = _svg_for(
        _container("rectangle", angle=math.pi / 2),
        _bound_text(),
    )
    # 90° around the container center (200, 140) — not the text's own center.
    assert 'transform="rotate(90 200 140)"' in svg


def test_text_bound_to_arrow_keeps_stored_coordinates() -> None:
    arrow = {
        "id": "container-1",
        "type": "arrow",
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 0,
        "points": [[0, 0], [200, 0]],
        "boundElements": [{"type": "text", "id": "txt-1"}],
    }
    svg = _svg_for(arrow, _bound_text(x=70, y=10, textAlign="left", verticalAlign="top"))
    # Arrow labels keep their saved position: baseline = 10 + 17 = 27.
    assert '<text x="70" y="27"' in svg


def test_missing_container_falls_back_to_own_coordinates() -> None:
    svg = _svg_for(_bound_text(x=30, y=40, textAlign="left", verticalAlign="top"))
    assert '<text x="30" y="57"' in svg

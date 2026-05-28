"""Parser tests — exercise each element type and key common fields."""

from __future__ import annotations

from excalidraw_render.element import (
    ArrowElement,
    DiamondElement,
    EllipseElement,
    FrameElement,
    FreeDrawElement,
    ImageElement,
    LineElement,
    RectangleElement,
    TextElement,
    UnknownElement,
    parse_element,
    parse_scene,
)


def _common(et: str, extra: dict | None = None) -> dict:
    base = {
        "id": "el1",
        "type": et,
        "x": 10,
        "y": 20,
        "width": 100,
        "height": 50,
        "strokeColor": "#222",
        "backgroundColor": "#a5d8ff",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": ["g1"],
        "isDeleted": False,
    }
    if extra:
        base.update(extra)
    return base


def test_parse_rectangle_with_roundness() -> None:
    el = parse_element(_common("rectangle", {"roundness": {"type": 3, "value": 25}}))
    assert isinstance(el, RectangleElement)
    assert el.x == 10
    assert el.background_color == "#a5d8ff"
    assert el.group_ids == ("g1",)
    assert el.roundness is not None
    assert el.roundness.type == 3
    assert el.roundness.value == 25


def test_parse_ellipse_defaults() -> None:
    el = parse_element({"id": "e", "type": "ellipse", "x": 0, "y": 0, "width": 50, "height": 50})
    assert isinstance(el, EllipseElement)
    assert el.stroke_color == "#1e1e1e"
    assert el.opacity == 100


def test_parse_diamond() -> None:
    el = parse_element(_common("diamond"))
    assert isinstance(el, DiamondElement)


def test_parse_arrow_with_points_and_arrowheads() -> None:
    raw = _common("arrow", {
        "points": [[0, 0], [50, 0], [50, 50]],
        "endArrowhead": "triangle",
        "startBinding": {"elementId": "shape1", "focus": 0.0, "gap": 4},
    })
    el = parse_element(raw)
    assert isinstance(el, ArrowElement)
    assert el.points == ((0.0, 0.0), (50.0, 0.0), (50.0, 50.0))
    assert el.end_arrowhead == "triangle"
    assert el.start_binding is not None
    assert el.start_binding.element_id == "shape1"


def test_parse_line() -> None:
    el = parse_element(_common("line", {"points": [[0, 0], [100, 0]]}))
    assert isinstance(el, LineElement)
    assert len(el.points) == 2


def test_parse_text_with_container_binding() -> None:
    raw = _common("text", {
        "text": "Hello\nworld",
        "fontSize": 20,
        "fontFamily": 1,
        "textAlign": "center",
        "verticalAlign": "middle",
        "containerId": "rect1",
        "lineHeight": 1.25,
    })
    el = parse_element(raw)
    assert isinstance(el, TextElement)
    assert el.text == "Hello\nworld"
    assert el.text_align == "center"
    assert el.container_id == "rect1"


def test_parse_freedraw() -> None:
    raw = _common("freedraw", {
        "points": [[0, 0], [10, 5], [20, 12]],
        "pressures": [0.5, 0.6, 0.55],
        "simulatePressure": True,
    })
    el = parse_element(raw)
    assert isinstance(el, FreeDrawElement)
    assert len(el.points) == 3
    assert el.pressures == (0.5, 0.6, 0.55)


def test_parse_image() -> None:
    raw = _common("image", {"fileId": "f1", "status": "saved", "scale": [1.0, 1.0]})
    el = parse_element(raw)
    assert isinstance(el, ImageElement)
    assert el.file_id == "f1"
    assert el.scale == (1.0, 1.0)


def test_parse_frame() -> None:
    raw = _common("frame", {"name": "Section A"})
    el = parse_element(raw)
    assert isinstance(el, FrameElement)
    assert el.name == "Section A"


def test_parse_unknown_element_preserves_raw() -> None:
    raw = _common("magicframe", {"name": "AI-suggested"})
    el = parse_element(raw)
    assert isinstance(el, UnknownElement)
    assert el.raw["name"] == "AI-suggested"


def test_parse_scene_drops_deleted_elements() -> None:
    scene = parse_scene({
        "elements": [
            _common("rectangle"),
            _common("ellipse", {"isDeleted": True}),
        ],
    })
    assert len(scene.elements) == 1
    assert scene.elements[0].type == "rectangle"


def test_parse_scene_loads_files() -> None:
    scene = parse_scene({
        "elements": [],
        "files": {
            "f1": {
                "mimeType": "image/png",
                "dataURL": "data:image/png;base64,iVBOR",
                "created": 1716000000,
            },
        },
    })
    assert "f1" in scene.files
    assert scene.files["f1"].mime_type == "image/png"

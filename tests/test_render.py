"""Renderer integration tests using small fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from excalidraw_render.render import load_scene, render_jpg, render_pdf, render_png, render_svg

FIXTURES = Path(__file__).parent / "fixtures"


def _fx(name: str) -> Path:
    return FIXTURES / name


def test_rectangle_basic_renders_a_rect() -> None:
    scene = load_scene(_fx("rectangle_basic.excalidraw"))
    svg = render_svg(scene)
    assert "<rect" in svg
    assert 'rx="' in svg  # rounded
    assert "#a5d8ff" in svg  # background color
    assert "viewBox=" in svg


def test_text_in_rectangle_renders_centered_text() -> None:
    scene = load_scene(_fx("text_in_rectangle.excalidraw"))
    svg = render_svg(scene)
    assert "<rect" in svg
    assert "<text" in svg
    assert ">Hello<" in svg
    assert 'text-anchor="middle"' in svg


def test_arrow_with_head_renders_polygon_arrowhead() -> None:
    scene = load_scene(_fx("arrow_with_head.excalidraw"))
    svg = render_svg(scene)
    assert "<path" in svg
    # The arrowhead is rendered as a polygon (triangle).
    assert "<polygon" in svg


def test_freedraw_renders_cubic_path() -> None:
    scene = load_scene(_fx("freedraw_simple.excalidraw"))
    svg = render_svg(scene)
    assert "<path" in svg
    assert "C " in svg  # Catmull-Rom expands to cubic Bezier (C ...)


def test_mixed_scene_renders_all_element_types() -> None:
    scene = load_scene(_fx("mixed_scene.excalidraw"))
    svg = render_svg(scene)
    assert "<rect" in svg
    assert "<ellipse" in svg
    assert "<polygon" in svg  # diamond + arrowhead
    assert "<path" in svg  # arrows are paths
    assert "<text" in svg
    assert "Flow Diagram" in svg
    # Dashed arrow should add a dasharray.
    assert "stroke-dasharray" in svg


def test_render_png_writes_a_real_png(tmp_path: Path) -> None:
    scene = load_scene(_fx("mixed_scene.excalidraw"))
    out = tmp_path / "out.png"
    render_png(scene, out, width=600)
    assert out.exists()
    # PNG signature.
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    # Has at least some content.
    assert out.stat().st_size > 200


def test_render_pdf_writes_a_real_pdf(tmp_path: Path) -> None:
    scene = load_scene(_fx("mixed_scene.excalidraw"))
    out = tmp_path / "out.pdf"
    render_pdf(scene, out)
    assert out.read_bytes()[:5] == b"%PDF-"
    assert out.stat().st_size > 200


def test_render_pdf_to_stream() -> None:
    from io import BytesIO

    scene = load_scene(_fx("rectangle_basic.excalidraw"))
    buf = BytesIO()
    render_pdf(scene, buf)
    assert buf.getvalue()[:5] == b"%PDF-"


def test_render_jpg_writes_a_real_jpeg(tmp_path: Path) -> None:
    scene = load_scene(_fx("mixed_scene.excalidraw"))
    out = tmp_path / "out.jpg"
    render_jpg(scene, out, width=600)
    # JPEG SOI marker.
    assert out.read_bytes()[:3] == b"\xff\xd8\xff"
    assert out.stat().st_size > 200


def test_render_jpg_flattens_transparent_background(tmp_path: Path) -> None:
    """JPEG has no alpha — background=None must flatten onto white, not crash."""
    from PIL import Image

    scene = load_scene(_fx("rectangle_basic.excalidraw"))
    out = tmp_path / "out.jpg"
    render_jpg(scene, out, background=None)
    img = Image.open(out)
    assert img.mode == "RGB"
    # A corner pixel (outside the rect, in the padding) should be white.
    assert img.getpixel((1, 1)) == (255, 255, 255)


def test_render_jpg_quality_changes_file_size(tmp_path: Path) -> None:
    scene = load_scene(_fx("mixed_scene.excalidraw"))
    hi = tmp_path / "hi.jpg"
    lo = tmp_path / "lo.jpg"
    render_jpg(scene, hi, quality=95)
    render_jpg(scene, lo, quality=20)
    assert lo.stat().st_size < hi.stat().st_size


def test_empty_scene_does_not_crash() -> None:
    scene = load_scene(_fx("rectangle_basic.excalidraw"))
    # Strip elements to simulate an empty scene.
    from excalidraw_render.element import Scene
    empty = Scene(elements=(), files=scene.files, app_state=scene.app_state)
    svg = render_svg(empty)
    assert "<svg" in svg
    assert "</svg>" in svg


@pytest.mark.parametrize("fixture", [
    "rectangle_basic.excalidraw",
    "text_in_rectangle.excalidraw",
    "arrow_with_head.excalidraw",
    "freedraw_simple.excalidraw",
    "mixed_scene.excalidraw",
])
def test_every_fixture_renders_to_valid_svg(fixture: str) -> None:
    """Smoke check: each fixture parses + renders without throwing."""
    scene = load_scene(_fx(fixture))
    svg = render_svg(scene)
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")

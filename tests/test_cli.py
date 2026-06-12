"""CLI smoke tests."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from excalidraw_render.cli import _parse_args, _poll_and_render, main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_single_file_to_default_png(tmp_path: Path) -> None:
    src = tmp_path / "rect.excalidraw"
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", src)
    rc = main([str(src)])
    assert rc == 0
    assert (tmp_path / "rect.png").exists()


def test_cli_single_file_explicit_output_and_format(tmp_path: Path) -> None:
    src = tmp_path / "rect.excalidraw"
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", src)
    out = tmp_path / "subdir" / "result.svg"
    rc = main([str(src), "-o", str(out), "-f", "svg"])
    assert rc == 0
    assert out.exists()
    assert "<svg" in out.read_text()


def test_cli_directory_batch_mode(tmp_path: Path) -> None:
    # Copy two fixtures into a temp dir.
    for name in ("rectangle_basic.excalidraw", "mixed_scene.excalidraw"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    out_dir = tmp_path / "out"
    rc = main([str(tmp_path), "-o", str(out_dir)])
    assert rc == 0
    assert (out_dir / "rectangle_basic.png").exists()
    assert (out_dir / "mixed_scene.png").exists()


def test_cli_pdf_format(tmp_path: Path) -> None:
    src = tmp_path / "rect.excalidraw"
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", src)
    rc = main([str(src), "-f", "pdf"])
    assert rc == 0
    assert (tmp_path / "rect.pdf").read_bytes()[:5] == b"%PDF-"


def test_cli_jpg_format_with_quality(tmp_path: Path) -> None:
    src = tmp_path / "rect.excalidraw"
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", src)
    rc = main([str(src), "-f", "jpg", "--quality", "60"])
    assert rc == 0
    assert (tmp_path / "rect.jpg").read_bytes()[:3] == b"\xff\xd8\xff"


def test_watch_poll_renders_new_and_changed_only(tmp_path: Path) -> None:
    src = tmp_path / "rect.excalidraw"
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", src)
    args = _parse_args([str(tmp_path), "-f", "svg", "--watch"])
    mtimes: dict[Path, float] = {}

    # First poll renders everything.
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)
    out = tmp_path / "rect.svg"
    assert out.exists()

    # Unchanged source → no re-render.
    out.unlink()
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)
    assert not out.exists()

    # Bumped mtime → re-render.
    stat = src.stat()
    os.utime(src, (stat.st_atime, stat.st_mtime + 10))
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)
    assert out.exists()

    # A new file appearing mid-watch gets picked up.
    src2 = tmp_path / "second.excalidraw"
    shutil.copy(FIXTURES / "mixed_scene.excalidraw", src2)
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)
    assert (tmp_path / "second.svg").exists()


def test_watch_poll_survives_render_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.excalidraw"
    bad.write_text("{ not json")
    args = _parse_args([str(tmp_path), "-f", "svg", "--watch"])
    mtimes: dict[Path, float] = {}
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)  # must not raise
    assert "error rendering" in capsys.readouterr().err

    # Once fixed, the changed mtime triggers a successful render.
    stat = bad.stat()
    shutil.copy(FIXTURES / "rectangle_basic.excalidraw", bad)
    os.utime(bad, (stat.st_atime, stat.st_mtime + 10))
    _poll_and_render(mtimes, tmp_path, args, batch_dir=tmp_path)
    assert (tmp_path / "bad.svg").exists()


def test_cli_missing_input_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main([str(tmp_path / "nope.excalidraw")])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_cli_wrong_extension_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "wrong.txt"
    bad.write_text("nope")
    rc = main([str(bad)])
    assert rc == 1
    assert "expected .excalidraw" in capsys.readouterr().err

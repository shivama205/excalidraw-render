"""CLI smoke tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from excalidraw_render.cli import main

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

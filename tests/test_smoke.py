"""Smoke test — package imports cleanly."""

from __future__ import annotations


def test_version_is_a_string() -> None:
    from excalidraw_render import __version__

    assert isinstance(__version__, str)
    assert __version__

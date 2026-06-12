"""Command-line entry point for excalidraw-render.

Usage:
    excalidraw-render FILE.excalidraw
        → renders to FILE.png next to the source

    excalidraw-render FILE.excalidraw -o out.svg --format svg
        → renders to out.svg

    excalidraw-render FILE.excalidraw --width 1200
        → PNG at 1200px wide (height auto, aspect preserved)

    excalidraw-render DIR/
        → batch mode: every .excalidraw file in DIR rendered to <name>.png next to source
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from excalidraw_render._version import __version__
from excalidraw_render.render import load_scene, render_jpg, render_pdf, render_png, render_svg


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="excalidraw-render",
        description="Clean, browser-free renderer for .excalidraw files.",
    )
    parser.add_argument("input", help="path to a .excalidraw file or directory")
    parser.add_argument(
        "-o", "--output",
        help="output file path (single-file mode) or output directory (batch mode). "
             "default: same path as input with the format's extension",
    )
    parser.add_argument(
        "-f", "--format",
        choices=("png", "svg", "pdf", "jpg", "jpeg"),
        default="png",
        help="output format. default: png",
    )
    parser.add_argument(
        "--width",
        type=int,
        help="output width in pixels (PNG only; height computed from aspect ratio)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="scale factor for PNG output when --width is not set. default: 1.0",
    )
    parser.add_argument(
        "--no-background",
        action="store_true",
        help="render with a transparent background instead of white",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=20.0,
        help="padding around the scene's bounding box in SVG units. default: 20",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=90,
        help="JPEG quality, 1-100 (jpg/jpeg format only). default: 90",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"excalidraw-render {__version__}",
    )
    return parser.parse_args(argv)


def _output_path_for(source: Path, requested: str | None, fmt: str, *, batch_dir: Path | None) -> Path:
    """Resolve the output path for a single source file."""
    suffix = f".{fmt}"
    if batch_dir is not None:
        return batch_dir / (source.stem + suffix)
    if requested:
        out = Path(requested)
        # If the requested path has no extension, append the format's extension.
        if out.suffix == "":
            out = out.with_suffix(suffix)
        return out
    return source.with_suffix(suffix)


def _render_one(source: Path, output: Path, args: argparse.Namespace) -> None:
    scene = load_scene(source)
    background = None if args.no_background else "#ffffff"
    raster_kwargs = {
        "width": args.width,
        "scale": args.scale,
        "padding": args.padding,
        "background": background,
    }
    if args.format == "svg":
        svg = render_svg(scene, padding=args.padding, background=background)
        output.write_text(svg)
    elif args.format == "pdf":
        render_pdf(scene, output, **raster_kwargs)
    elif args.format in ("jpg", "jpeg"):
        render_jpg(scene, output, quality=args.quality, **raster_kwargs)
    else:
        render_png(scene, output, **raster_kwargs)
    print(f"{source} -> {output}", file=sys.stderr)


def _iter_excalidraw_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix == ".excalidraw")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"excalidraw-render: not found: {input_path}", file=sys.stderr)
        return 1

    if input_path.is_dir():
        sources = _iter_excalidraw_files(input_path)
        if not sources:
            print(f"excalidraw-render: no .excalidraw files in {input_path}", file=sys.stderr)
            return 1
        batch_dir = Path(args.output) if args.output else input_path
        batch_dir.mkdir(parents=True, exist_ok=True)
        for src in sources:
            _render_one(src, _output_path_for(src, None, args.format, batch_dir=batch_dir), args)
        return 0

    if input_path.suffix != ".excalidraw":
        print(
            f"excalidraw-render: expected .excalidraw file, got {input_path.suffix or '(no extension)'}",
            file=sys.stderr,
        )
        return 1

    output = _output_path_for(input_path, args.output, args.format, batch_dir=None)
    output.parent.mkdir(parents=True, exist_ok=True)
    _render_one(input_path, output, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

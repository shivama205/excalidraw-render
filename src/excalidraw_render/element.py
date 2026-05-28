"""Typed dataclasses for Excalidraw elements + JSON loader.

Schema reference:
https://github.com/excalidraw/excalidraw/blob/master/packages/excalidraw/element/types.ts

We model only what the renderer needs. Fields we ignore (e.g., `versionNonce`,
`seed`, `updated`, `frameId`, `boundElements` reverse-references handled at
layout time) are dropped during parsing.

Forward-compat: unknown fields are tolerated. Unknown element types are surfaced
through `parse_scene()` so callers can decide whether to skip, warn, or fail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# ----------------------------------------------------------------------- enums

StrokeStyle = Literal["solid", "dashed", "dotted"]
FillStyle = Literal["solid", "hachure", "cross-hatch", "zigzag", "zigzag-line", "dots", "dashed"]
TextAlign = Literal["left", "center", "right"]
VerticalAlign = Literal["top", "middle", "bottom"]
FontFamily = Literal[1, 2, 3, 4, 5, 6, 7, 8]  # Excalidraw uses ints for font families
Arrowhead = Literal[
    "arrow", "bar", "dot", "triangle", "triangle_outline",
    "diamond", "diamond_outline",
    "crowfoot_one", "crowfoot_many", "crowfoot_one_or_many",
]
LinearElementType = Literal["arrow", "line"]


# --------------------------------------------------------------- common bases

@dataclass(frozen=True, kw_only=True)
class ExcalidrawElementBase:
    """Fields shared by every Excalidraw element."""

    id: str
    type: str
    x: float
    y: float
    width: float
    height: float
    angle: float = 0.0
    stroke_color: str = "#1e1e1e"
    background_color: str = "transparent"
    fill_style: FillStyle = "solid"
    stroke_width: float = 2.0
    stroke_style: StrokeStyle = "solid"
    roughness: int = 1
    opacity: float = 100.0
    group_ids: tuple[str, ...] = ()
    frame_id: str | None = None
    is_deleted: bool = False
    link: str | None = None
    locked: bool = False
    # Per-element type-specific data goes in subclasses.


# ----------------------------------------------------------- shape elements

@dataclass(frozen=True, kw_only=True)
class RectangleElement(ExcalidrawElementBase):
    type: Literal["rectangle"] = "rectangle"
    roundness: Roundness | None = None


@dataclass(frozen=True, kw_only=True)
class EllipseElement(ExcalidrawElementBase):
    type: Literal["ellipse"] = "ellipse"


@dataclass(frozen=True, kw_only=True)
class DiamondElement(ExcalidrawElementBase):
    type: Literal["diamond"] = "diamond"
    roundness: Roundness | None = None


@dataclass(frozen=True)
class Roundness:
    """Excalidraw stores roundness as { type: int, value?: float }."""

    type: int
    value: float | None = None


# ---------------------------------------------------- linear elements (arrow/line)

@dataclass(frozen=True, kw_only=True)
class LinearElement(ExcalidrawElementBase):
    """Common base for arrow and line. Points are deltas from (x, y)."""

    points: tuple[tuple[float, float], ...] = ()
    start_arrowhead: Arrowhead | None = None
    end_arrowhead: Arrowhead | None = None
    start_binding: Binding | None = None
    end_binding: Binding | None = None


@dataclass(frozen=True, kw_only=True)
class ArrowElement(LinearElement):
    type: Literal["arrow"] = "arrow"


@dataclass(frozen=True, kw_only=True)
class LineElement(LinearElement):
    type: Literal["line"] = "line"


@dataclass(frozen=True)
class Binding:
    """Linear element bound to a shape (start/end). element_id is the target shape."""

    element_id: str
    focus: float = 0.0
    gap: float = 0.0


# ----------------------------------------------------------------- text

@dataclass(frozen=True, kw_only=True)
class TextElement(ExcalidrawElementBase):
    type: Literal["text"] = "text"
    text: str = ""
    font_size: float = 20.0
    font_family: FontFamily = 1
    text_align: TextAlign = "left"
    vertical_align: VerticalAlign = "top"
    container_id: str | None = None
    original_text: str | None = None
    line_height: float = 1.25


# ---------------------------------------------------------------- freedraw

@dataclass(frozen=True, kw_only=True)
class FreeDrawElement(ExcalidrawElementBase):
    type: Literal["freedraw"] = "freedraw"
    points: tuple[tuple[float, float], ...] = ()
    pressures: tuple[float, ...] = ()
    simulate_pressure: bool = True
    last_committed_point: tuple[float, float] | None = None


# ----------------------------------------------------------------- image

@dataclass(frozen=True, kw_only=True)
class ImageElement(ExcalidrawElementBase):
    type: Literal["image"] = "image"
    file_id: str | None = None
    status: Literal["pending", "saved", "error"] = "saved"
    scale: tuple[float, float] = (1.0, 1.0)


# ----------------------------------------------------------------- frame

@dataclass(frozen=True, kw_only=True)
class FrameElement(ExcalidrawElementBase):
    type: Literal["frame"] = "frame"
    name: str | None = None


# ---------------------------------------------------------- unknown element

@dataclass(frozen=True, kw_only=True)
class UnknownElement(ExcalidrawElementBase):
    """Element with a type we don't recognize. Preserved so callers can decide."""

    raw: dict[str, Any] = field(default_factory=dict)


ExcalidrawElement = (
    RectangleElement
    | EllipseElement
    | DiamondElement
    | ArrowElement
    | LineElement
    | TextElement
    | FreeDrawElement
    | ImageElement
    | FrameElement
    | UnknownElement
)


# ----------------------------------------------------------------- files

@dataclass(frozen=True)
class EmbeddedFile:
    """Image data referenced from ImageElement.file_id."""

    id: str
    mime_type: str
    data_url: str  # e.g. "data:image/png;base64,..."
    created: int = 0


# ----------------------------------------------------------------- scene

@dataclass(frozen=True)
class Scene:
    """A parsed .excalidraw document — elements + embedded files."""

    elements: tuple[ExcalidrawElement, ...]
    files: dict[str, EmbeddedFile] = field(default_factory=dict)
    app_state: dict[str, Any] = field(default_factory=dict)
    source: str = ""


# ---------------------------------------------------------------- parsing

def _common_fields(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract fields present on every element."""
    return {
        "id": raw["id"],
        "type": raw["type"],
        "x": float(raw.get("x", 0)),
        "y": float(raw.get("y", 0)),
        "width": float(raw.get("width", 0)),
        "height": float(raw.get("height", 0)),
        "angle": float(raw.get("angle", 0)),
        "stroke_color": raw.get("strokeColor", "#1e1e1e"),
        "background_color": raw.get("backgroundColor", "transparent"),
        "fill_style": raw.get("fillStyle", "solid"),
        "stroke_width": float(raw.get("strokeWidth", 2)),
        "stroke_style": raw.get("strokeStyle", "solid"),
        "roughness": int(raw.get("roughness", 1)),
        "opacity": float(raw.get("opacity", 100)),
        "group_ids": tuple(raw.get("groupIds", []) or []),
        "frame_id": raw.get("frameId"),
        "is_deleted": bool(raw.get("isDeleted", False)),
        "link": raw.get("link"),
        "locked": bool(raw.get("locked", False)),
    }


def _parse_roundness(raw: Any) -> Roundness | None:
    if not isinstance(raw, dict):
        return None
    return Roundness(type=int(raw.get("type", 0)), value=raw.get("value"))


def _parse_binding(raw: Any) -> Binding | None:
    if not isinstance(raw, dict):
        return None
    return Binding(
        element_id=raw.get("elementId", ""),
        focus=float(raw.get("focus", 0)),
        gap=float(raw.get("gap", 0)),
    )


def _parse_points(raw: Any) -> tuple[tuple[float, float], ...]:
    if not raw:
        return ()
    return tuple((float(p[0]), float(p[1])) for p in raw if len(p) >= 2)


def parse_element(raw: dict[str, Any]) -> ExcalidrawElement:
    """Parse a single element dict into the matching typed dataclass."""
    base = _common_fields(raw)
    etype = raw.get("type")

    if etype == "rectangle":
        return RectangleElement(**base, roundness=_parse_roundness(raw.get("roundness")))
    if etype == "ellipse":
        return EllipseElement(**base)
    if etype == "diamond":
        return DiamondElement(**base, roundness=_parse_roundness(raw.get("roundness")))
    if etype in ("arrow", "line"):
        cls = ArrowElement if etype == "arrow" else LineElement
        return cls(
            **base,
            points=_parse_points(raw.get("points")),
            start_arrowhead=raw.get("startArrowhead"),
            end_arrowhead=raw.get("endArrowhead"),
            start_binding=_parse_binding(raw.get("startBinding")),
            end_binding=_parse_binding(raw.get("endBinding")),
        )
    if etype == "text":
        return TextElement(
            **base,
            text=raw.get("text", ""),
            font_size=float(raw.get("fontSize", 20)),
            font_family=raw.get("fontFamily", 1),
            text_align=raw.get("textAlign", "left"),
            vertical_align=raw.get("verticalAlign", "top"),
            container_id=raw.get("containerId"),
            original_text=raw.get("originalText"),
            line_height=float(raw.get("lineHeight", 1.25)),
        )
    if etype == "freedraw":
        lcp_raw = raw.get("lastCommittedPoint")
        last_committed: tuple[float, float] | None = (
            (float(lcp_raw[0]), float(lcp_raw[1]))
            if lcp_raw is not None and len(lcp_raw) >= 2
            else None
        )
        return FreeDrawElement(
            **base,
            points=_parse_points(raw.get("points")),
            pressures=tuple(float(p) for p in raw.get("pressures", []) or []),
            simulate_pressure=bool(raw.get("simulatePressure", True)),
            last_committed_point=last_committed,
        )
    if etype == "image":
        scale_raw = raw.get("scale", [1, 1])
        scale: tuple[float, float] = (float(scale_raw[0]), float(scale_raw[1]))
        return ImageElement(
            **base,
            file_id=raw.get("fileId"),
            status=raw.get("status", "saved"),
            scale=scale,
        )
    if etype == "frame":
        return FrameElement(**base, name=raw.get("name"))

    return UnknownElement(**base, raw=raw)


def parse_files(raw: Any) -> dict[str, EmbeddedFile]:
    if not isinstance(raw, dict):
        return {}
    return {
        fid: EmbeddedFile(
            id=fid,
            mime_type=meta.get("mimeType", "application/octet-stream"),
            data_url=meta.get("dataURL", ""),
            created=int(meta.get("created", 0)),
        )
        for fid, meta in raw.items()
        if isinstance(meta, dict)
    }


def parse_scene(data: dict[str, Any], *, source: str = "") -> Scene:
    """Parse a top-level .excalidraw JSON dict into a Scene."""
    elements = tuple(
        parse_element(el)
        for el in data.get("elements", [])
        if isinstance(el, dict) and not el.get("isDeleted", False)
    )
    files = parse_files(data.get("files"))
    app_state = data.get("appState", {}) if isinstance(data.get("appState"), dict) else {}
    return Scene(elements=elements, files=files, app_state=app_state, source=source)

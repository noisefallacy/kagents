"""Guarded chart artifact generation tools."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from kagents.config import PROJECT_ROOT, settings


ALLOWED_CHART_TYPES = {"line", "bar", "scatter"}
MAX_POINTS = 5000
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
DEFAULT_STYLE = {
    "figure_size": [8, 4.5],
    "dpi": 150,
    "line_color": "#1f77b4",
    "bar_color": "#1f77b4",
    "scatter_color": "#1f77b4",
    "marker": "o",
    "line_width": 2.0,
    "grid": True,
    "grid_axis": "y",
    "grid_alpha": 0.25,
    "background_color": "#ffffff",
    "axes_facecolor": "#ffffff",
    "title_color": "#111827",
    "label_color": "#374151",
    "tick_color": "#4b5563",
}
STYLE_KEYS = set(DEFAULT_STYLE)
COLOR_KEYS = {
    "line_color",
    "bar_color",
    "scatter_color",
    "background_color",
    "axes_facecolor",
    "title_color",
    "label_color",
    "tick_color",
}
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def _safe_output_path(output_path: str | None, title: str, chart_type: str) -> Path:
    if output_path:
        candidate = Path(output_path)
    else:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", title.strip().lower()).strip("_")
        candidate = Path("outputs") / f"{slug or chart_type}_chart.png"

    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (PROJECT_ROOT / candidate).resolve()

    output_root = OUTPUT_ROOT.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(f"Chart output must be under {output_root}") from exc

    if resolved.suffix.lower() != ".png":
        raise ValueError("Chart output must use a .png extension")

    return resolved


def _coerce_y_values(y_values: list[Any]) -> list[float]:
    values: list[float] = []
    for value in y_values:
        try:
            values.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Y values must be numeric. Invalid value: {value!r}") from exc
    return values


def _coerce_x_values(x_values: list[Any], chart_type: str) -> list[Any]:
    if chart_type != "scatter":
        return [str(value) for value in x_values]

    values: list[float] = []
    for value in x_values:
        try:
            values.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Scatter chart X values must be numeric. Invalid value: {value!r}") from exc
    return values


def _load_chart_styles(styles_path: str | None = None) -> dict[str, Any]:
    path = Path(styles_path or settings.chart_styles_path)
    if not path.exists():
        return {"default_style": "default", "styles": {"default": DEFAULT_STYLE}}

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or not isinstance(data.get("styles"), dict):
        raise ValueError("Chart styles file must contain a styles object.")

    return data


def _validated_style(style: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(style, dict):
        raise ValueError("Chart style must be an object.")

    unexpected = sorted(set(style) - STYLE_KEYS)
    if unexpected:
        raise ValueError(f"Unsupported chart style keys: {unexpected}")

    merged = {**DEFAULT_STYLE, **style}
    figure_size = merged["figure_size"]
    if (
        not isinstance(figure_size, list)
        or len(figure_size) != 2
        or not all(isinstance(value, (int, float)) and value > 0 for value in figure_size)
    ):
        raise ValueError("Chart style figure_size must be two positive numbers.")

    if not isinstance(merged["dpi"], int) or merged["dpi"] < 72 or merged["dpi"] > 400:
        raise ValueError("Chart style dpi must be an integer between 72 and 400.")

    if not isinstance(merged["line_width"], (int, float)) or merged["line_width"] <= 0:
        raise ValueError("Chart style line_width must be positive.")

    if not isinstance(merged["grid"], bool):
        raise ValueError("Chart style grid must be true or false.")

    if merged["grid_axis"] not in {"x", "y", "both"}:
        raise ValueError("Chart style grid_axis must be x, y, or both.")

    if not isinstance(merged["grid_alpha"], (int, float)) or not 0 <= merged["grid_alpha"] <= 1:
        raise ValueError("Chart style grid_alpha must be between 0 and 1.")

    if not isinstance(merged["marker"], str):
        raise ValueError("Chart style marker must be a string.")

    for key in COLOR_KEYS:
        if not isinstance(merged[key], str) or not HEX_COLOR_PATTERN.match(merged[key]):
            raise ValueError(f"Chart style {key} must be a #RRGGBB color.")

    return merged


def _get_chart_style(
    style_name: str | None = None,
    styles_path: str | None = None,
) -> tuple[str, dict[str, Any]]:
    styles_data = _load_chart_styles(styles_path)
    styles = styles_data["styles"]
    resolved_style_name = (style_name or styles_data.get("default_style") or "default").strip()

    if resolved_style_name not in styles:
        raise ValueError(
            f"Unknown chart style: {resolved_style_name}. Available styles: {sorted(styles)}"
        )

    return resolved_style_name, _validated_style(styles[resolved_style_name])


def create_chart_png(
    chart_type: str,
    x_values: list[Any],
    y_values: list[Any],
    title: str = "Chart",
    output_path: str | None = None,
    x_label: str = "",
    y_label: str = "",
    style_name: str | None = None,
    styles_path: str | None = None,
) -> dict[str, Any]:
    """
    Create a guarded PNG chart artifact under the project outputs directory.

    Args:
        chart_type: One of line, bar, or scatter.
        x_values: X-axis values. Scatter charts require numeric X values.
        y_values: Numeric Y-axis values.
        title: Chart title.
        output_path: Optional output path. Must resolve under outputs/ and end in .png.
        x_label: Optional X-axis label.
        y_label: Optional Y-axis label.
        style_name: Optional named style from the configured chart styles file.
        styles_path: Optional chart styles JSON path, mainly for tests.
    """

    normalized_type = chart_type.strip().lower()
    if normalized_type not in ALLOWED_CHART_TYPES:
        return {
            "status": "error",
            "message": f"Unsupported chart type: {chart_type}. Allowed: {sorted(ALLOWED_CHART_TYPES)}",
            "path": None,
        }

    if not x_values or not y_values:
        return {
            "status": "error",
            "message": "x_values and y_values must both be non-empty.",
            "path": None,
        }

    if len(x_values) != len(y_values):
        return {
            "status": "error",
            "message": "x_values and y_values must have the same length.",
            "path": None,
        }

    if len(x_values) > MAX_POINTS:
        return {
            "status": "error",
            "message": f"Too many chart points: {len(x_values)}. Maximum is {MAX_POINTS}.",
            "path": None,
        }

    try:
        resolved_output_path = _safe_output_path(output_path, title, normalized_type)
        chart_x_values = _coerce_x_values(x_values, normalized_type)
        chart_y_values = _coerce_y_values(y_values)
        resolved_style_name, chart_style = _get_chart_style(style_name, styles_path)
    except ValueError as exc:
        return {
            "status": "error",
            "message": str(exc),
            "path": None,
        }

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(
        figsize=tuple(chart_style["figure_size"]),
        dpi=chart_style["dpi"],
        facecolor=chart_style["background_color"],
    )
    ax.set_facecolor(chart_style["axes_facecolor"])

    if normalized_type == "line":
        marker = chart_style["marker"] or None
        ax.plot(
            chart_x_values,
            chart_y_values,
            marker=marker,
            linewidth=chart_style["line_width"],
            color=chart_style["line_color"],
        )
    elif normalized_type == "bar":
        ax.bar(chart_x_values, chart_y_values, color=chart_style["bar_color"])
    else:
        ax.scatter(chart_x_values, chart_y_values, color=chart_style["scatter_color"])

    ax.set_title(title, color=chart_style["title_color"])
    if x_label:
        ax.set_xlabel(x_label, color=chart_style["label_color"])
    if y_label:
        ax.set_ylabel(y_label, color=chart_style["label_color"])
    ax.tick_params(colors=chart_style["tick_color"])
    ax.grid(
        chart_style["grid"],
        axis=chart_style["grid_axis"],
        alpha=chart_style["grid_alpha"],
    )
    fig.tight_layout()
    fig.savefig(resolved_output_path)
    plt.close(fig)

    return {
        "status": "success",
        "chart_type": normalized_type,
        "style_name": resolved_style_name,
        "path": str(resolved_output_path),
        "point_count": len(chart_x_values),
    }

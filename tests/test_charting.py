import json
from pathlib import Path

from kagents.tools.charting import create_chart_png


def test_create_chart_png_writes_png_under_outputs(tmp_path: Path, monkeypatch) -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "outputs" / "test_chart.png"
    if output_path.exists():
        output_path.unlink()

    result = create_chart_png(
        chart_type="line",
        x_values=["Jan", "Feb", "Mar"],
        y_values=[10, 12, 15],
        title="Test Chart",
        output_path="outputs/test_chart.png",
        x_label="Month",
        y_label="Value",
    )

    assert result["status"] == "success"
    assert result["point_count"] == 3
    assert result["style_name"] == "portfolio"
    assert Path(result["path"]).exists()
    assert Path(result["path"]).suffix == ".png"

    output_path.unlink()


def test_create_chart_png_blocks_paths_outside_outputs() -> None:
    result = create_chart_png(
        chart_type="bar",
        x_values=["A"],
        y_values=[1],
        output_path="data/not_allowed.png",
    )

    assert result["status"] == "error"
    assert "under" in result["message"]


def test_create_chart_png_requires_png_extension() -> None:
    result = create_chart_png(
        chart_type="bar",
        x_values=["A"],
        y_values=[1],
        output_path="outputs/not_allowed.svg",
    )

    assert result["status"] == "error"
    assert ".png" in result["message"]


def test_create_chart_png_rejects_unsupported_chart_type() -> None:
    result = create_chart_png(
        chart_type="pie",
        x_values=["A"],
        y_values=[1],
    )

    assert result["status"] == "error"
    assert "Unsupported chart type" in result["message"]


def test_create_chart_png_rejects_non_numeric_y_values() -> None:
    result = create_chart_png(
        chart_type="line",
        x_values=["A"],
        y_values=["not-a-number"],
    )

    assert result["status"] == "error"
    assert "Y values must be numeric" in result["message"]


def test_create_chart_png_uses_named_style(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    styles_path = tmp_path / "chart_styles.json"
    output_path = project_root / "outputs" / "styled_chart.png"
    styles_path.write_text(
        json.dumps(
            {
                "default_style": "minimal",
                "styles": {
                    "minimal": {
                        "line_color": "#111827",
                        "marker": "",
                        "grid": False,
                    },
                    "presentation": {
                        "line_color": "#0f766e",
                        "marker": "o",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    if output_path.exists():
        output_path.unlink()

    result = create_chart_png(
        chart_type="line",
        x_values=["A", "B"],
        y_values=[1, 2],
        output_path="outputs/styled_chart.png",
        style_name="presentation",
        styles_path=str(styles_path),
    )

    assert result["status"] == "success"
    assert result["style_name"] == "presentation"
    assert Path(result["path"]).exists()

    output_path.unlink()


def test_create_chart_png_rejects_unknown_style() -> None:
    result = create_chart_png(
        chart_type="line",
        x_values=["A"],
        y_values=[1],
        style_name="not-a-style",
    )

    assert result["status"] == "error"
    assert "Unknown chart style" in result["message"]

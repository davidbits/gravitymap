from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import plotly.graph_objects as go

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from gravitymap.constants import AU
from gravitymap.models import BodyState, HeatmapResult


def _body_marker_sizes(bodies: list[BodyState]) -> list[float]:
    return [
        float(np.clip(np.log10(body.radius_m) * 5.0 - 20.0, 8.0, 24.0))
        for body in bodies
    ]


def build_plotly_figure(result: HeatmapResult, bodies: list[BodyState]) -> go.Figure:
    display_ppb = (result.ratio - 1.0) * 1e9

    figure = go.Figure()
    figure.add_trace(
        go.Heatmap(
            x=result.x_au,
            y=result.y_au,
            z=display_ppb,
            colorscale="RdBu_r",
            colorbar={"title": "(H - 1) × 10^9"},
            hovertemplate="x=%{x:.3f} AU<br>y=%{y:.3f} AU<br>Δ=%{z:.3f} ppb<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[body.position_m[0] / AU for body in bodies],
            y=[body.position_m[1] / AU for body in bodies],
            mode="markers+text",
            text=[body.name for body in bodies],
            textposition="top center",
            marker={
                "size": _body_marker_sizes(bodies),
                "color": [body.color for body in bodies],
                "line": {"color": "#111111", "width": 1},
            },
            hovertemplate="%{text}<br>x=%{x:.4f} AU<br>y=%{y:.4f} AU<extra></extra>",
            showlegend=False,
        )
    )
    figure.update_layout(
        title=f"Solar-System Proper-Time Heatmap ({result.velocity_model})",
        xaxis_title="x [AU]",
        yaxis_title="y [AU]",
        template="plotly_white",
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
    )
    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    return figure


def save_heatmap(
    path: str | Path, result: HeatmapResult, bodies: list[BodyState]
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    display_values = (result.ratio - 1.0) * 1e9
    extent = (
        result.x_au.min(),
        result.x_au.max(),
        result.y_au.min(),
        result.y_au.max(),
    )

    figure, axis = plt.subplots(figsize=(10, 8), constrained_layout=True)
    image = axis.imshow(
        display_values,
        origin="lower",
        extent=extent,
        cmap="RdBu_r",
        aspect="equal",
    )
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label(r"$(H - 1) \times 10^9$ [ppb relative to Earth]")

    axis.set_title(f"Solar-System Proper-Time Heatmap ({result.velocity_model})")
    axis.set_xlabel("x [AU]")
    axis.set_ylabel("y [AU]")

    axis.scatter(
        [body.position_m[0] / AU for body in bodies],
        [body.position_m[1] / AU for body in bodies],
        s=_body_marker_sizes(bodies),
        c=[body.color for body in bodies],
        edgecolors="black",
        linewidths=0.8,
    )
    for body in bodies:
        axis.annotate(
            body.name,
            (body.position_m[0] / AU, body.position_m[1] / AU),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
            color="black",
        )

    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def save_field_data(path: str | Path, result: HeatmapResult) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path, x_au=result.x_au, y_au=result.y_au, ratio=result.ratio
    )
    return output_path

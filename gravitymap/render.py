from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from gravitymap.constants import AU
from gravitymap.models import Body, HeatmapResult


def save_heatmap(path: str | Path, result: HeatmapResult, bodies: list[Body]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    display_values = (result.ratio - 1.0) * 1e9
    extent = (result.x_au.min(), result.x_au.max(), result.y_au.min(), result.y_au.max())

    figure, axis = plt.subplots(figsize=(10, 8), constrained_layout=True)
    image = axis.imshow(
        display_values,
        origin="lower",
        extent=extent,
        cmap="coolwarm",
        aspect="equal",
    )
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label(r"$(H - 1) \times 10^9$ [ppb relative to Earth]")

    axis.set_title(f"Local Solar-System Proper-Time Heatmap ({result.velocity_model})")
    axis.set_xlabel("x [AU]")
    axis.set_ylabel("y [AU]")

    body_x = [body.position[0] / AU for body in bodies]
    body_y = [body.position[1] / AU for body in bodies]
    axis.scatter(body_x, body_y, s=25, c="black")

    for body in bodies:
        axis.annotate(
            body.name,
            (body.position[0] / AU, body.position[1] / AU),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=9,
            color="black",
        )

    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def save_field_data(path: str | Path, result: HeatmapResult) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, x_au=result.x_au, y_au=result.y_au, ratio=result.ratio)
    return output_path

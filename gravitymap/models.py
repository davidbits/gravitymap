from __future__ import annotations

from dataclasses import dataclass

import numpy as np


Vector = np.ndarray


@dataclass(frozen=True, slots=True)
class Body:
    name: str
    mass: float
    radius: float
    position: Vector
    velocity: Vector


@dataclass(frozen=True, slots=True)
class ReferenceClock:
    position: Vector
    velocity: Vector
    factor: float


@dataclass(frozen=True, slots=True)
class HeatmapResult:
    x_au: np.ndarray
    y_au: np.ndarray
    ratio: np.ndarray
    velocity_model: str

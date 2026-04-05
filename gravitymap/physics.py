from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from gravitymap.constants import AU, C, G
from gravitymap.models import BodyState, HeatmapResult, ReferenceClock


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=float)
    if array.shape[-1] != 3:
        raise ValueError("Points must have shape (..., 3).")
    return array


def potential_from_body(points: np.ndarray, body: BodyState) -> np.ndarray:
    points_array = _as_points(points)
    displacement = points_array - body.position_m
    radius = np.linalg.norm(displacement, axis=-1)
    outside = radius >= body.radius_m

    interior = (
        -G
        * body.mass_kg
        * (3.0 * body.radius_m**2 - radius**2)
        / (2.0 * body.radius_m**3)
    )
    exterior = np.zeros_like(radius, dtype=float)
    np.divide(-G * body.mass_kg, radius, out=exterior, where=radius != 0.0)

    return np.where(outside, exterior, interior)


def gravitational_potential(
    points: np.ndarray, bodies: Iterable[BodyState]
) -> np.ndarray:
    points_array = _as_points(points)
    potential = np.zeros(points_array.shape[:-1], dtype=float)
    for body in bodies:
        potential += potential_from_body(points_array, body)
    return potential


def velocity_squared(velocity: np.ndarray) -> np.ndarray:
    velocity_array = _as_points(velocity)
    return np.sum(velocity_array * velocity_array, axis=-1)


def proper_time_rate_factor(
    points: np.ndarray, velocity: np.ndarray, bodies: Iterable[BodyState]
) -> np.ndarray:
    potential = gravitational_potential(points, bodies)
    speed_squared = velocity_squared(velocity)
    return 1.0 + potential / C**2 - speed_squared / (2.0 * C**2)


def time_rate_ratio(
    points: np.ndarray,
    velocity: np.ndarray,
    bodies: Iterable[BodyState],
    reference_factor: float,
) -> np.ndarray:
    return proper_time_rate_factor(points, velocity, bodies) / reference_factor


def velocity_field(
    points: np.ndarray, bodies: Iterable[BodyState], model: str
) -> np.ndarray:
    points_array = _as_points(points)
    velocity = np.zeros_like(points_array, dtype=float)

    if model == "stationary-barycentric":
        return velocity

    if model != "circular-solar-orbit":
        raise ValueError(f"Unsupported velocity model: {model}")

    sun = next(body for body in bodies if body.name == "Sun")
    relative = points_array - sun.position_m
    planar_radius = np.linalg.norm(relative[..., :2], axis=-1)
    valid = planar_radius > sun.radius_m

    speed = np.zeros_like(planar_radius, dtype=float)
    np.divide(G * sun.mass_kg, planar_radius, out=speed, where=valid)
    speed = np.sqrt(speed, where=valid, out=speed)

    tangential_x = np.zeros_like(planar_radius, dtype=float)
    tangential_y = np.zeros_like(planar_radius, dtype=float)
    np.divide(-relative[..., 1], planar_radius, out=tangential_x, where=valid)
    np.divide(relative[..., 0], planar_radius, out=tangential_y, where=valid)

    velocity[..., 0] = speed * tangential_x + sun.velocity_m_per_s[0]
    velocity[..., 1] = speed * tangential_y + sun.velocity_m_per_s[1]
    velocity[..., 2] = sun.velocity_m_per_s[2]
    return velocity


def sample_ecliptic_plane(
    *,
    width_au: float,
    height_au: float,
    resolution: int,
    z_au: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if width_au <= 0.0 or height_au <= 0.0:
        raise ValueError("Plot dimensions must be positive.")
    if resolution < 2:
        raise ValueError("Resolution must be at least 2.")

    x_au = np.linspace(-width_au / 2.0, width_au / 2.0, resolution, dtype=float)
    y_resolution = max(2, int(round(resolution * height_au / width_au)))
    y_au = np.linspace(-height_au / 2.0, height_au / 2.0, y_resolution, dtype=float)
    xx_au, yy_au = np.meshgrid(x_au, y_au)

    plane = np.stack(
        (
            xx_au * AU,
            yy_au * AU,
            np.full_like(xx_au, z_au * AU),
        ),
        axis=-1,
    )
    return x_au, y_au, plane


def evaluate_heatmap(
    *,
    bodies: list[BodyState],
    reference_clock: ReferenceClock,
    width_au: float,
    height_au: float,
    resolution: int,
    z_au: float,
    velocity_model_name: str,
) -> HeatmapResult:
    x_au, y_au, plane = sample_ecliptic_plane(
        width_au=width_au,
        height_au=height_au,
        resolution=resolution,
        z_au=z_au,
    )
    velocity = velocity_field(plane, bodies, velocity_model_name)
    ratio = time_rate_ratio(plane, velocity, bodies, reference_clock.factor)
    return HeatmapResult(
        x_au=x_au,
        y_au=y_au,
        ratio=ratio,
        velocity_model=velocity_model_name,
    )

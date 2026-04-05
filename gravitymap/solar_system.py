from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np

from gravitymap.constants import (
    EARTH_MASS,
    EARTH_ORBIT_RADIUS,
    EARTH_RADIUS,
    EARTH_ROTATION_ANGULAR_SPEED,
    G,
    JUPITER_MASS,
    JUPITER_ORBIT_RADIUS,
    JUPITER_RADIUS,
    SUN_MASS,
    SUN_RADIUS,
)
from gravitymap.models import Body, ReferenceClock
from gravitymap.physics import proper_time_rate_factor


def circular_orbit_state(radius: float, phase_deg: float, central_mass: float) -> tuple[np.ndarray, np.ndarray]:
    phase = math.radians(phase_deg)
    position = np.array(
        [radius * math.cos(phase), radius * math.sin(phase), 0.0],
        dtype=float,
    )
    speed = math.sqrt(G * central_mass / radius)
    velocity = np.array(
        [-speed * math.sin(phase), speed * math.cos(phase), 0.0],
        dtype=float,
    )
    return position, velocity


def build_local_solar_system(
    *,
    earth_phase_deg: float = 0.0,
    jupiter_phase_deg: float = 60.0,
    include_jupiter: bool = True,
) -> list[Body]:
    earth_position, earth_velocity = circular_orbit_state(
        EARTH_ORBIT_RADIUS,
        earth_phase_deg,
        SUN_MASS,
    )

    planet_specs: list[tuple[str, float, float, np.ndarray, np.ndarray]] = [
        ("Earth", EARTH_MASS, EARTH_RADIUS, earth_position, earth_velocity),
    ]

    if include_jupiter:
        jupiter_position, jupiter_velocity = circular_orbit_state(
            JUPITER_ORBIT_RADIUS,
            jupiter_phase_deg,
            SUN_MASS,
        )
        planet_specs.append(
            ("Jupiter", JUPITER_MASS, JUPITER_RADIUS, jupiter_position, jupiter_velocity)
        )

    sun_position = -sum(mass * position for _, mass, _, position, _ in planet_specs) / SUN_MASS
    sun_velocity = -sum(mass * velocity for _, mass, _, _, velocity in planet_specs) / SUN_MASS

    bodies = [
        Body(
            name="Sun",
            mass=SUN_MASS,
            radius=SUN_RADIUS,
            position=sun_position,
            velocity=sun_velocity,
        )
    ]

    for name, mass, radius, position, velocity in planet_specs:
        bodies.append(
            Body(
                name=name,
                mass=mass,
                radius=radius,
                position=position + sun_position,
                velocity=velocity + sun_velocity,
            )
        )

    return bodies


def get_body(bodies: Iterable[Body], name: str) -> Body:
    for body in bodies:
        if body.name == name:
            return body
    raise KeyError(f"Body {name!r} not found.")


def earth_surface_reference_clock(bodies: Iterable[Body]) -> ReferenceClock:
    earth = get_body(bodies, "Earth")
    sun = get_body(bodies, "Sun")

    direction_to_sun = sun.position - earth.position
    direction_to_sun /= np.linalg.norm(direction_to_sun)

    surface_offset = EARTH_RADIUS * direction_to_sun
    angular_velocity = np.array([0.0, 0.0, EARTH_ROTATION_ANGULAR_SPEED], dtype=float)
    rotational_velocity = np.cross(angular_velocity, surface_offset)

    position = earth.position + surface_offset
    velocity = earth.velocity + rotational_velocity
    factor = float(proper_time_rate_factor(position, velocity, list(bodies)))

    return ReferenceClock(position=position, velocity=velocity, factor=factor)

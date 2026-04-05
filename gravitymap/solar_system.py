from __future__ import annotations

import math
from collections.abc import Iterable
from datetime import date, datetime, time, timezone

import numpy as np

from gravitymap.catalog import (
    BODY_DEFINITIONS,
    DEFAULT_BODY_SEQUENCE,
    MOON_MEAN_ORBIT,
    PLANETARY_SERIES,
)
from gravitymap.constants import (
    AU,
    DAY_SECONDS,
    EARTH_OBLIQUITY_DEG,
    G,
    J2000_JULIAN_DATE,
    JULIAN_CENTURY_DAYS,
)
from gravitymap.models import BodyState, OrbitalSeries, ReferenceClock, SatelliteOrbit
from gravitymap.physics import proper_time_rate_factor


def _normalize_angle_deg(angle_deg: float) -> float:
    return angle_deg % 360.0


def _rotation_matrix(
    longitude_node_rad: float, inclination_rad: float, argument_periapsis_rad: float
) -> np.ndarray:
    cos_o = math.cos(longitude_node_rad)
    sin_o = math.sin(longitude_node_rad)
    cos_i = math.cos(inclination_rad)
    sin_i = math.sin(inclination_rad)
    cos_w = math.cos(argument_periapsis_rad)
    sin_w = math.sin(argument_periapsis_rad)

    return np.array(
        [
            [
                cos_w * cos_o - sin_w * sin_o * cos_i,
                -sin_w * cos_o - cos_w * sin_o * cos_i,
                sin_o * sin_i,
            ],
            [
                cos_w * sin_o + sin_w * cos_o * cos_i,
                -sin_w * sin_o + cos_w * cos_o * cos_i,
                -cos_o * sin_i,
            ],
            [
                sin_w * sin_i,
                cos_w * sin_i,
                cos_i,
            ],
        ],
        dtype=float,
    )


def _solve_kepler(mean_anomaly_rad: float, eccentricity: float) -> float:
    eccentric_anomaly = mean_anomaly_rad
    for _ in range(16):
        delta = (
            eccentric_anomaly
            - eccentricity * math.sin(eccentric_anomaly)
            - mean_anomaly_rad
        ) / (1.0 - eccentricity * math.cos(eccentric_anomaly))
        eccentric_anomaly -= delta
        if abs(delta) < 1e-13:
            break
    return eccentric_anomaly


def julian_date(moment: date | datetime) -> float:
    if isinstance(moment, date) and not isinstance(moment, datetime):
        moment = datetime.combine(moment, time(12, 0), tzinfo=timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    moment = moment.astimezone(timezone.utc)

    year = moment.year
    month = moment.month
    day = moment.day
    fractional_day = (
        moment.hour
        + moment.minute / 60.0
        + (moment.second + moment.microsecond / 1e6) / 3600.0
    ) / 24.0

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + a // 4
    jd = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + fractional_day
        + b
        - 1524.5
    )
    return jd


def orbital_state_from_series(
    series: OrbitalSeries, julian_day: float, mu_central: float
) -> tuple[np.ndarray, np.ndarray]:
    centuries = (julian_day - series.epoch_julian_date) / JULIAN_CENTURY_DAYS
    semi_major_axis = (
        series.semi_major_axis_au
        + series.semi_major_axis_rate_au_per_century * centuries
    ) * AU
    eccentricity = (
        series.eccentricity + series.eccentricity_rate_per_century * centuries
    )
    inclination_rad = math.radians(
        series.inclination_deg + series.inclination_rate_deg_per_century * centuries
    )
    longitude_rad = math.radians(
        _normalize_angle_deg(
            series.mean_longitude_deg
            + series.mean_longitude_rate_deg_per_century * centuries
        )
    )
    perihelion_rad = math.radians(
        _normalize_angle_deg(
            series.longitude_of_perihelion_deg
            + series.longitude_of_perihelion_rate_deg_per_century * centuries
        )
    )
    node_rad = math.radians(
        _normalize_angle_deg(
            series.longitude_of_ascending_node_deg
            + series.longitude_of_ascending_node_rate_deg_per_century * centuries
        )
    )

    mean_anomaly_rad = math.radians(
        _normalize_angle_deg(math.degrees(longitude_rad - perihelion_rad))
    )
    argument_periapsis_rad = perihelion_rad - node_rad

    eccentric_anomaly = _solve_kepler(mean_anomaly_rad, eccentricity)
    radius = semi_major_axis * (1.0 - eccentricity * math.cos(eccentric_anomaly))
    mean_motion = math.sqrt(mu_central / semi_major_axis**3)

    x_orb = semi_major_axis * (math.cos(eccentric_anomaly) - eccentricity)
    y_orb = (
        semi_major_axis * math.sqrt(1.0 - eccentricity**2) * math.sin(eccentric_anomaly)
    )
    vx_orb = (
        -semi_major_axis
        * mean_motion
        * math.sin(eccentric_anomaly)
        / (1.0 - eccentricity * math.cos(eccentric_anomaly))
    )
    vy_orb = (
        semi_major_axis
        * mean_motion
        * math.sqrt(1.0 - eccentricity**2)
        * math.cos(eccentric_anomaly)
        / (1.0 - eccentricity * math.cos(eccentric_anomaly))
    )

    rotation = _rotation_matrix(node_rad, inclination_rad, argument_periapsis_rad)
    position = rotation @ np.array([x_orb, y_orb, 0.0], dtype=float)
    velocity = rotation @ np.array([vx_orb, vy_orb, 0.0], dtype=float)

    if not np.isfinite(radius):
        raise ValueError("Non-finite orbital radius encountered.")

    return position, velocity


def orbital_state_from_satellite_orbit(
    orbit: SatelliteOrbit, julian_day: float, mu_central: float
) -> tuple[np.ndarray, np.ndarray]:
    semi_major_axis = orbit.semi_major_axis_km * 1_000.0
    mean_motion = 2.0 * math.pi / (orbit.period_days * DAY_SECONDS)
    mean_anomaly_rad = (
        math.radians(orbit.mean_anomaly_deg)
        + mean_motion * (julian_day - orbit.epoch_julian_date) * DAY_SECONDS
    )
    mean_anomaly_rad = math.radians(
        _normalize_angle_deg(math.degrees(mean_anomaly_rad))
    )
    eccentric_anomaly = _solve_kepler(mean_anomaly_rad, orbit.eccentricity)

    x_orb = semi_major_axis * (math.cos(eccentric_anomaly) - orbit.eccentricity)
    y_orb = (
        semi_major_axis
        * math.sqrt(1.0 - orbit.eccentricity**2)
        * math.sin(eccentric_anomaly)
    )
    vx_orb = (
        -semi_major_axis
        * mean_motion
        * math.sin(eccentric_anomaly)
        / (1.0 - orbit.eccentricity * math.cos(eccentric_anomaly))
    )
    vy_orb = (
        semi_major_axis
        * mean_motion
        * math.sqrt(1.0 - orbit.eccentricity**2)
        * math.cos(eccentric_anomaly)
        / (1.0 - orbit.eccentricity * math.cos(eccentric_anomaly))
    )

    rotation = _rotation_matrix(
        math.radians(orbit.longitude_of_ascending_node_deg),
        math.radians(orbit.inclination_deg),
        math.radians(orbit.argument_of_periapsis_deg),
    )
    position = rotation @ np.array([x_orb, y_orb, 0.0], dtype=float)
    velocity = rotation @ np.array([vx_orb, vy_orb, 0.0], dtype=float)
    return position, velocity


def build_solar_system(
    *,
    moment: date | datetime,
    include_moon: bool = True,
    include_pluto: bool = True,
) -> list[BodyState]:
    julian_day = julian_date(moment)
    sun = BODY_DEFINITIONS["Sun"]
    sun_mu = G * sun.mass_kg

    heliocentric: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "Sun": (np.zeros(3, dtype=float), np.zeros(3, dtype=float)),
    }

    for name in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"):
        definition = BODY_DEFINITIONS[name]
        heliocentric[name] = orbital_state_from_series(
            PLANETARY_SERIES[name],
            julian_day,
            sun_mu + G * definition.mass_kg,
        )

    if include_pluto:
        pluto = BODY_DEFINITIONS["Pluto"]
        heliocentric["Pluto"] = orbital_state_from_series(
            PLANETARY_SERIES["Pluto"],
            julian_day,
            sun_mu + G * pluto.mass_kg,
        )

    earth = BODY_DEFINITIONS["Earth"]
    moon = BODY_DEFINITIONS["Moon"]
    emb_position, emb_velocity = orbital_state_from_series(
        PLANETARY_SERIES["EM Barycenter"],
        julian_day,
        sun_mu + G * (earth.mass_kg + moon.mass_kg),
    )

    if include_moon:
        moon_rel_position, moon_rel_velocity = orbital_state_from_satellite_orbit(
            MOON_MEAN_ORBIT,
            julian_day,
            G * (earth.mass_kg + moon.mass_kg),
        )
        moon_fraction = moon.mass_kg / (earth.mass_kg + moon.mass_kg)
        earth_position = emb_position - moon_fraction * moon_rel_position
        earth_velocity = emb_velocity - moon_fraction * moon_rel_velocity
        heliocentric["Earth"] = (earth_position, earth_velocity)
        heliocentric["Moon"] = (
            earth_position + moon_rel_position,
            earth_velocity + moon_rel_velocity,
        )
    else:
        heliocentric["Earth"] = (emb_position, emb_velocity)

    states: list[BodyState] = []
    for name in DEFAULT_BODY_SEQUENCE:
        if name == "Moon" and not include_moon:
            continue
        if name == "Pluto" and not include_pluto:
            continue
        if name not in heliocentric:
            continue
        definition = BODY_DEFINITIONS[name]
        position, velocity = heliocentric[name]
        states.append(
            BodyState(
                name=name,
                mass_kg=definition.mass_kg,
                radius_m=definition.radius_m,
                position_m=position,
                velocity_m_per_s=velocity,
                color=definition.color,
            )
        )

    total_mass = sum(body.mass_kg for body in states)
    barycenter = sum(body.mass_kg * body.position_m for body in states) / total_mass
    barycenter_velocity = (
        sum(body.mass_kg * body.velocity_m_per_s for body in states) / total_mass
    )

    barycentric_states = [
        BodyState(
            name=body.name,
            mass_kg=body.mass_kg,
            radius_m=body.radius_m,
            position_m=body.position_m - barycenter,
            velocity_m_per_s=body.velocity_m_per_s - barycenter_velocity,
            color=body.color,
        )
        for body in states
    ]

    return barycentric_states


def get_body(bodies: Iterable[BodyState], name: str) -> BodyState:
    for body in bodies:
        if body.name == name:
            return body
    raise KeyError(f"Body {name!r} not found.")


def earth_surface_reference_clock(
    bodies: Iterable[BodyState],
    *,
    latitude_deg: float = 0.0,
    local_solar_time_hours: float = 12.0,
    altitude_m: float = 0.0,
) -> ReferenceClock:
    body_list = list(bodies)
    earth = get_body(body_list, "Earth")
    sun = get_body(body_list, "Sun")

    spin_axis = np.array(
        [
            0.0,
            math.sin(math.radians(EARTH_OBLIQUITY_DEG)),
            math.cos(math.radians(EARTH_OBLIQUITY_DEG)),
        ],
        dtype=float,
    )

    direction_to_sun = sun.position_m - earth.position_m
    direction_to_sun /= np.linalg.norm(direction_to_sun)

    subsolar_projection = (
        direction_to_sun - np.dot(direction_to_sun, spin_axis) * spin_axis
    )
    if np.linalg.norm(subsolar_projection) < 1e-12:
        subsolar_projection = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        subsolar_projection /= np.linalg.norm(subsolar_projection)

    east = np.cross(spin_axis, subsolar_projection)
    east /= np.linalg.norm(east)

    hour_angle_rad = math.radians(15.0 * (local_solar_time_hours - 12.0))
    local_meridian = (
        math.cos(hour_angle_rad) * subsolar_projection + math.sin(hour_angle_rad) * east
    )

    latitude_rad = math.radians(latitude_deg)
    surface_normal = (
        math.cos(latitude_rad) * local_meridian + math.sin(latitude_rad) * spin_axis
    )
    surface_normal /= np.linalg.norm(surface_normal)

    surface_offset = (earth.radius_m + altitude_m) * surface_normal
    sidereal_day_seconds = 86_164.0905
    angular_velocity = (2.0 * math.pi / sidereal_day_seconds) * spin_axis
    rotational_velocity = np.cross(angular_velocity, surface_offset)

    position = earth.position_m + surface_offset
    velocity = earth.velocity_m_per_s + rotational_velocity
    factor = float(proper_time_rate_factor(position, velocity, body_list))

    return ReferenceClock(
        position_m=position,
        velocity_m_per_s=velocity,
        factor=factor,
        latitude_deg=latitude_deg,
        local_solar_time_hours=local_solar_time_hours,
        altitude_m=altitude_m,
    )


def valid_approximation_window() -> tuple[date, date]:
    return date(1800, 1, 1), date(2050, 12, 31)


def default_render_moment() -> datetime:
    return datetime(2026, 4, 5, 12, 0, tzinfo=timezone.utc)

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


Vector = np.ndarray


@dataclass(frozen=True, slots=True)
class OrbitalSeries:
    semi_major_axis_au: float
    semi_major_axis_rate_au_per_century: float
    eccentricity: float
    eccentricity_rate_per_century: float
    inclination_deg: float
    inclination_rate_deg_per_century: float
    mean_longitude_deg: float
    mean_longitude_rate_deg_per_century: float
    longitude_of_perihelion_deg: float
    longitude_of_perihelion_rate_deg_per_century: float
    longitude_of_ascending_node_deg: float
    longitude_of_ascending_node_rate_deg_per_century: float
    epoch_julian_date: float


@dataclass(frozen=True, slots=True)
class SatelliteOrbit:
    semi_major_axis_km: float
    eccentricity: float
    argument_of_periapsis_deg: float
    mean_anomaly_deg: float
    inclination_deg: float
    longitude_of_ascending_node_deg: float
    period_days: float
    epoch_julian_date: float


@dataclass(frozen=True, slots=True)
class BodyDefinition:
    name: str
    mass_kg: float
    radius_m: float
    color: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BodyState:
    name: str
    mass_kg: float
    radius_m: float
    position_m: Vector
    velocity_m_per_s: Vector
    color: str


@dataclass(frozen=True, slots=True)
class ReferenceClock:
    position_m: Vector
    velocity_m_per_s: Vector
    factor: float
    latitude_deg: float
    local_solar_time_hours: float
    altitude_m: float


@dataclass(frozen=True, slots=True)
class HeatmapResult:
    x_au: np.ndarray
    y_au: np.ndarray
    ratio: np.ndarray
    velocity_model: str


@dataclass(frozen=True, slots=True)
class SourceEntry:
    key: str
    title: str
    url: str
    note: str

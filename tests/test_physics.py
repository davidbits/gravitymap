import unittest
from datetime import date

import numpy as np

from gravitymap.constants import AU, J2000_JULIAN_DATE
from gravitymap.physics import proper_time_rate_factor, time_rate_ratio, velocity_field
from gravitymap.solar_system import (
    build_solar_system,
    earth_surface_reference_clock,
    get_body,
    julian_date,
    orbital_state_from_series,
)
from gravitymap.catalog import BODY_DEFINITIONS, PLANETARY_SERIES


class GravitymapPhysicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bodies = build_solar_system(moment=date(2026, 4, 5))
        self.reference_clock = earth_surface_reference_clock(self.bodies)

    def test_julian_date_at_j2000_noon(self) -> None:
        self.assertAlmostEqual(
            julian_date(date(2000, 1, 1)), J2000_JULIAN_DATE, places=6
        )

    def test_solar_system_contains_major_bodies(self) -> None:
        names = {body.name for body in self.bodies}
        self.assertEqual(
            names,
            {
                "Sun",
                "Mercury",
                "Venus",
                "Earth",
                "Moon",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            },
        )

    def test_reference_clock_is_normalized(self) -> None:
        ratio = time_rate_ratio(
            self.reference_clock.position_m,
            self.reference_clock.velocity_m_per_s,
            self.bodies,
            self.reference_clock.factor,
        )
        self.assertAlmostEqual(float(ratio), 1.0, places=15)

    def test_near_sun_time_runs_slower_than_on_earth(self) -> None:
        sun = get_body(self.bodies, "Sun")
        point = sun.position_m + np.array([0.1 * AU, 0.0, 0.0])
        ratio = time_rate_ratio(
            point, np.zeros(3), self.bodies, self.reference_clock.factor
        )
        self.assertLess(float(ratio), 1.0)

    def test_far_from_bodies_time_runs_faster_than_on_earth(self) -> None:
        point = np.array([60.0 * AU, 0.0, 0.0])
        ratio = time_rate_ratio(
            point, np.zeros(3), self.bodies, self.reference_clock.factor
        )
        self.assertGreater(float(ratio), 1.0)

    def test_circular_solar_orbit_is_slower_than_stationary_at_same_point(self) -> None:
        point = np.array([[2.0 * AU, 0.0, 0.0]])
        stationary = proper_time_rate_factor(point, np.zeros((1, 3)), self.bodies)
        orbiting = proper_time_rate_factor(
            point,
            velocity_field(point, self.bodies, "circular-solar-orbit"),
            self.bodies,
        )
        self.assertLess(float(orbiting[0]), float(stationary[0]))

    def test_earth_moon_barycenter_stays_near_one_au(self) -> None:
        sun_mass = BODY_DEFINITIONS["Sun"].mass_kg
        earth_mass = BODY_DEFINITIONS["Earth"].mass_kg
        moon_mass = BODY_DEFINITIONS["Moon"].mass_kg
        emb_position, _ = orbital_state_from_series(
            PLANETARY_SERIES["EM Barycenter"],
            J2000_JULIAN_DATE,
            6.67430e-11 * (sun_mass + earth_mass + moon_mass),
        )
        self.assertGreater(np.linalg.norm(emb_position) / AU, 0.98)
        self.assertLess(np.linalg.norm(emb_position) / AU, 1.02)


if __name__ == "__main__":
    unittest.main()

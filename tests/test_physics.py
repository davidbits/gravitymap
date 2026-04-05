import unittest

import numpy as np

from gravitymap.constants import AU
from gravitymap.physics import proper_time_rate_factor, time_rate_ratio, velocity_field
from gravitymap.solar_system import build_local_solar_system, earth_surface_reference_clock, get_body


class GravitymapPhysicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bodies = build_local_solar_system()
        self.reference_clock = earth_surface_reference_clock(self.bodies)

    def test_reference_clock_is_normalized(self) -> None:
        ratio = time_rate_ratio(
            self.reference_clock.position,
            self.reference_clock.velocity,
            self.bodies,
            self.reference_clock.factor,
        )
        self.assertAlmostEqual(float(ratio), 1.0, places=15)

    def test_near_sun_time_runs_slower_than_on_earth(self) -> None:
        sun = get_body(self.bodies, "Sun")
        point = sun.position + np.array([0.1 * AU, 0.0, 0.0])
        ratio = time_rate_ratio(point, np.zeros(3), self.bodies, self.reference_clock.factor)
        self.assertLess(float(ratio), 1.0)

    def test_far_from_bodies_time_runs_faster_than_on_earth(self) -> None:
        point = np.array([10.0 * AU, 10.0 * AU, 0.0])
        ratio = time_rate_ratio(point, np.zeros(3), self.bodies, self.reference_clock.factor)
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


if __name__ == "__main__":
    unittest.main()

import unittest
from dataclasses import replace
import numpy as np
from gyro_sim import Config, Experiment, sample, simulate


class StartupTests(unittest.TestCase):
    def test_reset_then_space_starts_small_wheels_before_ring(self):
        e = Experiment(Config(startup="staged"))
        self.assertTrue(e.paused)
        np.testing.assert_array_equal(e.data.qvel, 0)
        e.handle_key(32)
        e.tick(1.0)
        row = sample(e.model, e.data, e.c)
        self.assertLess(abs(row["ring_rpm"]), .01)
        self.assertGreater(row["rotor0_rpm"], 500)
        self.assertLess(row["rotor0_rpm"], 700)
        self.assertTrue(all(e.data.eq_active))

        # Reproduce the user's exact reset/start sequence after it has been running.
        e.handle_key(82)
        self.assertTrue(e.paused)
        self.assertEqual(e.data.time, 0)
        np.testing.assert_array_equal(e.data.qvel, 0)
        e.tick(.2)
        self.assertEqual(e.data.time, 0)
        e.handle_key(32)
        e.tick(2.4)
        row = sample(e.model, e.data, e.c)
        self.assertLess(abs(row["ring_rpm"]), .01)
        for j in range(4):
            self.assertAlmostEqual(row[f"rotor{j}_rpm"], 1200, delta=1)
        self.assertTrue(all(e.data.eq_active))
        e.tick(1.6)
        row = sample(e.model, e.data, e.c)
        self.assertGreater(row["ring_rpm"], 10)
        self.assertFalse(any(e.data.eq_active))
        for j in range(4):
            self.assertAlmostEqual(row[f"rotor{j}_rpm"], 1200, delta=20)
            self.assertLessEqual(abs(e.data.actuator(f"rotor_motor{j}").ctrl[0]), 1)

        e.handle_key(32)
        before = e.data.time
        e.tick(.5)
        self.assertEqual(e.data.time, before)
        e.handle_key(82)
        self.assertTrue(all(e.data.eq_active))
        self.assertTrue(e.paused)

    def test_staged_startup_converges(self):
        c = Config(startup="staged", duration=5)
        a, sa = simulate(c)
        b, sb = simulate(replace(c, dt=.0001))
        self.assertIsNone(sa["relative_energy_drift"])
        self.assertEqual(sa["numerical_warnings"], 0)
        self.assertEqual(sb["numerical_warnings"], 0)
        self.assertAlmostEqual(a[-1]["ring_rpm"], b[-1]["ring_rpm"], delta=.03)
        for j in range(4):
            self.assertAlmostEqual(a[-1][f"tilt{j}_deg"], b[-1][f"tilt{j}_deg"], delta=.1)

    def test_free_flight_rejects_ground_motor(self):
        with self.assertRaisesRegex(ValueError, "ground-mounted motor"):
            Experiment(Config(mode="free", startup="staged"))


if __name__ == "__main__":
    unittest.main()

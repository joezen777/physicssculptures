import unittest
from flight import flight_config, measure
from gyro_sim import Experiment

class PoweredFlightTests(unittest.TestCase):
    def test_lift_and_external_momentum(self):
        r = measure(flight_config())
        self.assertGreater(r["com_rise_m"], 4)
        self.assertGreater(r["thrust_N"], r["weight_N"])
        self.assertLess(r["momentum_residual_Ns"], 1e-5)
        self.assertEqual(r["warnings"], 0)

    def test_internal_motors_cannot_lift_without_air(self):
        for gravity in (0., 9.81):
            r = measure(flight_config(False, gravity=gravity, duration=1.))
            self.assertAlmostEqual(r["com_rise_m"], -.5*gravity, places=5)
            self.assertLess(r["momentum_residual_Ns"], 1e-5)

    def test_no_world_motor_or_support_in_flight(self):
        e = Experiment(flight_config())
        self.assertEqual(e.model.nu, 8)
        self.assertEqual(e.model.neq, 0)
        self.assertEqual(e.model.joint("base").type[0], 0)
        with self.assertRaises(ValueError):
            Experiment(flight_config(mode="supported"))

if __name__ == "__main__":
    unittest.main()

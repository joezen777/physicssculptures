"""Physical invariants, not animation appearance, are the acceptance criteria."""
from dataclasses import replace
import unittest
import numpy as np
import mujoco
from gyro_sim import Config, make_model, initial_data, sample, simulate


class PhysicsTests(unittest.TestCase):
    def test_static_support_carries_weight(self):
        c = Config(ring_rpm=0, rotor_rpm=0, tilt_deg=0)
        m, _ = make_model(c)
        d = initial_data(m, c)
        r = sample(m, d, c)
        self.assertAlmostEqual(r["support_up_N"],
                               m.body_subtreemass[1]*c.gravity, places=7)

    def test_free_zero_gravity_conservation(self):
        c = Config(mode="free", gravity=0, duration=.8)
        _, s = simulate(c)
        self.assertLess(s["max_ballistic_com_error_m"], 1e-7)
        self.assertLess(s["max_linear_momentum_error_kg_m_s"], 1e-7)
        self.assertLess(s["max_angular_momentum_error_kg_m2_s"], 1e-7)
        self.assertLess(s["relative_energy_drift"], 1e-7)

    def test_free_gravity_is_ballistic(self):
        _, s = simulate(Config(mode="free", duration=.8))
        self.assertLess(s["max_ballistic_com_error_m"], 1e-7)
        self.assertLess(s["max_linear_momentum_error_kg_m_s"], 1e-7)
        self.assertLess(s["max_angular_momentum_error_kg_m2_s"], 1e-7)
        self.assertLess(s["relative_energy_drift"], 1e-7)

    def test_timestep_convergence(self):
        c = Config(mode="free", gravity=0, duration=.5, dt=.0004)
        coarse, _ = simulate(c)
        fine, _ = simulate(replace(c, dt=.0002))
        finer, _ = simulate(replace(c, dt=.0001))
        fields = ["ring_z", "tilt0_deg", "tilt1_deg", "tilt2_deg", "tilt3_deg"]
        v = lambda rows: np.array([rows[-1][k] for k in fields])
        e1 = np.linalg.norm(v(coarse)-v(fine))
        e2 = np.linalg.norm(v(fine)-v(finer))
        self.assertLess(e2, max(e1*.4, 1e-9))
        self.assertLess(e2, 1e-4)

    def test_known_external_torque_changes_angular_momentum(self):
        c = Config(mode="free", gravity=0, duration=.1)
        m, _ = make_model(c)
        d = initial_data(m, c)
        before = sample(m, d, c)
        # World-frame torque on the whole ring, no translational force.
        d.xfrc_applied[m.body("ring").id, 3] = .1
        for _ in range(round(c.duration/c.dt)):
            mujoco.mj_step(m, d)
        after = sample(m, d, c)
        self.assertAlmostEqual(after["h_x"]-before["h_x"], .1*d.time, places=7)
        self.assertAlmostEqual(after["h_y"]-before["h_y"], 0, places=7)
        self.assertAlmostEqual(after["h_z"]-before["h_z"], 0, places=7)


if __name__ == "__main__":
    unittest.main()

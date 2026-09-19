import unittest
from dataclasses import replace
import math
import numpy as np
import mujoco
from gyro_sim import Config, Experiment, make_model, initial_data, simulate, sample, advance, rotor_load
from mechanics import release_rpm, mount_height


class MechanismTests(unittest.TestCase):
    def test_passive_latch_stays_closed_below_threshold_and_releases_above(self):
        low = Config(startup="staged", ring_rpm=20, rotor_rpm=0, duration=6)
        rows, _ = simulate(low)
        self.assertTrue(all(r["locked0"] for r in rows))
        self.assertLess(max(r["tilt0_deg"] for r in rows), .1)
        high = replace(low, ring_rpm=60)
        rows, _ = simulate(high)
        first = next(i for i,r in enumerate(rows) if not r["locked0"])
        self.assertGreater(rows[first]["time"], high.rotor_ramp+high.rotor_hold)
        self.assertGreater(rows[first]["ring_rpm"], release_rpm(high)*.9)
        self.assertGreaterEqual(max(r["pin0_mm"] for r in rows[:first+1]), high.pin_travel*1000)
        self.assertTrue(all(not r["locked0"] for r in rows[first:]))
        stronger = replace(high, spring_preload=.3)
        rows, _ = simulate(stronger)
        self.assertTrue(all(r["locked0"] for r in rows))

    def test_collar_axis_and_brace_clearance(self):
        c = Config(latch=False, ring_rpm=0, rotor_rpm=0, tilt_deg=35, duration=2)
        m,_ = make_model(c)
        for j in range(4):
            a=j*math.pi/2
            np.testing.assert_allclose(m.joint(f"tilt{j}").axis, [-math.sin(a),math.cos(a),0], atol=1e-12)
            pos=m.geom(f"brace{j}").pos
            angle=math.atan2(pos[1],pos[0])
            self.assertAlmostEqual(math.cos(angle-a), math.sqrt(.5), places=8)
        d=initial_data(m,c)
        for step in range(round(c.duration/c.dt)):
            advance(m,d,c)
            if step%50==0:
                mujoco.mj_forward(m,d)
                z=d.body("rod0").xmat.reshape(3,3)[:,2]
                self.assertAlmostEqual(z[1],0,places=7)
                self.assertGreater(z[2],-.01)

    def test_ball_stop_is_hemisphere_not_twist_limit(self):
        c=Config(joint_type="ball",latch=False,ring_rpm=0,rotor_rpm=0,tilt_deg=45,duration=2)
        rows,_=simulate(c)
        self.assertLess(max(r["tilt0_deg"] for r in rows),90.5)
        self.assertGreater(max(r["tilt0_deg"] for r in rows),85)
        m,_=make_model(c)
        d=initial_data(m,replace(c,tilt_deg=0))
        # 180 degrees of axial twist must not engage the upper-hemisphere stop.
        d.joint("ball0").qpos[:]=[0,0,0,1]
        mujoco.mj_forward(m,d)
        self.assertLess(d.ten_length[m.tendon("hemisphere0").id],1e-8)
        self.assertGreater(mount_height(c)-c.rotor_radius,.022)

    def test_propeller_scaling_direction_and_external_momentum(self):
        c=Config(mode="free",rotor_type="propeller",rotor_mass=.03,rotor_radius=.12,
                 joint_type="collar",latch=False,joint_limits=False,collisions=False,
                 ring_rpm=0,rotor_rpm=6000,gravity=0,duration=.05,alternating=True)
        m,_=make_model(c)
        d=initial_data(m,c)
        f=[rotor_load(m,d,c,j)[1][2] for j in range(4)]
        self.assertTrue(all(v>0 for v in f))
        expected=c.thrust_coefficient*c.air_density*(6000/60)**2*(2*c.rotor_radius)**4
        self.assertAlmostEqual(f[0],expected,places=7)
        d2=initial_data(m,replace(c,rotor_rpm=12000))
        self.assertAlmostEqual(rotor_load(m,d2,c,0)[1][2]/f[0],4,places=8)
        d0=initial_data(m,replace(c,rotor_rpm=0))
        self.assertEqual(np.linalg.norm(rotor_load(m,d0,c,0)[1]),0)
        impulse=0.
        for _ in range(round(c.duration/c.dt)):
            advance(m,d,c)
            impulse+=sum(d.xfrc_applied[m.body(f"rotor{j}").id,2] for j in range(4))*c.dt
        r=sample(m,d,c)
        self.assertGreater(r["p_z"],0)
        self.assertAlmostEqual(r["p_z"],impulse,delta=1e-6)

    def test_ball_staged_and_propeller_runs_stay_finite(self):
        for c in [Config(joint_type="ball",startup="staged",duration=6),
                  Config(joint_type="ball",rotor_type="propeller",rotor_mass=.03,rotor_radius=.12,
                         rotor_rpm=8000,alternating=True,startup="staged",duration=6),
                  Config(rotor_type="propeller",rotor_mass=.03,rotor_radius=.12,
                         rotor_rpm=8000,alternating=True,startup="staged",duration=6)]:
            rows,s=simulate(c)
            self.assertEqual(s["numerical_warnings"],0)
            self.assertTrue(all(math.isfinite(r["energy"]) for r in rows))
            self.assertLess(max(r[f"tilt{j}_deg"] for r in rows for j in range(4)),90.5)


if __name__=="__main__":
    unittest.main()

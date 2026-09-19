import unittest
from dataclasses import replace
import numpy as np
from gyro_sim import Experiment, advance, sample
from steering import steering_config
from fastapi.testclient import TestClient
from server import app

class SteeringTests(unittest.TestCase):
    def test_tracks_two_live_targets_and_support_carries_weight(self):
        e=Experiment(steering_config())
        m,d=e.model,e.data
        first=sample(m,d,e.c)
        initial_h=np.array([first["h_"+a] for a in "xyz"])
        for x,y in [(8,0),(-6,5)]:
            e.c=replace(e.c,steer_x_deg=x,steer_y_deg=y)
            for _ in range(round(4/e.c.dt)):
                advance(m,d,e.c)
            row=sample(m,d,e.c)
            self.assertLess(abs(row["steer_x_deg"]-x),.7)
            self.assertLess(abs(row["steer_y_deg"]-y),.7)
            self.assertAlmostEqual(row["support_up_N"],row["weight_N"],places=5)
            np.testing.assert_allclose([row["h_"+a] for a in "xyz"],initial_h,atol=1e-5)
        self.assertEqual(sum(w.number for w in d.warning),0)
        self.assertEqual(m.nu,8)
        self.assertTrue(all(m.actuator_trnid[:,0] != m.joint("base").id))

    def test_live_target_preserves_time_and_rejects_invalid(self):
        client=TestClient(app)
        s=client.post("/api/preset/steering").json()
        r=client.post("/api/steer",json={"x":-5,"y":7})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["revision"],s["revision"])
        self.assertEqual(r.json()["config"]["steer_y_deg"],7)
        self.assertEqual(client.post("/api/steer",json={"x":99,"y":0}).status_code,422)

if __name__=="__main__": unittest.main()

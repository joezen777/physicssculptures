import unittest
from fastapi.testclient import TestClient
from server import app, lab


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app)
        self.client.post("/api/config",json={"mode":"supported","startup":"staged","joint_type":"collar","rotor_type":"flywheel","rotor_rpm":1200.,"ring_rpm":60.})

    def test_apply_both_speeds_resets_and_pause_does_not_reset(self):
        r=self.client.post("/api/config",json={"rotor_rpm":1800.,"ring_rpm":50.,"joint_type":"ball"})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["config"]["rotor_rpm"],1800)
        self.assertEqual(r.json()["config"]["ring_rpm"],50)
        self.assertEqual(r.json()["metrics"]["time"],0)
        self.assertTrue(r.json()["paused"])
        self.client.post("/api/action/toggle",json={})
        lab.experiment.tick(.1)
        r=self.client.post("/api/action/toggle",json={})
        self.assertTrue(r.json()["paused"])
        self.assertGreater(r.json()["metrics"]["time"],0)
        r=self.client.post("/api/action/reset",json={})
        self.assertEqual(r.json()["metrics"]["time"],0)
        self.assertTrue(r.json()["paused"])

    def test_invalid_spring_does_not_replace_model(self):
        before=self.client.get("/api/state").json()["revision"]
        r=self.client.post("/api/config",json={"spring_k":0})
        self.assertEqual(r.status_code,422)
        self.assertEqual(self.client.get("/api/state").json()["revision"],before)

    def test_propeller_geometry_is_served_after_switch(self):
        r=self.client.post("/api/config",json={"rotor_type":"propeller","rotor_radius":.12,"rotor_mass":.03})
        self.assertEqual(r.status_code,200)
        model=self.client.get("/api/model").json()
        props=[g for g in model["geoms"] if g["name"].startswith("propeller")]
        self.assertEqual(len(props),4)
        self.assertEqual(model["revision"],r.json()["revision"])


if __name__=="__main__":
    unittest.main()

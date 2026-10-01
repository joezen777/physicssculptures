import unittest
from dataclasses import replace
from math import pi, sqrt
from fastapi.testclient import TestClient
from whistle import Config, Module, simulate, example_config, spring_force, spring_energy, pneumatic, frequency
from whistle_server import app, clean

class WhistlePhysicsTests(unittest.TestCase):
    def test_geometry_validation(self):
        for patch in (dict(travel_mm=100),dict(kinetic_n=.1),dict(valve_close=.95),
                      dict(rpm=float("nan")),dict(stator_cam=True)):
            with self.assertRaises(ValueError):replace(Config(),**patch).validate()

    def test_breakaway_static_friction(self):
        c=Config(rpm=0,spring_k=0,preload_n=.004,initial_fraction=.5,inlet_mm2=0)
        m=Module(c)
        for i in range(100):m.step(i*.0005,.0005)
        self.assertEqual(m.x,.5*c.stroke)
        self.assertEqual(m.v,0)
        self.assertAlmostEqual(m.forces["friction"],.004)

    def test_centrifugal_is_position_dependent(self):
        c=Config()
        m=Module(c);m.step(0,.0005);first=m.forces["fc"]
        m=Module(c);m.x=c.stroke;m.step(0,.0005)
        self.assertAlmostEqual(m.forces["fc"]/first,c.radius/c.r0,places=8)

    def test_linear_equilibrium_without_air(self):
        c=Config(inlet_mm2=0,static_n=0,kinetic_n=0,damping=.12,duration=8)
        s=simulate(c,False)["summary"]
        expected=(c.mass_g/1000*c.omega**2*c.r0-c.preload_n)/(c.spring_k-c.mass_g/1000*c.omega**2)
        self.assertAlmostEqual(s["equilibrium_mm"],1000*expected,delta=.01)
        self.assertFalse(s["self_cycles"])

    def test_bistable_force_is_conservative(self):
        c=Config(mode="C")
        for frac in (.1,.3,.5,.7,.9):
            x=c.stroke*frac;eps=1e-7
            numerical=-(spring_energy(c,x+eps)-spring_energy(c,x-eps))/(2*eps)
            self.assertAlmostEqual(spring_force(c,x),numerical,places=7)

    def test_dump_does_not_remove_centrifugal_force(self):
        c=Config(mode="B",spring_k=0,preload_n=0,initial_fraction=.95,duration=4)
        result=simulate(c)
        self.assertTrue(result["rows"][-1]["open"])
        self.assertAlmostEqual(result["rows"][-1]["x"],c.stroke)
        self.assertFalse(result["summary"]["self_cycles"])

    def test_pressure_dump_reduces_equilibrium_pressure(self):
        c=example_config()
        ps,gi,go,_,_=pneumatic(c,0,False)
        _,_,gv,_,_=pneumatic(c,0,True)
        self.assertGreater(ps*gi/(gi+go),10*ps*gi/(gi+gv))

    def test_default_does_not_cycle(self):
        for mode in "ABCD":
            s=simulate(Config(mode=mode,duration=8),False)["summary"]
            self.assertFalse(s["self_cycles"],mode)
            self.assertEqual(s["reset_count"],0,mode)

    def test_candidate_cycles_with_energy_and_converges(self):
        c=example_config()
        a=simulate(c,False)["summary"]
        b=simulate(replace(c,dt=c.dt/2),False)["summary"]
        self.assertTrue(a["self_cycles"])
        self.assertTrue(b["self_cycles"])
        self.assertGreater(a["pressure_work_j"],0)
        self.assertGreater(a["source_power_w"],0)
        self.assertLess(abs(a["cycle_hz"]-b["cycle_hz"])/b["cycle_hz"],.01)
        self.assertLess(abs(a["effective_energy_change_j"]-a["pressure_work_j"]+a["dissipation_j"]),2e-5)
        self.assertFalse(simulate(replace(c,recovery=0),False)["summary"]["self_cycles"])

    def test_acoustic_models(self):
        c=Config()
        high,_=frequency(c,0);low,_=frequency(c,c.stroke)
        self.assertAlmostEqual(high,343/(4*(.025+.6*.006)),places=7)
        self.assertGreater(high,low)
        c=replace(c,acoustic="helmholtz")
        self.assertAlmostEqual(frequency(c,0)[0]/frequency(c,c.stroke)[0],2,places=7)

    def test_balance_and_mass_fault(self):
        c=Config(modules=2,duration=2)
        run=simulate(c)
        self.assertLess(run["summary"]["peak_imbalance"],1e-10)
        fault=simulate(replace(c,fault="mass"))
        expected=.05*c.mass_g/1000*c.r0*c.omega**2
        self.assertAlmostEqual(fault["rows"][0]["imbalance_n"],expected,places=8)
        self.assertGreater(fault["summary"]["peak_imbalance"],.01)

    def test_cam_is_classified_as_forced(self):
        c=Config(mode="D",stator_cam=True,rpm=60,spring_k=0,preload_n=0,
                 static_n=.001,kinetic_n=.0005,duration=10)
        s=simulate(c,False)["summary"]
        self.assertTrue(s["maintained"])
        self.assertTrue(s["forced"])
        self.assertFalse(s["self_cycles"])
        self.assertGreater(s["cam_work_j"],0)

    def test_high_rpm_is_flagged(self):
        s=simulate(Config(rpm=3000,duration=2),False)["summary"]
        self.assertGreater(s["max_g"],100)
        self.assertEqual(s["screening"],"MECHANICALLY UNSAFE")

class ApiTests(unittest.TestCase):
    def test_validation_and_defaults(self):
        client=TestClient(app)
        self.assertEqual(client.get("/api/defaults").json()["rpm"],600)
        self.assertEqual(client.post("/api/jobs",json={"config":{"rpm":-2}}).status_code,422)
        self.assertEqual(client.get("/api/jobs/nonexistent").status_code,404)
        self.assertEqual(client.get("/api/example").json()["mode"],"B")
        import json
        json.dumps(clean(simulate(Config(duration=2),False)),allow_nan=False)

if __name__=="__main__":unittest.main()

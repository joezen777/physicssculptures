"""Supported tilt control using only internal collar and rotor motors."""
import math
import numpy as np
import mujoco

def steering_config(**changes):
    from gyro_sim import Config
    from dataclasses import replace
    return replace(Config(mode="pivot", startup="coast", steering=True,
                   latch=False, ring_rpm=3, rotor_rpm=3000, alternating=True,
                   rod_length=.04, dt=.0005), **changes)

def control(m,d,c):
    # Ball-joint velocities are expressed in the rotating ring frame.
    R = d.body("ring").xmat.reshape(3,3)
    target = np.array([math.tan(math.radians(c.steer_x_deg)),
                       math.tan(math.radians(c.steer_y_deg)),1.])
    target /= np.linalg.norm(target)
    error = R.T @ np.cross(R[:,2],target)
    omega = d.joint("base").qvel
    # Allocate desired reaction torque through the spinning rotors' gimbal rates.
    requested = 4*error-2*np.array([omega[0],omega[1],0.])
    pivot=d.xanchor[m.joint("base").id]
    gravity_torque=np.cross(d.subtree_com[1]-pivot,np.array([0.,0.,-m.body_subtreemass[1]*c.gravity]))
    requested -= R.T@gravity_torque
    J = []
    angles = []
    for j in range(4):
        spin = d.joint(f"spin{j}")
        sign = -1 if c.alternating and j%2 else 1
        d.actuator(f"rotor_motor{j}").ctrl[0] = np.clip(.15*(sign*c.rotor_rpm*2*math.pi/60-spin.qvel[0]),-1,1)
        q = d.joint(f"tilt{j}").qpos[0]
        angles.append(q)
        a = j*math.pi/2
        H = .5*c.rotor_mass*c.rotor_radius**2*spin.qvel[0]
        J.append(-H*np.array([math.cos(a)*math.cos(q),math.sin(a)*math.cos(q),-math.sin(q)]))
    J = np.array(J).T
    rates = J.T@np.linalg.solve(J@J.T+.01*np.eye(3),requested)
    accelerations=[]
    for j in range(4):
        q = d.joint(f"tilt{j}")
        rate = np.clip(rates[j],-.7,.7)
        if abs(angles[j])>math.radians(65) and rate*angles[j]>0:
            rate=0.
        accelerations.append(30*(rate-q.qvel[0]))
    M=np.zeros((m.nv,m.nv))
    mujoco.mj_fullM(m,d,M)
    inv=np.linalg.inv(M)
    force=d.qfrc_passive.copy()-d.qfrc_bias
    for j in range(4):
        force[m.joint(f"spin{j}").dofadr[0]] += d.actuator(f"rotor_motor{j}").ctrl[0]
    ids=[m.joint(f"tilt{j}").dofadr[0] for j in range(4)]
    torques=np.linalg.solve(inv[np.ix_(ids,ids)],np.array(accelerations)-(inv@force)[ids])
    for j in range(4):
        d.actuator(f"tilt_motor{j}").ctrl[0]=np.clip(torques[j],-2,2)

if __name__ == "__main__":
    from gyro_sim import Experiment,advance,sample
    e=Experiment(steering_config())
    for i in range(20000):
        advance(e.model,e.data,e.c)
        if (i+1)%2000==0:
            r=sample(e.model,e.data,e.c)
            print({k:r[k] for k in ("time","steer_x_deg","steer_y_deg","tilt0_deg","tilt1_deg","support_up_N")},flush=True)

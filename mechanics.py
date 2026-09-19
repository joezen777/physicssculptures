"""Rigid-body geometry, joint stops and passive centrifugal latch."""
import math
import xml.etree.ElementTree as ET
import mujoco
import numpy as np


def el(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})


def mount_height(c):
    # A full +/-90 degree sweep leaves the entire rotor above the ring top.
    return c.rotor_radius + .045


def release_rpm(c):
    force = c.spring_preload + c.spring_k*c.pin_travel
    return 60/(2*math.pi)*math.sqrt(force/(c.pin_mass*(c.radius+.035+c.pin_travel)))


def make_model(c):
    c.validate()
    root = ET.Element("mujoco", model=f"{c.joint_type} / {c.rotor_type} laboratory")
    el(root, "compiler", angle="radian")
    option = el(root, "option", timestep=c.dt, gravity=f"0 0 {-c.gravity}", integrator="RK4")
    el(option, "flag", energy="enable")
    defaults = el(root, "default")
    el(defaults, "geom", contype="1" if c.collisions else "0",
       conaffinity="1" if c.collisions else "0", rgba=".2 .65 .75 1",
       friction=".3 .005 .0001", solref=".004 1")
    el(defaults, "joint", damping="0", armature="0", solreflimit=".002 1",
       solimplimit=".99 .999 .0001")
    visual = el(root, "visual")
    el(visual, "global", offwidth="960", offheight="720")
    world = el(root, "worldbody")
    el(world, "light", pos="0 -2 4", dir="0 .3 -1")
    el(world, "geom", type="plane", size="4 4 .1", rgba=".12 .15 .2 1",
       contype="0", conaffinity="0")
    ring = el(world, "body", name="ring", pos="0 0 1")
    if c.mode == "free":
        el(ring, "freejoint", name="base")
    else:
        el(ring, "joint", name="base", type="hinge", axis="0 0 1")
        el(world, "geom", type="cylinder", pos="0 0 .5", size=".025 .5",
           rgba=".3 .36 .43 1", contype="0", conaffinity="0")
    ri, ro, height = .84*c.radius, 1.10*c.radius, .035
    iz = .5*c.ring_mass*(ri*ri+ro*ro)
    ix = c.ring_mass*(3*(ri*ri+ro*ro)+height*height)/12
    el(ring, "inertial", pos="0 0 0", mass=c.ring_mass, diaginertia=f"{ix} {ix} {iz}")
    for j in range(64):
        a, b = 2*math.pi*j/64, 2*math.pi*(j+1)/64
        el(ring, "geom", name=f"rim{j}", type="capsule",
           fromto=f"{c.radius*math.cos(a)} {c.radius*math.sin(a)} 0 "
                  f"{c.radius*math.cos(b)} {c.radius*math.sin(b)} 0",
           size=".022", rgba=".13 .57 .64 1")
    # Braces are halfway between joints and below their swept plane.
    for j in range(4):
        a = j*math.pi/2+math.pi/4
        el(ring, "geom", name=f"brace{j}", type="capsule",
           fromto=f"0 0 -.035 {c.radius*math.cos(a)} {c.radius*math.sin(a)} -.035",
           size=".009", rgba=".3 .4 .45 1")
    el(ring, "site", name="support", size=".008")
    equalities = el(root, "equality")
    if c.startup == "staged":
        el(equalities, "joint", name="ring_hold", joint1="base",
           polycoef="0 0 0 0 0", solref=".002 1")
    tendons = el(root, "tendon")
    actuators = el(root, "actuator")
    if c.startup == "staged":
        el(actuators, "motor", name="ring_motor", joint="base",
           ctrllimited="true", ctrlrange="-20 20")
        for j in range(4):
            el(actuators, "motor", name=f"rotor_motor{j}", joint=f"spin{j}",
               ctrllimited="true", ctrlrange="-1 1")
    h = mount_height(c)
    colors = [".98 .65 .2 1", ".4 .75 1 1", ".98 .4 .4 1", ".65 .5 1 1"]
    for j in range(4):
        a = j*math.pi/2
        radial = np.array([math.cos(a), math.sin(a), 0])
        tangent = np.array([-math.sin(a), math.cos(a), 0])
        x, y = c.radius*radial[:2]
        el(ring, "geom", name=f"pedestal{j}", type="capsule",
           fromto=f"{x} {y} .022 {x} {y} {h-.018}", size=".011",
           rgba=".33 .4 .46 1", contype="0", conaffinity="0")
        rod = el(ring, "body", name=f"rod{j}", pos=f"{x} {y} {h}")
        if c.joint_type == "collar":
            attrs = dict(name=f"tilt{j}", type="hinge",
                         axis=" ".join(map(str, tangent)))
            if c.joint_limits:
                attrs.update(limited="true", range=f"{-math.pi/2} {math.pi/2}", margin=".003")
            el(rod, "joint", **attrs)
            # Annular collar in the radial/vertical plane; axle is tangent.
            for k in range(20):
                u, v = 2*math.pi*k/20, 2*math.pi*(k+1)/20
                p = .027*(radial*math.cos(u)+np.array([0,0,math.sin(u)]))
                q = .027*(radial*math.cos(v)+np.array([0,0,math.sin(v)]))
                el(rod, "geom", type="capsule",
                   fromto=" ".join(map(str, [*p,*q])), size=".005",
                   rgba=".68 .75 .78 1", contype="0", conaffinity="0")
            el(ring, "geom", type="capsule",
               fromto=" ".join(map(str, [x-.035*tangent[0],y-.035*tangent[1],h,
                                        x+.035*tangent[0],y+.035*tangent[1],h])),
               size=".007", rgba=".82 .85 .87 1", contype="0", conaffinity="0")
        else:
            el(rod, "joint", name=f"ball{j}", type="ball")
            el(rod, "geom", type="sphere", size=".024", rgba=".75 .8 .84 1",
               contype="0", conaffinity="0")
        length, radius = c.rod_length, .008
        ix = c.rod_mass*(3*radius*radius+length*length)/12
        iz = .5*c.rod_mass*radius*radius
        el(rod, "inertial", pos=f"0 0 {length/2}", mass=c.rod_mass,
           diaginertia=f"{ix} {ix} {iz}")
        el(rod, "geom", name=f"shaft{j}", type="capsule",
           fromto=f"0 0 0 0 0 {length}", size=radius, rgba=".8 .84 .87 1")
        if c.joint_type == "ball" and c.joint_limits:
            # Distance stop constrains tilt, not twist: |tip-anchor| <= sqrt(2)*L.
            el(ring, "site", name=f"up{j}", pos=f"{x} {y} {h+length}",
               size=".001", rgba="0 0 0 0")
            el(rod, "site", name=f"tip{j}", pos=f"0 0 {length}",
               size=".001", rgba="0 0 0 0")
            tendon = el(tendons, "spatial", name=f"hemisphere{j}", limited="true",
                        range=f"0 {math.sqrt(2)*length}", margin=".006",
                        solreflimit=".0006 1", solimplimit=".99 .999 .0001",
                        width=".001", rgba="0 0 0 0")
            el(tendon, "site", site=f"up{j}")
            el(tendon, "site", site=f"tip{j}")
        rotor = el(rod, "body", name=f"rotor{j}", pos=f"0 0 {length}")
        el(rotor, "joint", name=f"spin{j}", type="hinge", axis="0 0 1")
        if c.rotor_type == "flywheel":
            thickness = .018
            iz = .5*c.rotor_mass*c.rotor_radius**2
            ix = c.rotor_mass*(3*c.rotor_radius**2+thickness**2)/12
            el(rotor, "inertial", pos="0 0 0", mass=c.rotor_mass,
               diaginertia=f"{ix} {ix} {iz}")
            el(rotor, "geom", name=f"disk{j}", type="cylinder",
               size=f"{c.rotor_radius} {thickness/2}", rgba=colors[j])
            el(rotor, "geom", type="box", pos=f"{c.rotor_radius/2} 0 .011",
               size=f"{c.rotor_radius/2} .006 .002", rgba=".1 .13 .16 1",
               contype="0", conaffinity="0")
        else:
            width, thickness = .025, .008
            ix = c.rotor_mass*(width*width+thickness*thickness)/12
            iy = c.rotor_mass*(4*c.rotor_radius**2+thickness*thickness)/12
            iz = c.rotor_mass*(4*c.rotor_radius**2+width*width)/12
            el(rotor, "inertial", pos="0 0 0", mass=c.rotor_mass,
               diaginertia=f"{ix} {iy} {iz}")
            el(rotor, "geom", name=f"propeller{j}", type="box",
               size=f"{c.rotor_radius} {width/2} {thickness/2}", rgba=colors[j])
            el(rotor, "geom", type="cylinder", size=".018 .012",
               rgba=".65 .71 .75 1", contype="0", conaffinity="0")
        if c.latch or c.startup == "staged":
            # Latch holds UPRIGHT, regardless of configured free initial tilt.
            theta = 0 if c.latch else math.radians(c.tilt_deg)
            quat = (math.cos(theta/2), *list(tangent*math.sin(theta/2)))
            el(equalities, "weld", name=f"rod_hold{j}", body1="ring", body2=f"rod{j}",
               relpose=" ".join(map(str, [x,y,h,*quat])), solref=".002 1",
               solimp=".99 .999 .0001")
        if c.latch:
            # Slider's inertia experiences the actual acceleration of the rotating ring.
            pin = el(ring, "body", name=f"pin{j}",
                     pos=f"{(c.radius+.035)*radial[0]} {(c.radius+.035)*radial[1]} {h}")
            el(pin, "inertial", pos="0 0 0", mass=c.pin_mass, diaginertia=".000001 .000001 .000001")
            el(pin, "joint", name=f"pin_slide{j}", type="slide",
               axis=" ".join(map(str,radial)), limited="true",
               range=f"0 {max(.012, c.pin_travel*2)}",
               stiffness=c.spring_k, springref=-c.spring_preload/c.spring_k,
               damping=".025")
            el(pin, "geom", name=f"pin_geom{j}", type="capsule",
               fromto=" ".join(map(str,[*(-.035*radial), *(.006*radial)])),
               size=".0045", mass=c.pin_mass, rgba="1 .75 .25 1",
               contype="0", conaffinity="0")
    if c.mode == "supported":
        sensors = el(root, "sensor")
        el(sensors, "force", name="support_force", site="support")
    xml=ET.tostring(root, encoding="unicode")
    return mujoco.MjModel.from_xml_string(xml), xml

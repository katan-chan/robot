"""Dựng mujoco.MjSpec từ build/model/ (robot.json + meshes, xuất từ Blender) và TOML vật lý.
Khối lượng gán vào geom, quán tính và vị trí chân do MuJoCo tính (13.2)."""
import json
from pathlib import Path

import mujoco
import numpy as np

from spider.model.config import JOINT_KINDS, Physics, Servo, load_physics, load_servos
from spider.sim.scene import add_scene

LEGS = ("fl", "fr", "rl", "rr")
ACTUATORS = [f"{leg}_{kind}" for leg in LEGS for kind in JOINT_KINDS]
G = mujoco.mjtGeom
ON = mujoco.mjtLimited.mjLIMITED_TRUE


def _bbox(obj: Path):
    v = np.array([l.split()[1:4] for l in obj.read_text().splitlines() if l.startswith("v ")], float)
    return v.min(axis=0), v.max(axis=0)


def _add_keys(spec: mujoco.MjSpec, physics: Physics, foot_radius: float):
    """home: mọi khớp 0; stand: theo physics.stand. Dời z thân để bàn chân thấp nhất chạm sàn."""
    m = spec.compile()
    d = mujoco.MjData(m)
    for name, angle in (("home", dict.fromkeys(JOINT_KINDS, 0.0)), ("stand", physics.stand)):
        ctrl = [angle[a.split("_", 1)[1]] for a in ACTUATORS]
        d.qpos[:] = m.qpos0
        for a, q in zip(ACTUATORS, ctrl):
            d.qpos[m.joint(a).qposadr[0]] = q
        mujoco.mj_kinematics(m, d)
        lowest = min(d.site(f"{leg}_foot").xpos[2] for leg in LEGS)
        d.qpos[2] += foot_radius - lowest
        spec.add_key(name=name, qpos=d.qpos.tolist(), ctrl=ctrl)


def build_spec(export_dir: Path = Path("build/model"), physics: Physics | None = None,
               servos: dict[str, Servo] | None = None) -> mujoco.MjSpec:
    export_dir = Path(export_dir).resolve()
    physics = physics or load_physics()
    servos = servos or load_servos()
    robot = json.loads((export_dir / "robot.json").read_text())
    drives = {l["joint"]["name"]: servos[l["servo"]] for l in robot["links"] if l["joint"]}
    density = physics.density * physics.fill

    spec = mujoco.MjSpec()
    add_scene(spec)
    bodies = {None: spec.worldbody}

    def mesh(item):
        spec.add_mesh(name=item["name"], file=str(export_dir / item["mesh"]))
        return item["name"]

    for l in robot["links"]:                     # cha đứng trước con
        b = bodies[l["parent"]].add_body(name=l["name"], pos=l["pos"], quat=l["quat"])
        bodies[l["name"]] = b
        b.add_geom(name=f"{l['name']}_mesh", type=G.mjGEOM_MESH, meshname=mesh(l),
                   density=density, contype=0, conaffinity=0)
        for s in l["servos_on_body"]:
            b.add_geom(name=s["name"], type=G.mjGEOM_MESH, meshname=mesh(s), pos=s["pos"], quat=s["quat"],
                       mass=drives[s["drives"]].mass, contype=0, conaffinity=0)
        j = l["joint"]
        if j is None:
            b.add_freejoint(name="root")
            lo, hi = _bbox(export_dir / l["mesh"])
            b.add_geom(name="torso_geom", type=G.mjGEOM_BOX, pos=(lo + hi) / 2, size=(hi - lo) / 2,
                       mass=physics.torso_extra_mass, contype=1, conaffinity=0)
        else:
            sv = drives[j["name"]]
            b.add_joint(name=j["name"], type=mujoco.mjtJoint.mjJNT_HINGE, axis=j["axis"], range=j["range"],
                        limited=ON, armature=sv.armature, damping=sv.damping, frictionloss=sv.frictionloss)
        if f := l["foot"]:
            foot_radius = f["radius"]
            b.add_geom(name=f"{f['name']}_geom", type=G.mjGEOM_SPHERE, size=[f["radius"], 0, 0], pos=f["pos"],
                       density=density, friction=[physics.foot_friction, 0.005, 0.0001], condim=3,
                       contype=1, conaffinity=0)
            b.add_site(name=f["name"], pos=f["pos"])

    for name in ACTUATORS:
        sv, j = drives[name], spec.joint(name)
        a = spec.add_actuator(name=name, target=name, trntype=mujoco.mjtTrn.mjTRN_JOINT)
        a.set_to_position(kp=sv.stall_torque / physics.kp_error, dampratio=physics.dampratio)
        a.forcelimited, a.forcerange = ON, [-sv.stall_torque, sv.stall_torque]
        a.ctrllimited, a.ctrlrange = ON, list(j.range)

    _add_keys(spec, physics, foot_radius)
    return spec


def build_model(export_dir: Path = Path("build/model"), physics: Physics | None = None,
                servos: dict[str, Servo] | None = None) -> mujoco.MjModel:
    return build_spec(export_dir, physics, servos).compile()

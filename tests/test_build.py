import json, math, subprocess
from pathlib import Path

import mujoco
import numpy as np
import pytest

from spider.model.build import ACTUATORS, build_model

ROOT = Path(__file__).resolve().parent.parent


def blender(*args):
    p = subprocess.run([str(ROOT / "tools/blender"), *args], cwd=ROOT, capture_output=True, text=True)
    r = json.loads(p.stdout)
    assert p.returncode == 0 and r["ok"], r
    return r


def build_and_export(d: Path, *extra) -> Path:
    blend, out = d / "s.blend", d / "model"
    blender("build", "--out", str(blend), *extra)
    blender("export", "--blend", str(blend), "--out", str(out))
    return out


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    return build_and_export(tmp_path_factory.mktemp("export"))


@pytest.fixture(scope="module")
def inspected(exported):
    return blender("inspect", "--blend", str(exported.parent / "s.blend"))


def test_export_writes_robot_json_and_meshes(exported):
    r = json.loads((exported / "robot.json").read_text())
    assert r["format"] == 1 and len(r["links"]) == 13
    assert all((exported / l["mesh"]).is_file() for l in r["links"])


def test_export_refuses_invalid_model(tmp_path):
    b = tmp_path / "s.blend"
    blender("build", "--out", str(b))
    blender("exec", "--blend", str(b), "--expr", 'bpy.data.objects["fl_femur"].scale = (2, 2, 2)')
    p = subprocess.run([str(ROOT / "tools/blender"), "export", "--blend", str(b), "--out", str(tmp_path / "m")],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 1 and not (tmp_path / "m").exists()


def test_compiles_with_12_named_position_servos(exported):     # check:mjcf-compiles
    m = build_model(exported)
    assert [m.actuator(i).name for i in range(m.nu)] == ACTUATORS and m.nbody == 14 and m.njnt == 13


def test_total_mass_in_budget(exported):                       # 9.5
    assert 0.25 <= mujoco.mj_getTotalmass(build_model(exported)) <= 0.35


def test_actuator_limits_follow_servo(exported):               # 9.1, 12.7
    m = build_model(exported)
    assert np.allclose(m.actuator("fl_knee").forcerange, [-0.177, 0.177]) and m.joint("fl_knee").armature == 2e-4


def test_knee_override_in_blender_changes_only_knees(tmp_path, exported):  # Review Focus 3
    base, m = build_model(exported), build_model(build_and_export(tmp_path, "--servo", "knee=MG996R"))
    for leg in ("fl", "fr", "rl", "rr"):
        assert np.allclose(m.actuator(f"{leg}_knee").forcerange, [-0.92, 0.92])
        assert np.allclose(m.actuator(f"{leg}_hip_pitch").forcerange, [-0.177, 0.177])
        assert np.allclose(m.actuator(f"{leg}_hip_yaw").forcerange, [-0.177, 0.177])
    assert math.isclose(mujoco.mj_getTotalmass(m) - mujoco.mj_getTotalmass(base), 4 * (0.055 - 0.0134), abs_tol=1e-9)


def test_only_feet_and_torso_touch_floor(exported):            # 9.3
    m = build_model(exported); floor = m.geom("floor").id
    for g in range(m.ngeom):
        name = m.geom(g).name
        assert bool(m.geom_contype[g] & m.geom_conaffinity[floor]) == (name == "torso_geom" or name.endswith("_foot_geom"))


def test_feet_match_blender_at_home(exported, inspected):      # Review Focus 4
    m = build_model(exported); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("home").id); mujoco.mj_kinematics(m, d)
    for leg in ("fl", "fr", "rl", "rr"):
        got = d.site(f"{leg}_foot").xpos - d.body("torso").xpos
        want = np.subtract(inspected["feet"][f"{leg}_foot"], inspected["feet"]["torso_origin"])
        assert np.allclose(got, want, atol=1e-6)


def test_stand_keyframe_feet_on_floor(exported):               # Review Focus 5
    m = build_model(exported); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id); mujoco.mj_kinematics(m, d)
    lowest = min(d.site(f"{l}_foot").xpos[2] for l in ("fl", "fr", "rl", "rr"))
    assert abs(lowest - m.geom("fl_foot_geom").size[0]) < 1e-4
    assert np.allclose(d.ctrl, m.key("stand").qpos[7:])

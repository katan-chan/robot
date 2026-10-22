import json, math, shutil, subprocess
from pathlib import Path

import mujoco
import numpy as np
import pytest

from spider.model.build import ACTUATORS, build_model
from spider.model.config import load_physics, load_servos

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVO = {"hip_yaw": "DS3235", "hip_pitch": "DS3240", "knee": "DS3235"}   # 19.4


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


def test_export_replaces_output_dir(exported, tmp_path):
    out = tmp_path / "m"
    blender("export", "--blend", str(exported.parent / "s.blend"), "--out", str(out))
    (out / "meshes/old_name.obj").write_text("stale")
    blender("export", "--blend", str(exported.parent / "s.blend"), "--out", str(out))
    assert not (out / "meshes/old_name.obj").exists() and (out / "robot.json").is_file()
    assert [p.name for p in tmp_path.iterdir()] == ["m"]          # không để lại thư mục tạm


def test_export_refuses_non_export_dir(exported, tmp_path):
    (tmp_path / "keep.txt").write_text("x")                        # thư mục có dữ liệu khác, không có robot.json
    p = subprocess.run([str(ROOT / "tools/blender"), "export", "--blend", str(exported.parent / "s.blend"),
                        "--out", str(tmp_path)], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 1 and json.loads(p.stdout)["errors"][0]["check"] == "out"
    assert [x.name for x in tmp_path.iterdir()] == ["keep.txt"]


def test_compiles_with_12_named_position_servos(exported):     # check:mjcf-compiles
    m = build_model(exported)
    assert [m.actuator(i).name for i in range(m.nu)] == [
        "fl_hip_yaw", "fl_hip_pitch", "fl_knee", "fr_hip_yaw", "fr_hip_pitch", "fr_knee",
        "rl_hip_yaw", "rl_hip_pitch", "rl_knee", "rr_hip_yaw", "rr_hip_pitch", "rr_knee"]
    assert ACTUATORS == [m.actuator(i).name for i in range(m.nu)] and m.nbody == 14 and m.njnt == 13


def test_actuators_and_joints_follow_config(exported):        # 9.1, 13.4
    m, servos, ph = build_model(exported), load_servos(), load_physics()
    for i in range(m.nu):
        a = m.actuator(i); j = m.joint(a.name); dof = j.dofadr[0]
        sv = servos[DEFAULT_SERVO[a.name.split("_", 1)[1]]]
        assert a.gainprm[0] == pytest.approx(sv.stall_torque / ph.kp_error)
        assert np.allclose(a.ctrlrange, j.range)
        assert (m.dof_damping[dof], m.dof_frictionloss[dof], m.dof_armature[dof]) == pytest.approx(
            (sv.damping, sv.frictionloss, sv.armature))
    for leg in ("fl", "fr", "rl", "rr"):
        g = m.geom(f"{leg}_foot_geom")
        assert g.friction[0] == pytest.approx(0.9) and g.condim[0] == 3


def test_default_export_dir_must_match_source_blend(exported, tmp_path, monkeypatch):
    import spider.model.build as b
    assert b.DEFAULT_EXPORT == ROOT / "build/model" and b.SOURCE_BLEND == ROOT / "models/spider.blend"  # không theo cwd
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(b, "DEFAULT_EXPORT", exported)
    monkeypatch.setattr(b, "SOURCE_BLEND", exported.parent / "s.blend")
    assert b.build_model().nu == 12                                 # khớp nguồn
    (tmp_path / "edited.blend").write_bytes(b"sua sau khi export")
    monkeypatch.setattr(b, "SOURCE_BLEND", tmp_path / "edited.blend")
    with pytest.raises(ValueError, match="tools/blender export"):
        b.build_model()


def test_total_mass_in_budget(exported):                       # 9.5
    assert 0.25 <= mujoco.mj_getTotalmass(build_model(exported)) <= 0.35


def test_actuator_limits_follow_servo(exported):               # 9.1, 12.7
    m = build_model(exported)
    assert np.allclose(m.actuator("fl_knee").forcerange, [-3.4, 3.4]) and m.joint("fl_knee").armature == 5e-3
    assert np.allclose(m.actuator("fl_hip_pitch").forcerange, [-3.92, 3.92])


def test_knee_override_in_blender_changes_only_knees(tmp_path, exported):  # Review Focus 3
    base, m = build_model(exported), build_model(build_and_export(tmp_path, "--servo", "knee=MG996R"))
    for leg in ("fl", "fr", "rl", "rr"):
        assert np.allclose(m.actuator(f"{leg}_knee").forcerange, [-0.92, 0.92])
        assert np.allclose(m.actuator(f"{leg}_hip_pitch").forcerange, [-3.92, 3.92])
        assert np.allclose(m.actuator(f"{leg}_hip_yaw").forcerange, [-3.4, 3.4])
    assert math.isclose(mujoco.mj_getTotalmass(m) - mujoco.mj_getTotalmass(base), 4 * (0.055 - 0.065), abs_tol=1e-9)


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


def test_stand_uses_each_foot_radius(exported, tmp_path):
    out = tmp_path / "model"; shutil.copytree(exported, out)
    r = json.loads((out / "robot.json").read_text())
    next(l for l in r["links"] if l["name"] == "fl_tibia")["foot"]["radius"] = 0.02   # fl to hơn, các chân khác 0.012
    (out / "robot.json").write_text(json.dumps(r))
    m = build_model(out); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id); mujoco.mj_kinematics(m, d)
    bottoms = [d.site(f"{l}_foot").xpos[2] - m.geom(f"{l}_foot_geom").size[0] for l in ("fl", "fr", "rl", "rr")]
    assert abs(min(bottoms)) < 1e-9

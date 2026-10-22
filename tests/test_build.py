import json, math, shutil, subprocess
from dataclasses import replace
from pathlib import Path

import mujoco
import numpy as np
import pytest

from spider.model.build import ACTUATORS, LEGS, build_model
from spider.model.config import JOINT_KINDS, load_physics, load_servos

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


def unloaded(exported):
    return build_model(exported, replace(load_physics(), payload_mass=0.0))


def test_total_mass_in_budget(exported):                       # 19.7
    assert 1.10 <= mujoco.mj_getTotalmass(unloaded(exported)) <= 1.45
    assert mujoco.mj_getTotalmass(build_model(exported)) <= 3.5


def test_payload_geom(exported):                               # 19.6
    m, bare = build_model(exported), unloaded(exported)
    g = m.geom("payload_geom")
    assert g.bodyid[0] == m.body("torso").id and g.contype[0] == 0 and g.conaffinity[0] == 0
    assert np.allclose(g.size, [0.075, 0.06, 0.025])
    top = m.geom("torso_geom").pos[2] + m.geom("torso_geom").size[2]
    assert np.allclose(g.pos, [*m.geom("torso_geom").pos[:2], top + 0.025])   # giữa mặt trên thân
    assert math.isclose(mujoco.mj_getTotalmass(m) - mujoco.mj_getTotalmass(bare), 2.0, abs_tol=1e-9)
    assert "payload_geom" not in [bare.geom(i).name for i in range(bare.ngeom)]


def test_stand_with_payload_holds(exported):                   # 19.1/stand, 10.5: không nới 50%
    m = build_model(exported); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id)
    torso, floor, peak = m.geom("torso_geom").id, m.geom("floor").id, np.zeros(m.nu)
    while d.time < 1.0:
        mujoco.mj_step(m, d)
        peak = np.maximum(peak, np.abs(d.actuator_force) / m.actuator_forcerange[:, 1])
        assert not any({c.geom1, c.geom2} == {torso, floor} for c in d.contact[:d.ncon]), d.time
    assert peak.max() < 0.5, dict(zip(ACTUATORS, peak.round(3)))


def _ik(m, qpos, targets):
    """Bình phương tối thiểu có giảm chấn trên Jacobian của MuJoCo (mj_jacSite): chỉnh 3 khớp mỗi chân để
    site bàn chân tới đích (khung thế giới); thân giữ nguyên ở qpos. Trả về (ctrl, sai số lớn nhất m)."""
    d, jac = mujoco.MjData(m), np.zeros((3, m.nv))
    d.qpos[:] = qpos
    for _ in range(200):
        mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)
        err = 0.0
        for leg, t in targets.items():
            e = t - d.site(f"{leg}_foot").xpos
            err = max(err, float(np.linalg.norm(e)))
            mujoco.mj_jacSite(m, d, jac, None, m.site(f"{leg}_foot").id)
            js = [m.joint(f"{leg}_{k}") for k in JOINT_KINDS]
            J = jac[:, [j.dofadr[0] for j in js]]
            for j, dq in zip(js, J.T @ np.linalg.solve(J @ J.T + 1e-6 * np.eye(3), e)):
                d.qpos[j.qposadr[0]] = np.clip(d.qpos[j.qposadr[0]] + dq, *j.range)
        if err < 1e-7:
            break
    return np.array([d.qpos[m.joint(a).qposadr[0]] for a in ACTUATORS]), err


def three_leg_ratios(m, lift, h=0.04):
    """Đứng 3 chân tĩnh (cách đo của probe da08237): dời thân ngang về tâm nội tiếp tam giác 3 chân đứng,
    rồi nhấc chân `lift` lên h (lệnh). Ramp 1 s + giữ 1 s, ramp nhấc 0.5 s + giữ 1.5 s. Ở tư thế đã lắng,
    mj_inverse với qvel = qacc = 0 cho mô-men tĩnh; trả về {actuator: |qfrc_inverse| / stall} và MjData."""
    key, d = m.key("stand"), mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, key.id); mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d)
    feet = {leg: d.site(f"{leg}_foot").xpos.copy() for leg in LEGS}
    A, B, C = (feet[leg][:2] for leg in LEGS if leg != lift)
    w = np.linalg.norm([B - C, C - A, A - B], axis=1)
    inc = (w[0] * A + w[1] * B + w[2] * C) / w.sum()                 # tâm nội tiếp (hình học)
    for alpha in np.arange(1.0, 0.0, -0.05):                       # dời xa nhất mà chân còn với tới
        q = key.qpos.copy(); q[:2] += alpha * (inc - d.subtree_com[m.body("torso").id][:2])
        (plant, e1), (up, e2) = _ik(m, q, feet), _ik(m, q, {**feet, lift: feet[lift] + [0, 0, h]})
        if max(e1, e2) < 1e-4:
            break
    assert max(e1, e2) < 1e-4, (lift, e1, e2)
    mujoco.mj_resetDataKeyframe(m, d, key.id)
    for c1, ramp, hold in ((plant, 1.0, 1.0), (up, 0.5, 1.5)):
        c0, t0 = d.ctrl.copy(), d.time
        while d.time < t0 + ramp + hold:
            d.ctrl[:] = c0 + (c1 - c0) * min(1.0, (d.time - t0) / ramp)
            mujoco.mj_step(m, d)
    assert np.abs(d.qvel).max() < 1e-3, (lift, np.abs(d.qvel).max())   # đã lắng
    d.qvel[:] = 0; d.qacc[:] = 0
    mujoco.mj_inverse(m, d)
    dof = [m.joint(a).dofadr[0] for a in ACTUATORS]
    return dict(zip(ACTUATORS, np.abs(d.qfrc_inverse[dof]) / m.actuator_forcerange[:, 1])), d


def test_three_leg_static_with_payload(exported):             # 19.8, 10.5: không nới 50%
    m = build_model(exported)
    assert m.geom("payload_geom").id >= 0                       # có tải 2 kg, không qua được khi không tải
    floor, torso = m.geom("floor").id, m.geom("torso_geom").id
    for lift in LEGS:
        r, d = three_leg_ratios(m, lift)
        touching = {g for c in d.contact[:d.ncon] if floor in (c.geom1, c.geom2) for g in (c.geom1, c.geom2)}
        assert m.geom(f"{lift}_foot_geom").id not in touching and torso not in touching, lift
        assert max(r.values()) <= 0.5, (lift, {k: round(v, 3) for k, v in r.items()})


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

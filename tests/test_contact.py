import mujoco
import numpy as np
import pytest

from spider.model.build import LEGS, build_model
from spider.model.config import load_physics
from tests.test_build import build_and_export


@pytest.fixture(scope="module")
def model(tmp_path_factory):
    return build_model(build_and_export(tmp_path_factory.mktemp("contact")))


def settled(m, seconds=1.0):
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id)
    while d.time < seconds:
        mujoco.mj_step(m, d)
    return d


def test_foot_friction_applies_at_floor_contact(model):     # BUG-001, Review Focus 1
    d, floor = settled(model), model.geom("floor").id
    feet = {model.geom(f"{leg}_foot_geom").id for leg in LEGS}
    pairs = [c for c in d.contact[:d.ncon] if {c.geom1, c.geom2} & feet and floor in (c.geom1, c.geom2)]
    assert len(pairs) == 4
    assert all(c.friction[0] == pytest.approx(load_physics().foot_friction) for c in pairs)


def push_slip(m, d0, deg, ramp=0.5, total=2.0):
    """Lực ngang lên thân theo hướng deg, tăng tuyến tính 0 → 0.5·μ·m·g trong `ramp` s rồi giữ, tổng `total` s.
    Trả về độ dời xy lớn nhất của bàn chân (m), so với trước khi đẩy."""
    d = mujoco.MjData(m); mujoco.mj_copyData(d, m, d0)
    p0 = {leg: d.site(f"{leg}_foot").xpos.copy() for leg in LEGS}
    full = 0.5 * load_physics().foot_friction * mujoco.mj_getTotalmass(m) * -m.opt.gravity[2]
    u, t0, torso = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0]), d.time, m.body("torso").id
    while d.time < t0 + total:
        d.xfrc_applied[torso, :3] = full * min(1.0, (d.time - t0) / ramp) * u
        mujoco.mj_step(m, d)
    return max(float(np.linalg.norm((d.site(f"{leg}_foot").xpos - p0[leg])[:2])) for leg in LEGS)


def test_feet_hold_under_half_friction_limit(model):     # BUG-002, Review Focus 2
    # Mọi hướng 0°, 15°, …, 345°; lực tăng dần 0.5 s rồi giữ 1.5 s (tổng 2 s đẩy). Đẩy đột ngột theo đường chéo
    # làm một chân trượt ≈ 0.7 mm một lần (quá độ, không phải bò), xem scene.py.
    d0 = settled(model)
    slip = {deg: push_slip(model, d0, deg) for deg in range(0, 360, 15)}
    assert max(slip.values()) < 0.5e-3, {k: round(v * 1e3, 3) for k, v in slip.items()}

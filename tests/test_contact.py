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


@pytest.mark.parametrize("axis", [0, 1])
def test_feet_hold_under_half_friction_limit(model, axis):  # BUG-002, Review Focus 2
    d = settled(model)
    p0 = {leg: d.site(f"{leg}_foot").xpos.copy() for leg in LEGS}
    weight = mujoco.mj_getTotalmass(model) * -model.opt.gravity[2]
    d.xfrc_applied[model.body("torso").id, axis] = 0.5 * load_physics().foot_friction * weight
    t0 = d.time
    while d.time < t0 + 2.0:
        mujoco.mj_step(model, d)
    slip = {leg: float(np.linalg.norm((d.site(f"{leg}_foot").xpos - p0[leg])[:2])) for leg in LEGS}
    assert max(slip.values()) < 0.5e-3, slip

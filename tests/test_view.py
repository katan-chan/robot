import mujoco
import numpy as np
import pytest
from PIL import Image

from spider.model.build import build_model
from spider.model.parts import parts_markdown, parts_table
from spider.sim.view import snapshot
from tests.test_build import blender, build_and_export


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    return build_and_export(tmp_path_factory.mktemp("view"))


@pytest.fixture(scope="module")
def model(exported):
    return build_model(exported)


def test_parts_table(model, exported):
    rows = parts_table(model, exported)
    assert len(rows) == 13
    assert sum(r["mass_g"] for r in rows) == pytest.approx(mujoco.mj_getTotalmass(model) * 1000)
    t = next(r for r in rows if r["body"] == "fl_tibia")
    assert t["joint"] == "fl_knee" and t["servo"] == "MG90S" and t["parent"] == "fl_femur"
    assert t["range_deg"] == pytest.approx((-30, 150))
    assert "Tổng" in parts_markdown(model, exported)


def _check(paths):
    assert len(paths) == 4
    for p in paths:
        assert np.asarray(Image.open(p)).std() > 5, p


def test_snapshot(model, tmp_path):
    _check(snapshot(model, tmp_path))


def test_blender_render(exported, tmp_path):
    blender("render", "--blend", str(exported.parent / "s.blend"), "--out", str(tmp_path), "--views", "front,side,top,iso")
    _check(sorted(tmp_path.glob("*.png")))

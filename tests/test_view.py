import itertools
import json
import subprocess

import mujoco
import numpy as np
import pytest
from PIL import Image

from spider.model.build import build_model
from spider.model.parts import parts_markdown, parts_table
from spider.sim.view import camera, orbit_video, snapshot
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
    assert t["joint"] == "fl_knee" and t["servo"] == "DS3235" and t["parent"] == "fl_femur"
    assert t["range_deg"] == pytest.approx((-30, 150))
    assert "Tổng" in parts_markdown(model, exported)


def _check(paths):
    assert len(paths) == 4
    imgs = [np.asarray(Image.open(p).convert("RGB"), float) for p in paths]
    for p, a in zip(paths, imgs):
        assert a.std() > 5, p
    for (p, a), (q, b) in itertools.combinations(zip(paths, imgs), 2):  # bốn góc nhìn phải khác nhau
        assert (np.abs(a - b).max(axis=-1) > 10).mean() > 0.005, (p, q)


def test_snapshot(model, tmp_path):
    _check(snapshot(model, tmp_path))


BLENDER_VIEWS = {"front": (1, 0, 0), "side": (0, 1, 0), "top": (0, 0, 1), "iso": (1, 1, 1)}  # blender/render_views.py


def test_snapshot_cameras_match_blender_views(model):
    d = mujoco.MjData(model); mujoco.mj_forward(model, d)
    with mujoco.Renderer(model, 48, 64) as r:
        for name, want in BLENDER_VIEWS.items():
            r.update_scene(d, camera(model, d, name))
            left, right = r.scene.camera[0], r.scene.camera[1]   # hai mắt stereo, lấy trung điểm
            eye = (np.array(left.pos) + right.pos) / 2 - d.body("torso").xpos
            cos = eye @ want / np.linalg.norm(eye) / np.linalg.norm(want)
            assert cos > np.cos(np.radians(10)), name  # cùng phía, lệch ≤ 10° (MuJoCo hạ camera 5° cho thấy sàn)
            if name == "top":
                assert left.up[1] > 0.99  # +y lên trên ảnh, như Blender


def test_blender_render(exported, tmp_path):
    blender("render", "--blend", str(exported.parent / "s.blend"), "--out", str(tmp_path), "--views", "front,side,top,iso")
    _check(sorted(tmp_path.glob("*.png")))


def _probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,width,height,nb_frames", "-of", "json", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"][0]


def test_orbit_video(model, tmp_path):
    p = orbit_video(model, tmp_path / "orbit.mp4", seconds=2, fps=15)
    s = _probe(p)
    assert (s["codec_name"], s["width"], s["height"]) == ("h264", 1280, 720)
    assert int(s["nb_frames"]) == 30
    assert p.stat().st_size < 10 * 1024 * 1024


def test_orbit_video_no_physics(model, tmp_path):
    # chỉ render: robot đứng yên, camera quay đúng 360°, nên khung đầu ≈ khung cuối (robot không đổ)
    frames = orbit_video(model, tmp_path / "o.mp4", seconds=1, fps=12, return_frames=True)[1]
    assert np.abs(frames[0].astype(float) - frames[-1].astype(float)).mean() < 8
    assert np.abs(frames[0].astype(float) - frames[len(frames) // 2].astype(float)).mean() > 8


def test_orbit_video_without_ffmpeg(model, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/nonexistent")
    with pytest.raises(RuntimeError, match="ffmpeg"):
        orbit_video(model, tmp_path / "x.mp4", seconds=1)
    assert not (tmp_path / "x.mp4").exists()

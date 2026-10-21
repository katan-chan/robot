"""Xem model trong MuJoCo: viewer tương tác, ảnh chụp 4 hướng, bảng thành phần (16.2, 16.3)."""
import argparse
from pathlib import Path

import mujoco
from PIL import Image

from spider.model.build import DEFAULT_EXPORT, build_model
from spider.model.parts import parts_markdown

# azimuth, elevation (độ). MuJoCo đặt camera ở lookat − distance·(cos el·cos az, cos el·sin az, sin el),
# nên az = hướng camera nhìn tới. Cùng phía với blender/render_views.py: front ở +x, side ở +y,
# top nhìn xuống (+y lên trên ảnh), iso ở (+1, +1, +1) (el = −asin(1/√3)).
VIEWS = {"front": (180, -5), "side": (-90, -5), "top": (90, -89), "iso": (-135, -35.26)}


def _data(m, keyframe):
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, keyframe))
    mujoco.mj_forward(m, d)
    return d


def camera(m: mujoco.MjModel, d: mujoco.MjData, view: str) -> mujoco.MjvCamera:
    cam = mujoco.MjvCamera()
    cam.lookat[:] = d.xpos[m.body("torso").id]
    cam.distance = 0.6
    cam.azimuth, cam.elevation = VIEWS[view]
    return cam


def snapshot(m: mujoco.MjModel, out_dir: Path, keyframe: str = "stand") -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    d = _data(m, keyframe)
    paths = []
    with mujoco.Renderer(m, 480, 640) as r:
        for name in VIEWS:
            r.update_scene(d, camera(m, d, name))
            paths.append(out_dir / f"{name}.png")
            Image.fromarray(r.render()).save(paths[-1])
    return paths


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--keyframe", default="stand", choices=["stand", "home"])
    p.add_argument("--snapshot", type=Path, metavar="DIR")
    p.add_argument("--parts", action="store_true")
    p.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT)
    a = p.parse_args()
    m = build_model(a.export_dir)
    if a.parts:
        print(parts_markdown(m, a.export_dir))
    if a.snapshot:
        print("\n".join(map(str, snapshot(m, a.snapshot, a.keyframe))))
    if not (a.parts or a.snapshot):
        import mujoco.viewer
        d = _data(m, a.keyframe)
        mujoco.viewer.launch(m, d)


if __name__ == "__main__":
    main()

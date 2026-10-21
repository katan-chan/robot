"""Xem model trong MuJoCo: viewer tương tác, ảnh chụp 4 hướng, bảng thành phần (16.2, 16.3)."""
import argparse
from pathlib import Path

import mujoco
from PIL import Image

from spider.model.build import build_model
from spider.model.parts import parts_markdown

VIEWS = {"front": (90, -5), "side": (180, -5), "top": (90, -89), "iso": (135, -30)}  # azimuth, elevation


def _data(m, keyframe):
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, keyframe))
    mujoco.mj_forward(m, d)
    return d


def snapshot(m: mujoco.MjModel, out_dir: Path, keyframe: str = "stand") -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    d = _data(m, keyframe)
    paths = []
    with mujoco.Renderer(m, 480, 640) as r:
        for name, (az, el) in VIEWS.items():
            cam = mujoco.MjvCamera()
            cam.lookat[:] = d.xpos[m.body("torso").id]
            cam.distance, cam.azimuth, cam.elevation = 0.6, az, el
            r.update_scene(d, cam)
            paths.append(out_dir / f"{name}.png")
            Image.fromarray(r.render()).save(paths[-1])
    return paths


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--keyframe", default="stand", choices=["stand", "home"])
    p.add_argument("--snapshot", type=Path, metavar="DIR")
    p.add_argument("--parts", action="store_true")
    p.add_argument("--export-dir", type=Path, default=Path("build/model"))
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

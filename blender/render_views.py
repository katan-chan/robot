"""Render PNG các góc nhìn bằng Workbench. Không lưu lại file .blend.

    blender -b --factory-startup F.blend --python blender/render_views.py -- --result R --out DIR [--views front,side,top,iso]
"""
import argparse, sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c

DIST = 1.0          # m, camera trực giao nên khoảng cách chỉ cần lớn hơn robot
ORTHO_SCALE = 0.55  # m, đủ khung cho sải chân ~0.45 m
VIEWS = {"front": Vector((1, 0, 0)), "side": Vector((0, 1, 0)), "top": Vector((0, 0, 1)), "iso": Vector((1, 1, 1))}


def render(a):
    views = a.views.split(",")
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        return {"ok": False, "errors": [c.err("views", ",".join(unknown), f"góc nhìn không có; hợp lệ: {', '.join(VIEWS)}", "sửa --views")]}
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x, scene.render.resolution_y = 800, 600
    scene.render.image_settings.file_format = "PNG"
    cam_data = bpy.data.cameras.new("render_cam")
    cam_data.type, cam_data.ortho_scale = "ORTHO", ORTHO_SCALE
    cam = bpy.data.objects.new("render_cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    bpy.context.view_layer.update()
    target = bpy.data.objects["torso"].matrix_world.translation.copy()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for v in views:
        d = VIEWS[v].normalized()
        cam.location = target + d * DIST
        # top: nhìn thẳng xuống, +y lên trên ảnh; còn lại: nhắm vào thân, z lên
        cam.rotation_euler = Euler((0, 0, 0)) if v == "top" else (-d).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out / f"{v}.png")
        bpy.ops.render.render(write_still=True)
        files.append(scene.render.filepath)
    return {"ok": True, "files": files}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--views", default="front,side,top,iso")
    c.run(render, p)

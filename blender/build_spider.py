"""Dựng model khởi điểm models/spider.blend theo Quy ước (14.4). Chỉ dùng bpy.data/bmesh, không bpy.ops
(trừ lưu file), để chạy không giao diện cho ổn định.

    blender -b --factory-startup --python blender/build_spider.py -- --result R --out F [--servo kind=NAME] [--force]
"""
import argparse, math, sys
from pathlib import Path

import bmesh, bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c

TORSO = (0.10, 0.08, 0.010)                     # m, dài x rộng x cao
LENGTH = {"coxa": 0.03, "femur": 0.055, "tibia": 0.075}
SEG_RADIUS = 0.006
FOOT_RADIUS = 0.008
ROOTS = {"fl": (0.05, 0.04, 45), "fr": (0.05, -0.04, -45), "rl": (-0.05, 0.04, 135), "rr": (-0.05, -0.04, -135)}
AXIS = {"hip_yaw": (0.0, 0.0, 1.0), "hip_pitch": (0.0, -1.0, 0.0), "knee": (0.0, 1.0, 0.0)}
RANGE = {"hip_yaw": (-60.0, 60.0), "hip_pitch": (-90.0, 90.0), "knee": (-30.0, 150.0)}
COLOR = {"torso": (0.45, 0.45, 0.45, 1), "coxa": (0.1, 0.6, 0.15, 1), "femur": (0.45, 0.15, 0.65, 1),
         "tibia": (0.03, 0.03, 0.03, 1), "servo": (0.1, 0.15, 0.4, 1)}


def box(size):
    return lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))


def cylinder_x(length, radius):
    """Trụ dọc +x cục bộ, từ 0 tới length (origin = khớp)."""
    m = Matrix.Translation((length / 2, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=radius, radius2=radius,
                                            depth=length, matrix=m)


def build(a):
    out = Path(a.out)
    if out.exists() and not a.force:
        return {"ok": False, "errors": [c.err("exists", str(out), "file đã có", "thêm --force để ghi đè")]}
    servos = c.load_servos()
    choice, errors = dict.fromkeys(c.KINDS, c.DEFAULT_SERVO), []
    for item in a.servo:
        kind, _, name = item.partition("=")
        if kind not in c.KINDS:
            errors.append(c.err("servo", kind, f"loại khớp '{kind}' không có; hợp lệ: {', '.join(c.KINDS)}", "dùng --servo kind=NAME"))
        elif name not in servos:
            errors.append(c.err("servo", kind, c.servo_msg(name, servos), "dùng --servo kind=NAME với tên hợp lệ"))
        else:
            choice[kind] = name
    if errors:
        return {"ok": False, "errors": errors}

    for o in list(bpy.data.objects):             # bỏ cube/camera/đèn của factory scene
        bpy.data.objects.remove(o)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1.0
    col = bpy.data.collections.new("robot")
    scene.collection.children.link(col)
    mats = {}
    for key, rgba in COLOR.items():
        mats[key] = bpy.data.materials.new(key)
        mats[key].diffuse_color = rgba

    def mesh_obj(name, make, mat, parent=None, loc=(0, 0, 0), yaw_deg=0.0):
        bm = bmesh.new()
        make(bm)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mats[mat])
        o = bpy.data.objects.new(name, me)
        col.objects.link(o)
        o.parent, o.location, o.rotation_euler = parent, loc, (0, 0, math.radians(yaw_deg))
        return o

    torso = mesh_obj("torso", box(TORSO), "torso")
    for leg, (x, y, yaw) in ROOTS.items():
        parent, loc, rot = torso, (x, y, 0), yaw
        for seg, kind in zip(c.SEGMENTS, c.KINDS):
            sv = servos[choice[kind]]
            L, W, H = sv["size"]
            # vỏ servo nằm trên body cha, tâm tại khớp; chiều cao (trục ra) dọc trục khớp
            mesh_obj(f"{leg}_{kind}_servo", box((L, W, H) if kind == "hip_yaw" else (L, H, W)), "servo", parent, loc, rot)
            o = mesh_obj(f"{leg}_{seg}", cylinder_x(LENGTH[seg], SEG_RADIUS), seg, parent, loc, rot)
            o["joint"], o["kind"], o["axis"] = f"{leg}_{kind}", kind, AXIS[kind]
            o["range_deg"], o["servo"] = RANGE[kind], choice[kind]
            parent, loc, rot = o, (LENGTH[seg], 0, 0), 0.0
        foot = bpy.data.objects.new(f"{leg}_foot", None)
        foot.empty_display_type, foot.empty_display_size = "SPHERE", FOOT_RADIUS
        col.objects.link(foot)
        foot.parent, foot.location = parent, loc  # đầu mút tibia

    bpy.context.view_layer.update()
    errors = c.validate(scene, servos)
    if errors:
        return {"ok": False, "errors": errors}
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    return {"ok": True, "blend": str(out), "servos": choice}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--servo", action="append", default=[])
    p.add_argument("--force", action="store_true")
    c.run(build, p)

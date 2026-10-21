"""Phần dùng chung cho các script trong blender/. Chạy bằng Python của Blender:
chỉ bpy, mathutils, thư viện chuẩn. Không import mujoco (18.9).

Quy ước model: xem global-constraints, mục "Quy ước model trong Blender".
"""
import json, math, sys, tomllib, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVOS_TOML = ROOT / "spider/model/servos.toml"
LEGS = ("fl", "fr", "rl", "rr")
KINDS = ("hip_yaw", "hip_pitch", "knee")
SEGMENTS = ("coxa", "femur", "tibia")      # đoạn thứ i do khớp KINDS[i] lái
PROPS = ("joint", "kind", "axis", "range_deg", "servo")
DEFAULT_SERVO = "MG90S"

# tên link -> (cha, loại khớp nối với cha), theo thứ tự cha trước con
LINKS = {"torso": (None, None)}
for _leg in LEGS:
    _parent = "torso"
    for _seg, _kind in zip(SEGMENTS, KINDS):
        LINKS[f"{_leg}_{_seg}"] = (_parent, _kind)
        _parent = f"{_leg}_{_seg}"


def load_servos(path=SERVOS_TOML):
    with open(path, "rb") as f:
        return tomllib.load(f)


def err(check, obj, msg, fix):
    return {"check": check, "object": obj, "msg": msg, "fix": fix}


def servo_msg(name, servos):
    return f"servo '{name}' không có trong danh mục; tên hợp lệ: {', '.join(servos)}"


def write_result(path, obj):
    Path(path).write_text(json.dumps(obj))


def run(fn, parser):
    """Đọc tham số sau '--', chạy fn(args) và ghi kết quả JSON vào --result."""
    parser.add_argument("--result", required=True)
    a = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    try:
        out = fn(a)
    except Exception as e:
        traceback.print_exc()
        out = {"ok": False, "errors": [err("exception", "", f"{type(e).__name__}: {e}", "xem traceback trong stderr")]}
    write_result(a.result, out)


def robot_objects(scene):
    col = scene.collection.children.get("robot")
    return None if col is None else {o.name: o for o in col.all_objects}


def validate(scene, servos):
    e = []
    u = scene.unit_settings
    if u.system != "METRIC" or abs(u.scale_length - 1) > 1e-9:
        e.append(err("units", "scene", f"system={u.system}, scale_length={u.scale_length}",
                     "Scene > Units: Unit System = Metric, Unit Scale = 1"))
    objs = robot_objects(scene)
    if objs is None:
        return e + [err("collection", "robot", "không có collection 'robot' trong scene", "tạo collection 'robot' chứa mọi object của robot")]

    for o in objs.values():
        if any(abs(s - 1) > 1e-9 for s in o.scale):
            e.append(err("scale", o.name, f"scale = {tuple(round(s, 6) for s in o.scale)}, cần (1, 1, 1)",
                         "Object > Apply > Scale, hoặc sửa kích thước trong mesh"))

    for name, (parent, kind) in LINKS.items():
        o = objs.get(name)
        if o is None or o.type != "MESH":
            e.append(err("links", name, "thiếu link (object mesh)", f"tạo object mesh '{name}' trong collection robot"))
            continue
        got = o.parent.name if o.parent else None
        if got != parent:
            e.append(err("parent", name, f"cha là {got}, cần {parent}", f"đặt cha của {name} là {parent}"))
        if kind is None:
            continue
        missing = [k for k in PROPS if k not in o]
        if missing:
            e.append(err("property", name, f"thiếu custom property {missing}", f"thêm {', '.join(missing)} vào {name}"))
            continue
        joint = f"{name[:2]}_{kind}"
        if o["kind"] != kind or o["joint"] != joint:
            e.append(err("joint", name, f"joint={o['joint']}, kind={o['kind']}", f"đặt joint={joint}, kind={kind}"))
        try:
            axis = [float(v) for v in o["axis"]]
            bad = len(axis) != 3 or abs(math.hypot(*axis) - 1) > 1e-6
        except (TypeError, ValueError):
            bad = True
        if bad:
            e.append(err("axis", name, f"axis = {o['axis']!r} không phải vector đơn vị 3 chiều", "đặt axis là 3 số, độ dài 1"))
        servo = o["servo"]
        if servo not in servos:
            e.append(err("servo", name, servo_msg(servo, servos), f"đặt servo của {name} là một tên hợp lệ"))
        travel = servos.get(servo, {}).get("travel_deg")
        try:
            lo, hi = (float(v) for v in o["range_deg"])
            bad = not lo < hi or (travel is not None and hi - lo > travel)
        except (TypeError, ValueError):
            bad, lo, hi = True, None, None
        if bad:
            e.append(err("range", name, f"range_deg = [{lo}, {hi}] cần lo < hi và hi − lo ≤ hành trình servo {travel}°",
                         "thu hẹp range_deg hoặc đổi servo"))

    for leg in LEGS:
        f = objs.get(f"{leg}_foot")
        if f is None or f.type != "EMPTY" or f.empty_display_type != "SPHERE" or f.parent is None or f.parent.name != f"{leg}_tibia":
            e.append(err("foot", f"{leg}_foot", "thiếu Empty sphere bàn chân, con của tibia",
                         f"tạo Empty sphere '{leg}_foot' làm con của {leg}_tibia"))
        for seg, kind in zip(SEGMENTS, KINDS):
            name, want = f"{leg}_{kind}_servo", LINKS[f"{leg}_{seg}"][0]
            s = objs.get(name)
            if s is None or s.type != "MESH" or s.parent is None or s.parent.name != want:
                e.append(err("servo_box", name, f"thiếu hộp servo mesh, con của {want}", f"tạo hộp mesh '{name}' làm con của {want}"))
    return e


def _r(vals):
    return [round(v, 9) for v in vals]


def collect(scene):
    """Mô tả link như build/model/robot.json nhưng chưa có mesh. Giả định validate() đã qua."""
    objs = robot_objects(scene)
    links = []
    for name, (parent, kind) in LINKS.items():
        o = objs[name]
        rel = o.matrix_world if parent is None else o.parent.matrix_world.inverted() @ o.matrix_world
        foot = None
        if kind == "knee":
            f = objs[f"{name[:2]}_foot"]
            foot = {"name": f.name, "pos": _r((o.matrix_world.inverted() @ f.matrix_world).to_translation()),
                    "radius": round(f.empty_display_size, 9)}
        links.append({
            "name": name, "parent": parent,
            "pos": _r(rel.to_translation()), "quat": _r(rel.to_quaternion()),
            "joint": None if kind is None else {
                "name": o["joint"], "kind": kind, "axis": [float(v) for v in o["axis"]],
                "range": [math.radians(v) for v in o["range_deg"]]},
            "servo": o.get("servo"),
            "servos_on_body": [{"name": c.name, "drives": c.name.removesuffix("_servo")}
                               for c in sorted(o.children, key=lambda c: c.name) if c.name.endswith("_servo")],
            "foot": foot,
        })
    feet = {f"{leg}_foot": _r(objs[f"{leg}_foot"].matrix_world.translation) for leg in LEGS}
    feet["torso_origin"] = _r(objs["torso"].matrix_world.translation)
    u = scene.unit_settings
    return {"links": links, "feet": feet,
            "units": {"system": u.system, "scale_length": u.scale_length, "length_unit": u.length_unit}}

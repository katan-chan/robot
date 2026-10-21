"""Xuất model sang build/model/: robot.json + meshes/<object>.obj (tam giác, khung cục bộ, có modifier).
Kiểm validate() trước; có lỗi thì không ghi gì. Ghi vào thư mục tạm cạnh D rồi thay D,
nên không còn file .obj cũ hoặc dở dang.

    blender -b --factory-startup F.blend --python blender/export_model.py -- --result R --out D
"""
import argparse, hashlib, json, shutil, sys, tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c


def write_obj(o, depsgraph, path):
    ev = o.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        lines = [f"# {o.name}"]
        lines += [f"v {v.co.x:.9f} {v.co.y:.9f} {v.co.z:.9f}" for v in me.vertices]
        lines += ["f " + " ".join(str(i + 1) for i in t.vertices) for t in me.loop_triangles]
        path.write_text("\n".join(lines) + "\n")
    finally:
        ev.to_mesh_clear()


def export(a):
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    errors = c.validate(scene, c.load_servos())
    if errors:
        return {"ok": False, "errors": errors}
    out = Path(a.out)
    # chỉ thay thư mục trống hoặc bản export cũ, không xoá nhầm dữ liệu khác
    if out.exists() and not (out.is_dir() and (not any(out.iterdir()) or (out / "robot.json").is_file())):
        return {"ok": False, "errors": [c.err("out", str(out), "đã có và không phải bản export (thiếu robot.json)",
                                              "chọn --out khác hoặc xoá thư mục đó")]}
    model = c.collect(scene)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))   # ghi xong mới thay out
    try:
        (tmp / "meshes").mkdir()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        objs = c.robot_objects(scene)
        files = []
        for link in model["links"]:
            for item in (link, *link["servos_on_body"]):
                rel = f"meshes/{item['name']}.obj"
                write_obj(objs[item["name"]], depsgraph, tmp / rel)
                item["mesh"] = rel
                files.append(rel)
        blend = Path(bpy.data.filepath)
        sha = hashlib.sha256(blend.read_bytes()).hexdigest()
        try:
            source = str(blend.relative_to(c.ROOT))
        except ValueError:
            source = str(blend)
        robot = {"format": 1, "blender_version": ".".join(map(str, bpy.app.version)),
                 "source": source, "source_sha256": sha, "links": model["links"]}
        (tmp / "robot.json").write_text(json.dumps(robot, indent=1))
        if out.exists():
            shutil.rmtree(out)
        tmp.rename(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"ok": True, "files": ["robot.json", *files], "source_sha256": sha}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    c.run(export, p)

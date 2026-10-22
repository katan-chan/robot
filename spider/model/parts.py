"""Bảng thành phần đọc từ MjModel (16.2). Khối lượng lấy từ MuJoCo, không tự tính (13.2)."""
import json
from pathlib import Path

import mujoco
import numpy as np

from spider.model.build import DEFAULT_EXPORT
from spider.model.config import Physics, load_physics


def parts_table(m: mujoco.MjModel, export_dir: Path = DEFAULT_EXPORT, physics: Physics | None = None) -> list[dict]:
    """13 dòng (torso + 12 link), thêm dòng `payload` nếu có payload_geom. Tên servo nằm trong robot.json.
    MjModel không lưu khối lượng từng geom: tải lấy đúng payload.mass_kg (MuJoCo dùng nguyên `mass=` của geom)
    và trừ khỏi dòng torso, để tổng các dòng vẫn bằng mj_getTotalmass. `physics` phải là bản đã dựng m."""
    servo = {l["name"]: l["servo"] for l in json.loads((Path(export_dir) / "robot.json").read_text())["links"]}
    rows = []
    for b in range(1, m.nbody):
        body = m.body(b)
        jid = int(m.body_jntadr[b])
        hinge = jid >= 0 and m.jnt_type[jid] == mujoco.mjtJoint.mjJNT_HINGE
        rows.append({
            "body": body.name,
            "parent": m.body(int(m.body_parentid[b])).name,
            "joint": m.joint(jid).name if jid >= 0 else None,
            "range_deg": tuple(np.degrees(m.jnt_range[jid])) if hinge else None,
            "servo": servo.get(body.name),
            "mass_g": float(m.body_mass[b]) * 1000,
            "geoms": [m.geom(g).name for g in range(m.ngeom) if m.geom_bodyid[g] == b],
        })
    if "payload_geom" in rows[0]["geoms"]:
        pay = (physics or load_physics()).payload_mass * 1000
        rows[0]["mass_g"] -= pay
        rows[0]["geoms"].remove("payload_geom")
        rows.append({"body": "payload", "parent": "torso", "joint": None, "range_deg": None, "servo": None,
                     "mass_g": pay, "geoms": ["payload_geom"]})
    return rows


def parts_markdown(m: mujoco.MjModel, export_dir: Path = DEFAULT_EXPORT) -> str:
    lines = ["| body | parent | joint | range (deg) | servo | mass (g) | geoms |", "|---|---|---|---|---|---|---|"]
    rows = parts_table(m, export_dir)
    for r in rows:
        rng = "-" if r["range_deg"] is None else f"{r['range_deg'][0]:.0f} .. {r['range_deg'][1]:.0f}"
        lines.append(f"| {r['body']} | {r['parent']} | {r['joint'] or '-'} | {rng} | {r['servo'] or '-'} "
                     f"| {r['mass_g']:.1f} | {', '.join(r['geoms'])} |")
    total = mujoco.mj_getTotalmass(m) * 1000
    pay = sum(r["mass_g"] for r in rows if r["body"] == "payload")
    lines.append(f"\nTổng: {total:.1f} g (không tải {total - pay:.1f} g, tải {pay:.1f} g)")
    return "\n".join(lines)

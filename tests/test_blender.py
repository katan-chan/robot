import hashlib, json, math, subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    p = subprocess.run([str(ROOT / "tools/blender"), *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


def test_bad_args_give_json_error():
    code, r = run("inspect", "--bogus")
    assert code == 1 and any(e["check"] == "args" for e in r["errors"])


def build(tmp_path, *extra):
    b = tmp_path / "s.blend"
    assert run("build", "--out", str(b), *extra)[0] == 0
    return b


def test_version_reports_blender_52():
    code, r = run("version")
    assert code == 0 and r["blender"].startswith("5.2")


def test_build_then_inspect_has_13_links_in_x_layout(tmp_path):
    b = build(tmp_path)
    code, r = run("inspect", "--blend", str(b))
    assert code == 0 and r["ok"]
    links = {l["name"]: l for l in r["links"]}
    assert len(links) == 13 and links["fl_tibia"]["parent"] == "fl_femur"
    assert links["fl_femur"]["joint"]["axis"] == [0, -1, 0]
    assert links["rr_tibia"]["joint"]["name"] == "rr_knee"
    assert math.isclose(math.degrees(links["fl_coxa"]["joint"]["range"][1]), 60)
    assert set(r["feet"]) == {"fl_foot", "fr_foot", "rl_foot", "rr_foot", "torso_origin"}


def test_build_refuses_to_overwrite_without_force(tmp_path):
    b = build(tmp_path)
    before = hashlib.sha256(b.read_bytes()).hexdigest()
    code, r = run("build", "--out", str(b))
    assert code == 1 and not r["ok"]
    assert hashlib.sha256(b.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("prop", ["scale", "delta_scale"])
def test_inspect_rejects_scaled_object(tmp_path, prop):           # Review Focus 1
    b = build(tmp_path)
    assert run("exec", "--blend", str(b), "--expr",
               f'bpy.data.objects["fl_femur"].{prop} = (1000, 1000, 1000)')[0] == 0
    code, r = run("inspect", "--blend", str(b))
    assert code == 1
    assert any(e["check"] == "scale" and e["object"] == "fl_femur" for e in r["errors"])


def test_inspect_rejects_bad_servo_and_wide_range(tmp_path):      # Review Focus 2
    code, r = run("build", "--out", str(tmp_path / "bad.blend"), "--servo", "knee=MG90")
    assert code == 1 and any("MG90S" in e["msg"] for e in r["errors"])
    b = build(tmp_path)
    assert run("exec", "--blend", str(b), "--expr",
               'bpy.data.objects["fl_tibia"]["range_deg"] = [-30, 160]')[0] == 0
    code, r = run("inspect", "--blend", str(b))
    assert code == 1
    assert any(e["check"] == "range" and e["object"] == "fl_tibia" for e in r["errors"])

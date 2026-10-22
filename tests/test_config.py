import math, re, tomllib
import pytest
from spider.model.config import load_physics, load_servos, parse_physics, PHYSICS, SERVOS

def _raw():
    return tomllib.loads(PHYSICS.read_text())

def test_physics_converts_to_rad():                # 13.4
    p = load_physics()
    assert p.stand["knee"] == pytest.approx(math.radians(100))
    assert p.kp_error == pytest.approx(math.radians(11.46))
    assert p.robot_budget == (1.10, 1.45) and p.total_max == 3.5          # 19.7
    assert p.payload_mass == 2.0 and p.payload_size == (0.15, 0.12, 0.05)  # 19.6
    assert p.torso_extra_mass == 0.20                                      # 19.5

@pytest.mark.parametrize("mutate, field", [
    (lambda d: d["material"].update(density=0), "density"),
    (lambda d: d["material"].update(fill=0), "fill"),
    (lambda d: d["material"].update(fill=1.5), "fill"),
    (lambda d: d["stand_deg"].pop("knee"), "stand_deg.knee"),
    (lambda d: d.update(torso_extra_mass=0), "torso_extra_mass"),
    (lambda d: d["contact"].update(foot_friction=-0.1), "contact.foot_friction"),
    (lambda d: d["actuator"].update(kp_error_deg=0), "actuator.kp_error_deg"),
    (lambda d: d["actuator"].update(dampratio=0), "actuator.dampratio"),
    (lambda d: d["payload"].update(mass_kg=-0.1), "payload.mass_kg"),
    (lambda d: d["payload"].update(size=[0.15, 0, 0.05]), "payload.size"),
    (lambda d: d["payload"].update(size=[0.15, 0.12]), "payload.size"),
    (lambda d: d["budget"].update(robot_kg=[1.45, 1.10]), "budget.robot_kg"),
    (lambda d: d["budget"].update(total_max_kg=0), "budget.total_max_kg"),
])
def test_parse_physics_rejects_bad_input(mutate, field):
    d = _raw(); mutate(d)
    with pytest.raises(ValueError, match=field):
        parse_physics(d)

@pytest.mark.parametrize("field, value", [
    ("speed", None),           # thiếu trường
    ("stall_torque", "0"),     # phải > 0
    ("mass", "-0.0134"),
    ("travel_deg", "0"),
])
def test_load_servos_rejects_bad_entry(tmp_path, field, value):
    text = SERVOS.read_text().split("[SG90]")[0]    # chỉ MG90S
    bad = re.sub(rf"^{field} = .*$", "" if value is None else f"{field} = {value}", text, count=1, flags=re.M)
    assert bad != text
    (tmp_path / "s.toml").write_text(bad)
    with pytest.raises(ValueError, match=rf"MG90S.*{field}"):
        load_servos(tmp_path / "s.toml")

def test_servo_catalog():
    s = load_servos()["MG996R"]
    assert s.stall_torque == 0.92 and s.travel == math.radians(180)
    assert set(load_servos()) == {"MG90S", "SG90", "MG996R", "DS3235", "DS3240"}
    ds35, ds40 = load_servos()["DS3235"], load_servos()["DS3240"]          # 19.4
    assert (ds35.stall_torque, ds35.speed, ds35.mass, ds35.size) == (3.4, 8.0, 0.065, (0.040, 0.020, 0.041))
    assert (ds40.stall_torque, ds40.speed, ds40.mass, ds40.size) == (3.92, 7.5, 0.066, (0.040, 0.020, 0.041))
    assert (ds40.armature, ds40.damping, ds40.frictionloss, ds40.travel) == (5e-3, 0.2, 0.1, math.radians(180))

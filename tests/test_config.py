import math, tomllib
import pytest
from spider.model.config import load_physics, load_servos, parse_physics, PHYSICS

def _raw():
    return tomllib.loads(PHYSICS.read_text())

def test_physics_converts_to_rad():                # 13.4
    p = load_physics()
    assert p.stand["knee"] == pytest.approx(math.radians(100))
    assert p.kp_error == pytest.approx(math.radians(11.46))
    assert p.mass_budget == (0.25, 0.35)

@pytest.mark.parametrize("mutate, field", [
    (lambda d: d["material"].update(density=0), "density"),
    (lambda d: d["material"].update(fill=0), "fill"),
    (lambda d: d["material"].update(fill=1.5), "fill"),
    (lambda d: d["stand_deg"].pop("knee"), "stand_deg.knee"),
])
def test_parse_physics_rejects_bad_input(mutate, field):
    d = _raw(); mutate(d)
    with pytest.raises(ValueError, match=field):
        parse_physics(d)

def test_servo_catalog():
    s = load_servos()["MG996R"]
    assert s.stall_torque == 0.92 and s.travel == math.radians(180)
    assert set(load_servos()) == {"MG90S", "SG90", "MG996R"}

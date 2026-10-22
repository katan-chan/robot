"""Đọc servos.toml và physics.toml. TOML dùng độ, ở đây đổi sang rad (SI)."""
import math, tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent
SERVOS = HERE / "servos.toml"
PHYSICS = HERE / "physics.toml"
JOINT_KINDS = ("hip_yaw", "hip_pitch", "knee")


@dataclass(frozen=True)
class Servo:
    name: str
    stall_torque: float   # N·m
    speed: float          # rad/s
    mass: float           # kg
    size: tuple[float, float, float]  # m
    travel: float         # rad
    armature: float
    damping: float
    frictionloss: float


@dataclass(frozen=True)
class Physics:
    torso_extra_mass: float  # kg
    density: float           # kg/m³
    fill: float              # (0, 1]
    foot_friction: float
    kp_error: float          # rad
    dampratio: float
    stand: dict[str, float]  # rad
    payload_mass: float      # kg, 0 = không tải
    payload_size: tuple[float, float, float]  # m
    robot_budget: tuple[float, float]  # kg, robot không tải
    total_max: float         # kg, có tải


SERVO_FIELDS = ("stall_torque", "speed", "mass", "size", "travel_deg", "armature", "damping", "frictionloss")
SERVO_POSITIVE = ("stall_torque", "speed", "mass", "travel_deg")


def _servo(n: str, s: dict) -> Servo:
    for k in SERVO_FIELDS:
        if k not in s:
            raise ValueError(f"servo {n}: thiếu trường {k}")
    for k in SERVO_POSITIVE:
        if not s[k] > 0:
            raise ValueError(f"servo {n}: {k} phải > 0, nhận {s[k]}")
    return Servo(n, s["stall_torque"], s["speed"], s["mass"], tuple(s["size"]),
                 math.radians(s["travel_deg"]), s["armature"], s["damping"], s["frictionloss"])


def load_servos(path=SERVOS) -> dict[str, Servo]:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    return {n: _servo(n, s) for n, s in raw.items()}


def _get(d: dict, dotted: str):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            raise ValueError(f"thiếu trường {dotted}")
        d = d[k]
    return d


def _positive(d: dict, dotted: str):
    v = _get(d, dotted)
    if not v > 0:
        raise ValueError(f"{dotted} phải > 0, nhận {v}")
    return v


def parse_physics(d: dict) -> Physics:
    density = _positive(d, "material.density")
    fill = _get(d, "material.fill")
    if not 0 < fill <= 1:
        raise ValueError(f"fill phải thuộc (0, 1], nhận {fill}")
    stand = {k: math.radians(_get(d, f"stand_deg.{k}")) for k in JOINT_KINDS}
    lo, hi = _get(d, "budget.robot_kg")
    if not 0 < lo <= hi:
        raise ValueError(f"budget.robot_kg phải có 0 < min <= max, nhận {[lo, hi]}")
    payload_mass = _get(d, "payload.mass_kg")
    if not payload_mass >= 0:
        raise ValueError(f"payload.mass_kg phải >= 0, nhận {payload_mass}")
    size = _get(d, "payload.size")
    if len(size) != 3 or not all(v > 0 for v in size):
        raise ValueError(f"payload.size phải là 3 số > 0, nhận {size}")
    return Physics(
        torso_extra_mass=_positive(d, "torso_extra_mass"),
        density=density, fill=fill,
        foot_friction=_positive(d, "contact.foot_friction"),
        kp_error=math.radians(_positive(d, "actuator.kp_error_deg")),
        dampratio=_positive(d, "actuator.dampratio"),
        stand=stand, payload_mass=payload_mass, payload_size=tuple(size),
        robot_budget=(lo, hi), total_max=_positive(d, "budget.total_max_kg"),
    )


def load_physics(path=PHYSICS) -> Physics:
    with open(path, "rb") as f:
        return parse_physics(tomllib.load(f))

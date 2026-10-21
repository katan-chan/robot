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
    mass_budget: tuple[float, float]  # kg


def load_servos(path=SERVOS) -> dict[str, Servo]:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    return {
        n: Servo(n, s["stall_torque"], s["speed"], s["mass"], tuple(s["size"]),
                 math.radians(s["travel_deg"]), s["armature"], s["damping"], s["frictionloss"])
        for n, s in raw.items()
    }


def _get(d: dict, dotted: str):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            raise ValueError(f"thiếu trường {dotted}")
        d = d[k]
    return d


def parse_physics(d: dict) -> Physics:
    density = _get(d, "material.density")
    if not density > 0:
        raise ValueError(f"density phải > 0, nhận {density}")
    fill = _get(d, "material.fill")
    if not 0 < fill <= 1:
        raise ValueError(f"fill phải thuộc (0, 1], nhận {fill}")
    stand = {k: math.radians(_get(d, f"stand_deg.{k}")) for k in JOINT_KINDS}
    lo, hi = _get(d, "budget.mass_kg")
    if not 0 < lo <= hi:
        raise ValueError(f"budget.mass_kg phải có 0 < min <= max, nhận {[lo, hi]}")
    return Physics(
        torso_extra_mass=_get(d, "torso_extra_mass"),
        density=density, fill=fill,
        foot_friction=_get(d, "contact.foot_friction"),
        kp_error=math.radians(_get(d, "actuator.kp_error_deg")),
        dampratio=_get(d, "actuator.dampratio"),
        stand=stand, mass_budget=(lo, hi),
    )


def load_physics(path=PHYSICS) -> Physics:
    with open(path, "rb") as f:
        return parse_physics(tomllib.load(f))

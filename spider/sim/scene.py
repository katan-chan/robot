"""Cảnh MuJoCo: sàn, đèn, lưới, bộ giải (6.2, 9.2). Dựng bằng MjSpec."""
import mujoco


def add_scene(spec: mujoco.MjSpec) -> None:
    spec.compiler.degree = False
    spec.option.timestep = 0.002
    spec.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    # Chân không bò dưới giới hạn ma sát (BUG-002): nón elliptic + impratio 10 làm ma sát cứng hơn,
    # noslip_iterations 10 khử trượt mềm còn lại. Chỉ cả hai mới đạt < 0.5 mm / 2 s ở 50% μ·m·g.
    spec.option.cone = mujoco.mjtCone.mjCONE_ELLIPTIC
    spec.option.impratio = 10
    spec.option.noslip_iterations = 10
    spec.add_texture(name="grid", type=mujoco.mjtTexture.mjTEXTURE_2D,
                     builtin=mujoco.mjtBuiltin.mjBUILTIN_CHECKER,
                     rgb1=[0.2, 0.3, 0.4], rgb2=[0.1, 0.2, 0.3], width=256, height=256)
    mat = spec.add_material(name="grid", texrepeat=[4, 4], reflectance=0.1)
    mat.textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "grid"
    spec.worldbody.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE,
                            size=[0, 0, 0.05], material="grid", contype=0, conaffinity=1)
    spec.worldbody.add_light(pos=[0, 0, 3], dir=[0, 0, -1])


def box_drop_spec(height: float = 0.5, half: float = 0.05) -> mujoco.MjSpec:
    spec = mujoco.MjSpec()
    add_scene(spec)
    body = spec.worldbody.add_body(name="box", pos=[0, 0, height])
    body.add_freejoint()
    body.add_geom(type=mujoco.mjtGeom.mjGEOM_BOX, size=[half] * 3, mass=0.1,
                  contype=1, conaffinity=0)
    return spec

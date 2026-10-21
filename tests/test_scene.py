import mujoco, numpy as np
from spider.sim.scene import box_drop_spec

def test_box_falls_and_rests_on_floor():          # check:box-fall (6.2)
    m = box_drop_spec(height=0.5, half=0.05).compile(); d = mujoco.MjData(m)
    while d.time < 3.0: mujoco.mj_step(m, d)
    assert abs(d.body("box").xpos[2] - 0.05) < 1e-3
    assert np.linalg.norm(d.qvel) < 1e-3

def test_scene_solver_settings():                  # 9.2
    m = box_drop_spec().compile()
    assert m.opt.timestep == 0.002 and m.opt.integrator == mujoco.mjtIntegrator.mjINT_IMPLICITFAST

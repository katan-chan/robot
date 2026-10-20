# Phase 1 — tới cổng G1 (xem model 3D) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng môi trường MuJoCo và model robot nhện 4 chân × 3 khớp bằng khối hình đơn giản, sinh từ file tham số, để người dùng xem được model 3D và bảng thành phần của nó (cổng G1).

**Architecture:** `spider/model/` đọc `params.toml` + `servos.toml` → dựng `mujoco.MjSpec` bằng code (không ghép chuỗi XML) → `MjModel`. `spider/sim/` có cảnh (sàn, đèn), công cụ xem (viewer MuJoCo dùng riêng, 14.1) và chụp ảnh offscreen. Mọi đại lượng vật lý (khối lượng, quán tính, vị trí chân) đọc từ MuJoCo, không tự tính (13.2).

**Tech Stack:** Python 3.12 qua `uv`, `mujoco` (ghim đúng một phiên bản, ≥ 3.7.0), `pytest`, `Pillow` (lưu PNG).

**Spec:** `docs/decisions/` (README + 01–16), đặc biệt 3.2, 5.3, 6.2, 7.3, 9.1–9.3, 12.7, 13.2–13.4, 14.1, 14.4–14.5, 16.2–16.4. Quy ước repo: `AGENTS.md`, `docs/harness/task-graph.md`.

## Global Constraints

- Python 3.12 qua `uv`; không dùng python hệ thống (3.9.6). Chạy mọi thứ bằng `uv run …`.
- `mujoco` ghim **một phiên bản chính xác** (`mujoco==X.Y.Z`), tối thiểu 3.7.0 (cần `dcmotor`, delay ≥ 3.5.0). Đổi phiên bản về sau = cổng người dùng (AGENTS.md luật 3).
- Đơn vị SI trong code: m, kg, rad, N·m, s. Chỉ `params.toml` dùng độ cho góc; bộ đọc đổi sang rad.
- Không tự tính lại cái MuJoCo tính: khối lượng gán vào `geom.mass`, quán tính do MuJoCo tính; vị trí chân đọc qua `mj_kinematics` + `data.site_xpos`; tổng khối lượng qua `mujoco.mj_getTotalmass` (13.2).
- Bộ giải: `integrator = implicitfast`, `timestep = 0.002` (9.2).
- Va chạm: chỉ bàn chân (cầu) và thân chạm sàn; không tự va chạm (9.3). Ma sát chân 0.9, `condim = 3`.
- Không dùng `mjpython`/`launch_passive`; viewer là công cụ riêng `mujoco.viewer.launch` (14.1).
- Vai trò (17.2–17.6): mỗi task do **một subagent `implementer`** làm trong git worktree riêng, lần lượt từng task. Implementer chỉ ghi `pyproject.toml`, `uv.lock`, `.gitignore`, `spider/`, `tests/test_env.py`, `tests/test_scene.py`, `tests/test_model.py`, `tests/test_view.py`. Các bước đánh dấu **[coordinator]** (ghi `docs/`, `AGENTS.md`) do phiên chính làm sau khi gộp nhánh. Coordinator gộp bằng `git merge --ff-only` sau khi test qua và reviewer duyệt.
- Mỗi task kết thúc bằng commit; hook `pre-commit` (kb check + selftest) phải qua.

### Quy ước tên (các task sau dựa vào đây)

- Chân: `fl` (trước-trái), `fr` (trước-phải), `rl` (sau-trái), `rr` (sau-phải). Trục x hướng trước, y sang trái, z lên.
- Body: `torso`, `{leg}_coxa`, `{leg}_femur`, `{leg}_tibia`. Khớp gốc: freejoint `root`.
- Khớp và actuator cùng tên: `{leg}_hip_yaw`, `{leg}_hip_pitch`, `{leg}_knee`. Thứ tự 12 actuator: `fl, fr, rl, rr` × `hip_yaw, hip_pitch, knee`.
- Geom servo: `{leg}_{joint}_servo`. Site bàn chân: `{leg}_foot`. Keyframe: `home` (mọi khớp 0), `stand`.
- Bố trí hình chữ X (14.4): gốc chân tại góc thân `(±hip_offset.x, ±hip_offset.y)`, hướng ra ngoài theo góc `fl=+45°`, `fr=−45°`, `rl=+135°`, `rr=−135°`.
- Tư thế 0: mọi đoạn chân nằm ngang theo hướng ra ngoài. Trục: `hip_yaw` = z (dương = xoay ngược chiều kim đồng hồ nhìn từ trên); `hip_pitch` = (0, −1, 0) trong khung coxa (dương = nhấc đùi lên); `knee` = (0, 1, 0) trong khung femur (dương = gập cẳng xuống).
- Khối lượng servo gắn vào body **cha** của khớp nó lái (vỏ servo nằm trên body cha): servo `hip_yaw` trên `torso`, `hip_pitch` trên `coxa`, `knee` trên `femur`.

## Review Focus

1. **Tham số nhập bằng mm thay vì m** (vd `femur_length = 55`): bộ đọc phải từ chối với thông báo nêu tên trường, không dựng ra robot dài 55 m. → test ở Task 3.
2. **Hành trình khớp rộng hơn hành trình servo** (vd knee `[-30, 160]` = 190° > 180°): phải từ chối. → Task 3.
3. **Tên servo không có trong danh mục** (vd `servo = "MG90"`): phải từ chối và liệt kê các tên hợp lệ. → Task 3.
4. **Ghi đè servo cho một loại khớp** (gối dùng MG996R): khối lượng và giới hạn lực của đúng 4 khớp gối phải đổi theo, các khớp khác giữ nguyên. → Task 4.
5. **Keyframe `stand` đặt robot lơ lửng hoặc chìm dưới sàn:** thấp nhất của bàn chân phải chạm đúng mặt sàn. → Task 4.

---

### Task 1: Môi trường Python + MuJoCo ghim phiên bản (T0.1)

**Files:**
- Create: `pyproject.toml`, `uv.lock` (do uv sinh), `spider/__init__.py`, `tests/test_env.py`
- Modify: `.gitignore` (thêm `build/`, `.pytest_cache/`); **[coordinator]** `AGENTS.md` (mục Lệnh), `docs/decisions/16-gate-dau-tien.md` (dòng 16.5)

**Interfaces:**
- Produces: package `spider` cài được ở chế độ editable; lệnh `uv run pytest` chạy được.

- [ ] **Step 1: Tạo project** — `pyproject.toml`: `name = "spider"`, `requires-python = ">=3.12,<3.13"`, build backend `hatchling`, packages `["spider"]`. Chạy `uv python pin 3.12`, `uv add "mujoco>=3.7"`, `uv add Pillow`, `uv add --dev pytest`. Sau đó sửa dòng mujoco trong `pyproject.toml` thành `mujoco==<phiên bản uv vừa cài>` và chạy `uv lock`.

- [ ] **Step 2: Viết test thất bại** `tests/test_env.py`

```python
import tomllib, importlib.metadata, pathlib, re
import mujoco

def test_mujoco_pinned_exactly_and_recent_enough():
    pyproject = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
    pins = [d for d in pyproject["project"]["dependencies"] if d.startswith("mujoco")]
    assert len(pins) == 1 and re.fullmatch(r"mujoco==\d+\.\d+\.\d+", pins[0])
    assert importlib.metadata.version("mujoco") == pins[0].split("==")[1]
    assert tuple(map(int, mujoco.__version__.split(".")[:2])) >= (3, 7)

def test_python_is_312():
    import sys
    assert sys.version_info[:2] == (3, 12)
```

- [ ] **Step 3: Chạy** `uv run pytest tests/test_env.py -v` — mong đợi PASS sau Step 1 (nếu FAIL ở pin: sửa `pyproject.toml` cho đúng phiên bản đã cài).

- [ ] **Step 4: [coordinator] Ghi lại** — thêm dòng `| 16.5 | Ghim mujoco==X.Y.Z, Python 3.12 | [Claude tự quyết] | Đang áp dụng |` vào `docs/decisions/16-gate-dau-tien.md`; thêm `uv run pytest -q` vào mục Lệnh của `AGENTS.md`.

- [ ] **Step 5: Commit (implementer, trước Step 4)** — `git add pyproject.toml uv.lock .gitignore spider tests && git commit -m "feat(env): uv project with pinned mujoco (T0.1)"`. Báo lại phiên bản mujoco đã ghim cho coordinator.

---

### Task 2: Cảnh mô phỏng + khối hộp rơi (T0.2, T0.3)

**Files:**
- Create: `spider/sim/__init__.py`, `spider/sim/scene.py`, `tests/test_scene.py`

**Interfaces:**
- Produces:
  - `add_scene(spec: mujoco.MjSpec) -> None` — thêm vào `spec`: sàn `floor` (plane, `contype=0`, `conaffinity=1`, ma sát mặc định), đèn hướng từ trên, bầu trời/lưới để dễ nhìn; đặt `spec.option.timestep = 0.002`, `spec.option.integrator = mjINT_IMPLICITFAST`, `spec.compiler.degree = False`.
  - `box_drop_spec(height: float = 0.5, half: float = 0.05) -> mujoco.MjSpec` — cảnh + một hộp `box` có freejoint, `contype=1`, `conaffinity=0`, khối lượng 0.1 kg, tâm ở `z = height`.
- Không có hằng số vật lý tự tính; trọng lực để mặc định của MuJoCo.

- [ ] **Step 1: Test thất bại** `tests/test_scene.py`

```python
import mujoco, numpy as np
from spider.sim.scene import box_drop_spec

def test_box_falls_and_rests_on_floor():          # check:box-fall (6.2)
    m = box_drop_spec(height=0.5, half=0.05).compile()
    d = mujoco.MjData(m)
    while d.time < 3.0:
        mujoco.mj_step(m, d)
    z = d.body("box").xpos[2]
    assert abs(z - 0.05) < 1e-3                    # nằm trên sàn, xuyên < 1 mm (9.4)
    assert np.linalg.norm(d.qvel) < 1e-3           # đã nằm yên

def test_scene_uses_spec_solver_settings():        # 9.2
    m = box_drop_spec().compile()
    assert m.opt.timestep == 0.002
    assert m.opt.integrator == mujoco.mjtIntegrator.mjINT_IMPLICITFAST
```

- [ ] **Step 2: Chạy** `uv run pytest tests/test_scene.py -v` — mong đợi FAIL (`ModuleNotFoundError: spider.sim.scene`).
- [ ] **Step 3: Viết** `add_scene` và `box_drop_spec` trong `spider/sim/scene.py` bằng API `MjSpec` (`spec.worldbody.add_geom`, `add_body`, `add_freejoint`, `add_light`). Kiểm tên thuộc tính theo tài liệu `MjSpec` của phiên bản đã ghim.
- [ ] **Step 4: Chạy** `uv run pytest tests/test_scene.py -v` — mong đợi PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat(sim): scene and box-drop smoke test (T0.2, T0.3)"`

Ghi chú **[coordinator]**: kiểm tra `uv run mjpython` ở 6.2 không còn cần vì 14.1 bỏ `launch_passive`. Ghi chú "Đã thay → 14.1" cho phần đó trong `docs/decisions/06-moi-truong-mo-phong.md`.

---

### Task 3: Danh mục servo + file tham số + bộ đọc (T1.1)

**Files:**
- Create: `spider/model/__init__.py`, `spider/model/servos.toml`, `spider/model/params.toml`, `spider/model/config.py`, `tests/test_model.py` (phần config)

**Interfaces:**
- Produces (trong `spider/model/config.py`):
  - `@dataclass(frozen=True) class Servo: name: str; stall_torque: float; speed: float; mass: float; size: tuple[float, float, float]; travel: float; armature: float; damping: float; frictionloss: float` (đơn vị SI; `travel` rad).
  - `@dataclass(frozen=True) class Params` với các trường: `servo: str`, `servo_override: dict[str, str]` (khoá ∈ `{"hip_yaw","hip_pitch","knee"}`), `torso_size: tuple[float,float,float]`, `torso_mass: float`, `hip_offset: tuple[float,float]`, `coxa_length, femur_length, tibia_length, link_radius, foot_radius: float`, `coxa_mass, femur_mass, tibia_mass: float`, `joint_range: dict[str, tuple[float,float]]` (rad), `stand: dict[str, float]` (rad), `foot_friction: float`, `kp_error: float` (rad), `dampratio: float`.
  - `load_servos(path: Path = SERVOS) -> dict[str, Servo]`
  - `parse_params(d: dict, servos: dict[str, Servo] | None = None) -> Params` — đổi đơn vị, kiểm, báo `ValueError` nêu tên trường.
  - `load_params(path: Path = PARAMS, servos=None) -> Params` = `parse_params(tomllib.load(...), servos)`.
  - `servo_for(p: Params, servos: dict[str, Servo], kind: str) -> Servo`
  - Hằng `JOINT_KINDS = ("hip_yaw", "hip_pitch", "knee")`, `LEGS = {"fl": 45, "fr": -45, "rl": 135, "rr": -135}` (độ, hướng chân).

- [ ] **Step 1: Viết `servos.toml`** — số liệu datasheet ở 4.8 V; `armature`, `damping`, `frictionloss` là **ước lượng**, ghi rõ trong trường `source`, hiệu chỉnh ở Giai đoạn 8 (13.4):

| tên | stall_torque N·m | speed rad/s | mass kg | size m | travel_deg | armature kg·m² | damping N·m·s/rad | frictionloss N·m |
|---|---|---|---|---|---|---|---|---|
| MG90S | 0.177 | 10.47 | 0.0134 | [0.0228, 0.0122, 0.0285] | 180 | 2e-4 | 0.01 | 0.01 |
| SG90 | 0.177 | 10.47 | 0.009 | [0.0222, 0.0118, 0.031] | 180 | 1.5e-4 | 0.01 | 0.01 |
| MG996R | 0.92 | 6.16 | 0.055 | [0.0407, 0.0197, 0.0429] | 180 | 1e-3 | 0.05 | 0.05 |

- [ ] **Step 2: Viết `params.toml`** với giá trị khởi điểm (14.4, 9.5): `servo = "MG90S"`, `[servo_override]` rỗng; `torso.size = [0.10, 0.08, 0.035]`, `torso.mass = 0.12` (thân + 2 pin 18650 + mạch, không gồm servo); `hip_offset = [0.05, 0.04]`; `coxa_length = 0.03`, `femur_length = 0.055`, `tibia_length = 0.075`; `link_radius = 0.006`, `foot_radius = 0.008`; `coxa_mass = 0.004`, `femur_mass = 0.005`, `tibia_mass = 0.004`; `[joint_range_deg] hip_yaw = [-60, 60]`, `hip_pitch = [-90, 90]`, `knee = [-30, 150]`; `[stand_deg] hip_yaw = 0`, `hip_pitch = 30`, `knee = 100`; `foot_friction = 0.9`; `[actuator] kp_error_deg = 11.46` (≈ 0.2 rad: servo đạt mô-men cực đại khi lệch 0.2 rad), `dampratio = 1.0`. Mỗi trường có một dòng chú thích tiếng Việt kèm đơn vị.

- [ ] **Step 3: Test thất bại** (thêm vào `tests/test_model.py`)

```python
import math, pytest, tomllib, dataclasses
from spider.model.config import load_params, parse_params, load_servos, servo_for, PARAMS

def _params_with(edit):
    d = tomllib.loads(PARAMS.read_text()); edit(d); return d

def test_default_params_load_in_si():
    p = load_params()
    assert p.femur_length == 0.055
    assert math.isclose(p.joint_range["knee"][1], math.radians(150))

def test_rejects_millimetres():                               # Review Focus 1
    with pytest.raises(ValueError, match="femur_length"):
        parse_params(_params_with(lambda d: d["leg"].update(femur_length=55)))

def test_rejects_range_wider_than_servo_travel():             # Review Focus 2
    with pytest.raises(ValueError, match="knee"):
        parse_params(_params_with(lambda d: d["joint_range_deg"].update(knee=[-30, 160])))

def test_rejects_unknown_servo_and_lists_known():             # Review Focus 3
    with pytest.raises(ValueError, match="MG90S"):
        parse_params(_params_with(lambda d: d.update(servo="MG90")))

def test_servo_override_per_joint_kind():
    s = load_servos(); p = dataclasses.replace(load_params(), servo_override={"knee": "MG996R"})
    assert servo_for(p, s, "knee").name == "MG996R" and servo_for(p, s, "hip_yaw").name == "MG90S"
```

Đặt khoá TOML theo đúng các bảng ở Step 2 (`[leg]` chứa độ dài, khối lượng, bán kính; `[torso]`; `[joint_range_deg]`; `[stand_deg]`; `[actuator]`; `[contact]`).

- [ ] **Step 4: Chạy** `uv run pytest tests/test_model.py -v` — FAIL (`ModuleNotFoundError`).
- [ ] **Step 5: Viết** `config.py` bằng `tomllib` + `dataclasses` (`load_params` chỉ đọc file rồi gọi `parse_params`). Luật kiểm: mọi độ dài và khối lượng `> 0`; độ dài `< 1.0` m (bắt lỗi mm); khoảng khớp `lo < hi` và `hi − lo ≤ servo.travel`; tư thế `stand` nằm trong khoảng khớp; `servo` và mọi giá trị `servo_override` có trong danh mục, khoá override ∈ `JOINT_KINDS`.
- [ ] **Step 6: Chạy** `uv run pytest tests/test_model.py -v` — PASS.
- [ ] **Step 7: Commit** — `git commit -m "feat(model): servo catalog, params file, validating loader (T1.1)"`

---

### Task 4: Dựng model robot bằng MjSpec + actuator servo (T1.2, T1.3)

**Files:**
- Create: `spider/model/build.py`
- Test: `tests/test_model.py` (thêm)

**Interfaces:**
- Consumes: Task 2 `add_scene`; Task 3 `load_params`, `load_servos`, `servo_for`, `LEGS`, `JOINT_KINDS`.
- Produces:
  - `build_spec(p: Params | None = None, servos: dict[str, Servo] | None = None) -> mujoco.MjSpec` (mặc định đọc file mặc định).
  - `build_model(p=None, servos=None) -> mujoco.MjModel`
  - `ACTUATORS: list[str]` — 12 tên theo thứ tự ở Global Constraints.
  - Keyframe `home` và `stand` trong model (`qpos` + `ctrl`).

- [ ] **Step 1: Test thất bại**

```python
import mujoco, numpy as np, dataclasses
from spider.model.build import build_model, ACTUATORS
from spider.model.config import load_params, load_servos

def test_compiles_with_12_named_position_servos():           # check:mjcf-compiles
    m = build_model()
    assert [m.actuator(i).name for i in range(m.nu)] == ACTUATORS and m.nu == 12
    assert m.nbody == 14                                      # world + torso + 12 đoạn chân
    assert m.njnt == 13                                       # root + 12

def test_total_mass_in_budget():                              # 9.5: 250–350 g
    assert 0.25 <= mujoco.mj_getTotalmass(build_model()) <= 0.35

def test_actuator_limits_follow_servo_and_joint_range():      # 9.1, 12.7
    m, p = build_model(), load_params()
    a = m.actuator("fl_knee")
    assert np.allclose(a.forcerange, [-0.177, 0.177])
    assert np.allclose(a.ctrlrange, p.joint_range["knee"])
    assert m.joint("fl_knee").armature == 2e-4

def test_knee_override_changes_only_knees():                 # Review Focus 4
    base = build_model()
    p = dataclasses.replace(load_params(), servo_override={"knee": "MG996R"})
    m = build_model(p)
    assert np.allclose(m.actuator("rr_knee").forcerange, [-0.92, 0.92])
    assert np.allclose(m.actuator("rr_hip_pitch").forcerange, [-0.177, 0.177])
    assert mujoco.mj_getTotalmass(m) - mujoco.mj_getTotalmass(base) == pytest.approx(4 * (0.055 - 0.0134))

def test_only_feet_and_torso_touch_floor():                  # 9.3
    m = build_model()
    for g in range(m.ngeom):
        name = m.geom(g).name
        hits_floor = bool(m.geom_contype[g] & m.geom_conaffinity[m.geom("floor").id])
        assert hits_floor == (name == "torso_geom" or name.endswith("_foot_geom"))
    assert np.isclose(m.geom("fl_foot_geom").friction[0], 0.9)

def test_stand_keyframe_puts_feet_exactly_on_floor():        # Review Focus 5
    m = build_model(); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id)
    mujoco.mj_kinematics(m, d)
    lowest = min(d.site(f"{l}_foot").xpos[2] for l in ("fl", "fr", "rl", "rr"))
    assert abs(lowest - load_params().foot_radius) < 1e-4
    assert np.allclose(d.ctrl, m.key("stand").qpos[7:])       # servo giữ đúng tư thế
```

(`import pytest` ở đầu file.)

- [ ] **Step 2: Chạy** — FAIL (`ModuleNotFoundError: spider.model.build`).
- [ ] **Step 3: Viết** `build_spec` trong `spider/model/build.py`:
  - Gọi `add_scene(spec)`. Thêm body `torso` có freejoint `root`, geom hộp `torso_geom` (`size` = nửa `torso_size`, `mass = torso_mass`, `contype=1`, `conaffinity=0`, màu xám).
  - Với mỗi chân trong `LEGS`: body `{leg}_coxa` đặt tại góc thân, quay quanh z theo góc của chân; khớp `hip_yaw`; capsule `coxa` dọc trục x cục bộ (màu xanh lá). Body `femur` ở đầu coxa, khớp `hip_pitch` trục (0, −1, 0), capsule tím. Body `tibia` ở đầu femur, khớp `knee` trục (0, 1, 0), capsule đen. Cuối tibia: geom cầu `{leg}_foot_geom` (`foot_radius`, ma sát `foot_friction`, `condim=3`, `contype=1`, `conaffinity=0`) và site `{leg}_foot`.
  - Geom đoạn chân mang `mass` của đoạn đó, `contype=0`, `conaffinity=0`. Geom hộp `{leg}_{kind}_servo` (kích thước servo, `mass = servo.mass`, `contype=0`, `conaffinity=0`, màu đen) đặt trên body cha của khớp.
  - Mỗi khớp: `range` = `joint_range[kind]`, `armature`/`damping`/`frictionloss` lấy từ servo của khớp đó.
  - Actuator cùng tên khớp, kiểu position: `kp = servo.stall_torque / kp_error`, `dampratio = p.dampratio`, `forcerange = ±stall_torque` (bật forcelimited), `ctrlrange` = khoảng khớp. Dùng `actuator.set_to_position(...)` nếu phiên bản ghim có; nếu không thì đặt `gainprm`/`biasprm` theo XML reference.
  - Keyframe `home`: mọi khớp 0, thân cao `torso_size[2]`, `ctrl` = 0. Keyframe `stand`: khớp = `p.stand`, `ctrl` = cùng giá trị. Độ cao thân tính bằng cách: compile một lần, đặt `qpos`, gọi `mj_kinematics`, đọc `site_xpos` thấp nhất, rồi dời z sao cho chân chạm sàn (đọc từ MuJoCo, 13.2). Sau đó `spec.add_key(...)` và compile lại.
- [ ] **Step 4: Chạy** `uv run pytest tests/test_model.py -v` — PASS. Nếu `test_total_mass_in_budget` hỏng: báo coordinator, không tự đổi ngưỡng (14.5: đổi kích thước hoặc khối lượng trong `params.toml`, ghi quyết định).
- [ ] **Step 5: Commit** — `git commit -m "feat(model): build spider MjSpec with position servos and keyframes (T1.2, T1.3)"`

---

### Task 5: Công cụ xem, ảnh chụp, bảng thành phần → cổng G1 (16.2–16.4)

**Files:**
- Create: `spider/model/parts.py`, `spider/sim/view.py`, `tests/test_view.py`
- **[coordinator]** sau khi gộp: `docs/reference/g1/README.md`, `docs/reference/g1/*.png` (sinh bằng CLI), `AGENTS.md` (mục Lệnh)

**Interfaces:**
- Consumes: Task 4 `build_model`, `ACTUATORS`; Task 3 `load_params`, `servo_for`.
- Produces:
  - `parts_table(m: mujoco.MjModel) -> list[dict]` — một dòng cho mỗi body trừ world (13 dòng), khoá: `body`, `parent`, `joint`, `range_deg` (hoặc `None`), `servo` (tên servo lái khớp của body, hoặc `None`), `mass_g` (= `m.body_mass` × 1000, gồm cả servo đặt trên body đó), `geoms` (tên các geom). Mọi số đọc từ `MjModel`.
  - `parts_markdown(m) -> str` — bảng Markdown của `parts_table`, thêm dòng tổng `mj_getTotalmass`.
  - `snapshot(m: mujoco.MjModel, out_dir: Path, keyframe: str = "stand", size=(800, 600)) -> list[Path]` — vẽ offscreen bằng `mujoco.Renderer`, 4 góc nhìn `front`, `side`, `top`, `iso` (đặt `MjvCamera` free: `lookat` = tâm thân, `distance = 0.45`, azimuth/elevation lần lượt `(180,-10)`, `(90,-10)`, `(90,-90)`, `(135,-30)`), lưu PNG bằng Pillow.
  - CLI `uv run python -m spider.sim.view [--keyframe stand|home] [--snapshot DIR] [--parts]`. Không có cờ: mở `mujoco.viewer.launch(m, d)` sau khi `mj_resetDataKeyframe` (không cần `mjpython`). `--snapshot`: chỉ chụp ảnh. `--parts`: in bảng.

- [ ] **Step 1: Test thất bại** `tests/test_view.py`

```python
import mujoco, numpy as np
from PIL import Image
from spider.model.build import build_model
from spider.model.parts import parts_table, parts_markdown
from spider.sim.view import snapshot

def test_parts_table_reads_masses_from_mujoco():
    m = build_model(); rows = parts_table(m)
    assert len(rows) == 13
    assert sum(r["mass_g"] for r in rows) == pytest.approx(mujoco.mj_getTotalmass(m) * 1000)
    knee = next(r for r in rows if r["body"] == "fl_tibia")
    assert knee["joint"] == "fl_knee" and knee["servo"] == "MG90S" and knee["range_deg"] == pytest.approx((-30, 150))
    assert "Tổng" in parts_markdown(m)

def test_snapshot_writes_four_nonblank_pngs(tmp_path):
    files = snapshot(build_model(), tmp_path)
    assert sorted(f.stem for f in files) == ["front", "iso", "side", "top"]
    for f in files:
        assert np.asarray(Image.open(f)).std() > 5     # không phải ảnh trơn
```

(`import pytest` ở đầu file.)

- [ ] **Step 2: Chạy** `uv run pytest tests/test_view.py -v` — FAIL.
- [ ] **Step 3: Viết** `spider/model/parts.py` và `spider/sim/view.py` theo Interfaces.
- [ ] **Step 4: Chạy** `uv run pytest -q` — toàn bộ PASS.
- [ ] **Step 5: [coordinator, sau khi gộp] Sinh tài liệu G1** — chạy `uv run python -m spider.sim.view --snapshot docs/reference/g1` và `uv run python -m spider.sim.view --parts`. Viết `docs/reference/g1/README.md` gồm:
  - 4 ảnh.
  - Bảng thành phần (dán từ `--parts`).
  - Bảng tham số chính kèm đường dẫn `spider/model/params.toml`.
  - Cách xem 3D: lệnh mở viewer; trong viewer bật *Rendering → Label: Joint* và *Frame: Body* để thấy tên khớp; dùng *Control* để quay thử từng servo; Space để dừng hoặc chạy vật lý; chuột phải kéo để xoay camera.
  - Checklist cho người duyệt: 4 chân hình chữ X; mỗi chân 3 khớp quay đúng chiều (hông xoay ngang, đùi nhấc lên khi dương, gối gập xuống khi dương); kích thước và tỉ lệ giống ảnh tham khảo; tổng khối lượng.
- [ ] **Step 6: [coordinator] Cập nhật** mục Lệnh trong `AGENTS.md`: `uv run python -m spider.sim.view` (xem), `--snapshot`, `--parts`.
- [ ] **Step 7: Commit** — implementer commit code sau Step 4: `git commit -m "feat(view): viewer tool, snapshots, parts table"`; coordinator commit tài liệu sau Step 6: `git commit -m "docs(g1): model snapshots and parts table for gate G1"`
- [ ] **Step 8: [coordinator] CỔNG G1 — dừng lại.** Báo người dùng: đường dẫn `docs/reference/g1/README.md` và lệnh mở viewer. Chờ người dùng duyệt. Nếu cần sửa: chỉ sửa `params.toml` (và ghi quyết định), chạy lại Step 5. Ghi kết quả duyệt thành dòng 16.6 trong `docs/decisions/16-gate-dau-tien.md`.

---

## Sau G1 (phác thảo — lập kế hoạch chi tiết riêng sau khi G1 qua)

Theo `docs/harness/task-graph.md`:

1. **T1.4 — implementer, tuần tự:** vòng mô phỏng `spider/sim/loop.py` (một luồng sở hữu `MjData`, hàng đợi lệnh, canh thời gian thật, báo hệ số thời gian thực); robot đứng ở keyframe `stand` vài giây; kiểm mô-men tĩnh bằng `mj_inverse` (9.5, 14.5). Coordinator viết **hợp đồng** (`docs/harness/contracts.md`), implementer chuyển thành code: JSON lệnh controller (`vx, vy, wz, speed, stop`), JSON trạng thái (14.11), định dạng thư mục lần chạy (11.5), móc ghi log của vòng lặp. physics-verifier và determinism-verifier soát.
2. **Tách 4 worker song song**, mỗi worker một worktree:
   - gait-worker: T1.6, IK giải trực tiếp + dáng đi.
   - checks-worker: T1.8 + T1.12, bộ kiểm tra mức 1/2, cổng khả thi trong code, script hook.
   - record-worker: T1.9, record, replay 2 chế độ, bug.
   - server-worker: T1.7 → T1.10 → T1.11, server 2 cổng, controller web, khoá, API agent, CLI `drive`.
3. **Verifier:** physics (gait, checks), determinism (record), security (server).
4. **Gộp — coordinator** (chỉ gộp nhánh và chạy test, không sửa code): test đầu-cuối: agent lái qua CLI → lần chạy được ghi → replay chính xác khớp.
5. **Cổng người dùng (14.8):** lái thử từ điện thoại qua Tailscale theo checklist.

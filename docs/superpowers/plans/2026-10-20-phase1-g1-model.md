# Phase 1 — tới cổng G1 (model 3D trong Blender → MuJoCo) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Robot nhện 4 chân × 3 khớp có model 3D nguồn trong Blender (`models/spider.blend`). Agent điều khiển Blender qua CLI. Model xuất được sang MuJoCo thành model vật lý có 12 servo. Người dùng xem model và các thành phần của nó trong Blender (cổng G1).

**Architecture:**
- Blender giữ hình học: link, origin tại khớp, trục, giới hạn, servo từng khớp (18.1, 18.4).
- `tools/blender` chạy Blender không giao diện với các script `bpy` trong `blender/` (18.7–18.9). Lệnh `export` ghi `build/model/robot.json` và mesh OBJ từng link.
- `spider/model/build.py` (môi trường `uv`) đọc file xuất cùng TOML vật lý, rồi dựng `mujoco.MjSpec`.
- Mọi đại lượng vật lý đọc từ MuJoCo (13.2).

**Tech Stack:** Blender 5.2.2 LTS (Python đi kèm 3.13, chỉ dùng `bpy` + thư viện chuẩn); Python 3.12 qua `uv`; `mujoco` ghim đúng một phiên bản (≥ 3.7.0); `pytest`; `Pillow`.

**Spec:** `docs/decisions/` (README + 01–18), đặc biệt 5.3, 6.2, 9.1–9.5, 12.7, 13.2–13.4, 14.1, 14.4–14.5, 16.2, 16.3, 17.x, 18.x. Quy ước: `AGENTS.md`, `docs/harness/task-graph.md`.

## Global Constraints

- Mọi lệnh chạy qua `uv run …` hoặc `tools/blender …`. Không dùng python hệ thống (3.9.6).
- `mujoco` ghim **một phiên bản chính xác** (`mujoco==X.Y.Z`), tối thiểu 3.7.0. Đổi phiên bản về sau = cổng người dùng.
- Script trong `blender/` chạy bằng Python của Blender: chỉ `bpy`, `mathutils`, thư viện chuẩn (có `tomllib`). **Không import `mujoco`** (18.9).
- Agent không sửa file `.blend` đang mở trong GUI. Chỉnh bằng script, mỗi lần lưu `.blend` là một commit (18.10). Agent giao tiếp với Blender qua CLI, không qua MCP (18.11).
- Đơn vị SI: m, kg, rad, N·m, s. Scene Blender: hệ mét, `scale_length = 1.0`, mọi object có scale = 1. TOML dùng độ cho góc; bộ đọc đổi sang rad.
- Không tự tính cái MuJoCo tính (13.2): khối lượng gán vào geom (`mass` hoặc `density`), quán tính do MuJoCo tính; vị trí chân đọc qua `mj_kinematics`; tổng khối lượng qua `mujoco.mj_getTotalmass`.
- Bộ giải: `integrator = implicitfast`, `timestep = 0.002` (9.2). Va chạm: chỉ cầu bàn chân và hộp thân chạm sàn, không tự va chạm (9.3). Ma sát chân 0.9, `condim = 3`.
- Viewer MuJoCo là công cụ riêng `mujoco.viewer.launch`, không dùng `mjpython` (14.1).
- Vai trò (17.2–17.6): mỗi task do **một subagent `implementer`** làm trong worktree riêng, lần lượt. Implementer ghi `pyproject.toml`, `uv.lock`, `.gitignore`, `spider/`, `blender/`, `models/`, `tools/blender`, `tests/`. Các bước **[coordinator]** (ghi `docs/`, `AGENTS.md`) do phiên chính làm sau khi gộp bằng `git merge --ff-only`.
- Hook `pre-commit` (kb check + selftest) phải qua ở mọi commit.

### Quy ước model trong Blender (các task sau dựa vào đây)

- Mọi object của robot nằm trong collection `robot`. Cây cha–con giữa các object chính là cây động học.
- **Link** là object mesh tên `torso`, `{leg}_coxa`, `{leg}_femur`, `{leg}_tibia`, với `leg ∈ {fl, fr, rl, rr}` (trước-trái, trước-phải, sau-trái, sau-phải).
  - Trục x hướng trước, y sang trái, z lên.
  - Origin của link đặt tại khớp nối nó với cha. Trục x cục bộ hướng dọc đoạn chân, ra ngoài.
- **Custom property trên mỗi link trừ `torso`:**
  - `joint` (tên khớp `{leg}_hip_yaw`, `{leg}_hip_pitch`, `{leg}_knee`)
  - `kind` (`hip_yaw`, `hip_pitch`, `knee`)
  - `axis` (3 số, trong khung cục bộ của link)
  - `range_deg` (2 số)
  - `servo` (tên trong `spider/model/servos.toml`)
- **Trục khớp:** `hip_yaw` = (0, 0, 1). `hip_pitch` = (0, −1, 0), dương = nhấc đùi lên. `knee` = (0, 1, 0), dương = gập cẳng xuống.
- **Servo:** object mesh hộp `{leg}_{kind}_servo` làm con của link cha của khớp nó lái. Vỏ servo nằm trên body cha: servo `hip_yaw` trên `torso`, `hip_pitch` trên `coxa`, `knee` trên `femur`.
- **Bàn chân:** Empty kiểu sphere `{leg}_foot`, con của `{leg}_tibia`, `empty_display_size` = bán kính.
- **Bố trí chữ X (14.4):** gốc chân tại góc thân `(±0.05, ±0.04, 0)`, hướng `fl = +45°`, `fr = −45°`, `rl = +135°`, `rr = −135°`. Kích thước khởi điểm: thân 0.10 × 0.08 × 0.010 m (tấm phẳng như ảnh; bản đầu 0.035 m vượt ngân sách khối lượng, xem ledger Task 5); coxa 0.03, femur 0.055, tibia 0.075 m; bán kính đoạn chân 0.006 m; bán kính bàn chân 0.008 m; khoảng khớp `hip_yaw [−60, 60]`, `hip_pitch [−90, 90]`, `knee [−30, 150]` độ; servo mặc định `MG90S`.

### Định dạng `build/model/robot.json` (hợp đồng Blender → MuJoCo)

```json
{ "format": 1, "blender_version": "5.2.2", "source": "models/spider.blend", "source_sha256": "…",
  "links": [ { "name": "fl_femur", "parent": "fl_coxa",
               "pos": [x,y,z], "quat": [w,x,y,z],          // so với link cha, đơn vị m
               "joint": {"name": "fl_hip_pitch", "kind": "hip_pitch", "axis": [0,-1,0], "range": [lo,hi]},  // rad; torso: null
               "servo": "MG90S", "mesh": "meshes/fl_femur.obj",
               "servos_on_body": [ {"name": "fl_knee_servo", "drives": "fl_knee", "mesh": "meshes/fl_knee_servo.obj"} ],
               "foot": null } ] }                            // tibia: {"name":"fl_foot","pos":[…],"radius":0.008}
```

Mesh OBJ ghi trong **khung cục bộ của object** (origin = khớp). `pos`/`quat` tính bằng `parent.matrix_world.inverted() @ child.matrix_world`. Quaternion theo thứ tự (w, x, y, z), khớp với cả `mathutils` lẫn MuJoCo.

## Review Focus

1. **Object bị scale khác 1, hoặc scene không ở hệ mét / `scale_length ≠ 1`** (lỗi đơn vị kinh điển): `inspect` phải báo lỗi có cấu trúc, nêu tên object, không xuất. → Task 4.
2. **Custom property thiếu hoặc sai**: thiếu `axis`, khoảng khớp rộng hơn hành trình servo (vd knee 190° > 180°), tên servo không có trong danh mục. `inspect` phải báo lỗi và liệt kê tên servo hợp lệ. → Task 4.
3. **Đổi servo một loại khớp trong Blender** (gối dùng MG996R): khối lượng và giới hạn lực của đúng 4 khớp gối đổi theo, các khớp khác giữ nguyên. → Task 5.
4. **Blender và MuJoCo lệch nhau** do sai quy ước pos/quat hoặc mesh: vị trí bàn chân ở tư thế `home` trong MuJoCo phải trùng vị trí Empty bàn chân trong Blender, sai số < 1e-6 m. → Task 5.
5. **Keyframe `stand` đặt robot lơ lửng hoặc chìm dưới sàn:** điểm thấp nhất của bàn chân phải chạm đúng mặt sàn. → Task 5.

---

### Task 1: Môi trường Python + MuJoCo ghim phiên bản (T0.1)

**Files:** Create `pyproject.toml`, `uv.lock`, `spider/__init__.py`, `tests/test_env.py`. Modify `.gitignore` (thêm `build/`, `.pytest_cache/`).

**Interfaces:** Produces package `spider` cài được ở chế độ editable; `uv run pytest` chạy được.

- [x] **Step 1:** `pyproject.toml`: `name = "spider"`, `requires-python = ">=3.12,<3.13"`, build backend `hatchling`, packages `["spider"]`. Chạy `uv python pin 3.12`, `uv add "mujoco>=3.7"`, `uv add Pillow`, `uv add --dev pytest`. Sửa dòng mujoco thành `mujoco==<bản vừa cài>`, rồi `uv lock`.
- [x] **Step 2: Test** `tests/test_env.py`

```python
import tomllib, importlib.metadata, pathlib, re, sys
import mujoco

def test_mujoco_pinned_exactly_and_recent_enough():
    deps = tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["dependencies"]
    pins = [d for d in deps if d.startswith("mujoco")]
    assert len(pins) == 1 and re.fullmatch(r"mujoco==\d+\.\d+\.\d+", pins[0])
    assert importlib.metadata.version("mujoco") == pins[0].split("==")[1]
    assert tuple(map(int, mujoco.__version__.split(".")[:2])) >= (3, 7)

def test_python_is_312():
    assert sys.version_info[:2] == (3, 12)
```

- [x] **Step 3:** `uv run pytest tests/test_env.py -v` → PASS.
- [x] **Step 4: Commit** `feat(env): uv project with pinned mujoco (T0.1)`. Báo phiên bản mujoco cho coordinator.
- [x] **Step 5: [coordinator]** thêm dòng 16.5 (ghim `mujoco==X.Y.Z`, Python 3.12) vào `docs/decisions/16-gate-dau-tien.md`; thêm `uv run pytest -q` vào mục Lệnh của `AGENTS.md`.

---

### Task 2: Cảnh MuJoCo + khối hộp rơi (T0.2, T0.3)

**Files:** Create `spider/sim/__init__.py`, `spider/sim/scene.py`, `tests/test_scene.py`.

**Interfaces — Produces:**
- `add_scene(spec: mujoco.MjSpec) -> None`
  - Thêm sàn `floor` (plane, `contype=0`, `conaffinity=1`), đèn, lưới.
  - Đặt `spec.option.timestep = 0.002`, `spec.option.integrator = mjINT_IMPLICITFAST`, `spec.compiler.degree = False`.
- `box_drop_spec(height: float = 0.5, half: float = 0.05) -> mujoco.MjSpec`
  - Hộp `box` có freejoint, `contype=1`, `conaffinity=0`, khối lượng 0.1 kg.

- [x] **Step 1: Test**

```python
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
```

- [x] **Step 2:** chạy → FAIL. **Step 3:** viết bằng API `MjSpec` (kiểm tên thuộc tính theo phiên bản đã ghim). **Step 4:** chạy → PASS. **Step 5: Commit** `feat(sim): scene and box-drop smoke test (T0.2, T0.3)`.
- [x] **Step 6: [coordinator]** ghi chú trong `docs/decisions/06-moi-truong-mo-phong.md`: kiểm `mjpython` → "Đã thay → 14.1".

---

### Task 3: TOML vật lý + danh mục servo (T1.1)

**Files:** Create `spider/model/__init__.py`, `spider/model/servos.toml`, `spider/model/physics.toml`, `spider/model/config.py`, `tests/test_config.py`.

**Interfaces — Produces** (`spider/model/config.py`):
- `@dataclass(frozen=True) Servo`: `name: str`, `stall_torque: float`, `speed: float`, `mass: float`, `size: tuple[float, float, float]`, `travel: float` (rad), `armature: float`, `damping: float`, `frictionloss: float`.
- `@dataclass(frozen=True) Physics`:
  - `torso_extra_mass: float` (kg, pin + mạch)
  - `density: float` (kg/m³)
  - `fill: float` (0–1)
  - `foot_friction: float`
  - `kp_error: float` (rad)
  - `dampratio: float`
  - `stand: dict[str, float]` (rad, khoá ∈ `JOINT_KINDS`)
  - `mass_budget: tuple[float, float]` (kg)
- `load_servos(path=SERVOS) -> dict[str, Servo]`
- `parse_physics(d: dict) -> Physics`; `load_physics(path=PHYSICS) -> Physics`
- Hằng `JOINT_KINDS = ("hip_yaw", "hip_pitch", "knee")`; đường dẫn `SERVOS`, `PHYSICS`.

- [x] **Step 1: `servos.toml`** (datasheet ở 4.8 V; `armature`, `damping`, `frictionloss` là **ước lượng**, ghi trong trường `source`, hiệu chỉnh ở Giai đoạn 8, 13.4):

| tên | stall_torque N·m | speed rad/s | mass kg | size m | travel_deg | armature kg·m² | damping | frictionloss |
|---|---|---|---|---|---|---|---|---|
| MG90S | 0.177 | 10.47 | 0.0134 | [0.0228, 0.0122, 0.0285] | 180 | 2e-4 | 0.01 | 0.01 |
| SG90 | 0.177 | 10.47 | 0.009 | [0.0222, 0.0118, 0.031] | 180 | 1.5e-4 | 0.01 | 0.01 |
| MG996R | 0.92 | 6.16 | 0.055 | [0.0407, 0.0197, 0.0429] | 180 | 1e-3 | 0.05 | 0.05 |

- [x] **Step 2: `physics.toml`**, mỗi trường một dòng chú thích tiếng Việt kèm đơn vị:
  - `torso_extra_mass = 0.10` (2 pin 18650 + mạch)
  - `[material] density = 1240` (PLA), `fill = 0.35` (ước lượng)
  - `[contact] foot_friction = 0.9`
  - `[actuator] kp_error_deg = 11.46`, `dampratio = 1.0`
  - `[stand_deg] hip_yaw = 0`, `hip_pitch = 30`, `knee = 100`
  - `[budget] mass_kg = [0.25, 0.35]` (9.5)
- [x] **Step 3: Test** `tests/test_config.py`: `load_physics()` đổi `knee` stand sang rad (`math.radians(100)`); `parse_physics` báo `ValueError` nêu tên trường khi `density <= 0`, `fill ∉ (0, 1]`, hoặc thiếu khoá `stand_deg.knee`; `load_servos()["MG996R"].stall_torque == 0.92` và `travel == math.radians(180)`.
- [x] **Step 4:** chạy → FAIL. **Step 5:** viết `config.py` bằng `tomllib` + `dataclasses`. **Step 6:** chạy → PASS. **Step 7: Commit** `feat(model): physics TOML and servo catalog (T1.1)`.

---

### Task 4: Blender CLI + model nguồn + `inspect` + `render` (T1.2)

**Files:** Create `tools/blender`, `blender/common.py`, `blender/build_spider.py`, `blender/inspect_model.py`, `blender/render_views.py`, `models/spider.blend` (sinh ra, commit), `tests/test_blender.py`.

**Interfaces — Produces:**
- **`tools/blender`**: executable, Python chạy bằng `uv run --script` (khối PEP 723, `requires-python = ">=3.11"`, không phụ thuộc gói ngoài).
  - Tìm Blender theo thứ tự `$BLENDER_BIN` → `blender` trên PATH → `~/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender` → `/Applications/Blender.app/Contents/MacOS/Blender`.
  - Gọi `<blender> -b --factory-startup [<file.blend>] --python blender/<script>.py -- --result <tmp.json> <args>`.
  - In đúng một dòng JSON ra stdout. Exit 0 khi `"ok": true`, exit 1 khi có lỗi.
  - Lỗi có dạng `{"ok": false, "errors": [{"check": "...", "object": "...", "msg": "...", "fix": "..."}]}` (10.7).
  - Lệnh con:
    - `version` → `{"ok": true, "blender": "5.2.2", "python": "3.13.x", "path": "..."}`
    - `build [--out models/spider.blend] [--servo kind=NAME ...] [--force]`: dựng model khởi điểm theo Quy ước. Từ chối ghi đè file đã có nếu không có `--force`.
    - `inspect [--blend models/spider.blend]` → `{"ok": true, "links": [...13 dòng...], "feet": {...}, "units": {...}}`. `feet` là vị trí thế giới của 4 Empty bàn chân và `torso_origin`, ở tư thế đang lưu (tư thế 0).
    - `exec --blend B --expr "<python bpy>"`: chạy code rồi lưu file. Chỉ dùng cho test và cho các script chỉnh model.
    - `export [--blend …] [--out build/model]` (Task 5)
    - `render [--blend …] --out DIR [--views front,side,top,iso]`: ghi PNG bằng engine Workbench, trả danh sách file.
- **`blender/common.py`**:
  - `collect(scene) -> dict`: đọc collection `robot`, trả mô tả link như `robot.json` nhưng chưa có mesh.
  - `validate(scene, servos: dict) -> list[dict]`: trả danh sách lỗi theo dạng trên.
  - Bộ đọc `servos.toml` bằng `tomllib`.
  - `write_result(path, obj)`.
- **Luật của `validate`:**
  - Scene ở hệ mét, `scale_length == 1`.
  - Mọi object trong `robot` có `scale == (1, 1, 1)` (sai số 1e-9).
  - Đủ 13 link với đúng tên. Cha đúng theo cây.
  - Mỗi link trừ `torso` có đủ `joint`, `kind`, `axis` (độ dài 1 ± 1e-6), `range_deg` (`lo < hi`, `hi − lo ≤ travel` của servo).
  - `servo` có trong danh mục (thông báo liệt kê các tên hợp lệ).
  - Có 4 Empty bàn chân.
  - Có 12 hộp servo đúng tên.

- [x] **Step 1: Test** `tests/test_blender.py` (gọi `tools/blender` bằng `subprocess`, đọc JSON; mỗi test dựng file `.blend` riêng trong `tmp_path`, không đụng `models/spider.blend`):

```python
def run(*args): ...   # subprocess.run(["tools/blender", *args]) → (returncode, json.loads(stdout))

def test_version_reports_blender_52():
    code, r = run("version"); assert code == 0 and r["blender"].startswith("5.2")

def test_build_then_inspect_has_13_links_in_x_layout(tmp_path):
    b = tmp_path / "s.blend"; assert run("build", "--out", str(b))[0] == 0
    code, r = run("inspect", "--blend", str(b)); assert code == 0
    links = {l["name"]: l for l in r["links"]}
    assert len(links) == 13 and links["fl_tibia"]["parent"] == "fl_femur"
    assert links["fl_femur"]["joint"]["axis"] == [0, -1, 0]
    assert links["rr_tibia"]["joint"]["name"] == "rr_knee"
    assert math.isclose(math.degrees(links["fl_coxa"]["joint"]["range"][1]), 60)

def test_build_refuses_to_overwrite_without_force(tmp_path): ...  # lần 2 không --force → exit 1, sha256 file không đổi

def test_inspect_rejects_scaled_object(tmp_path):                 # Review Focus 1
    # build, rồi exec: bpy.data.objects["fl_femur"].scale = (1000, 1000, 1000)
    code, r = run("inspect", "--blend", str(b)); assert code == 1
    assert any(e["check"] == "scale" and e["object"] == "fl_femur" for e in r["errors"])

def test_inspect_rejects_bad_servo_and_wide_range(tmp_path):      # Review Focus 2
    # build --servo knee=MG90 → exit 1, msg chứa "MG90S"
    # build hợp lệ, exec đặt range_deg của fl_tibia = [-30, 160] → lỗi check "range", object "fl_tibia"
```

- [x] **Step 2:** `uv run pytest tests/test_blender.py -v` → FAIL.
- [x] **Step 3:** viết `tools/blender` và `blender/*.py` theo Interfaces và Quy ước.
  - `build_spider.py` dựng mesh bằng `bpy.data`/`bmesh`, không dùng `bpy.ops`, để chạy không giao diện cho ổn định: thân là hộp; mỗi đoạn chân là trụ dọc +x cục bộ; hộp servo; Empty bàn chân.
  - Tô màu giống ảnh tham khảo: thân xám, coxa xanh lá, femur tím, tibia đen.
- [x] **Step 4:** chạy → PASS.
- [x] **Step 5: Sinh model nguồn:** `tools/blender build --out models/spider.blend`, rồi `tools/blender inspect` → `"ok": true`.
- [x] **Step 6: Commit** `feat(blender): CLI wrapper, source model, inspect and render (T1.2)`, gồm cả `models/spider.blend`.
- [x] **Step 7: [coordinator]** mục Lệnh của `AGENTS.md`: `tools/blender version|build|inspect|exec|render`.

---

### Task 5: `export` + dựng model MuJoCo (T1.3)

**Files:** Create `blender/export_model.py`, `spider/model/build.py`, `tests/test_build.py`. Modify `tools/blender` (lệnh `export`).

**Interfaces:**
- **Consumes:**
  - Task 4: `collect`, `validate`, `tools/blender`, trường `feet` của `inspect`.
  - Task 3: `load_physics`, `load_servos`, `JOINT_KINDS`.
  - Task 2: `add_scene`.
- **Produces:**
  - `tools/blender export --blend B --out D`
    - Chạy `validate` trước. Có lỗi thì exit 1, không ghi gì.
    - Ghi `D/robot.json` theo định dạng ở trên, `D/meshes/<object>.obj` (tam giác, toạ độ cục bộ, có modifier).
    - Trả `{"ok": true, "files": [...], "source_sha256": "..."}`.
  - `build_spec(export_dir: Path = Path("build/model"), physics=None, servos=None) -> mujoco.MjSpec`; `build_model(...) -> mujoco.MjModel`.
    - Mesh link: geom mesh, `density = physics.density × physics.fill`, `contype=0`, `conaffinity=0`.
    - Hộp servo: geom mesh, `mass = servo.mass`, không va chạm.
    - `torso`: thêm geom hộp `torso_geom` theo bounding box của mesh thân, `mass = torso_extra_mass`, `contype=1`, `conaffinity=0`.
    - Bàn chân: geom cầu `{leg}_foot_geom` (ma sát 0.9, `condim=3`, `contype=1`, `conaffinity=0`) và site `{leg}_foot`.
    - Khớp: `range`, `armature`/`damping`/`frictionloss` lấy từ servo của khớp.
    - Actuator position cùng tên khớp: `kp = stall_torque / kp_error`, `dampratio`, `forcerange = ±stall_torque` (forcelimited), `ctrlrange = range`. Dùng `set_to_position` nếu phiên bản ghim có, nếu không thì đặt `gainprm`/`biasprm` theo XML reference.
    - Keyframe `home` (mọi khớp 0) và `stand` (theo `physics.stand`, `ctrl` = cùng giá trị). Độ cao thân: compile, đặt `qpos`, `mj_kinematics`, đọc `site_xpos` thấp nhất, dời z để chân chạm sàn; rồi `add_key` và compile lại.
  - `ACTUATORS: list[str]` — `fl, fr, rl, rr` × `hip_yaw, hip_pitch, knee`.

- [x] **Step 1: Test** `tests/test_build.py`. Fixture `exported`: `tools/blender build` vào `tmp_path`, rồi `tools/blender export`. Fixture `inspected`: kết quả `inspect` của cùng file.

```python
def test_compiles_with_12_named_position_servos(exported):     # check:mjcf-compiles
    m = build_model(exported)
    assert [m.actuator(i).name for i in range(m.nu)] == ACTUATORS and m.nbody == 14 and m.njnt == 13

def test_total_mass_in_budget(exported):                       # 9.5
    assert 0.25 <= mujoco.mj_getTotalmass(build_model(exported)) <= 0.35

def test_actuator_limits_follow_servo(exported):               # 9.1, 12.7
    m = build_model(exported)
    assert np.allclose(m.actuator("fl_knee").forcerange, [-0.177, 0.177]) and m.joint("fl_knee").armature == 2e-4

def test_knee_override_in_blender_changes_only_knees(tmp_path): # Review Focus 3
    # build --servo knee=MG996R → export → model: rr_knee forcerange ±0.92, rr_hip_pitch ±0.177,
    # tổng khối lượng tăng đúng 4 × (0.055 − 0.0134) so với bản mặc định

def test_only_feet_and_torso_touch_floor(exported):            # 9.3
    m = build_model(exported); floor = m.geom("floor").id
    for g in range(m.ngeom):
        name = m.geom(g).name
        assert bool(m.geom_contype[g] & m.geom_conaffinity[floor]) == (name == "torso_geom" or name.endswith("_foot_geom"))

def test_feet_match_blender_at_home(exported, inspected):      # Review Focus 4
    m = build_model(exported); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("home").id); mujoco.mj_kinematics(m, d)
    for leg in ("fl", "fr", "rl", "rr"):
        got = d.site(f"{leg}_foot").xpos - d.body("torso").xpos
        want = np.subtract(inspected["feet"][leg], inspected["feet"]["torso_origin"])
        assert np.allclose(got, want, atol=1e-6)

def test_stand_keyframe_feet_on_floor(exported):               # Review Focus 5
    m = build_model(exported); d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id); mujoco.mj_kinematics(m, d)
    lowest = min(d.site(f"{l}_foot").xpos[2] for l in ("fl", "fr", "rl", "rr"))
    assert abs(lowest - m.geom("fl_foot_geom").size[0]) < 1e-4
    assert np.allclose(d.ctrl, m.key("stand").qpos[7:])
```

- [x] **Step 2:** chạy → FAIL. **Step 3:** viết `export_model.py` (OBJ tự ghi từ `evaluated_get(depsgraph).to_mesh()` và `loop_triangles`, không dùng operator xuất) và `build.py`. **Step 4:** `uv run pytest -q` → PASS. Nếu ngân sách khối lượng hỏng: báo coordinator, không tự đổi ngưỡng (14.5).
- [x] **Step 5: Commit** `feat(model): export Blender model and build MuJoCo spec (T1.3)`.

---

### Task 6: Tài liệu G1 + cổng duyệt (16.2, 16.3, 18.3)

**Files:** Create `spider/model/parts.py`, `spider/sim/view.py`, `tests/test_view.py`. **[coordinator]** sau khi gộp: `docs/reference/g1/README.md`, `docs/reference/g1/*.png`, `AGENTS.md`.

**Interfaces — Produces:**
- `parts_table(m) -> list[dict]`: 13 dòng; khoá `body`, `parent`, `joint`, `range_deg`, `servo`, `mass_g` (từ `m.body_mass`), `geoms`.
- `parts_markdown(m) -> str`: bảng và dòng `Tổng` (lấy từ `mj_getTotalmass`).
- `snapshot(m, out_dir, keyframe="stand") -> list[Path]`: 4 ảnh MuJoCo `front`, `side`, `top`, `iso`, vẽ bằng `mujoco.Renderer` + Pillow.
- CLI `uv run python -m spider.sim.view [--keyframe stand|home] [--snapshot DIR] [--parts]`: không cờ thì mở `mujoco.viewer.launch`.

- [ ] **Step 1: Test** `tests/test_view.py`:
  - Tổng `mass_g` = `mj_getTotalmass × 1000`.
  - Dòng `fl_tibia` có `joint == "fl_knee"`, `servo == "MG90S"`, `range_deg ≈ (-30, 150)`.
  - `snapshot` ghi 4 PNG có `std > 5`.
  - `tools/blender render --out tmp --views front,side,top,iso` ghi 4 PNG có `std > 5`.
- [ ] **Step 2–4:** FAIL → viết → PASS. **Step 5: Commit** `feat(view): parts table, MuJoCo viewer and snapshots`.
- [ ] **Step 6: [coordinator, sau khi gộp]** chạy `tools/blender render --out docs/reference/g1/blender`, `uv run python -m spider.sim.view --snapshot docs/reference/g1/mujoco`, và `--parts`. Viết `docs/reference/g1/README.md` gồm:
  - Ảnh Blender và ảnh MuJoCo đặt cạnh nhau.
  - Bảng thành phần.
  - Cách xem trong Blender: mở `models/spider.blend`; Outliner → collection `robot` để thấy cây link; chọn link → N-panel → Item → Custom Properties để xem `joint`, `axis`, `range_deg`, `servo`.
  - Cách xem trong MuJoCo: lệnh viewer; bật *Rendering → Label: Joint*; *Control* để quay thử từng servo.
  - Checklist cho người duyệt: 4 chân chữ X; chiều quay đúng; tỉ lệ giống ảnh tham khảo; tổng khối lượng; ảnh Blender và MuJoCo trùng nhau.
- [ ] **Step 7: [coordinator] CỔNG G1 — dừng lại.**
  - Báo người dùng: đường dẫn README, lệnh mở viewer, và `models/spider.blend`.
  - Người dùng có thể chỉnh trực tiếp trong Blender GUI rồi lưu.
  - Sau đó coordinator giao implementer chạy lại `inspect` → `export` → `uv run pytest -q` → Step 6, rồi commit `.blend`.
  - Ghi kết quả duyệt thành dòng 16.6 trong `docs/decisions/16-gate-dau-tien.md`.

---

## Sau G1 (phác thảo — lập kế hoạch chi tiết riêng sau khi G1 qua, 16.7)

1. **T1.4 — implementer:** vòng mô phỏng, robot đứng, kiểm mô-men tĩnh bằng `mj_inverse` (9.5, 14.5). Coordinator viết hợp đồng `docs/harness/contracts.md`. physics-verifier và determinism-verifier soát.
2. **Tách 4 worker** (worktree riêng): gait (T1.6), checks + hooks (T1.8, T1.12), record (T1.9), server + khoá + API + CLI `drive` (T1.7 → T1.10 → T1.11).
3. **Verifier:** physics, determinism, security. **Gộp:** coordinator chạy test đầu-cuối. **Cổng 14.8:** lái thử từ điện thoại.

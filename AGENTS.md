# AGENTS.md — Robot nhện mô phỏng

Hướng dẫn chung cho mọi agent làm việc trong repo này (Claude Code, Codex, Cursor…).
Harness theo mô hình 8 thành phần của Harness², xem [harness.toml](harness.toml).

## Dự án

Robot nhện 4 chân, mỗi chân 3 servo (12 servo), mô phỏng bằng MuJoCo trên MacBook Pro M1 Max (macOS, không có GPU NVIDIA).
Ảnh tham khảo: [docs/reference/spider-reference.png](docs/reference/spider-reference.png).

**Phase 1** (đang làm) = Giai đoạn 0 + 1:
- Robot dựng bằng khối hình đơn giản, di chuyển được trong mô phỏng vật lý chính xác.
- Điều khiển bằng tay qua trang web controller, từ điện thoại hoặc laptop, qua Tailscale.
- Agent điều khiển được qua cùng API, bằng CLI.
- Tiêu chí xong: quyết định 14.8.

Stack: model 3D nguồn trong Blender (`models/spider.blend`) → `tools/blender export` → `build/model/` → Python dựng `mujoco.MjSpec` cùng file TOML vật lý → MuJoCo (18.1, 18.4–18.6). Python 3.12 qua `uv`, phiên bản `mujoco` được ghim.

## Nguồn sự thật

| Cần biết | Xem |
|---|---|
| Mọi quyết định thiết kế | [docs/decisions/README.md](docs/decisions/README.md) và các file 01–NN |
| Quan hệ giữa quyết định, thành phần, task, kiểm tra | Knowledge graph: `uv run tools/kb.py …` (xem mục Lệnh) |
| Task và thứ tự | [docs/decisions/07-trinh-tu-task.md](docs/decisions/07-trinh-tu-task.md) |
| Ai làm gì, ai được ghi file nào | [docs/harness/task-graph.md](docs/harness/task-graph.md) |
| Bài học đã rút ra | [docs/harness/lessons.md](docs/harness/lessons.md) |
| Blog nhật ký (tiếng Anh, công khai) | [docs/journal/](docs/journal/index.md), quyết định [20](docs/decisions/20-blog-nhat-ky.md) |

## Quy trình làm việc

1. **Trước khi sửa:** tìm các quyết định liên quan, xem thay đổi ảnh hưởng tới đâu:
   `uv run tools/kb.py find <từ khoá>` rồi `uv run tools/kb.py impact <mã>`.
2. **Chỉ ghi vào file mà vai trò của mình được ghi** (task-graph.md, mục 3).
3. **Thay đổi thiết kế chưa chắc chắn:** làm theo Propose–Probe–Compose (task-graph.md, mục 6). Thử 2–3 phương án, đo bằng bộ kiểm tra, chọn theo số liệu.
4. **Quyết định mới hoặc đổi quyết định:** ghi vào `docs/decisions/` theo cách đánh dấu trong README.
   - Không xoá dòng cũ. Chuyển dòng cũ sang "Đã thay → <mã mới>".
   - Thêm thành phần, kiểm tra hay quan hệ mới thì sửa `docs/kb/curated.toml`.
   - Không sửa tay `docs/kb/graph.json`; hook tự dựng lại file này.
5. **Sửa bug:** tái hiện (replay) → viết test hồi quy → sửa → test qua (11.11). Mỗi bug có `docs/bugs/BUG-NNN.md`.
6. **Xong task:** đúc kết bài học nếu có (task-graph.md, mục 7).

## Lệnh

```sh
uv run tools/kb.py check            # kiểm knowledge graph (hook tự chạy build)
uv run tools/kb.py selftest         # chạy các câu hỏi năng lực trong docs/kb/ontology.toml
uv run tools/kb.py find servo       # tìm nút theo từ khoá
uv run tools/kb.py show 12.7        # một nút và các cạnh của nó
uv run tools/kb.py impact 12.7      # đổi 12.7 thì ảnh hưởng tới đâu
uv run tools/kb.py deps T1.11       # task nào phải xong trước
git config core.hooksPath .githooks # bật hook pre-commit, làm một lần sau khi clone
uv run pytest -q                    # chạy toàn bộ test (mujoco==3.16.0, Python 3.12)
tools/blender version               # Blender tìm thấy ở đâu, phiên bản nào (JSON một dòng); BLENDER_BIN chọn Blender, BLENDER_TIMEOUT (mặc định 300 s)
tools/blender build --out models/spider.blend [--servo knee=MG996R] [--force]  # dựng model khởi điểm
tools/blender inspect [--blend models/spider.blend]  # kiểm model theo Quy ước, in link + bàn chân
tools/blender exec --blend B --expr "<python bpy>"   # chạy code bpy rồi lưu file
tools/blender render --out DIR [--views front,side,top,iso]  # ảnh PNG (Workbench)
tools/blender export [--blend models/spider.blend] [--out build/model]  # robot.json + mesh OBJ cho MuJoCo
uv run python -m spider.sim.view [--keyframe stand|home]  # mở viewer MuJoCo (cần export trước)
uv run python -m spider.sim.view --parts                  # bảng thành phần, khối lượng đọc từ MuJoCo
uv run python -m spider.sim.view --snapshot DIR [--keyframe home]  # 4 ảnh PNG từ MuJoCo
uv run python -m spider.sim.view --video OUT.mp4 [--keyframe stand]  # video xoay quanh robot, chỉ render (không mj_step)
```

Các lệnh sẽ có ở Phase 1, thêm vào đây khi task tương ứng xong:
- chạy mô phỏng (T1.4)
- kiểm tra khả thi (T1.8)
- `replay` (T1.9)
- tạo và thu hồi khoá (T1.10)
- `drive` (T1.11)

## Luật luôn bật

Mỗi luật ghi kèm nguồn. Luật mới chỉ được thêm khi có bằng chứng, và người dùng phải duyệt (10.10, task-graph.md mục 7).

1. **Không tự tính lại cái MuJoCo đã tính:** khối lượng, quán tính, mô-men (`mj_inverse`), lực, tiếp xúc, state. Không viết code vật lý. (13.2, 13.3)
2. **Không chạy mô phỏng khi cổng khả thi báo lỗi, và không lách cổng.** Sửa tham số trước. Nếu không qua kiểm tra mô-men thì đổi kích thước chân trước, rồi mới đổi servo. Không nới biên an toàn 50%. (10.5, 14.5)
3. **Vật lý phải tái hiện được.**
   - Chỉ một luồng ghi vào `MjData`.
   - Vật lý không đọc giờ thật. Lệnh ghi theo số bước.
   - Mọi phần ngẫu nhiên đều có seed.
   - Không đổi phiên bản `mujoco` đã ghim nếu người dùng chưa duyệt.
   (9.6, 11.6, Bước 11)
4. **Bảo mật:**
   - Không mở cổng ra internet công khai. Không dùng `tailscale funnel`.
   - Không trỏ proxy hay tunnel nào vào cổng `127.0.0.1`.
   - Token không được nằm trong URL, log hay git. Chỉ lưu `sha256` của token.
   (12.9–12.14)
5. **Người luôn được ưu tiên hơn agent.** Nút dừng khẩn cấp thắng mọi lệnh. (12.15, 14.13)
6. **Việc khó đảo ngược phải hỏi người dùng trước** (task-graph.md, mục 5): push, Tailscale, khoá, nâng `mujoco`, xoá dữ liệu lần chạy hoặc bug, sửa luật này.
7. **Agent chính chỉ điều phối; việc làm giao cho subagent.** Phiên chính không viết code sản phẩm (`spider/`, `tests/`, `tools/`, `web/`, `pyproject.toml`). Subagent làm trong worktree riêng; coordinator gộp sau khi test và verifier qua. (17.2–17.6)
8. **Ưu tiên CLI hơn MCP.** Giao tiếp với Blender qua `tools/blender` (chạy không giao diện); với robot qua CLI `drive`. MCP chỉ dùng khi không có CLI tương đương. (18.7, 18.11)

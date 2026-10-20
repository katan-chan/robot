# Bước 11. Module record: ghi lần chạy, tái hiện, ghi bug, trace

Ngày: 2026-10-20.

## Yêu cầu của người dùng

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 11.1 | Duyệt harness ở Bước 10. Người dùng sẽ tự điều chỉnh cách làm việc cho hợp | [Người dùng] | Đang áp dụng |
| 11.2 | Cần module record | [Người dùng] | Đang áp dụng |
| 11.3 | Trước đó cần phần ghi bug và trace bug | [Người dùng] | Đang áp dụng |
| 11.4 | Log trong mô phỏng phải đủ để tái hiện chính xác hành vi và bug | [Người dùng] | Đang áp dụng |

## MuJoCo hỗ trợ tái hiện đến đâu

Theo tài liệu chính thức (https://github.com/google-deepmind/mujoco/blob/main/doc/computation/index.rst, mục Reproducibility):

- Mô phỏng của MuJoCo hoàn toàn tất định. Cùng một state, gọi `mj_step` thì ra cùng một state tiếp theo.
- Phải lưu đủ **integration state** (`mjSTATE_INTEGRATION`), kể cả warmstart, nếu muốn giống hệt từng bit.
- Sai khác dù rất nhỏ cũng sẽ phóng to theo thời gian, nhất là khi có va chạm. Robot 4 chân va chạm liên tục, nên điểm này rất quan trọng.
- Tái hiện chính xác chỉ được bảo đảm khi **cùng phiên bản MuJoCo và cùng kiến trúc máy**. Đổi phiên bản hoặc đổi hệ điều hành thì quỹ đạo sẽ khác.

Hệ quả: chỉ cần ghi lại model, state ban đầu và chuỗi lệnh điều khiển là chạy lại ra đúng y hệt, với điều kiện giữ nguyên phiên bản `mujoco`.

## Đề xuất thiết kế

| # | Đề xuất | Người chốt | Trạng thái |
|---|---|---|---|
| 11.5 | Mỗi lần chạy mô phỏng tự tạo một thư mục `runs/<thời gian>-<mã>/` gồm 5 file (xem dưới) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.6 | Lệnh từ trang web ghi theo **số bước mô phỏng**, không theo giờ thật. Lệnh chỉ áp dụng ở ranh giới bước | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.7 | Lệnh `replay` chạy lại một lần chạy từ thư mục của nó, so khớp với các checkpoint. Có thể dừng ở bước N để xem | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.8 | Mỗi bug có một file `docs/bugs/BUG-NNN.md` và giữ lại thư mục lần chạy gây bug | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.9 | Sửa bug xong thì lần chạy đó thành **test hồi quy**: replay và khẳng định lỗi không còn. Hook `pre-commit` chạy các test này | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.10 | Trang web có nút "Báo bug": đánh dấu bước hiện tại và tạo khung `BUG-NNN.md` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.11 | Thêm luật vào `AGENTS.md`: sửa bug phải theo thứ tự tái hiện → test hồi quy → sửa → test qua | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.12 | Định dạng: JSON/JSONL cho manifest, lệnh, sự kiện; `.npz` (numpy) cho dữ liệu số. Công cụ xem như Rerun hay MCAP để sau, chỉ thêm khi cần | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

### Thư mục một lần chạy (11.5)

| File | Nội dung | Dùng để |
|---|---|---|
| `manifest.json` | Commit git (và có sửa chưa commit hay không), bản sao file tham số và MJCF, mã băm model, phiên bản `mujoco`, Python, macOS/kiến trúc, timestep, seed, dòng lệnh đã chạy | Dựng lại đúng model và môi trường |
| `inputs.jsonl` | Mọi lệnh điều khiển (từ web hoặc script) kèm số bước. Thêm `ctrl` của 12 servo ở mỗi nhịp điều khiển | Chạy lại y hệt. Ghi cả `ctrl` để replay được kể cả khi code dáng đi đã đổi |
| `checkpoints.npz` | Integration state đầy đủ ở bước 0 và mỗi 1 giây mô phỏng | Nhảy nhanh tới gần chỗ bug. Phát hiện replay bị lệch |
| `trace.npz` | Mỗi nhịp điều khiển (khoảng 50 Hz): thời gian, `qpos`, `qvel`, `ctrl`, lực actuator, cảm biến, số tiếp xúc, pha dáng đi, điểm đích IK | Trace: lần theo nguyên nhân |
| `events.jsonl` | Cảnh báo của MuJoCo (`mjData.warning`), kiểm tra 8.5 bị vi phạm, actuator bão hoà, web kết nối/ngắt, nút "Báo bug" | Tìm nhanh lúc có chuyện |

Ước tính dung lượng: khoảng 1–2 MB mỗi phút mô phỏng. `runs/` không commit vào git. Chỉ thư mục lần chạy gây bug được giữ lại trong `docs/bugs/`.

### Trace: lần theo chuỗi nguyên nhân

Mỗi nhịp điều khiển ghi đủ các tầng, nên lần ngược được từ triệu chứng về nguyên nhân:

```
lệnh web → pha dáng đi → điểm đích IK → ctrl servo → lực actuator → tiếp xúc chân → chuyển động thân
```

Ví dụ: robot ngã ở giây 12.4.
1. Replay tới giây 12.
2. Xem trace: điểm đích IK của chân sau-phải nằm ngoài tầm với, servo bão hoà, chân không chạm sàn đúng lúc.
3. Nguyên nhân nằm ở tầng IK, không phải ở vật lý.

Agent đọc trace qua một script tóm tắt, không đọc nguyên file số.

### Quy tắc để tái hiện được (bắt buộc)

- Chỉ một luồng mô phỏng ghi vào `MjData` (9.6).
- Vật lý không bao giờ đọc giờ thật. Lệnh web được xếp hàng và áp dụng ở bước kế tiếp, kèm số bước đó.
- Mọi nguồn ngẫu nhiên đều có seed và seed được ghi vào manifest.
- Ghim phiên bản `mujoco`. Bug ghi bằng phiên bản cũ, khi nâng cấp, phải ghi lại từ đầu.
- Tắt đa luồng bên trong MuJoCo nếu có.

### Mẫu `docs/bugs/BUG-NNN.md` (11.8)

```
# BUG-NNN: <tóm tắt>
- Trạng thái: mở | đã tái hiện | đã sửa
- Lần chạy: docs/bugs/BUG-NNN/run/  (bước <a>–<b>)
- Tái hiện: uv run ... replay docs/bugs/BUG-NNN/run --stop <bước>
- Mong đợi / Thực tế:
- Trace cho thấy:
- Nguyên nhân gốc:
- Cách sửa:
- Test hồi quy:
```

## Liên quan

- Kiến trúc web 9.6 phải theo 11.6.
- Bộ kiểm tra khả thi (Bước 10) ghi kết quả vào `events.jsonl` của lần chạy.

## Trả lời câu hỏi mở

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 11.13 | Repo lưu trên git | [Người dùng] | Đang áp dụng |
| 11.14 | Có thể dùng thêm agent khác ngoài Claude Code | [Người dùng] | Đang áp dụng |
| 11.15 | Vì 11.14: `AGENTS.md` là nguồn quy ước chung. Giữ hook cho cả Claude Code (`.claude/settings.json`) và Codex (`.codex/hooks.json`). Hai lớp không phụ thuộc agent là git `pre-commit` và cổng trong code, áp dụng cho mọi agent | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 11.16 | `.gitignore` bỏ qua `runs/`, `.venv/`, `__pycache__/`. Thư mục lần chạy gây bug nằm trong `docs/bugs/` và được commit | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Câu hỏi mở

- Có đẩy repo lên remote (GitHub…) không? Hiện chỉ dùng git trên máy.

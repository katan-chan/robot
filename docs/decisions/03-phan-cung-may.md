# Bước 3. Phần cứng máy và stack

Ngày: 2026-10-20.

## Máy hiện có

| Thành phần | Thông số |
|---|---|
| Máy | MacBook Pro (MacBookPro18,2) |
| Chip | Apple M1 Max, CPU 10 nhân (8P + 2E), GPU 32 nhân, Metal 4 |
| RAM | 32 GB |
| Ổ đĩa | Còn trống 673 GB |
| macOS | 26.5 |
| Blender | 5.2.2, cài qua Steam: `~/Library/Application Support/Steam/steamapps/common/Blender/Blender.app` |
| Python | Hệ thống 3.9.6 (quá cũ). `uv` có sẵn 3.11 và 3.12 |
| Công cụ | `brew`, `uv` |

## Đánh giá

- Chạy tốt: Blender, MuJoCo (native ARM), train RL quy mô nhỏ trên CPU, LLM agent qua MCP.
- Không chạy được: Isaac Sim/Isaac Lab. MJX và MuJoCo Warp không có đường chạy GPU hữu ích trên Apple Silicon (MJX chạy được trên JAX CPU nhưng không lợi hơn MuJoCo C; jax-metal còn thử nghiệm; Warp cần NVIDIA). Dùng MuJoCo C, chạy song song nhiều tiến trình.
- Lưu ý: trên macOS, chỉ `mujoco.viewer.launch_passive` bắt buộc chạy bằng `mjpython`. `python -m mujoco.viewer` và `viewer.launch()` không cần.
- Blender cài qua Steam sẽ tự cập nhật, nên phiên bản 5.2.2 sẽ thay đổi. Khi cần chạy script Blender không giao diện (`blender -b`), nên dùng một bản tải từ blender.org và giữ cố định.
- Nếu cần train lớn, thuê GPU cloud riêng cho bước train.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 3.1 | Stack: Blender 5.2 → MJCF → MuJoCo + Python 3.12 (`uv`) | [Claude đề xuất] | Đã thay → 3.2 |
| 3.2 | Stack: file tham số → script Python sinh MJCF → MuJoCo, Python 3.12 (`uv`). Blender chỉ xuất mesh hiển thị cho từng link | [Claude đề xuất] | Chờ chốt |

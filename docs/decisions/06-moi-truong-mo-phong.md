# Bước 6. Việc đầu tiên: dựng môi trường mô phỏng

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 6.1 | Việc đầu tiên: dựng thành công môi trường mô phỏng, trước khi làm robot | [Người dùng] | Đang áp dụng |
| 6.2 | Nội dung bước này (xem dưới) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Nội dung (6.2)

**Làm:**
- Tạo project Python 3.12 bằng `uv` ngay trong repo. Cài `mujoco`.
- Một file cảnh MJCF: sàn phẳng, ánh sáng, trọng lực, và một khối hộp thả từ trên cao để thử vật lý.
- Mở cảnh bằng viewer của MuJoCo (`python -m mujoco.viewer`; chỉ `launch_passive` mới bắt buộc `mjpython`).
- Một script kiểm tra chạy không cần màn hình: mô phỏng vài giây, xác nhận khối hộp rơi xuống và nằm yên trên sàn.
- Kiểm tra `uv run mjpython` có chạy không. Với Python do uv quản lý, lệnh này hay lỗi `Library not loaded: @rpath/libpython3.12.dylib`. Nếu lỗi thì ghi lại cách xử lý.
- Ghim phiên bản `mujoco` trong uv, vì MuJoCo ra bản mới vài tuần một lần và hay đổi API actuator.

**Thành công khi:**
- Script kiểm tra chạy qua. Đây là điều kiện bắt buộc.
- Viewer mở được và thấy khối hộp rơi. Điều kiện phụ, vì kiến trúc trang web (Bước 9) có thể không dùng viewer.

**Chưa làm:** robot nhện, Blender, cảm biến, học đi.

## Liên quan

- ~~Câu hỏi "đứng yên hay bước đi" ở Bước 5 hoãn tới khi làm robot.~~ → đã chốt ở 8.2.

# Nhật ký brainstorm: Robot nhện mô phỏng

> **Đã thay.** File này là bản nháp đầu, viết gộp một file và dừng ở Bước 5. Nội dung đúng và mới nhất nằm trong các file 01–10, xem [README.md](README.md). Chỉ giữ để tham khảo, không sửa tiếp.

Ghi lại từng bước của quá trình brainstorm, theo thứ tự thời gian.
Mỗi quyết định ghi rõ ai chốt: **[Người dùng]** hoặc **[Claude đề xuất]** (đề xuất thì người dùng còn sửa được).

---

## Bước 1. Tìm hiểu quy trình Blender → mô phỏng (2026-10-20)

Kết quả tìm hiểu:

- Quy trình phổ biến: dựng hình trong Blender (mỗi link một object, origin đặt ở trục khớp, đơn vị mét, Z-up, apply scale), sau đó export mesh theo từng link. Động học (joint, giới hạn, khối lượng, inertia) mô tả bằng URDF/MJCF.
- Armature của Blender không trở thành khớp vật lý trong simulator. Blender chỉ dùng để làm hình, khớp phải khai báo trong URDF/MJCF.
- Collision mesh nên đơn giản: dưới 1000 mặt mỗi link, hoặc dùng khối cơ bản.
- Add-on hỗ trợ: Phobos (DFKI, viết cho Blender 3.x, có thể không chạy trên 5.x), LinkForge (trên extensions.blender.org).
- MuJoCo tự gộp các khớp fixed và mặc định dùng collision mesh thay cho visual mesh.

## Bước 2. Cách simulator tương tác với agent (2026-10-20)

- **RL agent**: vòng lặp Gymnasium `obs → action → env.step() → reward`, chạy 50–1000 Hz.
- **LLM agent**: gọi tool qua MCP (đã có vài MuJoCo MCP server). LLM ra quyết định chậm cỡ giây, nên chỉ ra lệnh cấp cao. Bộ điều khiển cấp thấp chạy bên trong sim.
- **ROS 2**: MCP server chạy như một ROS node, publish/subscribe topic. Trên macOS cài khó.
- Hệ quả cho model: joint phải đặt tên rõ ràng, có actuator kèm giới hạn, có cảm biến, collision đơn giản.

## Bước 3. Kiểm tra phần cứng máy (2026-10-20)

- MacBook Pro M1 Max: CPU 10 nhân (8P + 2E), GPU 32 nhân, RAM 32 GB, ổ đĩa còn 673 GB, macOS 26.5.
- Blender 5.2.2, cài qua Steam: `~/Library/Application Support/Steam/steamapps/common/Blender/Blender.app`.
- Python hệ thống là 3.9.6, quá cũ. `uv` có sẵn Python 3.11 và 3.12. Có `brew`.
- Chạy tốt: Blender, MuJoCo (native ARM), train RL quy mô nhỏ trên CPU.
- Không chạy được: Isaac Sim/Isaac Lab và MuJoCo MJX trên GPU (cần NVIDIA/CUDA).
- Lưu ý: viewer tương tác của MuJoCo trên macOS phải chạy bằng `mjpython`.

**[Claude đề xuất]** Stack: Blender 5.2 → MJCF → MuJoCo + Python 3.12 (`uv`).

## Bước 4. Mục tiêu dự án (2026-10-20)

- **[Người dùng]** Loại robot: nhện 4 chân, giống ảnh tham khảo (mỗi chân 3 servo, tổng 12 servo).
- **[Người dùng]** Hiện chưa có gì: chưa có robot thật, chưa có file 3D.
- **[Người dùng]** Mục tiêu lâu dài:
  1. Chạy được trong mô phỏng.
  2. Gắn cảm biến dựng bản đồ để di chuyển trên đa tạp bất kỳ, kể cả mặt gấp khúc và có vật cản.
  3. Dùng LLM hoặc RL để học di chuyển.
  4. Thêm camera và loa để nói chuyện.

## Bước 5. Phạm vi trước mắt (2026-10-20)

- **[Người dùng]** Tạm bỏ qua phần học. Trước tiên làm ra được con robot.
- **[Người dùng]** Phần cứng thật quyết định sau. Trước tiên chốt bản minimal.

Bản minimal **[Claude đề xuất]**:

- Con nhện 4 chân trong MuJoCo, đứng vững dưới trọng lực trên sàn phẳng.
- Có thể cử động từng khớp bằng thanh trượt trong viewer.
- Mỗi chân 3 khớp: xoay ngang ở hông (yaw), nhấc đùi (pitch), gập gối. Tổng 12 khớp, mỗi khớp một actuator điều khiển theo vị trí (kiểu servo).
- Kích thước cỡ con trong ảnh: thân khoảng 10 cm, chân duỗi khoảng 15 cm.
- Hình dáng dựng trong Blender. Collision dùng khối hộp và trụ đơn giản.
- Kích cỡ việc: nhỏ, mô tả trong chat là đủ, không cần tài liệu thiết kế riêng.

Chưa làm: học đi, cảm biến, địa hình, camera, loa, LLM, robot thật.

---

## Câu hỏi còn mở

1. Bản minimal chỉ cần đứng và cử động khớp bằng tay, hay phải bước đi được bằng một dáng đi lập trình sẵn (không học)?
2. Con nhện có cần bò được trên tường dựng đứng và trần nhà (chân bám dính) không, hay trọng lực luôn kéo xuống? Để lại tới giai đoạn địa hình.
3. Người dùng tự chọn công cụ, hay giao cho Claude? Hiện mặc định Blender 5.2 + MuJoCo + Python 3.12.

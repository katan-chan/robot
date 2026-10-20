# Bước 7. Trình tự các task

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 7.1 | Sắp xếp toàn bộ task theo trình tự phù hợp | [Người dùng] | Đang áp dụng |
| 7.2 | Trình tự dưới đây | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 7.3 | Làm đúng động học và vật lý bằng khối hình đơn giản trước. Hình đẹp từ Blender làm sau và chỉ là lớp vỏ | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Lý do sắp xếp

- Mỗi giai đoạn chỉ bắt đầu khi giai đoạn trước đã chạy được và đã kiểm tra.
- Hình từ Blender không ảnh hưởng tới vật lý, với điều kiện geom hiển thị đặt `contype=0 conaffinity=0 mass=0` (hoặc mỗi body khai báo `<inertial>` riêng). Nếu không, MuJoCo vẫn tính khối lượng từ mesh hiển thị. Vì vậy Blender đứng sau robot khối hình, để không phải dựng lại hình mỗi lần đổi kích thước.
- Học đi cần cảm biến (làm đầu vào), nên cảm biến đứng trước RL.
- Địa hình khó cần robot đã đi được trên sàn phẳng.
- LLM chỉ ra lệnh cấp cao, nên cần sẵn một bộ đi được để điều khiển.
- Phần cứng thật để cuối, theo quyết định 5.2.

## Trình tự

### Giai đoạn 0. Môi trường mô phỏng (Bước 6)
- T0.1 Tạo project Python 3.12 bằng `uv`, cài `mujoco`.
- T0.2 Cảnh MJCF: sàn, ánh sáng, trọng lực, một khối hộp rơi. Mở bằng `python -m mujoco.viewer` (viewer là điều kiện phụ, xem Bước 6).
- T0.3 Script kiểm tra không cần màn hình: khối hộp rơi và nằm yên trên sàn.

**Xong khi:** viewer chạy và script kiểm tra qua.

### Giai đoạn 1. Robot nhện bằng khối hình đơn giản
- T1.1 Một file tham số duy nhất (theo 5.3): kích thước thân, chiều dài các đoạn chân, giới hạn góc, lực servo, khối lượng.
- T1.2 Script sinh MJCF từ file tham số: thân hộp, chân trụ, 4 × 3 khớp.
- T1.3 Gắn actuator điều khiển theo vị trí cho 12 khớp. Cử động bằng thanh trượt trong viewer.
- T1.4 Tư thế đứng mặc định. Kiểm tra: robot đứng vững vài giây và không có khớp nào vượt giới hạn.
- T1.5 ~~Chốt câu hỏi mở: chỉ đứng yên, hay bước đi bằng dáng đi lập trình sẵn?~~ Đã chốt: phải di chuyển được → xem Bước 8.
- T1.6 IK cho từng chân và dáng đi bò (creep) hoặc trot. Bắt buộc, theo 8.2.
- T1.7 Trang web điều khiển và server (theo 8.6). Chỉ một luồng mô phỏng được ghi vào `MjData`. Trang web chỉ gửi lệnh vào hàng đợi. Kiến trúc chờ chốt ở Bước 9.
- T1.8 Bộ kiểm tra tự động "mô phỏng chính xác" (theo 8.5), có ngưỡng số. Chạy không cần màn hình và không phụ thuộc đồng hồ thật.

**Xong khi:** robot di chuyển được trên sàn phẳng khi điều khiển từ trang web, và bộ kiểm tra T1.8 chạy qua.

### Giai đoạn 2. Hình dáng từ Blender
- T2.1 Dựng thân và các đoạn chân trong Blender theo đúng tham số ở T1.1, origin đặt tại trục khớp.
- T2.2 Export mesh từng link, gắn làm visual. Collision giữ khối đơn giản.
- T2.3 Kiểm tra mesh khớp đúng vị trí với khung động học, và tổng khối lượng robot không đổi so với Giai đoạn 1.

**Xong khi:** robot trong viewer trông giống ảnh tham khảo và vẫn đứng/đi như Giai đoạn 1.

### Giai đoạn 3. Cảm biến cơ bản
- T3.1 Encoder khớp (góc, vận tốc), IMU trên thân, cảm biến chạm ở bàn chân.
- T3.2 Hàm đọc toàn bộ cảm biến thành một vector quan sát.

**Xong khi:** đọc được số liệu đúng khi robot đứng, nghiêng, nhấc chân.

### Giai đoạn 4. Học đi (RL) trên sàn phẳng
- T4.1 Bọc mô phỏng thành môi trường Gymnasium (`reset`, `step`, reward).
- T4.2 Train PPO trên CPU.
- T4.3 So sánh với dáng đi lập trình sẵn từ T1.6.

**Xong khi:** policy học được đi thẳng và rẽ trên sàn phẳng.

### Giai đoạn 5. Địa hình và bản đồ
- T5.1 Chốt câu hỏi mở: có bò tường và trần không?
- T5.2 Địa hình: dốc, bậc, mặt cong, mặt gấp khúc, vật cản (heightfield và mesh).
- T5.3 Cảm biến bản đồ: camera độ sâu hoặc dãy tia đo khoảng cách (kiểu lidar).
- T5.4 Dựng bản đồ cục bộ, đưa vào quan sát của policy, train lại trên địa hình.

**Xong khi:** robot vượt được địa hình ngẫu nhiên có vật cản.

### Giai đoạn 6. Tầng LLM
- T6.1 MCP server mỏng: đọc trạng thái, ra lệnh "đi tới", "quay", "dừng".
- T6.2 LLM nhận lệnh bằng lời, gọi tool, policy RL thực thi.

**Xong khi:** nói một câu như "đi tới cái hộp đỏ", robot làm đúng.

### Giai đoạn 7. Camera và loa
- T7.1 Camera RGB trong sim, đưa ảnh cho LLM có thị giác.
- T7.2 Nhận giọng nói và phát giọng nói (STT/TTS) chạy trên máy Mac.

**Xong khi:** nói chuyện được với robot và robot trả lời bằng giọng.

### Giai đoạn 8. Robot thật
- T8.1 Chọn servo, vi điều khiển, pin, cảm biến theo thông số đã dùng trong sim.
- T8.2 In 3D, lắp ráp, hiệu chỉnh (calibration) cho khớp với sim.
- T8.3 Chuyển policy từ sim sang robot thật (sim2real).

## Ghi chú

- Mã task có tiền tố T (T1.6) để không trùng với mã quyết định (5.1, 8.2).
- Phase 1 = Giai đoạn 0 + Giai đoạn 1 (quyết định 8.4, chờ chốt).
- Thứ tự Giai đoạn 4 → 6 giả định quyết định 4.7 (RL đi, LLM ở tầng trên), hiện chờ chốt.
- Giai đoạn 6 có thể đưa lên ngay sau Giai đoạn 4 nếu muốn điều khiển bằng lời sớm. Khi đó LLM chỉ điều khiển được trên sàn phẳng.

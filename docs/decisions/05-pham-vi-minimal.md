# Bước 5. Phạm vi trước mắt: bản minimal

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 5.1 | Tạm bỏ qua phần học. Trước tiên làm ra được con robot | [Người dùng] | Đang áp dụng |
| 5.2 | Phần cứng thật quyết định sau. Trước tiên chốt bản minimal | [Người dùng] | Đang áp dụng |
| 5.3 | Model phải chỉnh được về sau: kích thước, số khớp, giới hạn servo nằm ở một chỗ, đổi xong là sinh lại model | [Người dùng] (Claude diễn giải từ câu "khả năng sau này phải chỉnh được") | Đang áp dụng |
| 5.4 | Nội dung bản minimal (xem dưới) | [Claude đề xuất] | Đã thay → xem Bước 7, 8 (hình dáng làm sau, điều khiển qua web, phải di chuyển được) |
| 5.5 | Kích cỡ việc: nhỏ, mô tả trong chat và trong file này là đủ | [Claude đề xuất] | Chờ chốt |

## Nội dung bản minimal (5.4)

- Con nhện 4 chân trong MuJoCo, đứng vững dưới trọng lực trên sàn phẳng.
- Cử động từng khớp bằng thanh trượt trong viewer.
- Mỗi chân 3 khớp: xoay ngang ở hông (yaw), nhấc đùi (pitch), gập gối. Tổng 12 khớp, mỗi khớp một actuator điều khiển theo vị trí (kiểu servo).
- Kích thước khởi điểm cỡ con trong ảnh: thân khoảng 10 cm, chân duỗi khoảng 15 cm. Chỉnh được theo 5.3.
- Hình dáng dựng trong Blender. Collision dùng khối hộp và trụ đơn giản.

Chưa làm: học đi, cảm biến, địa hình, camera, loa, LLM, robot thật.

## Câu hỏi mở

- ~~Bản minimal chỉ cần đứng và cử động khớp bằng tay, hay phải bước đi được bằng dáng đi lập trình sẵn (không học)?~~ → đã chốt ở 8.2: phải di chuyển được.

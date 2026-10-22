# Bước 19. Chở tải 2 kg, ưu tiên thăng bằng

Ngày: 2026-10-22. Chốt tại cổng G1, sau khi người dùng xem model 330 g trong MuJoCo.

## Bối cảnh

- Người dùng thấy model 330 g kém vững, muốn robot chở được tải và lấy thăng bằng làm khả năng chính.
- Mức tải đã cân nhắc: 5–10 kg cần động cơ không chổi than và khung nhôm, khác hẳn ảnh tham khảo. 3 kg không qua kiểm tra mô-men với cả 3 cấu hình thử. Người dùng chốt 2 kg.
- Số liệu đo bằng mô phỏng, theo Propose–Probe–Compose. Script đo ở nhánh `worktree-agent-a696800fd5e6798b8` (`probe/payload_3kg.py`, commit da08237).

Kết quả đo, tải 2 kg, đứng 3 chân, tỉ lệ mô-men lớn nhất so với mô-men cực đại:

| Cấu hình | Chân (coxa / femur / tibia) | Dáng đứng | Khớp nặng nhất | Dốc tối đa, μ 0.9 | Lực đẩy ngang chịu được |
|---|---|---|---|---|---|
| A | 0.06 / 0.11 / 0.15 m | xoè | hip_pitch 0.62 | 12° | 435 / 400 N |
| B | 0.05 / 0.09 / 0.12 m | xoè | hip_pitch 0.52 | 17° | 515 / 435 N |
| C | 0.06 / 0.11 / 0.15 m | khép | knee 0.59 | 24° | 185 / 120 N |
| **B-40** | như B, `hip_pitch` dùng DS3240 | xoè | **hip_pitch 0.45** | 18° | 415 / 455 N |

Cả 4 trượt trước khi đổ. Lực đẩy chủ yếu đo độ trượt.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 19.1 | Tải mục tiêu **2 kg**, đặt thấp ở giữa thân. Thăng bằng là khả năng chính | [Người dùng] | Đang áp dụng |
| 19.2 | Robot vẫn giống ảnh tham khảo (4.1): 4 chân xếp chữ X, chân xoè. Chỉ to hơn | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 19.3 | Kích thước theo cấu hình B: thân tấm 0.20 × 0.16 × 0.010 m; gốc chân `(±0.10, ±0.08, 0)`; coxa 0.05, femur 0.09, tibia 0.12 m; bán kính đoạn chân 0.010 m; bán kính bàn chân 0.012 m. Dáng đứng giữ `hip_pitch 30°`, `knee 100°`. Thay kích thước ở 14.4 | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 19.4 | Servo: `hip_pitch` dùng loại 40 kg·cm (DS3240); `hip_yaw` và `knee` dùng loại 35 kg·cm (DS3235). Thông số trong danh mục là **ước lượng**, hiệu chỉnh theo datasheet hoặc đo servo thật (13.4) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 19.5 | Nguồn: pin LiPo 2S 7.4 V, 2–3 Ah, kèm mạch hạ áp chịu 20–30 A. `torso_extra_mass` = 0.20 kg (ước lượng) | [Claude đề xuất] | Đang áp dụng |
| 19.6 | Tải là một hộp 2 kg, 0.15 × 0.12 × 0.05 m, đặt giữa mặt trên thân. Khối lượng và kích thước tải nằm trong `physics.toml`. Đặt khối lượng tải bằng 0 thì chạy được bản không tải | [Claude đề xuất] | Đang áp dụng |
| 19.7 | Ngân sách khối lượng tính riêng cho robot không tải: khoảng 1.1–1.45 kg (đo: 1.28 kg). Tổng có tải không quá 3.5 kg. Thay ngân sách 250–350 g ở 9.5 | [Claude đề xuất] | Đang áp dụng |
| 19.8 | Kiểm tra mô-men tĩnh (thay số liệu ở 9.5): **có tải 2 kg**, đứng 3 chân, mọi khớp không quá 50% mô-men cực đại. Không nới 50% (10.5, 14.5). Số đo hiện tại: hip_pitch 0.45, knee 0.25, hip_yaw 0.03 | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 19.9 | Hai lỗi phát hiện khi đo, sửa theo 11.11 trước khi qua G1: **BUG-001** ma sát bàn chân không có tác dụng (sàn để mặc định 1.0, MuJoCo lấy giá trị lớn hơn); **BUG-002** chân bò dần khi chịu lực ngang liên tục (thiết lập bộ giải tiếp xúc hiện tại) | [Claude đề xuất] | Đang áp dụng |
| 19.10 | Khi xem hay kiểm model thì chỉ mở MuJoCo. Blender vẫn là nơi chỉnh hình học (18.1), chỉ mở khi cần sửa. Thay phần "xem trong Blender" của 18.3 | [Người dùng] | Đang áp dụng |

## Ghi chú cho task sau

- Dưới tải, servo bị lún: lệnh nhấc chân 50 mm nhưng chân chỉ lên khoảng 20 mm. Dáng đi (T1.6) phải tính tới, hoặc chỉnh `kp_error` khi có số đo servo thật.
- Ma sát 0.6 thì dốc tối đa khoảng 16°, do ma sát giới hạn chứ không do servo. Bàn chân cần bọc cao su.
- Tải nặng làm trọng tâm cao hơn. Đặt tải càng thấp càng tốt.
- Số đo 19.8 phụ thuộc cách đo (physics-verifier, model cấu hình B có tải, sau BUG-002). Đứng 3 chân, nhấc lần lượt từng chân:
  - `mj_inverse` tại tư thế đã ổn định (`qvel = qacc = 0`), chân xấu nhất fr/rr: hip_pitch 0.448, knee 0.235, hip_yaw 0.014. Đây là số dùng cho kiểm tra 19.8, vì không dựa vào ma sát gánh lực ngang.
  - Mô phỏng giữ 1.5 s, đọc `actuator_force`: hip_pitch 0.28, knee 0.18, hip_yaw 0.06. Với bộ giải cũ (trước BUG-002) cách này cho hip_pitch 0.446.
- Đẩy ngang đột ngột (lực bậc thang 0.5·μ·m·g) theo hướng chéo 30–45° làm một bàn chân chạm giới hạn ma sát và trượt một lần khoảng 0.7 mm trong 0.5 s đầu, sau đó không bò. Đẩy tăng dần trong 0.5 s thì mọi hướng dưới 0.5 mm. Đây là rủi ro cần chốt ở G1: hạ tải xuống thấp hoặc mở rộng thế đứng nếu cần chịu được va đẩy đột ngột.

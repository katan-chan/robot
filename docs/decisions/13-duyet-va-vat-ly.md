# Bước 13. Duyệt toàn bộ, nguyên tắc tính toán và vật lý

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 13.1 | Duyệt toàn bộ các đề xuất đang chờ, batch B1–B7: 3.2, 4.7, 6.2, 7.2, 7.3, 8.3, 8.4, 9.1–9.6, 11.5–11.12, 11.15, 11.16, 12.4–12.9, 12.12–12.17 | [Người dùng] | Đang áp dụng |
| 13.2 | Cái gì MuJoCo đã tính thì đọc ra, không tự tính lại: khối lượng, quán tính, mô-men cần thiết (`mj_inverse`), lực actuator, tiếp xúc, Jacobian, state. Model dựng bằng `mujoco.MjSpec`. Ghi thành luật trong `AGENTS.md` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 13.3 | Không viết code vật lý. Toàn bộ vật lý do `mj_step` lo. Độ chính xác nằm ở **số liệu đầu vào**: hình học, khối lượng, ma sát, độ mềm tiếp xúc, bộ giải, thông số servo | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 13.4 | Phase 1 bỏ qua các hiện tượng MuJoCo không có sẵn: rơ bánh răng, vùng chết PWM, sụt áp pin, nhựa in bị cong. Bù bằng biên an toàn 50% mô-men. Xem xét lại ở Giai đoạn 8, khi có số đo từ con thật | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Phần phải tự code ở Phase 1

- IK giải trực tiếp cho chân 3 khớp.
- Bộ tạo dáng đi: biến lệnh controller thành bước chân.
- Giới hạn tốc độ servo, nếu không dùng `dcmotor`.
- So các con số đo được với ngưỡng kiểm tra.
- Ghi log, replay, khoá điều khiển, web server. Chủ yếu ghép các thư viện có sẵn.

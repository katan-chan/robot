# Bước 16. Cổng duyệt đầu tiên

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 16.1 | Bắt đầu viết kế hoạch chi tiết cho Phase 1 | [Người dùng] | Đang áp dụng |
| 16.2 | **Cổng G1**: người dùng xem được model 3D của con nhện và các thành phần của nó, trước khi làm tiếp | [Người dùng] | Đang áp dụng |
| 16.3 | G1 đặt ngay sau T1.3 (đã có tham số, model, servo). Việc trước G1: T0.1–T0.3, T1.1–T1.3. Chưa tách worker trước G1 | [Claude tự quyết] | Đang áp dụng |
| 16.4 | Cách xem ở G1: viewer MuJoCo (công cụ riêng 14.1) mở model, các khớp có tên và quay thử được. Kèm một bảng thành phần do script in ra: thân, từng đoạn chân, khớp, servo, khối lượng, kích thước, đọc từ model MuJoCo (13.2). Kèm ảnh chụp model từ vài góc | [Claude tự quyết] | Đã thay → 18.3 |
| 16.7 | Các cổng mốc sau G1 (G2, G3…) chốt sau khi G1 xong. Các cổng cố định vẫn áp dụng: việc khó đảo ngược (task-graph.md mục 5) và tiêu chí xong Phase 1 (14.8) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

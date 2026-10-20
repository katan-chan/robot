# Bước 18. Blender là nơi chỉnh model 3D chính

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 18.1 | Blender là nơi **chỉnh model 3D chính** của robot. Model được **xuất từ Blender** sang trình mô phỏng chính xác hơn (MuJoCo) để chạy vật lý | [Người dùng] | Đang áp dụng |
| 18.2 | Vật lý vẫn do MuJoCo lo (8.5, 13.3). Blender không dùng để mô phỏng vật lý | [Claude đề xuất] | Chờ chốt |
| 18.3 | Cổng G1 xem model và các thành phần **trong Blender**. Thêm: model đã xuất mở được trong MuJoCo, và bảng thành phần đọc từ MuJoCo khớp với Blender | [Claude đề xuất] | Chờ chốt |
| 18.4 | Phần vật lý không nằm trong hình học (danh mục servo, khối lượng servo và pin, ma sát, bộ giải) vẫn ở file TOML trong repo. Blender giữ hình dáng, vị trí khớp, trục khớp, giới hạn khớp, và servo nào gắn ở khớp nào | [Claude đề xuất] | Chờ chốt |
| 18.5 | Cách xuất từ Blender sang MuJoCo: chưa chốt (xem câu hỏi mở) | — | Chờ chốt |

## Quyết định cũ bị thay

- 3.2 (Python sinh model từ file tham số, Blender chỉ làm mesh hiển thị) → thay bởi 18.1.
- 7.3 (khối hình đơn giản trước, Blender làm sau) → thay bởi 18.1. Blender vào ngay Phase 1.
- 16.4 (G1 xem trong viewer MuJoCo) → thay bởi 18.3.
- Kế hoạch `docs/superpowers/plans/2026-10-20-phase1-g1-model.md` phải viết lại theo bước này.

## Câu hỏi mở

1. Xuất từ Blender bằng cách nào?
   - (a) Add-on **LinkForge**: dựng link và khớp trong Blender, có linter, xuất URDF. MuJoCo đọc URDF trực tiếp, rồi `MjSpec` thêm servo, cảnh và bộ giải. Cần kiểm tra LinkForge chạy được trên Blender 5.2. Giấy phép GPL v3, nhưng chỉ dùng như công cụ, không chép code của nó.
   - (b) Script `bpy` của dự án: đọc tên object, origin, custom property → xuất JSON mô tả robot và mesh từng link → `MjSpec` dựng MJCF.
2. Blender MCP (Blender Lab, cổng 9876) hiện chưa kết nối. Người dùng tự cài lại hay Claude hướng dẫn từng bước?

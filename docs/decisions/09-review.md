# Bước 9. Review bởi subagent

Ngày: 2026-10-20.

Có 2 reviewer:
- **Builder check**: đóng vai người thi công Phase 1, liệt kê những chỗ phải đoán.
- **Review kỹ thuật và nhất quán**: soát nội dung với tài liệu MuJoCo và mã nguồn.

Claude đã kiểm lại các tính năng MuJoCo mới mà reviewer nêu, đối chiếu với changelog chính thức:

| Tính năng | Kết quả |
|---|---|
| Actuator `dcmotor` (mô hình động cơ DC: điện cảm, cogging, ma sát LuGre) | Đúng, có từ 3.7.0 (14/4/2026) |
| Actuator cộng damping và armature "phản xạ" (scale theo gear²) vào khớp | Đúng, có từ 3.7.0 |
| Độ trễ cho actuator và cảm biến (bộ đệm lịch sử, `mjData.history`) | Đúng, có từ 3.5.0 (2/2026) |
| Actuator `pid` với `slewmax` | **Không tìm thấy** trong changelog và XML reference. Bỏ khỏi đề xuất 9.1 |
| Bindings WASM `@mujoco/mujoco` | Chưa kiểm. Chỉ cần nếu chọn vẽ robot trong trình duyệt |

Nguồn: https://mujoco.readthedocs.io/en/3.7.0/changelog.html

## Đã sửa ngay (lỗi nhất quán)

- 5.4 đổi sang **Đã thay**: hình dáng làm sau, điều khiển qua web, phải di chuyển được.
- Câu hỏi "đứng yên hay bước đi" ở Bước 5 và 6 gạch bỏ, chuyển thành "đã chốt ở 8.2".
- Bước 7: T1.6 thành bắt buộc. Thêm T1.7 (trang web điều khiển) và T1.8 (bộ kiểm tra chính xác). Giai đoạn 1 có một điều kiện "Xong khi" duy nhất.
- Mã task thêm tiền tố T để không trùng mã quyết định. Bước 4 đổi "Giai đoạn" thành "Mục tiêu".
- Bảng quyết định Bước 8 bị tách đôi bởi một dòng trống. Đã nối lại.
- `brainstorm-log.md` thêm dòng đầu ghi rõ "Đã thay", trỏ về README.
- 3.1 đổi sang **Đã thay → 3.2**: stack là file tham số → Python sinh MJCF → MuJoCo. Blender chỉ làm mesh hiển thị.
- Sửa các nhận định kỹ thuật sai hoặc chưa chính xác:
  - `mjpython` chỉ bắt buộc với `launch_passive`.
  - `fusestatic` và `discardvisual` chỉ mặc định bật khi import URDF.
  - `check_urdf` không áp dụng cho MJCF.
  - Gymnasium 1.x: `reset()` trả về `obs, info`.
  - Bổ sung mô tả MJX/Warp trên Apple Silicon.
  - Blender cài qua Steam tự cập nhật.
- Bước 6: điều kiện bắt buộc là script kiểm tra. Viewer là điều kiện phụ. Thêm việc kiểm tra `uv run mjpython` và ghim phiên bản `mujoco`.
- Bước 7: ghi rõ geom hiển thị phải đặt `mass=0` (hoặc dùng `<inertial>`), nếu không mesh Blender sẽ làm đổi khối lượng.

## Ghi chú kỹ thuật cho Phase 1 (người thi công tự quyết, Claude ghi lại)

| # | Ghi chú | Người chốt | Trạng thái |
|---|---|---|---|
| 9.1 | Servo: mô hình hoá đủ mô-men cực đại, tốc độ không tải, armature (quán tính rotor quy đổi), damping, frictionloss, độ trễ lệnh. Tất cả nằm trong file tham số T1.1. Mặc định dùng actuator `position` với `forcerange`, và tự giới hạn tốc độ lệnh trong bộ điều khiển. Độ trễ lệnh dùng tính năng delay (≥ 3.5.0). Có thể nâng lên `dcmotor` (≥ 3.7.0) nếu cần đường cong mô-men theo tốc độ | [Claude đề xuất] | Chờ chốt |
| 9.2 | Bộ giải: `integrator="implicitfast"`, timestep 1–2 ms, timeconst của `solref` ≥ 2 × timestep. Điều khiển chạy khoảng 50 Hz | [Claude đề xuất] | Chờ chốt |
| 9.3 | Va chạm: chỉ bàn chân và thân chạm sàn. Bàn chân là hình cầu, ma sát khoảng 0.8–1.0, `condim` 3 (lên 4 nếu chân bị xoay). Thêm `<exclude>` cho các cặp quanh hông để tránh rung | [Claude đề xuất] | Chờ chốt |
| 9.4 | Ngưỡng kiểm tra 8.5: xuyên sàn < 1 mm. Khớp không vượt giới hạn. Rung đo bằng RMS vận tốc khớp khi đứng yên (ngưỡng đặt sau khi đo lần đầu). Thêm kiểm tra: tỉ lệ thời gian actuator bị bão hoà, trượt chân, mô-men khi đứng thấp hơn mức an toàn (khoảng 50% mô-men cực đại) | [Claude đề xuất] | Chờ chốt |
| 9.5 | Kiểm tra mô-men tĩnh trong T1.4. Với servo cỡ MG90S và robot 250–350 g, mô-men ở hông/gối khi đứng 3 chân khoảng 0.08–0.1 N·m, gần 50% mô-men cực đại, sát giới hạn. Kích thước chân phải chọn theo kiểm tra này | [Claude đề xuất] | Chờ chốt |
| 9.6 | Kiến trúc web: chỉ một luồng mô phỏng sở hữu `MjData`. Web handler đẩy lệnh vào hàng đợi. Mô phỏng tự canh theo thời gian thật (bước tới khi `data.time` bắt kịp đồng hồ) và báo hệ số thời gian thực. Server chỉ nghe ở `127.0.0.1`. Kiểm tra tự động chạy không màn hình và không phụ thuộc đồng hồ thật | [Claude đề xuất] | Chờ chốt |

## Câu hỏi chỉ người dùng trả lời được

Xếp theo mức quan trọng:

1. **Trang web điều khiển ở mức nào?**
   - (a) Ra lệnh hướng và tốc độ (tiến, lùi, quay, đi ngang, dừng), dáng đi tự lo phần chân.
   - (b) Chỉnh tay từng khớp trong 12 khớp.
   - (c) Cả hai, thanh trượt khớp dùng để gỡ lỗi.

   Kèm câu hỏi: chỉ đi thẳng là đủ, hay phải rẽ và xoay tại chỗ?
2. **Xem robot ở đâu?**
   - Trong trình duyệt: server gửi khung hình, hoặc gửi vị trí để trình duyệt tự vẽ 3D.
   - Trong cửa sổ viewer của MuJoCo, còn trang web chỉ để gửi lệnh.

   Kèm câu hỏi: chỉ dùng trên máy Mac này, hay cả từ điện thoại hoặc máy khác?
3. **Mô phỏng theo loại servo nào?** Đây là thước đo cho chữ "chính xác". Mặc định Claude đề xuất là MG90S: mô-men cực đại khoảng 0.18–0.2 N·m, khoảng 0.1 s/60° ở 4.8–5 V. Đây là loại servo của bộ nhện 12 servo trong ảnh tham khảo. Đổi sau vẫn được (nằm trong file tham số), nhưng chọn sai loại có thể làm robot không đứng nổi.

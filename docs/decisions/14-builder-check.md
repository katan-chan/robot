# Bước 14. Kiểm tra cuối của người thi công

Ngày: 2026-10-20.

Một reviewer đóng vai người thi công đã đọc lại các Bước 1–13. Kết luận: không có quyết định nào mâu thuẫn tới mức chặn việc lên kế hoạch. Phần dưới ghi lại các điểm còn lại.

## Claude tự quyết (người dùng xem và sửa nếu muốn)

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 14.1 | Viewer MuJoCo chỉ là **công cụ riêng**: mở model hoặc xem lại một lần chạy. Viewer không hiển thị phiên đang lái từ web. Nhờ vậy không cần `mjpython`/`launch_passive`, và luồng mô phỏng giữ `MjData` một mình (9.6). Xem trực tiếp phiên đang lái thì dùng chính trang web, kể cả khi ngồi tại máy | [Claude tự quyết] | Đang áp dụng |
| 14.2 | Replay có 2 chế độ. **Chính xác**: phát lại `ctrl` đã ghi, so khớp checkpoint, dùng để chẩn đoán. **Mô phỏng lại**: đưa các lệnh controller đã ghi qua code hiện tại, kèm một điều kiện kiểm tra riêng cho từng bug, dùng làm test hồi quy (11.9). Lý do: phát lại `ctrl` cũ không thể cho thấy một bản sửa IK hay dáng đi | [Claude tự quyết] | Đang áp dụng |
| 14.3 | Khi replay một lần chạy đã lưu, cổng khả thi chỉ kiểm tra model biên dịch được và phiên bản `mujoco` khớp. Không chặn vì tham số xấu, vì chính tham số xấu có thể là nguyên nhân của bug đang điều tra | [Claude tự quyết] | Đang áp dụng |
| 14.4 | Ảnh tham khảo lưu tại [`docs/reference/spider-reference.png`](../reference/spider-reference.png). Kích thước khởi điểm lấy theo tỉ lệ trong ảnh: hông xếp hình chữ X, thân khoảng 10 cm, chân duỗi khoảng 15 cm | [Claude tự quyết] | Đang áp dụng |
| 14.5 | Kích thước mặc định phải qua cổng khả thi ngay từ ngày đầu. Nếu không qua kiểm tra mô-men: **đổi kích thước chân trước**, rồi mới đổi servo khoẻ hơn. Không nới biên an toàn 50% | [Claude tự quyết] | Đang áp dụng |

Thêm nhãn người chốt **[Claude tự quyết]**: điểm nhỏ, người thi công có thể tự quyết mà không đổi thứ được làm ra. Người dùng vẫn sửa được.

## Tình trạng hiện tại

- Tailscale đã cài trên Mac (`/usr/local/bin/tailscale`) nhưng đang tắt (`Stopped`) và chưa nối với thiết bị nào.

## Câu hỏi cho người dùng

1. Bạn sẽ lái robot từ thiết bị nào: điện thoại (nút cảm ứng), laptop (bàn phím), hay tay cầm chơi game thật?
2. Phase 1 có cần thử lái thật từ thiết bị thứ hai qua Tailscale mới tính là xong không? Hay chỉ cần lái được trên máy này, còn phần truy cập từ xa và token chỉ cần làm xong và qua test tự động?

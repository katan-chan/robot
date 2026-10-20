# Bước 12. Trang web điều khiển, cách xem robot, servo thay được

Ngày: 2026-10-20. Trả lời 3 câu hỏi ở Bước 9.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 12.1 | Trang web là một **controller**, như tay cầm chơi game, điều khiển **qua internet** | [Người dùng] | Đang áp dụng |
| 12.2 | Cách xem robot: ưu tiên cách đơn giản và dễ nhìn | [Người dùng] | Đang áp dụng |
| 12.3 | Servo phải thay được | [Người dùng] | Đang áp dụng |
| 12.4 | Controller ra lệnh mức cao: tiến/lùi, đi ngang, xoay tại chỗ, tốc độ, dừng. Dáng đi tự lo phần chân. Không có thanh trượt từng khớp trên trang web (bỏ, thêm khi cần gỡ lỗi) | [Claude đề xuất] | Chờ chốt |
| 12.5 | Xem robot ngay trên trang web. Server tự vẽ hình bằng MuJoCo (vẽ ngầm, không mở cửa sổ) rồi gửi khung hình JPEG về trình duyệt, khoảng 20–30 hình/giây, 640×480. Hình giống hệt viewer của MuJoCo, không phải viết phần vẽ 3D riêng. Viewer MuJoCo trên Mac vẫn dùng được khi ngồi tại máy | [Claude đề xuất] | Chờ chốt |
| 12.6 | Lý do chọn 12.5: điều khiển qua internet thì người điều khiển không nhìn thấy cửa sổ viewer trên Mac. Vẽ 3D trong trình duyệt (three.js hoặc MuJoCo WASM) đẹp hơn nhưng nhiều việc hơn | [Claude đề xuất] | Chờ chốt |
| 12.7 | Servo: một **danh mục servo** (MG90S, SG90, MG996R…) trong file tham số. Mỗi loại ghi mô-men cực đại, tốc độ, khối lượng, kích thước, hành trình góc. Chọn servo theo tên: một loại chung cho cả robot, có thể ghi đè riêng cho từng vị trí khớp (hông xoay, hông nhấc, gối). Mặc định MG90S | [Claude đề xuất] | Chờ chốt |
| 12.8 | Đổi servo thì bộ kiểm tra khả thi tự chạy lại (hook PostToolUse). Manifest của mỗi lần chạy ghi rõ servo đã dùng | [Claude đề xuất] | Chờ chốt |
| 12.9 | Truy cập qua internet: **không mở cổng công khai**. Mặc định dùng Tailscale (mạng riêng giữa các thiết bị của bạn). Trang web vẫn có mật khẩu hoặc token. Server chỉ nghe trên mạng Tailscale và `127.0.0.1` | [Claude đề xuất] | Chờ chốt |

## Cảnh báo bảo mật (12.9)

Trang web điều khiển chạy trên máy Mac. Nếu mở thẳng ra internet mà không có bảo vệ, bất kỳ ai tìm thấy địa chỉ đều điều khiển được. Họ còn có thể tấn công vào chính server chạy trên máy Mac. Vì vậy:
- Không mở port trên router.
- Ưu tiên Tailscale: chỉ thiết bị đã đăng nhập tài khoản của bạn mới vào được.
- Cách khác: Cloudflare Tunnel kết hợp Cloudflare Access. Dùng khi cần cho người ngoài truy cập.

## Ảnh hưởng tới các bước trước

- 9.6 (server chỉ nghe ở `127.0.0.1`) được mở rộng thành 12.9.
- Lệnh từ controller vẫn ghi theo số bước mô phỏng (11.6). Độ trễ mạng không làm hỏng việc replay.
- Đường truyền qua internet có trễ. Controller gửi lệnh "giữ" kèm thời hạn: mất kết nối quá khoảng 0.5 giây thì robot tự dừng.

## Câu hỏi mở

1. Ai được điều khiển: chỉ mình bạn trên thiết bị của bạn, hay cả người khác? Câu trả lời quyết định chọn Tailscale hay Cloudflare.
2. Thiết kế module record (11.5–11.16) đã được duyệt chưa?

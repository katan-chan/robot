# Bước 12. Trang web điều khiển, cách xem robot, servo thay được

Ngày: 2026-10-20. Trả lời 3 câu hỏi ở Bước 9.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 12.1 | Trang web là một **controller**, như tay cầm chơi game, điều khiển **qua internet** | [Người dùng] | Đang áp dụng |
| 12.2 | Cách xem robot: ưu tiên cách đơn giản và dễ nhìn | [Người dùng] | Đang áp dụng |
| 12.3 | Servo phải thay được | [Người dùng] | Đang áp dụng |
| 12.4 | Controller ra lệnh mức cao: tiến/lùi, đi ngang, xoay tại chỗ, tốc độ, dừng. Dáng đi tự lo phần chân. Không có thanh trượt từng khớp trên trang web (bỏ, thêm khi cần gỡ lỗi) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.5 | Xem robot ngay trên trang web. Server tự vẽ hình bằng MuJoCo (vẽ ngầm, không mở cửa sổ) rồi gửi khung hình JPEG về trình duyệt, khoảng 20–30 hình/giây, 640×480. Hình giống hệt viewer của MuJoCo, không phải viết phần vẽ 3D riêng. Viewer MuJoCo trên Mac vẫn dùng được khi ngồi tại máy | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.6 | Lý do chọn 12.5: điều khiển qua internet thì người điều khiển không nhìn thấy cửa sổ viewer trên Mac. Vẽ 3D trong trình duyệt (three.js hoặc MuJoCo WASM) đẹp hơn nhưng nhiều việc hơn | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.7 | Servo: một **danh mục servo** (MG90S, SG90, MG996R…) trong file tham số. Mỗi loại ghi mô-men cực đại, tốc độ, khối lượng, kích thước, hành trình góc. Chọn servo theo tên: một loại chung cho cả robot, có thể ghi đè riêng cho từng vị trí khớp (hông xoay, hông nhấc, gối). Mặc định MG90S | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.8 | Đổi servo thì bộ kiểm tra khả thi tự chạy lại (hook PostToolUse). Manifest của mỗi lần chạy ghi rõ servo đã dùng | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.9 | Truy cập qua internet: **không mở cổng công khai**. Mặc định dùng Tailscale (mạng riêng giữa các thiết bị của bạn). Xác thực bằng khoá theo 12.10–12.14 | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Cảnh báo bảo mật (12.9)

Trang web điều khiển chạy trên máy Mac. Nếu mở thẳng ra internet mà không có bảo vệ, bất kỳ ai tìm thấy địa chỉ đều điều khiển được. Họ còn có thể tấn công vào chính server chạy trên máy Mac. Vì vậy:
- Không mở port trên router.
- Ưu tiên Tailscale: chỉ thiết bị đã đăng nhập tài khoản của bạn mới vào được.
- Cách khác: Cloudflare Tunnel kết hợp Cloudflare Access. Dùng khi cần cho người ngoài truy cập.

## Ảnh hưởng tới các bước trước

- 9.6 (server chỉ nghe ở `127.0.0.1`) được mở rộng thành 12.9.
- Lệnh từ controller vẫn ghi theo số bước mô phỏng (11.6). Độ trễ mạng không làm hỏng việc replay.
- Đường truyền qua internet có trễ. Controller gửi lệnh "giữ" kèm thời hạn: mất kết nối quá khoảng 0.5 giây thì robot tự dừng.

## Khoá điều khiển (trả lời câu hỏi "ai được điều khiển")

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 12.10 | Điều khiển từ xa cần token (khoá riêng). Server chỉ lưu mã hash của token | [Người dùng] | Đang áp dụng |
| 12.11 | Máy Mac này mặc định luôn điều khiển được, không cần token | [Người dùng] | Đang áp dụng |
| 12.12 | Mỗi khoá có tên (ví dụ `iphone-minh`). Lệnh tạo khoá in token **một lần duy nhất**. Server lưu `tên + sha256(token) + ngày tạo` trong một file ngoài git (`~/.config/spider-robot/keys.json`, quyền 600). Thu hồi được từng khoá. Token dài 32 byte ngẫu nhiên (`secrets.token_urlsafe`), nên dùng sha256 là đủ. So sánh bằng `hmac.compare_digest` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.13 | Token không bao giờ nằm trong URL gửi lên server, vì URL dễ lọt vào log. Trang web nhận token qua ô nhập, hoặc qua phần `#` của link (trình duyệt không gửi phần này lên server), lưu trong trình duyệt rồi gửi qua header hoặc tin nhắn đầu tiên của WebSocket | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.14 | "Máy này" được nhận diện bằng **một cổng riêng chỉ nghe ở `127.0.0.1`**, không phải bằng địa chỉ IP của request. Cổng cho truy cập từ xa (trên Tailscale) luôn đòi token. Không trỏ tunnel hay proxy nào vào cổng `127.0.0.1` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.15 | Mỗi lúc chỉ một controller được lái. Máy này luôn giành quyền lái được. Mọi controller đều có nút dừng khẩn cấp | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.16 | `events.jsonl` ghi tên khoá đang lái (không ghi token) mỗi lần đổi người lái | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 12.17 | Đường truyền vẫn đi qua Tailscale (đã mã hoá). Muốn cho người khác lái thì chia sẻ máy Mac qua Tailscale và cấp cho họ một khoá. Cloudflare để sau | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

### Vì sao 12.14 quan trọng

Nếu server cho qua mọi request đến từ địa chỉ `127.0.0.1`, thì mọi tunnel hoặc proxy chạy trên máy (Tailscale Serve, Cloudflare Tunnel, ngrok…) đều biến người ngoài thành "máy này". Khi đó token bị bỏ qua. Tách hẳn hai cổng thì tránh được lỗi này.

## Câu hỏi mở

1. Thiết kế module record (11.5–11.16) đã được duyệt chưa?

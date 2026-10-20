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

## Trả lời của người dùng

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 14.6 | Lái được từ cả điện thoại (nút cảm ứng) và laptop (bàn phím). **Không** hỗ trợ tay cầm chơi game | [Người dùng] | Đang áp dụng |
| 14.7 | Trang controller tự đổi giao diện theo thiết bị: màn hình cảm ứng hiện joystick ảo và nút dừng lớn, laptop dùng phím (WASD, Q/E để xoay, Space để dừng). Cả hai cùng gửi một loại lệnh lên server | [Claude tự quyết] | Đang áp dụng |
| 14.8 | Phase 1 xong khi: (a) test tự động qua, gồm cả token và cổng từ xa; (b) **một lần thử tay** lái từ điện thoại qua Tailscale theo checklist; (c) một agent lái được robot qua API (14.9) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 14.9 | Có một **cổng cho agent** điều khiển robot | [Người dùng] | Đang áp dụng |
| 14.10 | Agent dùng **chung API** với trang controller: cùng loại lệnh (tiến/lùi, đi ngang, xoay, tốc độ, dừng), dạng JSON qua HTTP/WebSocket. Không làm API riêng. Kèm một lệnh dòng lệnh mỏng để agent gọi qua Bash (`... drive --vx 0.1 --for 2s`) | [Claude đề xuất] | Chờ chốt |
| 14.11 | Agent **đọc** được trạng thái: vị trí và hướng thân, vận tốc, tải servo, kết quả kiểm tra khả thi, sự kiện gần nhất, và một ảnh chụp khung hình hiện tại. Nhờ vậy agent "thấy" được robot | [Claude đề xuất] | Chờ chốt |
| 14.12 | Quyền truy cập: agent chạy trên máy này dùng cổng `127.0.0.1` (12.11) và phải tự khai tên, ví dụ `agent:claude`. Agent ở máy khác cần khoá như người (12.12). Tên agent được ghi vào log người lái (12.16) | [Claude đề xuất] | Chờ chốt |
| 14.12a | Lệnh CLI có `--host` và `--key`. Mặc định nối `127.0.0.1`. Agent ở máy khác chỉ cần máy đó đã vào Tailscale, rồi chạy cùng CLI với `--host macbook-pro --key <token>`. Agent chạy trên cloud phải có auth key của Tailscale mới vào được mạng. Việc này để sau và cần xem xét bảo mật riêng | [Claude đề xuất] | Chờ chốt |
| 14.12b | Robot thật sau này (Giai đoạn 8) dùng **cùng API và cùng CLI**. Agent không cần biết đang lái bản mô phỏng hay con thật | [Claude đề xuất] | Chờ chốt |
| 14.13 | Người luôn được ưu tiên: người giành quyền lái từ agent bất cứ lúc nào. Nút dừng khẩn cấp thắng mọi lệnh của agent | [Claude đề xuất] | Chờ chốt |
| 14.14 | MCP server (T6.1) để sau. Khi làm, MCP chỉ là lớp bọc mỏng quanh chính API này | [Claude đề xuất] | Chờ chốt |

## Cách dùng Tailscale (trả lời câu hỏi của người dùng)

1. **Trên Mac**: mở app Tailscale trên thanh menu, đăng nhập (Google, Apple, GitHub…).
2. **Trên điện thoại và laptop khác**: cài app Tailscale (App Store / Google Play / tailscale.com), đăng nhập **cùng tài khoản**.
3. Mỗi máy có một địa chỉ `100.x.y.z` và một tên, ví dụ `macbook-pro`. Kiểm tra bằng `tailscale status`.
4. Server bật cổng từ xa trên địa chỉ Tailscale của Mac. Điện thoại mở `http://macbook-pro:<cổng>`. Dữ liệu đã được Tailscale mã hoá.
5. Tạo khoá cho điện thoại bằng lệnh tạo khoá (12.12). Dán token vào trang web một lần, trình duyệt sẽ nhớ.
6. Mac phải thức khi đang lái từ xa: server tự giữ máy không ngủ (`caffeinate`) trong lúc chạy.
7. Cho người khác lái: dùng tính năng "Share" của Tailscale để chia sẻ riêng máy Mac, rồi cấp cho họ một khoá riêng.

Lưu ý: không trỏ `tailscale serve` hoặc `tailscale funnel` vào cổng `127.0.0.1` (12.14). `funnel` mở máy ra internet công khai, không dùng.

## Câu hỏi cho người dùng

1. ~~Đồng ý tiêu chí xong Phase 1 ở 14.8 không?~~ Đồng ý, kèm thêm cổng cho agent (14.9).
2. Duyệt thiết kế cổng agent 14.10–14.14?

# Nhật ký quyết định: Robot nhện mô phỏng

Mỗi bước brainstorm nằm trong một file riêng, đánh số theo thứ tự thời gian.
Mọi quyết định đều sửa được về sau.

## Cách đánh dấu

- Người chốt:
  - **[Người dùng]**: người dùng tự chốt.
  - **[Claude đề xuất]**: người dùng còn sửa được.
  - **[Người dùng] xác nhận đề xuất của Claude**: Claude đề xuất, người dùng đã đồng ý.
- Trạng thái: **Đang áp dụng**, **Chờ chốt**, hoặc **Đã thay** (ghi kèm "→ xem Bước N").
- Khi đổi một quyết định: không xoá dòng cũ. Đổi trạng thái thành **Đã thay** và ghi quyết định mới.
- Mã quyết định dạng `8.2` (Bước 8, quyết định 2). Mã task dạng `T1.6` (Giai đoạn 1, task 6, trong Bước 7).

## Thuật ngữ

- **Mục tiêu 1/2/…**: mục tiêu dài hạn của người dùng (Bước 4).
- **Giai đoạn 0–8**: trình tự thi công (Bước 7).
- **Phase 1** = Giai đoạn 0 + Giai đoạn 1: robot khối hình di chuyển được trong mô phỏng chính xác, điều khiển bằng tay qua web (Bước 8).

## Các bước

| Bước | File | Nội dung |
|---|---|---|
| 1 | [01-quy-trinh-blender-mo-phong.md](01-quy-trinh-blender-mo-phong.md) | Cách người ta làm: Blender → URDF/MJCF → simulator |
| 2 | [02-tuong-tac-agent.md](02-tuong-tac-agent.md) | Simulator tương tác với RL agent và LLM agent ra sao |
| 3 | [03-phan-cung-may.md](03-phan-cung-may.md) | Kiểm tra máy Mac, chọn stack |
| 4 | [04-muc-tieu.md](04-muc-tieu.md) | Loại robot và mục tiêu dài hạn |
| 5 | [05-pham-vi-minimal.md](05-pham-vi-minimal.md) | Phạm vi trước mắt: bản minimal |
| 6 | [06-moi-truong-mo-phong.md](06-moi-truong-mo-phong.md) | Việc đầu tiên: dựng môi trường mô phỏng |
| 7 | [07-trinh-tu-task.md](07-trinh-tu-task.md) | Trình tự toàn bộ task, Giai đoạn 0 → 8 |
| 8 | [08-dau-ra-phase-1.md](08-dau-ra-phase-1.md) | Đầu ra Phase 1: robot di chuyển được trong mô phỏng chính xác |
| 9 | [09-review.md](09-review.md) | Review bởi subagent: sửa lỗi, ghi chú kỹ thuật, câu hỏi còn lại |
| 10 | [10-harness-agent.md](10-harness-agent.md) | Harness cho agent: CLAUDE.md, AGENTS.md, hooks kiểm tra khả thi |
| 11 | [11-record-bug-trace.md](11-record-bug-trace.md) | Module record: ghi lần chạy, replay, ghi bug, trace |
| 12 | [12-controller-web.md](12-controller-web.md) | Trang web controller qua internet, xem robot trên web, danh mục servo |

`brainstorm-log.md` là bản nháp đầu tiên viết gộp một file. Đã được thay bằng các file 01–10, chỉ giữ để tham khảo.

## Câu hỏi đã chốt

- Chỉ đứng yên hay bước đi? → Phải di chuyển được (8.2).
- "Mô phỏng chính xác" nghĩa là gì? → Vật lý sát thực tế, có kiểm tra tự động (8.5).
- Phase 1 điều khiển thế nào? → Bằng tay, qua trang web (8.6).
- Harness có được duyệt không? → Có, 10.4–10.11 (11.1).
- Có dùng git không? → Có (11.13).
- Có dùng agent khác không? → Có thể (11.14).
- Trang web điều khiển ở mức nào? → Một controller, điều khiển qua internet (12.1).
- Xem robot ở đâu? → Cách đơn giản, dễ nhìn nhất (12.2), đề xuất ở 12.5.
- Servo nào? → Phải thay được (12.3), đề xuất danh mục servo ở 12.7.
- Ai được điều khiển qua internet? → Ai có token (khoá riêng, server chỉ lưu hash). Máy này luôn điều khiển được (12.10, 12.11).

## Câu hỏi còn mở

1. Thiết kế module record (11.5–11.16) đã duyệt chưa? → Bước 11
2. Robot có cần bò trên tường và trần không? Để tới T5.1. → Bước 4
3. Có đẩy repo lên remote (GitHub…) không? → Bước 11

## Đang chờ chốt

| Mã | Nội dung ngắn | File |
|---|---|---|
| 3.2 | Stack: tham số → Python sinh MJCF → MuJoCo; Blender chỉ làm mesh | Bước 3 |
| 4.7 | RL lo đi, LLM ở tầng trên | Bước 4 |
| 6.2 | Nội dung dựng môi trường mô phỏng | Bước 6 |
| 7.2 | Trình tự Giai đoạn 0 → 8 (phụ thuộc 4.7) | Bước 7 |
| 7.3 | Khối hình trước, Blender sau | Bước 7 |
| 8.3 | Phase 1 đi bằng dáng đi lập trình sẵn, không RL | Bước 8 |
| 8.4 | Phase 1 = Giai đoạn 0 + 1 | Bước 8 |
| 9.1–9.6 | Ghi chú kỹ thuật: servo, bộ giải, va chạm, ngưỡng kiểm tra, mô-men, kiến trúc web | Bước 9 |
| 11.5–11.12 | Record: thư mục mỗi lần chạy, lệnh theo số bước, replay, file bug, test hồi quy, nút báo bug, luật sửa bug, định dạng | Bước 11 |
| 11.15–11.16 | Hook cho Claude Code và Codex; nội dung `.gitignore` | Bước 11 |
| 12.4–12.9 | Lệnh controller, xem robot qua khung hình gửi về web, danh mục servo, truy cập qua Tailscale | Bước 12 |
| 12.12–12.17 | Khoá: lưu hash, token không nằm trong URL, cổng riêng cho máy này, một người lái mỗi lúc, ghi log người lái | Bước 12 |

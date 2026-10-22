# Bước 20. Blog nhật ký thiết kế công khai

Ngày: 2026-10-22. Nguồn: `docs/superpowers/specs/2026-10-22-blog-journal-design.md`. Bước 19 đã dùng cho quyết định tải 2 kg, nên blog là bước 20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 20.1 | Có một blog ghi lại quá trình làm robot nhện, từ brainstorm tới sản phẩm thật. Blog viết bằng **tiếng Anh**, người đọc là bất kỳ ai. Link blog để gắn vào portfolio sau này | [Người dùng] | Đang áp dụng |
| 20.2 | Giọng kể cụ thể, không chung chung: lỗi nào, quyết định nào, commit nào. Trọng tâm là **vấn đề của agent** và **vấn đề của người dùng**. Robot là bối cảnh. Không giấu hay tô đẹp sai lầm | [Người dùng] | Đang áp dụng |
| 20.3 | **Một repo công khai duy nhất**, không giấu notes, quyết định hay code. Trước lần push đầu tiên phải quét secret toàn bộ lịch sử git. Tạo remote, push, đổi sang công khai đều phải hỏi người dùng (task-graph mục 5) | [Người dùng] | Đang áp dụng |
| 20.4 | Xuất bản bằng **GitHub Pages**. Đổi email tác giả trong lịch sử git từ `ad@ads-MacBook-Pro.local` (tên máy) sang `lebinhminh_t67@hus.edu.vn`, chỉ đặt `git config user.email` cho repo này (không `--global`). Viết lại lịch sử không đảo ngược được: hỏi ngay trước khi chạy, giữ bản backup tới khi push xong | [Người dùng] | Đang áp dụng |
| 20.5 | Cấu trúc `docs/journal/`: `notes/<version>.md`, `media/<version>/`, `reference/README.md`, `templates/note.md`, `templates/post.md`, `posts/YYYY-MM-DD-<slug>.md`, `_drafts/`. `<version>` là tên gate: `brainstorm`, `g1`, `g2`… | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.6 | Mỗi **beat** trong note gồm: tiêu đề ngắn; loại (`agent-problem`, `human-problem`, `idea`); chuyện gì xảy ra; cách giải; bằng chứng (mã quyết định, commit, L-NNN, BUG-NNN, mã lần chạy); media nếu có. Mỗi beat tự đứng được bằng tiếng Anh, link tới tài liệu tiếng Việt chỉ để tham khảo thêm | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.7 | Hai bước mới của harness. (1) Sau mỗi task được gộp, coordinator hỏi thêm "có chuyện gì đáng kể cho blog không?", có thì thêm beat vào note của version hiện tại (không bắt buộc). (2) Khi qua mỗi gate: chụp ảnh Blender, ảnh MuJoCo, quay video MuJoCo vào `media/<gate>/`, viết note, rồi giao journal-writer viết bài nháp | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.8 | Bài nháp nằm trong `docs/journal/_drafts/` (Jekyll không đưa lên site). Chỉ bài trong `posts/` lên site, và chỉ sau khi người dùng duyệt từng bài. Không tự động đăng | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.9 | Vai trò mới **journal-writer** chỉ ghi `docs/journal/_drafts/` và `docs/journal/posts/`. Coordinator ghi phần còn lại của `docs/journal/`, `docs/_config.yml`, `docs/index.md`. Implementer viết lệnh quay video trong `spider/sim/`. Thêm `docs/journal/` vào thành phần memory của `harness.toml` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.10 | GitHub Pages dựng từ nhánh `main`, thư mục `/docs`, bằng Jekyll mặc định (theme `minima`). Repo là `katan-chan/robot`, blog ở `https://katan-chan.github.io/robot/journal/` (`baseurl: /robot`) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.11 | Clip là mp4 H.264, dài tối đa khoảng 20 s, không quá 10 MB. Quay video chỉ render, không chạy `mj_step`, không đổi `MjData` của lần chạy thật (luật 3). Không commit video của người khác, `reference/` chỉ chứa link | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 20.12 | Hook `PostToolUse` (Bash) `.claude/hooks/journal-reminder.sh` **nhắc** coordinator để lại chất liệu blog. Gộp task (`git merge`) thì nhắc ghi beat vào `notes/`. Đánh dấu gate bằng `git tag -a gN` thì nhắc chụp media, viết note gate và giao journal-writer viết bài nháp. Hook không tự viết bài và không đăng (20.8). Không dùng phiên Claude chạy ngầm (`claude -p`), vì tốn token, không ai giám sát, và thiếu bối cảnh | [Người dùng] chọn phương án A do Claude đề xuất | Đang áp dụng |

## Ghi chú

- Cấm: kể chung chung, giấu sai lầm, lộ token hay secret (luật 4), video của người khác, làm hỏng tính tái hiện.
- Tài liệu trong `docs/` không được chứa cú pháp Liquid (cặp ngoặc nhọn kép, hoặc ngoặc nhọn kèm `%`), trừ `docs/journal/index.md`, vì Jekyll sẽ xử lý chúng.
- Ngoài phạm vi lúc này: trang portfolio, tên miền riêng, bình luận, thống kê, quay màn hình web controller (thêm khi T1.7 xong).

# Blog nhật ký thiết kế — bản thiết kế

Ngày: 2026-10-22. Trạng thái: chờ người dùng duyệt.

## 1. Ý định

Người dùng muốn một blog cá nhân ghi lại quá trình làm robot nhện, từ brainstorm, qua từng version mô phỏng, đến khi ra sản phẩm thật. Blog có link trực tiếp để sau này gắn vào portfolio. Portfolio chưa có.

Người đọc là **bất kỳ ai**, không cần biết trước về robot hay MuJoCo.

**Giọng kể:** cụ thể, không chung chung. Mỗi bài xoay quanh ba thứ: ý tưởng, vấn đề gặp phải, và cách giải. Trọng tâm là **vấn đề của agent** và **vấn đề của người dùng**. Robot là bối cảnh, còn chuyện người và AI cùng làm một dự án phần cứng là nhân vật chính. Ý này ban đầu là phỏng đoán, người dùng đã đồng ý ("cứ thử đi").

Harness phải tự giữ lại chất liệu trong lúc làm, để khi viết bài không phải đào lại lịch sử.

## 2. Mục tiêu, ngoài phạm vi, điều cấm

**Mục tiêu**
- Có một thư mục markdown chứa thông tin để viết bài (notes).
- Có ảnh và video của từng version, xếp theo version.
- Có video tham khảo và mẫu (khuôn bài, khuôn note).
- Mỗi task và mỗi gate tự để lại chất liệu, như một bước của harness.
- Bù lại phần đã qua: brainstorm và G1.
- Blog tiếng Anh, xuất bản bằng GitHub Pages.

**Ngoài phạm vi (lúc này)**
- Trang portfolio.
- Tên miền riêng, theme cầu kỳ, bình luận, thống kê lượt xem.
- Quay màn hình web controller. Thêm khi T1.7 xong.
- Tự động đăng bài. Người dùng duyệt từng bài.

**Điều cấm (làm vậy là hỏng dù chạy được)**
- Kể chung chung kiểu "AI giúp tôi làm robot" mà không có chi tiết cụ thể: lỗi nào, quyết định nào, commit nào.
- Giấu hoặc tô đẹp sai lầm, cả của agent lẫn của người.
- Lộ token hoặc secret lên repo công khai (luật 4 trong AGENTS.md).
- Commit video của người khác vào repo, vì vướng bản quyền.
- Ghi chất liệu làm hỏng tính tái hiện của vật lý. Quay video không được đổi `MjData` của lần chạy thật (luật 3).

## 3. Ràng buộc

- **Một repo công khai duy nhất.** Người dùng chọn đẩy chính repo robot lên GitHub và không giấu notes, quyết định hay code. GitHub Pages phục vụ blog từ repo này.
- **Phải hỏi người dùng trước** khi tạo remote, push, hay đổi repo sang công khai (luật 6, task-graph mục 5).
- **Quét secret trước lần push đầu tiên.** Phải quét toàn bộ lịch sử git, không chỉ cây hiện tại. Thấy gì thì dừng lại và báo người dùng.
- **Đổi email tác giả trong lịch sử git** (người dùng chọn). Đổi mọi commit có tác giả hoặc committer `minh.le@gosmartlog.com` sang `lebinhminh_t67@hus.edu.vn`. Bước này làm trước lần push đầu tiên, sau khi quét secret.
  - Việc này không đảo ngược được, vì mọi mã commit sẽ đổi. Phải hỏi người dùng ngay trước khi chạy, và giữ một bản backup (bundle hoặc nhánh sao lưu) cho tới khi push xong.
  - Sau khi viết lại, cập nhật mọi mã commit được nhắc trong `docs/`, ví dụ c121e68 hay c8d0d6e.
  - Đặt `git config user.email lebinhminh_t67@hus.edu.vn` chỉ cho repo này (người dùng chọn). Không đặt ở mức `--global`.
  - Xoá các worktree và nhánh còn sót, ví dụ `worktree-agent-a696800fd5e6798b8`, hoặc viết lại cả chúng.
- **Phân quyền ghi giữ đúng task-graph mục 3.** `docs/journal/` thuộc coordinator. Code quay video nằm ở `spider/sim/`, do implementer làm trong worktree.
- **Không thêm dependency Python mới.** `ffmpeg` đã có sẵn ở `/opt/homebrew/bin/ffmpeg`. MuJoCo đã có `mujoco.Renderer` offscreen, và Pillow đã có.
- **Dung lượng.** Mỗi clip là mp4 H.264, dài tối đa khoảng 20 giây, không quá 10 MB (*tôi chọn*). GitHub chặn file trên 100 MB, và site Pages giới hạn 1 GB.
- **Ghi quyết định theo đúng quy trình.** Thêm `docs/decisions/20-*.md`, cập nhật `docs/kb/curated.toml`, `harness.toml` (thành phần memory) và task-graph mục 3 và 7. Sửa `harness.toml` cần người dùng duyệt.

## 4. Những gì đã chốt

### 4.1 Cấu trúc thư mục

```
docs/journal/
  notes/<version>.md       chất liệu viết bài, mỗi version một file
  media/<version>/         ảnh + video của chính dự án
  reference/README.md      link video tham khảo + mẫu, ghi rõ xem để học gì
  templates/note.md        khuôn note
  templates/post.md        khuôn bài
  posts/YYYY-MM-DD-<slug>.md  bài hoàn chỉnh, tiếng Anh
```

`<version>` là tên gate: `brainstorm`, `g1`, `g2`, …

Tên thư mục và chỗ đặt là *tôi chọn*, người dùng đã đồng ý.

### 4.2 Note: một "chuyện" (beat) gồm gì

Mỗi beat trong note có:
- tiêu đề ngắn;
- loại: `agent-problem`, `human-problem` hoặc `idea`;
- chuyện gì xảy ra, kể cụ thể;
- cách giải;
- bằng chứng: mã quyết định, commit, bài học (L-NNN), BUG-NNN, mã lần chạy;
- media liên quan, nếu có.

Note viết bằng tiếng Anh (*tôi chọn*, vì repo công khai và bài viết tiếng Anh).

### 4.3 Hai bước mới trong harness

1. **Sau mỗi task được gộp (task-graph mục 7).** Ngoài câu hỏi về bài học, coordinator hỏi thêm: "có chuyện gì đáng kể cho blog không?". Có thì thêm beat vào `notes/<version hiện tại>.md`. Không có thì bỏ qua. Không bắt buộc phải có beat.
2. **Khi qua mỗi gate.** Chạy lệnh chụp và quay version đó vào `media/<gate>/`, gồm:
   - ảnh Blender 4 góc nhìn (`tools/blender render`, đã có);
   - ảnh MuJoCo (`spider.sim.view --snapshot`, đã có);
   - **video MuJoCo (mới).** Ở G1 là video camera xoay quanh robot đứng yên ở keyframe `stand`. Video này chỉ render, không chạy `mj_step`. Từ T1.4 trở đi thêm clip robot chuyển động, lấy từ một lần chạy đã ghi (replay T1.9) để clip tái hiện được.

   Sau đó coordinator viết note cho gate, và giao một subagent viết bài nháp để người dùng duyệt.

### 4.4 Video tham khảo và mẫu

- `reference/README.md` là danh sách link video và bài của người khác. Ví dụ: robot nhện hoặc quadruped thật, nhện thật bò, devlog hay. Mỗi link kèm một dòng ghi xem để học gì, về dáng đi hay về cách kể chuyện.
- Không tải video người khác về repo.
- Khuôn bài `templates/post.md` theo thứ tự:
  1. Hook: một khoảnh khắc cụ thể.
  2. Bối cảnh ngắn cho người không biết gì.
  3. Vấn đề.
  4. Đã thử gì.
  5. Cách giải.
  6. Bài học.
  7. Ảnh/video.
  8. "Next".

### 4.5 Xuất bản

- Repo GitHub là `katan-chan/robot` (*tôi chọn*). `katan-chan` là tài khoản đang đăng nhập `gh`, còn `robot` là tên thư mục hiện tại. Link blog sẽ là `https://katan-chan.github.io/robot/journal/`, với `baseurl: /robot`.
- GitHub Pages lấy từ nhánh `main`, thư mục `/docs` (*tôi chọn*). Jekyll mặc định của Pages dựng markdown, không thêm framework.
- Blog nằm ở `<site>/journal/`.
- Các trang quyết định trong `docs/` cũng xem được trên web. Điều này hợp ý người dùng là không giấu gì.
- Bài dẫn link thẳng tới quyết định, commit và bài học trên GitHub.

### 4.6 Bù phần đã qua

- **`notes/brainstorm.md`.** Lấy từ `docs/decisions/brainstorm-log.md` và các dòng "Đã thay". Các beat ít nhất gồm:
  - stack đổi hai lần (3.1 → 3.2 → 18.1);
  - "dự án nhỏ, chat là đủ" (5.5) phải đổi;
  - xem G1 bằng MuJoCo hay Blender (16.4 → 18.3);
  - luật phiên chính chỉ điều phối (17.x).
- **`notes/g1.md`.** Các beat ít nhất gồm:
  - review phát hiện actuator `pid`/`slewmax` không tồn tại (bước 9);
  - tấm thân bị làm mỏng cho đủ khối lượng (commit c121e68);
  - mọi review từng task đều Approved mà camera Blender và MuJoCo vẫn lệch (L-004, c8d0d6e);
  - các fix trong G1 final review.
- **`media/g1/`.** Chép ảnh đã có trong `docs/reference/g1/` và thêm video xoay quanh robot.
- **`media/brainstorm/`.** Ảnh tham khảo gốc `docs/reference/spider-reference.png`.
- **Hai bài nháp tiếng Anh**, một cho brainstorm và một cho G1. Người dùng duyệt trước khi coi là xong.

### 4.7 Ai ghi file nào (*tôi chọn*)

- **coordinator** ghi những file sau:
  - `docs/journal/` (trừ `posts/` và `_drafts/`), `docs/_config.yml`, `docs/index.md`.
  - `media/<gate>/`. Coordinator chạy lệnh quay video do implementer viết, rồi commit kết quả. Việc chạy lệnh không phải là viết code.
- **journal-writer** là vai trò mới. Vai trò này chỉ ghi `docs/journal/_drafts/` và `docs/journal/posts/`. Nó viết bài nháp từ notes và media. Người dùng duyệt xong thì nó chuyển bài từ `_drafts/` sang `posts/`.
- **implementer** viết lệnh quay video trong `spider/sim/` và test của lệnh đó.
- Cập nhật task-graph mục 3, `curated.toml`, và `harness.toml` (thêm `docs/journal/` vào memory). Việc sửa `harness.toml` được tính là đã duyệt khi người dùng duyệt bản thiết kế này.

### 4.8 Bài nháp và bằng chứng

- **Bài nháp nằm trong `docs/journal/_drafts/`** (*tôi chọn*). Bài vẫn có trong repo nên không giấu gì, nhưng Jekyll không đưa nó lên site. Chỉ bài trong `posts/` mới lên site, và chỉ sau khi người dùng duyệt.
- **Mỗi beat tự đứng được bằng tiếng Anh** (*tôi chọn*). Beat phải có tóm tắt tiếng Anh đủ ý của quyết định hay bài học được nhắc tới. Link tới tài liệu tiếng Việt chỉ để tham khảo thêm, người đọc không cần mở mới hiểu.
- **Beat sau G1 ghi vào `notes/g2.md`** (*tôi chọn*). Khi các gate sau được định nghĩa (16.7) thì đổi tên theo đúng gate.

## 5. Để builder tự quyết

- Tên lệnh và cờ cho video. Ví dụ `spider.sim.view --video OUT.mp4 --orbit`, hoặc một lệnh gom cả bước chụp ở gate.
- Độ phân giải, fps, góc camera của video, miễn là trong giới hạn dung lượng.
- Cấu hình Jekyll (`docs/_config.yml`, theme có sẵn của Pages), trang chủ `/journal/`, và cách tránh Jekyll lỗi với nội dung có cú pháp Liquid (cặp ngoặc nhọn kép).
- Công cụ quét secret, ví dụ `gitleaks` nếu có sẵn hoặc grep theo mẫu. Không thêm dependency Python.
- Có chép ảnh G1 sang `media/g1/` hay trỏ thẳng tới `docs/reference/g1/`.
- Test cho phần quay video. Theo luật repo, có ít nhất một test kiểm tra lệnh ra file mp4 hợp lệ và không đổi state của lần chạy.

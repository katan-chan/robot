# Bước 10. Harness phát triển bằng agent: CLAUDE.md, AGENTS.md, hooks kiểm tra khả thi

Ngày: 2026-10-20.

## Yêu cầu của người dùng

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 10.1 | Có `CLAUDE.md` và `AGENTS.md` để mọi agent làm việc trong repo theo cùng một quy ước | [Người dùng] | Đang áp dụng |
| 10.2 | Có hooks dùng code để kiểm tra tính khả thi của model **trước khi** chạy mô phỏng | [Người dùng] | Đang áp dụng |
| 10.3 | Người dùng chưa có kinh nghiệm, Claude chọn cách làm và giải thích | [Người dùng] | Đang áp dụng |

## Tham khảo trên mạng

- **RoboMorph** (ICLR 2025 workshop): LLM đề xuất thiết kế robot theo một "ngữ pháp". Thiết kế được biên dịch ra XML cho MuJoCo. Biên dịch lỗi thì loại ngay, sau đó mới train và chấm điểm. Bài học: sinh model từ tham số có cấu trúc, và có cổng biên dịch trước khi chạy. https://arxiv.org/abs/2407.08626
- **AID-SR**: đưa trạng thái vật lý đo được trong simulator về cho LLM thiết kế, dưới dạng phản hồi có cấu trúc. 96,2% thiết kế qua bước "kiểm tra khả thi mô phỏng". Bài học: thông báo lỗi phải đủ rõ để agent tự sửa. https://arxiv.org/pdf/2605.14700
- **Articraft**: agent sinh URDF, nhập thẳng vào Isaac Sim để kiểm tra. Khối lượng và damping do LLM gán. https://arxiv.org/pdf/2605.15187
- **MorphoGen** (NeurIPS 2026): tiến hoá XML robot tự do bằng đột biến do LLM tạo. https://neurips.cc/virtual/2026/poster/150325
- **Text2Robot** (Duke): từ mô tả chữ ra robot 4 chân thật. Dùng thuật toán tiến hoá và PPO, không dùng agent viết MJCF. https://arxiv.org/pdf/2406.19963
- **AGENTS.md và CLAUDE.md**: Claude Code chỉ đọc `CLAUDE.md`, không đọc `AGENTS.md`. Cách phổ biến: nội dung chung để trong `AGENTS.md`, còn `CLAUDE.md` chỉ có `@AGENTS.md` cộng phần riêng của Claude. https://makandracards.com/makandra/626671-claude-code-read-agents-md
- **Hooks**: là lệnh shell chạy ở các thời điểm cố định, không phụ thuộc AI có "nhớ" hay không. Đây là cách duy nhất để ép "lần nào cũng phải làm X". Codex CLI cũng có hooks (`PreToolUse`…), cấu hình ở `.codex/hooks.json`. https://developers.openai.com/codex/hooks

Không tìm thấy dự án nào công khai làm đúng việc "hook kiểm tra MJCF trước khi chạy mô phỏng". Phần dưới là thiết kế của Claude, dựa trên các bài học ở trên.

## Đề xuất thiết kế

| # | Đề xuất | Người chốt | Trạng thái |
|---|---|---|---|
| 10.4 | `AGENTS.md` là nguồn quy ước duy nhất. `CLAUDE.md` chỉ gồm `@AGENTS.md` và vài dòng riêng cho Claude | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.5 | Cổng khả thi nằm **trong code**: script chạy mô phỏng tự gọi bộ kiểm tra trước, và từ chối chạy nếu kiểm tra lỗi. Như vậy agent nào, hay người nào, cũng không bỏ qua được. Hooks chỉ thêm phản hồi sớm | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.6 | Ba lớp hook (xem dưới), cùng gọi một lệnh kiểm tra | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.7 | Thông báo lỗi có cấu trúc: tên kiểm tra, giá trị đo, ngưỡng, gợi ý sửa. Agent đọc rồi tự sửa (bài học từ AID-SR) | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.8 | `AGENTS.md` có quy tắc: mọi quyết định thiết kế ghi vào `docs/decisions/`, theo đúng cách đánh dấu trong README | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

### Bộ kiểm tra khả thi (một lệnh duy nhất)

Chạy nhanh trong vài giây, không cần màn hình. Mức 1 không chạy mô phỏng.

**Mức 1, tĩnh:**
1. File tham số hợp lệ: kích thước dương, giới hạn góc nằm trong hành trình servo.
2. MJCF biên dịch được (`mujoco.MjModel`). MuJoCo tự kiểm khối lượng và inertia.
3. Tổng khối lượng nằm trong ngân sách. Không body nào thiếu khối lượng.
4. Mô-men tĩnh: ở tư thế đứng (và đứng 3 chân), tính mô-men cần ở từng khớp bằng `mj_inverse`. Mỗi khớp phải ≤ 50% mô-men cực đại của servo (9.5).
5. Va chạm: ở tư thế mặc định, chỉ bàn chân chạm sàn. Không có cặp chân–chân hay chân–thân chạm nhau (9.3).
6. Bộ giải: timestep, integrator và `solref` đúng 9.2.
7. Tầm với: các điểm đặt chân của dáng đi nằm trong vùng IK với tới được.

**Mức 2, chạy thử ngắn:** đứng yên khoảng 2 giây mô phỏng. Đo xuyên sàn < 1 mm, rung, khớp vượt giới hạn, actuator bão hoà (9.4).

### Ba lớp hook

| Lớp | Khi nào chạy | Làm gì | Áp dụng cho |
|---|---|---|---|
| Claude Code `PostToolUse` | Ngay sau khi agent sửa file tham số hoặc MJCF | Chạy Mức 1. Nếu lỗi, báo lại cho agent sửa tiếp | Claude Code |
| Claude Code `PreToolUse` và Codex `PreToolUse` | Trước lệnh Bash chạy mô phỏng | Chạy Mức 1 + 2. Nếu lỗi, chặn lệnh | Claude Code, Codex |
| Git `pre-commit` | Trước khi commit | Chạy Mức 1 + 2 | Mọi agent và người (cần `git init`) |

Lớp cuối cùng là cổng trong code (10.5). Nó luôn chạy, kể cả khi không có hook nào.

### File sẽ tạo

- `AGENTS.md`, `CLAUDE.md`
- `.claude/settings.json`: hooks của Claude Code, commit vào repo để dùng chung
- `.codex/hooks.json`: hooks của Codex. Kiểm lại định dạng với tài liệu chính thức khi làm
- Script kiểm tra trong thư mục code, viết cùng Giai đoạn 0/1. Hiện chưa có model nào để kiểm, nên khi làm Giai đoạn 0 chỉ có kiểm tra 2 và 6
- `.githooks/pre-commit` (nếu dùng git)

## Tham khảo thêm: Harness² (google-research/harness2)

https://github.com/google-research/harness2. Bài báo: https://arxiv.org/abs/2610.14224. Commit đã xem: `1cfe254`, ngày 13/10/2026.

- **Là gì**: framework nghiên cứu, tự động tối ưu harness của agent cho các benchmark công việc văn phòng và pháp lý (JobBench, LAB, WorkBuddy). Executor là OpenCode hoặc Codex, model gọi qua Vertex AI.
- **Không dùng trực tiếp được**: chỉ chạy trên Linux, cần Google Cloud/Vertex, chuyên về benchmark, không liên quan robot.
- **Ý tưởng đáng mượn**:
  1. Harness gồm 8 thành phần sửa được: system prompt, guardrails (luật luôn bật), memory (kiến thức lâu dài), tool guidance, subagents, skills, scripts, plugins/hooks. Phần hạ tầng (CLI, model) để cố định, không sửa.
  2. Một file manifest liệt kê các thành phần của harness nằm ở file nào.
  3. Guardrails và memory **bắt đầu rỗng**. Chỉ thêm luật hay bài học khi có bằng chứng từ lần chạy thật.
  4. Vòng Propose–Probe–Compose: đề xuất vài thay đổi, chạy thử từng cái trên cùng một việc, so sánh kết quả, rồi gộp phần tốt.

| # | Đề xuất | Người chốt | Trạng thái |
|---|---|---|---|
| 10.9 | Sắp harness của repo theo 8 thành phần của Harness². Map: `AGENTS.md` = system prompt + guardrails; `docs/decisions/` = memory quyết định; bộ kiểm tra khả thi = scripts; hooks = plugins. Skills và subagents (ví dụ reviewer vật lý) chỉ thêm khi thật sự cần | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.10 | Guardrails trong `AGENTS.md` bắt đầu ngắn. Mỗi luật mới phải kèm lý do: lỗi gì đã xảy ra, ở đâu | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |
| 10.11 | Khi chỉnh model, agent có thể làm theo kiểu Propose–Probe–Compose: thử 2–3 bộ tham số, chạy bộ kiểm tra khả thi cho từng bộ, so sánh, chọn bộ tốt nhất, rồi ghi lý do vào `docs/decisions/` | [Người dùng] xác nhận đề xuất của Claude | Đang áp dụng |

## Câu hỏi mở

Cả hai câu dưới đã có trả lời ở Bước 11 (11.13, 11.14).

1. Có dùng git cho repo không? Repo hiện chưa phải git repository. Lớp `pre-commit` và việc lưu lịch sử quyết định đều cần git.
2. Ngoài Claude Code, bạn có định dùng agent khác (Codex, Cursor…) không? Nếu không, bỏ `.codex/hooks.json`.

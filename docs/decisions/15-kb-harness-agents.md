# Bước 15. Knowledge base, harness và cách chia agent

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 15.1 | Dùng skill graph-engineering để làm knowledge base, harness và cách chia agent. Lấy Harness² làm cơ sở | [Người dùng] | Đang áp dụng |
| 15.2 | Knowledge base là graph lưu dạng cạnh có kiểu trong JSON. Quy mô nhỏ nên không dùng Neo4j. Schema ở `docs/kb/ontology.toml` với 11 loại nút, 18 quan hệ và 12 câu hỏi năng lực | [Claude tự quyết] | Đang áp dụng |
| 15.3 | Quyết định, task, SUPERSEDES, CITES được trích tự động bằng luật từ `docs/decisions/`, nên không bao giờ lệch với tài liệu. Phần ngữ nghĩa (thành phần, kiểm tra, vai trò, ràng buộc) biên soạn tay trong `docs/kb/curated.toml`. Mọi cạnh đều có nguồn | [Claude tự quyết] | Đang áp dụng |
| 15.4 | `tools/kb.py` chỉ dùng thư viện chuẩn, chạy bằng `uv run`. Lệnh: `build`, `check`, `selftest`, `show`, `impact`, `deps`, `path`, `find` | [Claude tự quyết] | Đang áp dụng |
| 15.5 | Harness ghi trong `harness.toml` theo đúng 8 thành phần của Harness². Hạ tầng cố định (CLI, model, MuJoCo, uv) không sửa trong repo | [Claude tự quyết] | Đang áp dụng |
| 15.6 | `AGENTS.md` là hướng dẫn chung, `CLAUDE.md` chỉ import nó. Luật luôn bật bắt đầu với 6 luật, mỗi luật trỏ về quyết định làm nguồn | [Claude tự quyết] | Đang áp dụng |
| 15.7 | Hook dùng chung `tools/hooks/kb-sync.sh` cho Claude Code và Codex (PostToolUse): dựng lại KB, nếu lỗi thì trả về agent. Git `pre-commit` chạy `kb check` và `selftest` | [Claude tự quyết] | Đang áp dụng |
| 15.8 | Hook kiểm tra khả thi (PreToolUse trước lệnh mô phỏng) làm ở T1.12, khi đã có bộ kiểm tra. Không làm hook trước khi có thứ để kiểm | [Claude tự quyết] | Đang áp dụng |
| 15.9 | Chia agent theo hình kim cương (`docs/harness/task-graph.md`). Một coordinator làm phần tuần tự T0.1–T1.4 và viết hợp đồng. 4 worker song song: dáng đi, kiểm tra, record, server. 3 verifier ở context riêng: vật lý, tái hiện, bảo mật. Sau cùng là cổng người dùng | [Claude tự quyết] | Đang áp dụng |
| 15.10 | Giới hạn: tối đa 3 vòng sửa ↔ kiểm, một người ghi mỗi file (kb.py kiểm tự động), tối đa 4 worker | [Claude tự quyết] | Đang áp dụng |
| 15.11 | Bài học (`docs/harness/lessons.md`) bắt đầu rỗng. Một bài học lặp lại từ 2 lần mới được đề xuất thành luật, và người dùng duyệt | [Claude tự quyết] | Đang áp dụng |
| 15.12 | Thêm T1.9–T1.12 vào Bước 7 cho record, khoá, API agent và hook, vì các phần này đã duyệt nhưng chưa có task | [Claude tự quyết] | Đang áp dụng |
| 15.13 | Mã nguồn đặt trong package `spider/`, mỗi thư mục con thuộc một vai trò | [Claude tự quyết] | Đang áp dụng |

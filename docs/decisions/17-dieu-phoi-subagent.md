# Bước 17. Phiên chính chỉ điều phối, việc làm giao cho subagent

Ngày: 2026-10-20.

## Quyết định

| # | Quyết định | Người chốt | Trạng thái |
|---|---|---|---|
| 17.1 | Ưu tiên dùng subagent. Thực hiện kế hoạch theo cách Subagent-driven | [Người dùng] | Đang áp dụng |
| 17.2 | Agent chính (phiên chính, coordinator) **chỉ điều phối**: chia việc, giao việc, gọi verifier, gộp, ghi quyết định, giữ KB và cấu hình harness. Agent chính **không viết code sản phẩm** | [Người dùng] | Đang áp dụng |
| 17.3 | Phần tuần tự (T0.1–T1.4) cũng giao cho subagent: vai trò mới `implementer`, mỗi lúc một subagent, task sau bắt đầu sau khi task trước đã gộp. Luật dừng vẫn giữ: không chạy song song việc tuần tự | [Claude tự quyết] | Đang áp dụng |
| 17.4 | Subagent viết code chạy trong git worktree riêng (`isolation: "worktree"`, tách từ HEAD trên máy: `worktree.baseRef = "head"`), commit trên nhánh riêng. Coordinator gộp vào `main` bằng `git merge --ff-only` sau khi test và verifier qua | [Claude tự quyết] | Đang áp dụng |
| 17.5 | Hook `PreToolUse` `.claude/hooks/coordinator-guard.sh` chặn phiên chính sửa `spider/`, `tests/`, `tools/`, `web/`, `blender/`, `models/`, `pyproject.toml`, `uv.lock` trong checkout chính. Sửa trong worktree thì không bị chặn | [Claude tự quyết] | Đang áp dụng |
| 17.6 | Coordinator chỉ ghi: `docs/`, `AGENTS.md`, `CLAUDE.md`, `harness.toml`, `.claude/`, `.codex/`, `.githooks/`. `tools/` (kể cả `kb.py`, hook script) chuyển cho `implementer` | [Claude tự quyết] | Đang áp dụng |
| 17.7 | Thông tin chuyển giữa các subagent qua: kế hoạch (khối Interfaces của từng task), hợp đồng ở `docs/harness/`, và knowledge graph. Không dựa vào trí nhớ trong hội thoại | [Claude tự quyết] | Đang áp dụng |

## Giới hạn đã biết

- Hook chỉ chặn được công cụ Edit/Write. Sửa file bằng lệnh Bash thì hook không thấy. Luật 7 trong `AGENTS.md` vẫn cấm cách này. Hook `pre-commit` bắt được các lỗi KB, nhưng không biết ai đã sửa.
- Codex không có cùng cơ chế subagent và worktree. Với Codex, luật 7 chỉ là hướng dẫn trong `AGENTS.md`.

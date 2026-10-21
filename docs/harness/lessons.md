# Bài học (memory của harness)

Theo Harness²: bắt đầu rỗng. Chỉ thêm bài học có bằng chứng thật từ lần làm việc.
Quy trình: [task-graph.md](task-graph.md), mục 7.

Mẫu:

```
## L-NNN: <tóm tắt một dòng>
- Ngày:
- Bằng chứng: BUG-NNN / runs/<mã> / commit <sha>
- Chuyện gì xảy ra:
- Bài học:
- Đã thành luật chưa: chưa | rồi → AGENTS.md "Luật luôn bật" mục N (người dùng duyệt ngày …)
```

## L-001: Subagent trong worktree không ghi được file ra ngoài worktree
- Ngày: 2026-10-21
- Bằng chứng: Task 1 (commit 07eb147), implementer báo Write bị chặn khi ghi `.superpowers/sdd/…/task-1-report.md` ở checkout chính
- Chuyện gì xảy ra: worktree isolation chỉ cho ghi trong worktree. Báo cáo phải gửi qua tin nhắn trả về
- Bài học: báo cáo của subagent nằm trong tin nhắn trả về; coordinator lưu lại. Không yêu cầu subagent ghi ra ngoài worktree
- Đã thành luật chưa: chưa

## L-002: Sandbox từ chối lệnh Bash ghép
- Ngày: 2026-10-21
- Bằng chứng: Task 1 (07eb147), Task 2 (6093062): implementer phải tách `uv …` và `git …` thành từng lệnh riêng
- Chuyện gì xảy ra: lệnh dạng `a && b` bị từ chối trong subagent
- Bài học: brief giao việc nên dặn chạy từng lệnh một
- Đã thành luật chưa: chưa

## L-003: Auto mode chặn giao việc cho subagent và chặn agent sửa quyền
- Ngày: 2026-10-21
- Bằng chứng: 3 lần `[Auto-Mode Bypass]` khi giao Task 2–3; 1 lần `[Self-Modification]` khi sửa `.claude/settings.json` → `permissions`
- Chuyện gì xảy ra: thiết kế "phiên chính bị hook chặn sửa code, giao code cho subagent" bị bộ kiểm hiểu là lách luật. Agent cũng không được tự đổi quyền của mình
- Bài học: chạy kế hoạch ở chế độ thường (không auto mode), hoặc người dùng thêm `allow: Agent` trong `.claude/settings.json` (17.11). Quyền chỉ người dùng sửa
- Đã thành luật chưa: chưa

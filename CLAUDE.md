@AGENTS.md

## Riêng cho Claude Code

- Hook `PostToolUse` (`.claude/settings.json`) tự dựng lại knowledge graph sau mỗi lần sửa file. Hook báo "KB LỖI" thì sửa nguồn theo nội dung lỗi, không sửa `graph.json`.
- Phiên chính là coordinator, chỉ điều phối. Code giao cho subagent qua Agent tool với `isolation: "worktree"`, kể cả task tuần tự. Hook `PreToolUse` (`.claude/hooks/coordinator-guard.sh`) chặn phiên chính sửa code ở checkout chính. Thực hiện kế hoạch bằng skill `superpowers:subagent-driven-development`.
- Mỗi subagent chỉ ghi vào thư mục của vai trò mình (docs/harness/task-graph.md, mục 3).
- Verifier nằm ở `.claude/agents/`: `physics-verifier`, `determinism-verifier`, `security-verifier`. Gọi verifier ở context riêng, không tự soát code mình vừa viết.

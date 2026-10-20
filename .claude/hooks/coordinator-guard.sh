#!/bin/sh
# PreToolUse (Edit|Write|MultiEdit|NotebookEdit): phiên chính chỉ điều phối (17.2).
# Chặn sửa code sản phẩm trong checkout chính; subagent sửa trong git worktree riêng
# (.claude/worktrees/...) nên không bị chặn. Tắt tạm bằng /hooks nếu người dùng cho phép.
f=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
rel=${f#"$root"/}
[ "$rel" = "$f" ] && exit 0   # ngoài repo: không quản
case "$rel" in
  spider/*|tests/*|tools/*|web/*|blender/*|models/*|pyproject.toml|uv.lock)
    echo "Chặn: phiên chính chỉ điều phối (AGENTS.md luật 7, quyết định 17.2). Giao '$rel' cho subagent implementer/worker chạy với isolation: \"worktree\"." >&2
    exit 2;;
esac
exit 0

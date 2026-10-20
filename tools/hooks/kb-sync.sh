#!/bin/sh
# Hook sau mỗi lần agent sửa file (Claude Code và Codex, PostToolUse).
# Dựng lại knowledge graph. Nếu nguồn sai schema thì trả lỗi về cho agent sửa (exit 2).
# Im lặng khi thành công.
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$PATH"
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 0
out=$(uv run -q tools/kb.py build 2>&1) && exit 0
printf '%s\n' "$out" >&2
exit 2

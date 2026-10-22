#!/bin/sh
# PostToolUse (Bash): nhắc coordinator để lại chất liệu cho blog (20.12).
# - gộp task (`git merge`)         -> ghi beat vào docs/journal/notes/<version>.md nếu có chuyện đáng kể
# - đánh dấu gate (`git tag ... gN`) -> chụp media, viết note gate, giao journal-writer viết bài nháp
# Hook chỉ nhắc, không tự viết bài và không đăng: bài lên site chỉ khi người dùng duyệt (20.8).
python3 -c '
import json, re, sys
cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
git = r"\bgit(?:\s+-C\s+\S+)?\s+"   # lệnh con ngay sau `git` (hoặc `git -C DIR`)
gate = re.search(git + r"tag\b[^;&|]*\b(g\d+)\b", cmd)
if gate:
    g = gate.group(1)
    msg = (f"Gate {g} vừa được đánh dấu. Theo task-graph mục \"Khi qua gate\": "
           f"chụp media vào docs/journal/media/{g}/ (3 lệnh), viết docs/journal/notes/{g}.md, "
           f"rồi giao journal-writer viết bài nháp vào docs/journal/_drafts/. Không chuyển sang posts/ khi người dùng chưa duyệt.")
elif re.search(git + r"merge\b", cmd):
    msg = ("Vừa gộp một task. Theo task-graph mục 7: có chuyện đáng kể cho blog không "
           "(vấn đề của agent, vấn đề của người, ý tưởng)? Có thì ghi một beat theo docs/journal/templates/note.md "
           "vào docs/journal/notes/<version hiện tại>.md, kèm bằng chứng công khai (mã quyết định, commit trên main, L-NNN).")
else:
    sys.exit(0)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}, ensure_ascii=False))
'

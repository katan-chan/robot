# Blog nhật ký thiết kế Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Blog tiếng Anh `https://katan-chan.github.io/robot/journal/` kể quá trình làm robot nhện. Chất liệu (notes, media theo gate, reference, mẫu) nằm trong `docs/journal/`, và harness tự để lại chất liệu sau mỗi task và mỗi gate.

**Architecture:**
- GitHub Pages dựng `main:/docs` bằng Jekyll mặc định, không có build riêng.
- Bài là các trang thường trong `docs/journal/posts/`. Trang `journal/index.md` liệt kê chúng bằng Liquid.
- Bài nháp ở `docs/journal/_drafts/`. Jekyll bỏ qua thư mục bắt đầu bằng `_`.
- Video MuJoCo là các khung hình từ `mujoco.Renderer`, đẩy qua `ffmpeg` (binary hệ thống) ra mp4 H.264.

**Tech Stack:** Python 3.12 qua `uv`; `mujoco` (đã ghim, không đổi); `ffmpeg`/`ffprobe` 9.0.1 ở `/opt/homebrew/bin`; GitHub Pages (Jekyll 3.x, theme `minima`); `gh` CLI (đăng nhập `katan-chan`).

**Spec:** `docs/superpowers/specs/2026-10-22-blog-journal-design.md`

## Global Constraints

- Không thêm dependency Python. `ffmpeg` gọi qua `subprocess`.
- Mỗi clip mp4 H.264 dài tối đa khoảng 20 s và không quá 10 MB.
- Quay video không chạy `mj_step` và không đụng `MjData` của lần chạy thật (luật 3).
- Bài, notes và templates viết bằng tiếng Anh. Mỗi beat có tóm tắt tiếng Anh tự đứng được.
- Không commit video của người khác. `reference/` chỉ chứa link.
- Phân quyền ghi:
  - **coordinator** ghi `docs/journal/notes/`, `docs/journal/media/`, `docs/journal/reference/`, `docs/journal/templates/`, `docs/journal/index.md`, `docs/_config.yml`, `docs/index.md`.
  - **journal-writer** ghi `docs/journal/_drafts/`, `docs/journal/posts/`.
  - **implementer** ghi `spider/sim/`, `spider/model/`, `tests/test_view.py`.
- **Cổng người dùng.** Hỏi người dùng ngay trước mỗi bước sau: viết lại lịch sử git, tạo repo công khai `katan-chan/robot`, push, bật Pages.
- Email mới `lebinhminh_t67@hus.edu.vn` chỉ đặt cho repo này, không đặt `--global`.
- Mọi commit phải qua hook pre-commit (`kb.py check` + `selftest`).
- Không có cú pháp Liquid (cặp ngoặc nhọn kép, hoặc ngoặc nhọn kèm `%`) trong `docs/`. Ngoại lệ duy nhất là `docs/journal/index.md`.

## Review Focus

1. **Máy không có `ffmpeg`.** Kỳ vọng: `orbit_video` báo `RuntimeError` có chữ "ffmpeg", không treo, không để lại file mp4 hỏng. Test ở Task 1.
2. **Video 720p vượt bộ đệm offscreen mặc định 640×480 của MuJoCo.** Kỳ vọng: model dựng sẵn bộ đệm đủ 1280×720, nên `Renderer(m, 720, 1280)` không lỗi. Test ở Task 1.
3. **Có tài liệu mới trong `docs/` chứa cú pháp Liquid.** Kỳ vọng: site vẫn build được. Lệnh grep ở Task 2 và Task 6 chặn trước khi push.
4. **Link ảnh hay video trong bài sai `baseurl` (`/robot`).** Kỳ vọng: bài mở trên Pages vẫn thấy media. Task 5 dùng đường dẫn tương đối. Task 6 kiểm bằng `curl` trên site thật.
5. **Lịch sử git còn token hoặc email cũ.** Kỳ vọng: quét ra 0 kết quả trước khi push. Kiểm ở Task 6.

---

### Task 1: Lệnh quay video xoay quanh robot [implementer, worktree]

**Files:**
- Modify: `spider/sim/view.py` (thêm `orbit_video`, cờ `--video`)
- Modify: `spider/model/build.py`: đặt bộ đệm offscreen trong spec, `spec.visual.global_.offwidth = 1280` và `offheight = 720`. Chỉ đổi phần hiển thị, không đổi vật lý.
- Test: `tests/test_view.py`

**Interfaces:**
- Consumes: `build_model(export_dir) -> mujoco.MjModel`, `_data(m, keyframe)`, `VIEWS`, fixture `model` trong `tests/test_view.py`.
- Produces: `orbit_video(m: mujoco.MjModel, out: Path, keyframe: str = "stand", seconds: float = 8, fps: int = 30, size: tuple[int, int] = (720, 1280), return_frames: bool = False) -> Path | tuple[Path, list[np.ndarray]]`, và CLI `uv run python -m spider.sim.view --video OUT.mp4 [--keyframe stand]`.

- [ ] **Step 1: Viết test hỏng**

```python
import json, subprocess
from spider.sim.view import orbit_video

def _probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,width,height,nb_frames", "-of", "json", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"][0]

def test_orbit_video(model, tmp_path):
    p = orbit_video(model, tmp_path / "orbit.mp4", seconds=2, fps=15)
    s = _probe(p)
    assert (s["codec_name"], s["width"], s["height"]) == ("h264", 1280, 720)
    assert int(s["nb_frames"]) == 30
    assert p.stat().st_size < 10 * 1024 * 1024

def test_orbit_video_no_physics(model, tmp_path):
    # chỉ render: robot đứng yên, camera quay đúng 360°, nên khung đầu ≈ khung cuối (robot không đổ)
    frames = orbit_video(model, tmp_path / "o.mp4", seconds=1, fps=12, return_frames=True)[1]
    assert np.abs(frames[0].astype(float) - frames[-1].astype(float)).mean() < 8
    assert np.abs(frames[0].astype(float) - frames[len(frames) // 2].astype(float)).mean() > 8

def test_orbit_video_without_ffmpeg(model, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/nonexistent")
    with pytest.raises(RuntimeError, match="ffmpeg"):
        orbit_video(model, tmp_path / "x.mp4", seconds=1)
    assert not (tmp_path / "x.mp4").exists()
```

Khi `return_frames=True`, hàm trả `(path, list[np.ndarray])`.

- [ ] **Step 2: Chạy test, phải hỏng**

Run: `uv run pytest tests/test_view.py -k orbit -v`
Expected: FAIL, `ImportError: cannot import name 'orbit_video'`

- [ ] **Step 3: Viết `orbit_video` trong `spider/sim/view.py` và đặt bộ đệm offscreen trong `build.py`**

Hướng làm:
- Dùng `shutil.which("ffmpeg")`. Không có thì `raise RuntimeError("ffmpeg not found on PATH")` trước khi mở file.
- Khung hình đầu tiên lấy góc azimuth của `VIEWS["iso"]`. Azimuth tăng đều `360 * i / n` với `n = round(seconds * fps)`, khung cuối trùng góc khung đầu. Dùng `camera()` cho lookat và distance.
- Đẩy RGB thô vào stdin của `ffmpeg -y -f rawvideo -pix_fmt rgb24 -s WxH -r FPS -i - -c:v libx264 -pix_fmt yuv420p -crf 28 -movflags +faststart OUT`. Nếu ffmpeg trả mã khác 0 thì xoá `OUT`.
- Thêm vào `main()` cờ `--video PATH`, in ra đường dẫn file.

- [ ] **Step 4: Chạy test, phải qua**

Run: `uv run pytest -q`
Expected: tất cả PASS, kể cả `test_snapshot*` cũ.

- [ ] **Step 5: Commit**

```bash
git add spider/sim/view.py spider/model/build.py tests/test_view.py
git commit -m "feat(sim): orbit video of the model via ffmpeg (journal media)"
```

---

### Task 2: Khung `docs/journal/`, cấu hình Pages, nối harness [coordinator]

Task này làm song song với Task 1, vì chỉ đụng tài liệu.

**Files:**
- Create: `docs/decisions/20-blog-nhat-ky.md`, theo khuôn file 18: bảng quyết định 20.1–20.N. Nội dung chép từ spec mục 3–4.8: blog, giọng kể, một repo công khai, cấu trúc thư mục, beat, hai bước harness, `_drafts`, vai trò journal-writer, Pages `main:/docs`, đổi email.
- Create:
  - `docs/_config.yml`: `title: Spider Robot Journal`, `baseurl: /robot`, `theme: minima`, `exclude: [kb/graph.json]`.
  - `docs/index.md`: một dòng giới thiệu kèm link `journal/`.
  - `docs/journal/index.md`: lời giới thiệu blog bằng tiếng Anh, và danh sách bài lấy bằng `site.pages | where_exp: "p", "p.path contains 'journal/posts/'" | sort: "date" | reverse`.
- Create: `docs/journal/templates/note.md` (khuôn beat theo spec 4.2) và `docs/journal/templates/post.md`. Khuôn bài có front matter `title`, `date`, `layout: post`, và 8 phần theo spec 4.4.
- Create: `docs/journal/reference/README.md`, gồm 2 phần:
  - "Motion": robot nhện hoặc quadruped thật, nhện thật bò.
  - "Storytelling": devlog hay.
  Mỗi link một dòng ghi "học gì". Agent tìm link bằng WebSearch, mỗi phần 3–6 link, mở thử từng link trước khi ghi.
- Create: `docs/journal/notes/.gitkeep`, `docs/journal/media/.gitkeep`.
- Modify:
  - `docs/harness/task-graph.md`: bảng mục 3 thêm dòng journal-writer, dòng coordinator thêm các đường dẫn journal. Mục 7 thêm câu hỏi beat. Thêm mục "Khi qua gate" ghi 3 lệnh chụp ở Task 4.
  - `docs/kb/curated.toml`: thêm `role:journal-writer`. `WRITES` có các đường dẫn theo Global Constraints. Nối quyết định 20.x vào role và harness.
  - `harness.toml`: thêm `docs/journal/` vào `components.memory.paths`.
  - `AGENTS.md`: bảng "Nguồn sự thật" thêm dòng Blog, mục "Lệnh" thêm lệnh `--video`.

- [ ] **Step 1: Viết các file trên**
- [ ] **Step 2: Kiểm KB**

Run: `uv run tools/kb.py check && uv run tools/kb.py selftest && uv run tools/kb.py show 20.1`
Expected: `KB OK`; selftest qua; 20.1 có cạnh tới `role:journal-writer` hoặc `harness:memory`.

- [ ] **Step 3: Kiểm Liquid**

Run: `grep -rlE '[{][{]|[{]%' docs AGENTS.md | grep -v '^docs/journal/index.md$'`
Expected: không in gì.

- [ ] **Step 4: Commit**

```bash
git add docs harness.toml AGENTS.md
git commit -m "docs(journal): blog skeleton, Pages config, decision 19, harness steps"
```

---

### Task 3: Notes bù cho brainstorm và G1 [coordinator]

Task này làm song song với Task 1.

**Files:**
- Create: `docs/journal/notes/brainstorm.md`, `docs/journal/notes/g1.md`, theo `templates/note.md`.

Nguồn đọc:
- `docs/decisions/brainstorm-log.md`, `docs/decisions/01–18`, đặc biệt các dòng "Đã thay" và mục "Kiểm tra thực tế".
- `docs/harness/lessons.md`.
- `git log --format='%h %ad %s' --date=short`.

Các beat bắt buộc:

| File | Beat (loại) | Bằng chứng |
|---|---|---|
| brainstorm | Stack đổi hai lần: Blender→MJCF, sang tham số + Python, rồi quay lại Blender (human-problem) | 3.1, 3.2, 18.1 |
| brainstorm | "Dự án nhỏ, chat là đủ" phải đổi (human-problem) | 5.5 |
| brainstorm | Xem G1 bằng MuJoCo hay Blender (idea) | 16.4 → 18.3 |
| brainstorm | Phiên chính chỉ điều phối, có hook chặn (agent-problem) | 17.2, 17.5 |
| g1 | Review phát hiện actuator `pid`/`slewmax` không tồn tại (agent-problem) | bước 9 |
| g1 | Tấm thân làm mỏng cho đủ khối lượng (idea) | c121e68 |
| g1 | Review từng task đều Approved mà camera vẫn lệch (agent-problem) | L-004, c8d0d6e |
| g1 | Các fix trong G1 final review (agent-problem) | các commit "(G1 final review)" |

Mỗi beat ghi mã commit dạng 7 ký tự. Task 6 sẽ thay các mã này sau khi viết lại lịch sử.

- [ ] **Step 1: Viết hai file**
- [ ] **Step 2: Kiểm**

Run: `grep -c '^## ' docs/journal/notes/brainstorm.md docs/journal/notes/g1.md && uv run tools/kb.py check`
Expected: brainstorm ≥ 4, g1 ≥ 4; `KB OK`.

- [ ] **Step 3: Commit**

```bash
git add docs/journal/notes
git commit -m "docs(journal): backfill notes for brainstorm and G1"
```

---

### Task 4: Media cho G1 và brainstorm [coordinator, sau khi gộp Task 1]

**Interfaces:**
- Consumes: CLI `--video` của Task 1; `tools/blender render`; `--snapshot`.
- Produces: `docs/journal/media/g1/{blender,mujoco}/{front,side,top,iso}.png`, `docs/journal/media/g1/orbit.mp4`, `docs/journal/media/brainstorm/spider-reference.png`.

- [ ] **Step 1: Chụp và quay**

```bash
tools/blender export
tools/blender render --out docs/journal/media/g1/blender
uv run python -m spider.sim.view --snapshot docs/journal/media/g1/mujoco --keyframe stand
uv run python -m spider.sim.view --video docs/journal/media/g1/orbit.mp4 --keyframe stand
mkdir -p docs/journal/media/brainstorm && cp docs/reference/spider-reference.png docs/journal/media/brainstorm/
```

- [ ] **Step 2: Kiểm**

Run: `ls -la docs/journal/media/g1/*/ docs/journal/media/g1/orbit.mp4 && ffprobe -v error -show_entries format=duration -of csv=p=0 docs/journal/media/g1/orbit.mp4`
Expected: 8 file PNG; mp4 dưới 10 MB; duration khoảng 8.

- [ ] **Step 3: Xem video**

Mở video bằng `open docs/journal/media/g1/orbit.mp4`. Robot phải đứng yên và camera phải quay đủ một vòng.

- [ ] **Step 4: Commit**

```bash
git add docs/journal/media
git commit -m "docs(journal): G1 and brainstorm media"
```

---

### Task 5: Hai bài nháp [journal-writer, worktree, sau Task 3 và 4]

**Files:**
- Create: `docs/journal/_drafts/2026-10-20-from-a-photo-to-eighteen-decisions.md`, về brainstorm.
- Create: `docs/journal/_drafts/2026-10-21-g1-the-robot-exists.md`, về G1.

Slug là *gợi ý*, writer được đổi.

Nội dung giao cho journal-writer:
- spec mục 1 (giọng kể), `templates/post.md`, notes tương ứng, và media.
- Dài 900–1500 từ, tiếng Anh, người đọc không cần biết robot.
- Mỗi bài có ít nhất 2 beat `agent-problem` và 1 beat `human-problem`, có media nhúng.
- Video nhúng bằng `<video src="../media/g1/orbit.mp4" controls muted loop playsinline></video>`.
- Ảnh dùng đường dẫn tương đối `../media/...`.
- Link tới quyết định hay commit dùng URL đầy đủ `https://github.com/katan-chan/robot/blob/main/...`.

- [ ] **Step 1: Viết hai bài**
- [ ] **Step 2: Kiểm**

Run: `for f in docs/journal/_drafts/*.md; do wc -w "$f"; grep -o '\.\./media/[^)" ]*' "$f" | sed 's#^\.\./#docs/journal/#' | xargs ls >/dev/null; done; grep -lE '[{][{]|[{]%' docs/journal/_drafts/*.md`
Expected: mỗi bài 900–1500 từ; mọi file media tồn tại; grep Liquid không in gì.

- [ ] **Step 3: Commit, rồi coordinator gộp `--ff-only`**
- [ ] **Step 4: Cổng người dùng.** Người dùng đọc hai bài. Có góp ý thì sửa. Duyệt xong thì journal-writer `git mv` bài sang `docs/journal/posts/`, thêm `layout: post` nếu thiếu, rồi commit.

---

### Task 6: Dọn, quét, đổi email, xuất bản [coordinator; mỗi bước có ★ phải hỏi người dùng trước]

- [ ] **Step 1: Dọn worktree và nhánh sót**

Run: `git worktree list && git branch`
Gỡ mọi worktree `.claude/worktrees/*` đã gộp hoặc bỏ, bằng `git worktree remove --force` (phải `unlock` trước nếu bị khoá). Xoá các nhánh `worktree-agent-*`.
Expected: chỉ còn `main`.

- [ ] **Step 2: Quét secret trên toàn bộ lịch sử**

Run: `git log --all -p | grep -nE 'gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|xox[baprs]-|tskey-' ; git log --all -p | grep -niE '(token|secret|password|api[_-]?key)\s*[=:]\s*["'"'"'][^"'"'"']{8,}'`
Expected: không in gì. Có kết quả thì **dừng** và báo người dùng.

- [ ] **Step 3: ★ Backup rồi viết lại email**

```bash
git bundle create ../robot-backup-2026-10-22.bundle --all
git config user.email lebinhminh_t67@hus.edu.vn
S=<scratchpad của phiên>
git rev-list --reverse main > $S/old.txt
git filter-branch --env-filter '
for v in AUTHOR COMMITTER; do
  eval e=\$GIT_${v}_EMAIL
  [ "$e" = "ad@ads-MacBook-Pro.local" ] && export GIT_${v}_EMAIL=lebinhminh_t67@hus.edu.vn
done' -- --all
git rev-list --reverse main > $S/new.txt
```

Expected: `git log --all --format='%ae %ce' | sort -u | grep -c ads-MacBook-Pro` in `0`.

- [ ] **Step 4: Cập nhật mã commit trong tài liệu**

Ghép `$S/old.txt` với `$S/new.txt` theo dòng. Với mỗi mã 7 ký tự cũ xuất hiện trong `docs/` hoặc `AGENTS.md`, thay bằng 7 ký tự mới.
Run: `grep -rhoE '\b[0-9a-f]{7}\b' docs AGENTS.md | sort -u | while read h; do git cat-file -e "$h^{commit}" 2>/dev/null || echo "MISSING $h"; done`
Expected: các mã từng là commit đều có trong lịch sử mới. Mã không phải commit (ví dụ màu hex) có thể vẫn báo MISSING; xem từng dòng.
Commit: `docs: remap commit ids after email rewrite`. Sau đó xoá `refs/original` bằng `git update-ref -d`.

- [ ] **Step 5: Kiểm Liquid lần cuối**

Run: `grep -rlE '[{][{]|[{]%' docs AGENTS.md | grep -v '^docs/journal/index.md$'`
Expected: không in gì.

- [ ] **Step 6: ★ Tạo repo công khai và push**

Run: `gh repo create katan-chan/robot --public --source . --remote origin --push`
Expected: in URL repo; `git ls-remote origin main` khớp `git rev-parse main`.

- [ ] **Step 7: ★ Bật Pages**

Run: `gh api -X POST repos/katan-chan/robot/pages -f 'source[branch]=main' -f 'source[path]=/docs'`
Sau đó chờ build xong: `gh api repos/katan-chan/robot/pages/builds/latest --jq .status` ra `built`.

- [ ] **Step 8: Kiểm site thật**

Run: `curl -sI https://katan-chan.github.io/robot/journal/ | head -1 && curl -sI https://katan-chan.github.io/robot/journal/media/g1/orbit.mp4 | head -1`
Expected: cả hai `HTTP/2 200`. Nếu đã có bài trong `posts/`, mở từng bài và `curl -sI` từng ảnh và video, tất cả phải 200.

- [ ] **Step 9: Bài học**

Có gì làm agent đi sai trong lúc làm thì ghi vào `docs/harness/lessons.md` (task-graph mục 7). Ghi beat vào `notes/g2.md` nếu có.
